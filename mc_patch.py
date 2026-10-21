"""Analisa Patch Note dari screenshot "Update Patch" in-game -> data/<versi>/PATCH_<nama>.html/.md.

Pemakaian (Python sistem; OCR memakai ocr_screens.ps1 = OCR bawaan Windows, hasilnya di-cache per folder):
  python mc_patch.py "screenshot\\season 7\\update patch" --files 1881-1885 --name "Penyesuaian 20-10"
  python mc_patch.py shot1.png shot2.png --season 7
Opsi: --files 1881-1885,1890 (nomor di nama file "Screenshot (N)"), --name, --season, --version, --no-ocr (pakai ocr.json yang ada).

Isi laporan: setiap perubahan per bagian (Commander, Sinergi, Hero, Go Go Card, Equipment, ...) dengan panah in-game
(↑ buff, ↓ nerf, ~ penyesuaian), angka lama → baru (+ persen), status di data (sudah di file game / diterapkan server /
tercatat di server_patch.json), dampak ke sinergi, dan DRAF entri server_patch.json untuk perubahan server yang belum dicatat
(periksa dulu sebelum disalin; teks pengganti dicari otomatis di deskripsi file game).
Screenshot yang tumpang tindih (panel di-scroll) digabung: baris yang sama hanya dihitung sekali.
"""
import argparse
import json
import os
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

import mc_validate as V
from mc_common import HERE, Names, chip, esc, load_season, md_table, page, slug, stamp, table, write_report

SECTION = re.compile(r"Penyesuaian\s+(Commander|Sinergi|Hero|Go Go Card|Equipment|Kartu|Lainnya|Umum|Sistem|Mekanisme)", re.I)
HEADER = re.compile(r"^(?:[-•·]\S{0,2}\s+)?(.+?)\s*\(\s*([^()]{0,6})\s*\)\s*$")  # "-A Turret of Guardians (l)": OCR noise
# in-game arrows as Windows OCR reads them: ↑ -> "t", ↓ -> "I"/"l"/"J", ~ stays
ARROWS = {"t": "buff", "↑": "buff", "f": "buff", "i": "nerf", "l": "nerf", "j": "nerf", "↓": "nerf", "1": "nerf", "|": "nerf",
          "~": "adjust", "-": "adjust", "baru": "baru"}
ARROW_LABEL = {"buff": "↑ buff", "nerf": "↓ nerf", "adjust": "~ penyesuaian", "baru": "baru", None: "-"}
ARROW_CLASS = {"buff": "buff", "nerf": "nerf"}
PAIR = re.compile(r"(\d[\d.,]*(?:\s*/\s*\d[\d.,]*)*\s*%?)\s*(?:>>|»|>)\s*(\d[\d.,]*(?:\s*/\s*\d[\d.,]*)*\s*%?)")
GROUP = re.compile(r"\d[\d.,]*(?:/\d[\d.,]*)*%?")
STATS = ["Batas Mana Awal", "Batas Mana", "Hybrid ATK", "Physical ATK", "Magic ATK", "ATK Speed", "HP"]
UNIT_WORDS = {"Gold", "Physical", "Magic", "Hybrid", "True", "Total", "Mana", "Shield", "Echo", "Energy", "Hero", "Equipment",
              "Detik", "Babak", "Stack", "Basic"}  # capitalised words that follow a number inside one statement
KIND_OF_SECTION = {"commander": "Commander", "sinergi": "Sinergi", "hero": "Hero", "go go card": "Go Go Card", "kartu": "Go Go Card",
                   "equipment": "Equipment"}


# ------------------------------------------------------------------ input

def pick_files(paths, files):
    """Image files from the arguments; --files keeps names whose "(N)" number is in the given ranges."""
    wanted = set()
    for part in (files or "").split(","):
        if "-" in part:
            a, b = part.split("-")
            wanted |= set(range(int(a), int(b) + 1))
        elif part.strip():
            wanted.add(int(part))
    out = []
    for p in map(Path, paths):
        for f in (sorted(p.rglob("*")) if p.is_dir() else [p]):
            m = re.search(r"\((\d+)\)", f.name)
            if f.suffix.lower() in (".png", ".jpg", ".jpeg") and not (wanted and not (m and int(m.group(1)) in wanted)):
                out.append(f.resolve())
    return out


