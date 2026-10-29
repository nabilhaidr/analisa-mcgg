"""Pemeriksaan konsistensi laporan pertandingan data/<versi>/MATCH_<nama>.md/.html (pengganti check.py yang dulu dipakai
setelah mc_match.py tapi tidak pernah masuk git). Jalankan setelah laporan dibuat ulang atau diubah.

Pemakaian (Python sistem + requirements.txt, sama dengan mc_match.py):
  python check_match.py                          semua laporan MATCH di data versi terbaru
  python check_match.py 15_38 Kalea              hanya laporan yang namanya mengandung salah satu teks ini
  python check_match.py --version 1.3.24.344.1   data versi tertentu
Keluar dengan kode 1 bila ada kesalahan; peringatan saja tidak menggagalkan. Tiap laporan satu baris ringkasan (seperti
check.py lama): pkt = peringkat, HP = HP akhir, babak = babak pertama–terakhir timeline, n = jumlah babak, kalah = babak
kehilangan HP, nama = nama terbaca sebagai teks / baris papan akhir; kesalahan dan peringatan di bawahnya.
Tes: python -m pytest test_check_match.py

Kesalahan:
- md dan html berbeda (ringkasan, catatan otomatis, timeline, HP semua pemain, kejadian, papan akhir, catatan metode, waktu
  dibuat), atau gambar yang dirujuk tidak ada.
- Timeline sendiri: label babak tidak naik, HP awal di luar 0-100 atau naik, perubahan != HP awal babak berikutnya - HP awal,
  hasil ("kalah", "tidak kehilangan HP", "kalah, tereliminasi") tidak sesuai, kotak HP akhir / Babak terbaca tidak sesuai.
  Peringkat > 1 = tereliminasi di babak terakhir dengan HP sendiri; peringkat 1 = HP akhir > 0.
- Tabel HP: babak beda dengan timeline, baris sendiri beda dengan timeline, nilai naik, nama yang tidak ada di layar hasil
  (atau gambar namanya), catatan "Tidak ada di tabel" tidak sama dengan baris layar hasil yang tidak ada di tabel.
- Catatan otomatis != mc_match.insights() dari tabel laporan itu sendiri (catatan lama setelah kode berubah).
- Kejadian: jenis di luar mc_match.EVENTS, babak tidak dikenal, waktu mundur.
- Papan akhir: peringkat bukan 1..N, baris "(kamu)" tidak tepat satu / beda dengan kotak Peringkat, hero, unit panggilan
  atau kartu yang bukan nama ikon S<n>.json (mc_vision.icon_labels: kartu Ⅰ/Ⅱ/Ⅲ bergambar sama = satu nama), sinergi !=
  dihitung ulang dari hero unik (seperti mc_match.py).
Peringatan: babak terlewat di timeline, HP sendiri kosong di timeline (kecuali babak setelah tereliminasi), laporan tanpa
papan akhir, level kosong di papan akhir, nama "baris N" tanpa gambar, pemain yang di tabel HP bertahan lebih lama tapi
peringkatnya lebih buruk (babak terakhir tabel tidak dihitung: bacaannya sering bolong saat rekaman berakhir), gambar di
match_<nama>/ yang tidak dirujuk, ID/poin pertandingan tidak terbaca.
"""
import argparse
import html
import re
import sys

import mc_match
import mc_vision
from mc_common import DATA, latest_version, load_season, round_label
from mc_lineup import Game

IMG_MD = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
IMG_HTML = re.compile(r'<img [^>]*?src="([^"]+)"[^>]*>')
CHIP = re.compile(r'<span class="chip[^"]*"[^>]*>(?:<img [^>]*>)?(.*?)</span>')
STAMP_MD = re.compile(r"^_(Data game (\S+), Season (\d+) .*? · dibuat [\d-]+ [\d:]+)_$", re.M)
STAMP_HTML = re.compile(r'<p class="meta">(.*?)</p>')
KINDS = {kind for _, kind in mc_match.EVENTS}