def ocr_lines(files, run_ocr):
    """{file: lines} (coordinates normalised to 1366x768 by mc_validate.load_ocr), OCR-ing each folder when needed."""
    shots = {}
    for folder in sorted({f.parent for f in files}):
        if run_ocr or not (folder / "ocr.json").exists():
            subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", str(HERE / "ocr_screens.ps1"), "-Folder", str(folder)],
                           check=True)
        loaded = V.load_ocr(folder)
        for f in files:
            if f.parent == folder and f.name in loaded:
                shots[f] = loaded[f.name]
    return shots


# ------------------------------------------------------------------ parsing

def add_line(lines, text):
    """Append an OCR line unless it repeats one already kept (scrolled screenshots); a longer reading replaces a cut one."""
    key = lambda s: re.sub(r"\W", "", s.lower())
    k = key(text)
    for i, old in enumerate(lines):
        if k in key(old):
            return
        if key(old) in k:
            lines[i] = text
            return
    lines.append(text)


def parse_entries(shots, known):
    """[{section, entity, arrow, lines}] in reading order; overlapping screenshots merged. A screenshot that starts in the
    middle of a section (scrolled) has no section title above its first items: those join the entry already seen."""
    entries, order = {}, []
    section, current = "Lainnya", None
    for f in sorted(shots, key=lambda p: (len(p.name), p.name)):
        titled = False
        for l in V.region(shots[f], 150, 768, 300, 1366):
            t = fix_ocr(l["t"].strip())
            m = SECTION.search(t)
            if m and len(t) < 40:
                section, titled = m.group(1).title(), True
                continue
            h = HEADER.match(t)
            raw = h.group(1).strip() if h and len(h.group(1)) <= 40 else (t if len(t) <= 40 and known.find(t, 0.9) else None)
            if raw:
                name = known.find(raw, 0.85) or raw
                marker = h.group(2).strip().lower() if h else ""
                arrow = ARROWS.get(marker) or ("baru" if "baru" in marker else None)
                key = (section, name)
                if not titled:  # continuation of the previous screenshot: reuse the latest entry with this name
                    key = next((k for k in reversed(order) if k[1] == name), key)
                    section = key[0]
                if key not in entries:
                    entries[key] = {"section": key[0], "entity": name, "arrow": arrow, "lines": []}
                    order.append(key)
                elif arrow and not entries[key]["arrow"]:
                    entries[key]["arrow"] = arrow
                current = key
                continue
            if current and l["x"] > 400 and not t.startswith(("Penyesuaian", "Patch")):
                add_line(entries[current]["lines"], t)
    return [entries[k] for k in order]


def statements(lines):
    """Join wrapped OCR lines, then split into statements (one change each): at sentence ends, and before a capital word
    that follows a value when both sides hold numbers ("...: 50%/50%/225% Saat menerima DMG, ... 50% >> 25%")."""
    text = re.sub(r"\s+", " ", " ".join(lines))
    out = []
    for part in re.split(r"(?<=[.;])\s+(?=[A-Z0-9])", text):
        while True:
            cut = next((m.start() for m in re.finditer(r"(?<=[\d%])\s+(?=([A-Z][a-z]+))", part)
                        if m.group(1) not in UNIT_WORDS
                        and re.search(r"\d", part[:m.start()]) and re.search(r"\d", part[m.start():])), None)
            if cut is None:
                break
            out.append(part[:cut])
            part = part[cut:]
        out.append(part)
    return [p.strip(" .;") for p in out if p.strip(" .;")]


def to_num(v):
    v = re.sub(r"(\d)\.(\d{3})(?!\d)", r"\1\2", v.replace(" ", "").rstrip("%"))  # 7.020 -> 7020
    try:
        return float(v.replace(",", "."))
    except ValueError:
        return None


def fix_ocr(text):
    """Common OCR slips in patch lines: '%' read as '0/0' and '/' as '1' (500/01500/012250/0 -> 50%/50%/225%),
    'Bintang 112' -> 'Bintang 1/2', and a '/' read as '1' in the new value (260/390 >> 3001450 -> 300/450)."""
    text = re.sub(r"(?<=\d)0/0", "%", text)
    text = re.sub(r"%1(?=\d)", "%/", text)
    text = re.sub(r"(Bintang\s+)([123])1([123])\b", r"\1\2/\3", text)

    def slash(m):
        old, new = m.group(1), m.group(3)
        parts = [len(p) for p in old.split("/")]
        if len(parts) == 2 and len(new) == sum(parts) + 1 and new[parts[0]] == "1":
            new = new[:parts[0]] + "/" + new[parts[0] + 1:]
        return f"{old}{m.group(2)}{new}"
    return re.sub(r"(\d+/\d+)(\s*(?:>>|»)?\s*)(\d{5,9})\b", slash, text)


def changes_of(statement):
    """[(label, old, new)] for a statement; ">>" dropped by OCR ("285 255") is accepted for two same-shape groups."""
    s = fix_ocr(statement)
    out = [(s[:m.start()].strip(" :"), m.group(1).replace(" ", ""), m.group(2).replace(" ", "")) for m in PAIR.finditer(s)]
    if not out:  # only "label: 285 255" (two values right after the colon, maybe a unit word) counts as a change
        m = re.search(r":\s*(" + GROUP.pattern + r")\s+(" + GROUP.pattern + r")(?:\s+[A-Za-z]+){0,2}\s*$", s)
        if m and m.group(1).count("/") == m.group(2).count("/") and m.group(1).endswith("%") == m.group(2).endswith("%"):
            out.append((s[:m.start()].strip(" :"), m.group(1), m.group(2)))
    return out


def percent(old, new):
    a, b = to_num(old.split("/")[-1]), to_num(new.split("/")[-1])
    return (b - a) / a * 100 if a and b is not None else None


# ------------------------------------------------------------------ status & drafts

def hero_status(hero, label, old, new):
    """Exact status of a hero stat line ("Hybrid ATK Dasar pada Bintang 1/2: a/b >> c/d") from the stat table; None if not one."""
    draft = hero_stat_draft(hero["name"], label, old, new)
    if not draft:
        return None
    stat = "Physical ATK" if draft["stat"] == "Hybrid ATK" else draft["stat"]
    cur = [to_num(str((hero["stats"].get(str(s)) or {}).get(stat, ""))) for s in draft["stars"]]
    if cur == [float(x) for x in draft["new"]]:
        return "sudah di file game"
    if cur == [float(x) for x in draft["old"]]:
        return "diterapkan server"
    return "diterapkan server (file game: " + "/".join(f"{x:g}" if x is not None else "?" for x in cur) + ")"


def status(texts, key, entity, old, new):
    data = texts.get(key(entity), "")
    if not data:
        return "tidak ada di data"
    ref = set(V.numbers(data, keep_single=True))
    ref |= {n.rstrip("%") for n in ref}

    def has(v):
        nums = V.numbers(v, keep_single=True)
        return bool(nums) and all(x in ref or x.rstrip("%") in ref for x in nums)
    if has(new) and not has(old):
        return "sudah di file game"
    if not has(new):
        return "diterapkan server"
    return "tidak bisa dipastikan"


def hero_stat_draft(entity, label, old, new):
    m = re.search(r"(" + "|".join(STATS) + r").*?Bintang\s*([\d/]+)", label)
    if not m:
        return None
    stat, stars = m.group(1), [int(x) for x in m.group(2).split("/") if x.isdigit()]
    olds, news = [to_num(x) for x in old.split("/")], [to_num(x) for x in new.split("/")]
    if len(olds) != len(news) or None in olds + news:
        return None
    if len(olds) == 1 and len(stars) > 1:  # "Batas Mana pada Bintang 1/2: 70 >> 50" = same value for both stars
        olds, news = olds * len(stars), news * len(stars)
    if len(stars) == 1 and len(olds) > 1:
        stars = list(range(stars[0], stars[0] + len(olds)))
    if len(stars) != len(olds):
        return None
    fmt = lambda xs: [int(x) if x == int(x) else x for x in xs]
    return {"name": entity, "stat": stat, "stars": stars, "old": fmt(olds), "new": fmt(news)}