def plain(cell):
    """Text of an HTML cell as md_table writes it: pictures as [img <src>], tags dropped, "|" as "/"."""
    cell = IMG_HTML.sub(lambda m: f"[img {html.unescape(m.group(1))}]", cell)
    return " ".join(html.unescape(re.sub(r"<[^>]+>", "", cell)).replace("|", "/").split())


def md_cell(cell):
    return " ".join(IMG_MD.sub(lambda m: f"[img {m.group(1)}]", cell).split())


def md_section(txt, title):
    m = re.search(rf"^## {re.escape(title)}\n\n(.*?)(?=^## |\Z)", txt, re.S | re.M)
    return m.group(1) if m else None


def md_rows(body):
    lines = [l for l in (body or "").splitlines() if l.startswith("|")]
    split = lambda l: [md_cell(c) for c in l.strip()[1:-1].split(" | ")]
    return (split(lines[0]), [split(l) for l in lines[2:]]) if len(lines) >= 2 else ([], [])


def md_list(body):
    return [l[2:] for l in (body or "").splitlines() if l.startswith("- ")]


def html_rows(sec):
    """(header texts, rows of cell HTML) of the table in one section."""
    rows = re.findall(r"<tr>(.*?)</tr>", sec or "", re.S)
    if not rows:
        return [], []
    head = [plain(c) for c in re.findall(r"<th>(.*?)</th>", rows[0], re.S)]
    return head, [re.findall(r"<td>(.*?)</td>", r, re.S) for r in rows[1:]]


def num(text):
    return int(text) if re.fullmatch(r"-?\d+", text or "") else None


def note_matches(text, want):
    """A note rebuilt from the report's tables equals the report's note. A player shown as a picture in the HP table
    ([img ...] here) is named by its HUD reading in the note ("Tereliminasi: ..."), so the picture matches any name."""
    parts = re.split(r"\[img [^\]]+\]", want)
    return text == want if len(parts) == 1 else re.fullmatch(".+?".join(map(re.escape, parts)), text) is not None