def replace_draft(desc, statement, old, new):
    """[[old phrase, new phrase]] for the occurrence of the old value in the game text whose surrounding words match the
    patch line best (Badang: "memiliki 50% peluang", not the earlier "50% ATK"), with a word on each side to keep it unique."""
    words = set(re.findall(r"[a-z]{3,}", statement.lower()))
    best = None
    for o, n in zip(old.split("/"), new.split("/")):
        for m in re.finditer(rf"(?<![\d.]){re.escape(o)}(?!\d)", desc):
            window = set(re.findall(r"[a-z]{3,}", desc[max(0, m.start() - 60):m.end() + 60].lower()))
            if best is None or len(words & window) > best[0]:
                best = (len(words & window), m, o, n)
    if not best:
        return None
    _, m, o, n = best
    left = re.search(r"(\S+[ \t]+)?\S*$", desc[:m.start()]).group(0)
    right = re.match(r"\S*([ \t]+\S+)?", desc[m.end():]).group(0)
    return [[left + o + right, left + n + right]]


def server_side(r):
    return r["status"].startswith("diterapkan server")


def status_text(r):
    return r["status"] + (" · tercatat di server_patch.json" if r["recorded"] and server_side(r) else "")


def drafts(d, rows):
    """server_patch.json-shaped draft for server-side changes not recorded yet; unplaced text becomes a note ("text")."""
    H = {h["name"]: h for h in d["heroes"]}
    C = {c["name"]: c for c in d["commanders"]}
    K = {c["name"]: c for c in d["cards"]}
    S = {s["name"]: s for s in d["synergies"]}
    out = {"heroes": [], "hero_skills": [], "commanders": [], "synergies": [], "cards": []}
    for r in rows:
        if not server_side(r) or r["recorded"]:
            continue
        e, kind = r["data_name"], r["kind"]
        text = f"{r['label']}: {r['old']} → {r['new']}" if r["old"] else r["statement"]
        if kind == "Hero" and e in H:
            stat = hero_stat_draft(e, r["label"], r["old"], r["new"]) if r["old"] else None
            if stat:
                out["heroes"].append(stat)
                continue
            skill = H[e]["skills"][0] if H[e]["skills"] else None
            rep = replace_draft(skill["description"], r["statement"], r["old"], r["new"]) if skill and r["old"] else None
            out["hero_skills"].append({"name": e, "skill": skill["name"] if skill else "?", **({"replace": rep} if rep else {}), "text": text})
        elif kind == "Commander" and e in C:
            best = None
            for s in C[e]["skills"]:
                rep = replace_draft(s["skill"]["description"], r["statement"], r["old"], r["new"]) if r["old"] else None
                if rep:
                    best = {"name": e, "skill": s["skill"]["name"], "replace": rep, "text": text}
                    break
            out["commanders"].append(best or {"name": e, "skill": C[e]["skills"][0]["skill"]["name"], "text": text})
        elif kind == "Go Go Card" and e in K:
            rep = replace_draft(K[e]["description"], r["statement"], r["old"], r["new"]) if r["old"] else None
            out["cards"].append({"id": K[e]["id"], "name": e, **({"replace": rep} if rep else {}), "text": text})
        elif kind == "Sinergi" and e in S:
            out["synergies"].append({"name": e, "text": text})
    return {k: v for k, v in out.items() if v}


# ------------------------------------------------------------------ main

def build_rows(d, entries):
    texts, key = V.entity_texts(d)
    recorded = V.recorded_server_changes(d.get("season"), key)
    heroes = {h["name"]: h for h in d["heroes"]}
    lookups = {"Hero": Names([h["name"] for h in d["heroes"]]), "Commander": Names([c["name"] for c in d["commanders"]]),
               "Sinergi": Names([s["name"] for s in d["synergies"]]), "Go Go Card": Names([c["name"] for c in d["cards"]]),
               "Equipment": Names([lv["name"] for e in d["equipment"] for lv in e["levels"]])}
    rows = []
    for e in entries:
        kind = KIND_OF_SECTION.get(e["section"].lower())
        name = lookups[kind].find(e["entity"]) if kind else None
        if not name:  # section unknown or name OCR'd badly: try every kind
            for k, look in lookups.items():
                if (name := look.find(e["entity"])):
                    kind = kind or k
                    break
        for st in statements(e["lines"]) or ["(tanpa keterangan)"]:
            base = {"section": e["section"], "entity": e["entity"], "data_name": name or e["entity"], "kind": kind or e["section"],
                    "arrow": e["arrow"], "statement": st, "recorded": key(name or e["entity"]) in recorded}
            pairs = changes_of(st)
            if not pairs:
                rows.append({**base, "label": st, "old": "", "new": "", "pct": None,
                             "status": "dihapus (server)" if "dihapus" in st.lower() else ("baru" if e["arrow"] == "baru" else "teks")})
            hero = heroes.get(name) if kind == "Hero" else None
            rows += [{**base, "label": label, "old": old, "new": new, "pct": percent(old, new),
                      "status": (hero and hero_status(hero, label, old, new)) or status(texts, key, name or e["entity"], old, new)}
                     for label, old, new in pairs]
    return rows


def entity_chip(d, r):
    for items in (d["heroes"], d["commanders"], d["synergies"], d["cards"]):
        for x in items:
            if x["name"] == r["data_name"] and x.get("icon"):
                return chip(r["data_name"], x["icon"])
    return chip(r["data_name"])


def impact(d, rows):
    """Synergies touched by hero changes (and synergy changes themselves): {synergy: [(hero, arrow)]}."""
    H = {h["name"]: h for h in d["heroes"]}
    out = defaultdict(list)
    for r in rows:
        if r["kind"] == "Hero" and r["data_name"] in H:
            for s in H[r["data_name"]]["synergies"]:
                if (r["data_name"], r["arrow"]) not in out[s]:
                    out[s].append((r["data_name"], r["arrow"]))
        elif r["kind"] == "Sinergi" and ("sinergi", r["arrow"]) not in out[r["data_name"]]:
            out[r["data_name"]].append(("sinergi", r["arrow"]))
    return dict(sorted(out.items()))