def check(md_path, seasons):
    """([errors], [warnings], {overview column: text}) of one report; main() prints the overview as one table row."""
    err, warn = [], []
    html_path = md_path.with_suffix(".html")
    if not html_path.exists():
        return [f"{html_path.name} tidak ada"], warn, {}
    txt, page = md_path.read_text(encoding="utf-8"), html_path.read_text(encoding="utf-8")
    secs = {html.unescape(k): v for k, v in re.findall(r"<section><h2>(.*?)</h2>(.*?)</section>", page, re.S)}

    stamp = STAMP_MD.search(txt)
    if not stamp:
        return ["baris waktu dibuat (_Data game ..._) tidak ada di md"], warn, {}
    meta = STAMP_HTML.search(page)
    if not meta or html.unescape(meta.group(1)) != stamp.group(1):
        err.append(f"waktu dibuat md/html beda: {stamp.group(1)!r} vs {meta and meta.group(1)!r}")
    key = (int(stamp.group(3)), stamp.group(2))
    if key not in seasons:
        d, data = load_season(*key)
        labels = lambda kind: set(mc_vision.icon_labels(d, data, kind))  # cards sharing a picture are one name
        seasons[key] = (Game(d), labels("hero") | labels("summon"), labels("card"))
    game, unit_names, card_names = seasons[key]

    # Ringkasan
    boxes = dict(re.findall(r"^- \*\*(.+?):\*\* (.*)$", txt.split("\n## ", 1)[0], re.M))
    hboxes = {html.unescape(k): html.unescape(v) for k, v in re.findall(r"<h4>(.*?)</h4><p>(.*?)</p>", secs.get("Ringkasan", ""))}
    if boxes != hboxes:
        err.append(f"kotak Ringkasan md/html beda: {boxes} vs {hboxes}")
    pm = re.search(r"^- Pemain: (.*)$", txt, re.M)
    me = pm.group(1) if pm and pm.group(1) != "-" else None
    hp_me = re.search(r'<p class="muted small">Pemain: (.*?)(?: · tata letak [^<]*)?</p>', secs.get("Ringkasan", ""))
    if not pm or not hp_me or html.unescape(hp_me.group(1)) != pm.group(1):
        err.append("baris Pemain md/html beda atau tidak ada")
    rank = num(boxes.get("Peringkat"))
    row = {"pkt": boxes.get("Peringkat", "-"), "HP": boxes.get("HP akhir", "-")}
    if not re.search(r"ID \d{15,20} · poin \d+ \([+-]\d+\)", boxes.get("Pertandingan", "")):
        warn.append(f"ID/poin pertandingan tidak terbaca: {boxes.get('Pertandingan')}")

    # md and html carry the same tables and lists
    def same_table(title, cols_html=None):
        mh, mrows = md_rows(md_section(txt, title))
        hh, hrows = html_rows(secs.get(title))
        hrows = [[(cols_html[i](c) if cols_html and i in cols_html else plain(c)) for i, c in enumerate(r)] for r in hrows]
        if (mh, mrows) != (hh, hrows):
            bad = next((i for i, (a, b) in enumerate(zip(mrows, hrows)) if a != b), min(len(mrows), len(hrows)))
            err.append(f"tabel {title!r} md/html beda (header {mh == hh}, baris {len(mrows)} vs {len(hrows)}, pertama beda "
                       f"di baris {bad + 1}: {mrows[bad] if bad < len(mrows) else '-'} vs {hrows[bad] if bad < len(hrows) else '-'})")
        return mh, mrows

    notes = md_list(md_section(txt, "Catatan otomatis"))
    hnotes = [(c, html.unescape(t)) for c, t in re.findall(r'<li(?: class="([^"]*)")?>(.*?)</li>', secs.get("Catatan otomatis", ""))]
    if notes != [t for _, t in hnotes]:
        err.append("Catatan otomatis md/html beda")
    timeline_title = next((t for t in secs if t.startswith("Timeline (")), None)
    _, tl = same_table(timeline_title) if timeline_title else ([], [])
    hp_head, hp = same_table("HP semua pemain")
    _, events = same_table("Kejadian")
    joined = lambda c: ", ".join(html.unescape(x) for x in CHIP.findall(c))
    _, board = same_table("Papan akhir (layar hasil)", {3: joined, 4: joined, 5: joined})
    method = md_list(md_section(txt, "Catatan metode"))
    if method != [html.unescape(x) for x in re.findall(r"<li>(.*?)</li>", secs.get("Catatan metode", ""), re.S)]:
        err.append("Catatan metode md/html beda")
    gone_md = next((l for l in (md_section(txt, "HP semua pemain") or "").splitlines() if l.startswith("Tidak ada di tabel")), None)
    gone_html = re.search(r'<p class="muted small">(Tidak ada di tabel.*?)</p>', secs.get("HP semua pemain", ""), re.S)
    if gone_md != (html.unescape(gone_html.group(1)) if gone_html else None):
        err.append("catatan 'Tidak ada di tabel' md/html beda")

    # pictures
    folder = md_path.parent
    refs = set(IMG_MD.findall(txt)) | {html.unescape(s) for s in IMG_HTML.findall(page)}
    for src in sorted(refs):
        if not (folder / src).is_file():
            err.append(f"gambar tidak ada: {src}")
    assets = folder / f"match_{md_path.stem[len('MATCH_'):]}"
    if assets.is_dir():
        for f in sorted(assets.iterdir()):
            if f"{assets.name}/{f.name}" not in refs:
                warn.append(f"gambar tidak dirujuk: {assets.name}/{f.name}")

    # own timeline
    rounds = []
    if tl:
        labels = [r[0] for r in tl]
        numbers = []
        for lab in labels:
            try:
                numbers.append(mc_match.round_number(lab))
            except (ValueError, IndexError):
                err.append(f"label babak tidak dikenal: {lab}")
                numbers.append(None)
        if None not in numbers:
            if any(b <= a for a, b in zip(numbers, numbers[1:])):
                err.append(f"label babak tidak naik: {labels}")
            elif numbers[-1] - numbers[0] + 1 != len(numbers):
                miss = sorted(set(range(numbers[0], numbers[-1] + 1)) - set(numbers))
                warn.append("babak terlewat di timeline: " + ", ".join(round_label(n) for n in miss))
        hps = [num(r[1]) for r in tl]
        known = [v for v in hps if v is not None]
        if any(not 0 <= v <= 100 for v in known) or any(b > a for a, b in zip(known, known[1:])):
            err.append(f"HP awal di luar 0-100 atau naik: {[r[1] for r in tl]}")
        out_at = None
        for i, r in enumerate(tl):
            m = re.fullmatch(r"([+-]\d+) (kalah, tereliminasi|kalah|tidak kehilangan HP)", r[2])
            if r[2] == "-":
                if i + 1 < len(tl) and hps[i] is not None and hps[i + 1] is not None:
                    err.append(f"{r[0]}: perubahan kosong padahal HP awal babak ini dan berikutnya ada")
                continue
            if not m:
                err.append(f"{r[0]}: kolom Perubahan tidak dikenal: {r[2]!r}")
                continue
            dlt, res = int(m.group(1)), m.group(2)
            if res == "kalah, tereliminasi":
                out_at = i
                if hps[i] is None or dlt != -hps[i]:
                    err.append(f"{r[0]}: tereliminasi harus -HP awal ({hps[i]}), tertulis {dlt}")
            elif (dlt < 0) != (res == "kalah") or (dlt == 0) != (res == "tidak kehilangan HP"):
                err.append(f"{r[0]}: perubahan {dlt:+d} tidak cocok dengan '{res}'")
            elif i + 1 < len(tl) and None not in (hps[i], hps[i + 1]) and dlt != hps[i + 1] - hps[i]:
                err.append(f"{r[0]}: perubahan {dlt:+d} != {hps[i + 1]} - {hps[i]}")
        empty = [r[0] for i, (r, v) in enumerate(zip(tl, hps)) if v is None and (out_at is None or i < out_at)]
        if empty:  # after the elimination round there is no own HP to read
            warn.append("HP sendiri kosong di timeline: " + ", ".join(empty))
        mine = [i for i, v in enumerate(hps) if v is not None]
        if rank and rank > 1 and mine and out_at != mine[-1]:
            err.append(f"peringkat {rank} tapi tidak tereliminasi di babak terakhir dengan HP sendiri ({tl[mine[-1]][0]})")
        if (rank == 1 or not rank) and out_at is not None:
            err.append(f"tertulis tereliminasi di {tl[out_at][0]} padahal peringkat {rank}")
        end = 0 if out_at is not None else (hps[mine[-1]] if mine else None)
        if mine and str(end) != boxes.get("HP akhir"):
            err.append(f"kotak HP akhir {boxes.get('HP akhir')} != {end}")
        if rank == 1 and end is not None and end <= 0:
            err.append("juara tapi HP akhir 0")
        losses = sum(1 for r in tl if re.match(r"-\d+ ", r[2]) and int(r[2].split()[0]) < 0)
        row.update(babak=f"{labels[0]}–{labels[-1]}", n=str(len(tl)), kalah=str(losses))
        want = f"{labels[0]} – {labels[-1]} ({len(tl)} babak), kehilangan HP di {losses} babak"
        if boxes.get("Babak terbaca") != want:
            err.append(f"kotak Babak terbaca {boxes.get('Babak terbaca')!r} != {want!r}")

        # all players
        if hp_head[1:] != labels:
            err.append("babak tabel HP beda dengan timeline")
        rows = {}
        for r in hp:
            vals = [num(c) for c in r[1:]]
            rows[r[0]] = vals
            seen = [v for v in vals if v is not None]
            if any(not 0 <= v <= 100 for v in seen) or any(b > a for a, b in zip(seen, seen[1:])):
                err.append(f"tabel HP {r[0]}: nilai di luar 0-100 atau naik")
        if me in rows and rows[me] != hps:
            err.append(f"tabel HP baris {me} beda dengan timeline")
        for i, lab in enumerate(labels):
            start = {p: v[i] for p, v in rows.items() if i < len(v) and v[i] is not None}
            rounds.append({"round": numbers[i], "label": lab, "start": start, "gold": num(tl[i][3]), "level": num(tl[i][4]),
                           "delta": {}})
        for cur, nxt in zip(rounds, rounds[1:]):
            cur["delta"] = {p: nxt["start"][p] - v for p, v in cur["start"].items() if p in nxt["start"]}
        if rank and rank > 1 and me:  # as in mc_match.main: eliminated after the last round with own HP
            last = next((r for r in reversed(rounds) if me in r["start"]), None)
            if last and me not in last["delta"]:
                last["delta"][me] = -last["start"][me]

    # final board
    board_names = []
    if board:
        ranks = [num(r[0]) for r in board]
        if ranks != list(range(1, len(board) + 1)) or len(board) > 8:
            err.append(f"peringkat papan akhir bukan 1..N: {[r[0] for r in board]}")
        own = [r for r in board if r[1].endswith(" (kamu)")]
        if me and rank and (len(own) != 1 or num(own[0][0]) != rank):
            err.append(f"baris (kamu) di papan akhir: {[r[0] for r in own]}, kotak Peringkat {rank}")
        hrows = html_rows(secs.get("Papan akhir (layar hasil)"))[1]
        for r, h in zip(board, hrows):
            name = r[1].removesuffix(" (kamu)")
            board_names.append((num(r[0]), name))
            if re.fullmatch(r"baris \d+", name):
                warn.append(f"papan akhir peringkat {r[0]}: nama 'baris N' tanpa gambar")
            lv = num(r[2])
            if lv is None:
                warn.append(f"papan akhir peringkat {r[0]} ({name}): level kosong")
            elif not 1 <= lv <= 10:
                err.append(f"papan akhir peringkat {r[0]}: level {lv}")
            units = [html.unescape(x) for x in CHIP.findall(h[3])]
            odd = [u for u in units if u not in unit_names]
            odd += [c for c in map(html.unescape, CHIP.findall(h[4])) if c not in card_names]
            if odd:
                err.append(f"papan akhir peringkat {r[0]}: hero/kartu bukan nama ikon S{key[0]}.json: {odd}")
            unique = list(dict.fromkeys(u for u in units if u in game.H))
            counts = game.counts(unique, [])
            want = ", ".join(f"{s} {counts[s]}" for s in game.active_tiers(unique, []))
            if r[5] != want:
                err.append(f"papan akhir peringkat {r[0]} ({name}): sinergi {r[5]!r} != dihitung ulang {want!r}")
        read = [n for _, n in board_names if not n.startswith("[img ") and not re.fullmatch(r"baris \d+", n)]
        row["nama"] = f"{len(read)}/{len(board)}"
    else:
        warn.append("tanpa papan akhir: tidak ada layar hasil yang terbaca")

    # HP table names against the result screen
    if hp and board_names:
        names = {n for _, n in board_names}
        for p in (r[0] for r in hp):
            if p not in names:
                err.append(f"tabel HP: {p!r} tidak ada di papan akhir")
        missing = [(rk, n) for rk, n in board_names if n not in {r[0] for r in hp}]
        if missing:
            want = ", ".join(f"peringkat {rk} " + ("(nama berupa gambar)" if n.startswith("[img ") else n) for rk, n in missing)
            if not gone_md or not gone_md.endswith(f": {want}."):
                err.append(f"catatan 'Tidak ada di tabel' harus menyebut: {want}")
        elif gone_md:
            err.append("catatan 'Tidak ada di tabel' padahal semua baris layar hasil ada di tabel")
        rank_of = {n: rk for rk, n in board_names}
        alive = {r[0]: max((i for i, c in enumerate(r[1:-1]) if (num(c) or 0) > 0), default=-1) for r in hp}
        for a in alive:
            for b in alive:
                if a in rank_of and b in rank_of and rank_of[a] < rank_of[b] and alive[a] < alive[b]:
                    warn.append(f"tabel HP: {b} (peringkat {rank_of[b]}) bertahan sampai {hp_head[alive[b] + 1]}, "
                                f"lebih lama dari {a} (peringkat {rank_of[a]}, sampai {hp_head[alive[a] + 1]})")

    # events and notes
    ev = []
    prev = -1
    for r in events:
        t = re.fullmatch(r"(\d+):(\d\d)", r[0])
        if r[2] not in KINDS:
            err.append(f"kejadian tidak dikenal: {r[2]!r} ({r[0]})")
        if not t or int(t.group(1)) * 60 + int(t.group(2)) < prev:
            err.append(f"waktu kejadian tidak dikenal atau mundur: {r[0]}")
        else:
            prev = int(t.group(1)) * 60 + int(t.group(2))
        try:
            rnd = mc_match.round_number(r[1]) if r[1] != "-" else None
        except (ValueError, IndexError):
            err.append(f"babak kejadian tidak dikenal: {r[1]}")
            rnd = None
        ev.append({"t": None, "round": rnd, "kind": r[2], "detail": r[3]})
    want = mc_match.insights(rounds, me, ev, rank) if (rounds or rank) else []
    if len(want) != len(hnotes) or not all(c == wc and note_matches(t, wt) for (c, t), (wc, wt) in zip(hnotes, want)):
        diff = [f"{t!r} -> {wt!r}" for (_, t), (_, wt) in zip(hnotes, want) if t != wt][:3]
        err.append(f"Catatan otomatis != mc_match.insights() ({len(hnotes)} vs {len(want)} baris) {'; '.join(diff)}")
    return err, warn, row


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Periksa konsistensi laporan MATCH_*.md/.html")
    ap.add_argument("names", nargs="*", help="hanya laporan yang namanya mengandung salah satu teks ini")
    ap.add_argument("--version", help="folder data/<versi>; default versi terbaru")
    args = ap.parse_args()
    folder = DATA / (args.version or latest_version())
    reports = [p for p in sorted(folder.glob("MATCH_*.md")) if not args.names or any(n in p.stem for n in args.names)]
    if not reports:
        sys.exit(f"Tidak ada laporan MATCH di {folder}")
    orphans = [p.name for p in sorted(folder.glob("MATCH_*.html")) if not p.with_suffix(".md").exists()]
    orphans += [p.name + "/" for p in sorted(folder.glob("match_*")) if p.is_dir()
                and not (folder / f"MATCH_{p.name[len('match_'):]}.md").exists()]
    seasons, n_err, n_warn = {}, 0, len(orphans)
    width = max(len(p.stem) - len("MATCH_") for p in reports)
    line = lambda status, name, row: (f"{status:5} {name:{width}}  {row.get('pkt', '-'):>3} {row.get('HP', '-'):>3}  "
                                      f"{row.get('babak', '-'):10} {row.get('n', '-'):>2} {row.get('kalah', '-'):>5} "
                                      f"{row.get('nama', '-'):>5}")
    print(line("", "laporan", {c: c for c in ("pkt", "HP", "babak", "n", "kalah", "nama")}))
    for p in reports:
        err, warn, row = check(p, seasons)
        n_err, n_warn = n_err + len(err), n_warn + len(warn)
        print(line("GAGAL" if err else "OK", p.stem[len("MATCH_"):], row) + (f"  ({len(warn)} peringatan)" if warn else ""))
        for e in err:
            print(f"      kesalahan: {e}")
        for w in warn:
            print(f"      peringatan: {w}")
    for o in orphans:
        print(f"peringatan: tanpa laporan .md: {o}")
    print(f"\n{len(reports)} laporan, {n_err} kesalahan, {n_warn} peringatan ({folder.relative_to(DATA.parent).as_posix()})")
    sys.exit(1 if n_err else 0)


if __name__ == "__main__":
    main()