def arrow_html(a):
    return f'<span class="{ARROW_CLASS.get(a, "muted")}">{ARROW_LABEL[a]}</span>'


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Analisa Patch Note dari screenshot Update Patch")
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--files", help="nomor screenshot, mis. 1881-1885,1890")
    ap.add_argument("--name")
    ap.add_argument("--season", type=int)
    ap.add_argument("--version")
    ap.add_argument("--no-ocr", action="store_true", help="jangan jalankan OCR; pakai ocr.json yang ada")
    args = ap.parse_args()
    d, folder = load_season(args.season, args.version)
    files = pick_files(args.paths, args.files)
    if not files:
        raise SystemExit("Tidak ada screenshot yang cocok.")
    shots = ocr_lines(files, not args.no_ocr)
    patch_shots = {f: l for f, l in shots.items() if V.classify(l) == "patch"}
    if not patch_shots:
        raise SystemExit(f"{len(shots)} screenshot dibaca, tidak ada yang dikenali sebagai layar Patch Note.")
    known = Names([x["name"] for x in d["heroes"] + d["commanders"] + d["synergies"] + d["cards"]])
    rows = build_rows(d, parse_entries(patch_shots, known))
    draft = drafts(d, rows)
    name = args.name or f"{files[0].parent.name} {files[0].stem}"

    entities = {(r["section"], r["data_name"]): r for r in rows}
    per_arrow, st_count = defaultdict(int), defaultdict(int)
    for r in entities.values():
        per_arrow[r["arrow"]] += 1
    for r in rows:
        st_count[("diterapkan server" if server_side(r) else r["status"]) + (" · tercatat" if r["recorded"] and server_side(r) else "")] += 1
    syn = impact(d, rows)

    summary = (f"{len(entities)} item berubah dari {len(patch_shots)} screenshot: " +
               ", ".join(f"{n} {ARROW_LABEL[a]}" for a, n in per_arrow.items()))
    status_summary = ", ".join(f"{n} {s}" for s, n in sorted(st_count.items()))
    body = [f'<section><h2>Ringkasan</h2><div class="grid3">'
            f'<div class="box"><h4>Perubahan</h4><p>{esc(summary)}</p></div>'
            f'<div class="box warn"><h4>Status di data</h4><p>{esc(status_summary)}</p>'
            '<p class="muted small">"diterapkan server" = angka baru belum ada di file game (dikirim server). '
            '"tercatat" = sudah ada di server_patch.json.</p></div></div></section>']
    md = [f"# Analisa Patch — {name}", "", f"_{stamp(d)}_", "", f"- {summary}", f"- Status di data: {status_summary}", ""]
    for section in dict.fromkeys(r["section"] for r in rows):
        cells, md_rows = [], []
        for r in (x for x in rows if x["section"] == section):
            pct = f" ({r['pct']:+.0f}%)" if r["pct"] is not None else ""
            stat = status_text(r)
            cells.append([entity_chip(d, r), arrow_html(r["arrow"]), esc(r["label"]),
                          f'{esc(r["old"])} → <b>{esc(r["new"])}</b><span class="muted">{pct}</span>' if r["old"] else "", esc(stat)])
            md_rows.append([r["data_name"], ARROW_LABEL[r["arrow"]], r["label"], f"{r['old']} → {r['new']}{pct}" if r["old"] else "", stat])
        body.append(f'<section><h2>Penyesuaian {esc(section)}</h2>{table(["Item", "Arah", "Perubahan", "Angka", "Status"], cells)}</section>')
        md += [f"## Penyesuaian {section}", ""] + md_table(["Item", "Arah", "Perubahan", "Angka", "Status"], md_rows) + [""]
    if syn:
        S = {s["name"]: s for s in d["synergies"]}
        items = [f'{chip(s, S[s].get("icon") if s in S else None)} ' + ", ".join(f"{esc(h)} {arrow_html(a)}" for h, a in v)
                 for s, v in syn.items()]
        body.append(f'<section><h2>Dampak ke sinergi</h2><ul>{"".join(f"<li>{x}</li>" for x in items)}</ul></section>')
        md += ["## Dampak ke sinergi", ""] + [f"- **{s}**: " + ", ".join(f"{h} {ARROW_LABEL[a]}" for h, a in v) for s, v in syn.items()] + [""]
    if draft:
        snippet = json.dumps({"patch": name, "source": f"Patch Note {name} (screenshot)", **draft}, ensure_ascii=False, indent=2)
        body.append(f'<section><h2>Draf server_patch.json</h2><p class="muted">Perubahan server yang belum tercatat. Periksa dulu '
                    f'(nama skill, teks pengganti), lalu tambahkan ke daftar season "{d["season"]}" di server_patch.json dan '
                    f'jalankan mc_data.py.</p><pre>{esc(snippet)}</pre></section>')
        md += ["## Draf server_patch.json", "", "_Periksa dulu sebelum disalin ke server_patch.json._", "", "```json", snippet, "```", ""]
    rel = lambda f: Path(os.path.relpath(f, folder)).as_posix()
    figs = "".join(f'<figure><a href="{esc(rel(f))}"><img class="shot" src="{esc(rel(f))}" alt="" loading="lazy"></a>'
                   f'<figcaption>{esc(f.name)}</figcaption></figure>' for f in patch_shots)
    body.append(f'<section><h2>Screenshot</h2><div class="shots">{figs}</div></section>')
    md += ["## Screenshot", ""] + [f"- `{f}`" for f in patch_shots]
    out_html, out_md = write_report(folder, f"PATCH_{slug(name)}", page(f"Analisa Patch — {name}", "".join(body), stamp(d)), md)
    print(summary)
    print("Status:", status_summary)
    print(f"Laporan: {out_html}\n         {out_md}")


if __name__ == "__main__":
    main()
