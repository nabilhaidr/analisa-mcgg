"""Analisa Patch Note dari screenshot "Update Patch" in-game -> data/<versi>/PATCH_<nama>.html/.md.

Pemakaian (Python sistem; OCR lewat mc_ocr.py = OCR bawaan Windows atau RapidOCR, hasilnya di-cache per folder):
  python mc_patch.py "screenshot\\season 7\\update patch" --files 1881-1885 --name "Penyesuaian 20-10"
  python mc_patch.py shot1.png shot2.png --season 7
Opsi: --files 1881-1885,1890 (nomor di nama file "Screenshot (N)"), --name, --season, --version, --no-ocr (pakai ocr.json yang ada),
--ocr auto|windows|rapid (auto: OCR Windows; di luar Windows ocr.json yang ada bila lengkap, lalu RapidOCR).

Isi laporan: setiap perubahan per bagian (Commander, Sinergi, Hero, Go Go Card, Equipment, ...) dengan panah in-game
(↑ buff, ↓ nerf, ~ penyesuaian), angka lama → baru (+ persen), status di data (sudah di file game / diterapkan server /
tercatat di server_patch.json), dampak ke sinergi, dan DRAF entri server_patch.json untuk perubahan server yang belum dicatat
(periksa dulu sebelum disalin; teks pengganti dicari otomatis di deskripsi file game).
Screenshot yang tumpang tindih (panel di-scroll) digabung: baris yang sama hanya dihitung sekali.
"""
import argparse
import difflib
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

import mc_ocr
import mc_validate as V
from mc_common import Names, chip, esc, load_season, md_table, page, rel_src, shown_path, slug, stamp, table, write_report

SECTION = re.compile(r"Penyesuaian\s+(Commander|Sinergi|Hero|Go Go Card|Equipment|Kartu|Lainnya|Umum|Sistem|Mekanisme)", re.I)
HEADER = re.compile(r"^(?:[-•·]\S{0,2}\s+)?(.+?)\s*\(\s*([^()]{0,6})\s*\)\s*$")  # "-A Turret of Guardians (l)": OCR noise
# in-game arrows as Windows OCR reads them: ↑ -> "t", ↓ -> "I"/"l"/"J", ~ stays
ARROWS = {"t": "buff", "↑": "buff", "f": "buff", "i": "nerf", "l": "nerf", "j": "nerf", "↓": "nerf", "1": "nerf", "|": "nerf",
          "~": "adjust", "-": "adjust", "—": "adjust", "–": "adjust", "baru": "baru"}
ARROW_LABEL = {"buff": "↑ buff", "nerf": "↓ nerf", "adjust": "~ penyesuaian", "baru": "baru", None: "-"}
ARROW_CLASS = {"buff": "buff", "nerf": "nerf"}
PAIR = re.compile(r"(\d[\d.,]*(?:\s*/\s*\d[\d.,]*)*\s*%?)\s*(?:>>|»|>)\s*(\d[\d.,]*(?:\s*/\s*\d[\d.,]*)*\s*%?)")
GROUP = re.compile(r"\d[\d.,]*(?:/\d[\d.,]*)*%?")
OCR_ROMAN = r"[IVXl1|]{1,4}"  # I read as 1 / l / |
ROUND_PAIR = re.compile(rf"(Babak\s+)({OCR_ROMAN})\s*-\s*([1-6])\s*(?:>>|»|>)\s*({OCR_ROMAN})\s*-\s*([1-6])(?!\d)")
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


def ocr_lines(files, engine):
    """{file: lines} (coordinates normalised to 1366x768 by mc_validate.scale_lines), OCR-ing each folder when needed;
    engine "cache" = only the existing ocr.json."""
    shots = {}
    for folder in sorted({f.parent for f in files}):
        mine = {mc_ocr.key_of(folder, f): f for f in files if f.parent == folder}
        images = mc_ocr.load_json(folder / "ocr.json") if engine == "cache" else mc_ocr.ocr_folder(folder, engine, list(mine.values()))
        for k, lines in V.scale_lines({k: v for k, v in images.items() if k in mine}).items():
            shots[mine[k]] = lines
    return shots


# ------------------------------------------------------------------ parsing

def line_key(text):
    return re.sub(r"\W", "", text.lower())


def same_line(a, b):
    """Two readings of one line (scrolled screenshots): one contains the other, or they differ by a few OCR slips but have
    the same digits ("Setelah 4 5 babak, Go Go Ca?d" vs "Setelan4>>5babak,Go GoCara"); lines that differ in a number
    are different lines (X.Borg 240/365 vs Gatotkaca 230/345)."""
    ka, kb = line_key(a), line_key(b)
    if ka in kb or kb in ka:
        return True
    return (min(len(ka), len(kb)) >= 20 and re.findall(r"\d", ka) == re.findall(r"\d", kb)
            and difflib.SequenceMatcher(None, ka, kb).ratio() >= 0.85)


def add_line(lines, text):
    """Append an OCR line unless it repeats one already kept; a longer reading, or one that kept its ">>", replaces the
    old one."""
    for i, old in enumerate(lines):
        if same_line(old, text):
            better = (">>" in text) > (">>" in old) or ((">>" in text) == (">>" in old) and len(line_key(text)) > len(line_key(old)))
            if better and line_key(text) not in line_key(old):
                lines[i] = text
            return
    lines.append(text)


def parse_entries(shots, known):
    """[{section, entity, arrow, lines}] in reading order; overlapping screenshots merged. A screenshot that starts in the
    middle of a section (scrolled) has no section title above its first items: those join the entry already seen. Lines
    above the first item title of a screenshot belong to the item before that title (the previous screenshot's last item
    when the title is new), so the overlap is matched against the right item."""
    entries, order = {}, []
    section, current = "Lainnya", None
    for f in sorted(shots, key=lambda p: (len(p.name), p.name)):
        titled, pending = False, ([] if current else None)  # None: no item yet, text above the first title is an intro
        for l in V.region(shots[f], 150, 768, 300, 1366):
            t = fix_ocr(l["t"].strip())
            m = SECTION.search(t)
            if m and len(t) < 40:
                section, titled = m.group(1).title(), True
                continue
            h = HEADER.match(t)
            raw = h.group(1).strip() if h and len(h.group(1)) <= 40 else (t if len(t) <= 40 and known.find(t, 0.9) else None)
            if not raw and " " not in t and not re.search(r"[\d.]", t) and len(t) >= 6 and known.find(t, 0.78):
                raw = t  # title cut at the bottom edge: "SolidAliancoll~i" = "Solid Alliance II (~)"
            if raw:
                raw = re.sub(r"(?<=\s)[Il1|]{1,3}$", lambda m: "I" * len(m.group(0)), raw)  # "Dimensional Shot Il" = Ⅱ
                name = known.find(raw, 0.85) or (known.find(raw, 0.78) if not h else None) or raw
                marker = h.group(2).strip().lower() if h else ""
                arrow = ARROWS.get(marker) or ("baru" if "baru" in marker else None)
                key = (section, name)
                if not titled:  # continuation of the previous screenshot: reuse the latest entry with this name
                    key = next((k for k in reversed(order) if k[1] == name), key)
                    section = key[0]
                if pending:
                    owner = order[order.index(key) - 1] if key in entries and order.index(key) > 0 else current
                    for line in pending:
                        add_line(entries[owner]["lines"], line)
                pending = None
                if key not in entries:
                    entries[key] = {"section": key[0], "entity": name, "arrow": arrow, "lines": []}
                    order.append(key)
                elif arrow and not entries[key]["arrow"]:
                    entries[key]["arrow"] = arrow
                current = key
                continue
            if current and l["x"] > 400 and not t.startswith(("Penyesuaian", "Patch")):
                if pending is not None:
                    pending.append(t)
                else:
                    add_line(entries[current]["lines"], t)
        for line in pending or []:  # no item title in this screenshot
            add_line(entries[current]["lines"], line)
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

    def lost_slash(m):  # "120/230/390 1640 >> 100/190/300/500": the new value has one part more
        old, rest, arrow, new = m.groups()
        return f"{old}/{rest}{arrow}{new}" if new.count("/") == old.count("/") + 1 else m.group(0)
    text = re.sub(r"(\d+(?:/\d+)+)\s+1(\d+)(\s*(?:>>|»)\s*)(\d+(?:/\d+)+)", lost_slash, text)

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
    roman = lambda r: re.sub(r"[1l|]", "I", r)
    out = [(s[:m.start()].strip(" :") + " " + m.group(1).strip(), f"{roman(m.group(2))}-{m.group(3)}", f"{roman(m.group(4))}-{m.group(5)}")
           for m in ROUND_PAIR.finditer(s)]
    s = ROUND_PAIR.sub(" ", s)  # "Babak 1-4 >> 1-3" is not the number pair 4 >> 1
    out += [(s[:m.start()].strip(" :"), m.group(1).replace(" ", ""), m.group(2).replace(" ", "")) for m in PAIR.finditer(s)]
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


def status(texts, key, entity, old, new, statement=""):
    data = texts.get(key(entity), "")
    if not data:
        return "tidak ada di data"
    if re.fullmatch(r"[IVX]+-\d", new):  # round label ("Mulai Babak I-4 >> I-3")
        has_label = lambda v: re.search(rf"(?<![IVX]){re.escape(v)}(?!\d)", data)
        return "sudah di file game" if has_label(new) and not has_label(old) else \
            "diterapkan server" if has_label(old) and not has_label(new) else "tidak bisa dipastikan"
    ref = set(V.numbers(data, keep_single=True))
    ref |= {n.rstrip("%") for n in ref}

    def has(v):
        nums = V.numbers(v, keep_single=True)
        return bool(nums) and all(x in ref or x.rstrip("%") in ref for x in nums)
    if has(new) and not has(old):
        return "sudah di file game"
    if not has(new):
        return "diterapkan server"
    found = context_values(data, statement, old, new)  # both numbers occur somewhere: look where the line points
    if new in found and old not in found:
        return "sudah di file game"
    if found and new not in found:
        return "diterapkan server" + ("" if old in found else f" (file game: {', '.join(sorted(found))})")
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


VALUE = r"(\d[\d.,]*(?:\s*/\s*\d[\d.,]*)*%?)"  # a value in the game text; "100 / 190 / 320/540" has spaces


def anchors(statement, old, new):
    """(word before, word after) the change in the patch line: "mendapatkan 30 >> 35 Shield" -> ("mendapatkan", "Shield")."""
    loose = lambda v: r"\s*/\s*".join(map(re.escape, v.split("/")))  # "120/230/390 /640"
    m = re.search(rf"(\w+)?\s*{loose(old)}\s*(?:>>|»|>)?\s*{loose(new)}\s*([A-Za-z]+)?", fix_ocr(statement))
    return (m.group(1), m.group(2)) if m else (None, None)


def anchor_matches(desc, statement, old, new):
    """Matches (group 1 = value) in the game text at the patch line's words around the change: before + after, else after."""
    before, after = anchors(statement, old, new)
    for pattern in ([rf"\b{before}\s+{VALUE}\s+{after}\b"] if before and after else []) + \
                   ([rf"(?<![\d.,/]){VALUE}\s+{after}\b"] if after else []):
        found = list(re.finditer(pattern, desc, re.I))
        if found:
            return found
    return []


def context_values(data, statement, old, new):
    """Values the game text holds where the patch line points ("mendapatkan <n> Shield"), without spaces."""
    return {m.group(1).replace(" ", "") for m in anchor_matches(data, statement, old, new)}


def replace_best(desc, statement, old, new):
    """(score, exact, [[old phrase, new phrase]]) for the spot in the game text that the patch line changes, or None.
    Candidates: each occurrence of an old value (Badang: "memiliki 50% peluang", not the earlier "50% ATK"), and the value at
    the line's words around the change, for patch notes that quote another old number (Dyrroth "1 >> 3 EXP", file
    "mendapatkan 2 EXP"). Best = most words shared with the patch line nearby, then an exact old value. A word on each side
    keeps the phrase unique."""
    words = set(re.findall(r"[a-z]{3,}", statement.lower()))
    score = lambda a, b: len(words & set(re.findall(r"[a-z]{3,}", desc[max(0, a - 60):b + 60].lower())))
    cands = []
    for o, n in zip(old.split("/"), new.split("/")):
        for m in re.finditer(rf"(?<![\d.]){re.escape(o)}(?!\d)", desc):
            cands.append((score(m.start(), m.end()), 1, m.start(), m.end(), n))
    for m in anchor_matches(desc, statement, old, new):
        value = m.group(1)
        sep = " / " if " / " in value else "/"
        if len(value.split("/")) == len(new.split("/")) and value.replace(" ", "") != new:
            cands.append((score(m.start(1), m.end(1)), 0, m.start(1), m.end(1), sep.join(new.split("/"))))
    if not cands:
        return None
    sc, exact, a, b, n = max(cands, key=lambda c: (c[0], c[1]))
    left = re.search(r"(\S+[ \t]+)?\S*$", desc[:a]).group(0)
    right = re.match(r"\S*([ \t]+\S+)?", desc[b:]).group(0)
    return sc, exact, [[left + desc[a:b] + right, left + n + right]]


def replace_draft(desc, statement, old, new):
    best = replace_best(desc, statement, old, new)
    return best[2] if best else None


def server_side(r):
    return r["status"].startswith("diterapkan server")


def status_text(r):
    return r["status"] + (" · tercatat di server_patch.json" if r["recorded"] and server_side(r) else "")


def best_target(items, statement, old, new, text_of, name_of=None):
    """(item, replace or None) among same-named cards or a commander's skills: the item named in the line (skill name
    "Abyssal Favor: ..."), then the best replace_best() score."""
    named = [x for x in items if name_of and name_of(x).lower() in statement.lower()]
    best = None
    for x in named or items:
        r = replace_best(text_of(x), statement, old, new) if old else None
        key = (r[0], r[1]) if r else (-1, 0)
        if best is None or key > best[0]:
            best = (key, x, r[2] if r else None)
    return best[1], best[2]


def drafts(d, rows):
    """server_patch.json-shaped draft for server-side changes not recorded yet; unplaced text becomes a note ("text")."""
    H = {h["name"]: h for h in d["heroes"]}
    C = {c["name"]: c for c in d["commanders"]}
    K = defaultdict(list)  # two cards can share a name (Lunox's Power 3017 and 3045)
    for c in d["cards"]:
        K[c["name"]].append(c)
    S = {s["name"]: s for s in d["synergies"]}
    out = {"heroes": [], "hero_skills": [], "commanders": [], "synergies": [], "cards": []}
    for r in rows:
        e, kind = r["data_name"], r["kind"]
        if r["status"] == "dihapus (server)" and kind == "Go Go Card" and e in K and not r["recorded"]:
            out["cards"].append({"id": K[e][0]["id"], "name": e, "removed": True})
        if not server_side(r) or r["recorded"]:
            continue
        text = f"{r['label']}: {r['old']} → {r['new']}" if r["old"] else r["statement"]
        if kind == "Hero" and e in H:
            stat = hero_stat_draft(e, r["label"], r["old"], r["new"]) if r["old"] else None
            if stat:
                out["heroes"].append(stat)
                continue
            if not H[e]["skills"]:
                out["hero_skills"].append({"name": e, "skill": "?", "text": text})
                continue
            skill, rep = best_target(H[e]["skills"], r["statement"], r["old"], r["new"], lambda x: x["description"], lambda x: x["name"])
            out["hero_skills"].append({"name": e, "skill": skill["name"], **({"replace": rep} if rep else {}), "text": text})
        elif kind == "Commander" and e in C:
            s, rep = best_target(C[e]["skills"], r["statement"], r["old"], r["new"], lambda x: x["skill"]["description"],
                                 lambda x: x["skill"]["name"])
            out["commanders"].append({"name": e, "skill": s["skill"]["name"], **({"replace": rep} if rep else {}), "text": text})
        elif kind == "Go Go Card" and e in K:
            card, rep = best_target([c for c in K[e] if c.get("active", True)] or K[e], r["statement"], r["old"], r["new"],
                                    lambda x: x["description"])
            out["cards"].append({"id": card["id"], "name": e, **({"replace": rep} if rep else {}), "text": text})
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
        if not name and not e["lines"]:
            continue  # unreadable title without text ("Dimen•innn' Qhnt" at the bottom edge of a screenshot)
        for st in statements(e["lines"]) or ["(tanpa keterangan)"]:
            base = {"section": e["section"], "entity": e["entity"], "data_name": name or e["entity"], "kind": kind or e["section"],
                    "arrow": e["arrow"], "statement": st, "recorded": key(name or e["entity"]) in recorded}
            pairs = changes_of(st)
            if not pairs:
                rows.append({**base, "label": st, "old": "", "new": "", "pct": None,
                             "status": "dihapus (server)" if "dihapus" in st.lower() else ("baru" if e["arrow"] == "baru" else "teks")})
            hero = heroes.get(name) if kind == "Hero" else None
            rows += [{**base, "label": label, "old": old, "new": new, "pct": percent(old, new),
                      "recorded": V.is_recorded(recorded, key(name or e["entity"]), new),
                      "status": (hero and hero_status(hero, label, old, new)) or status(texts, key, name or e["entity"], old, new, st)}
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
    ap.add_argument("--ocr", default="auto", choices=mc_ocr.ENGINES, help="mesin OCR (lihat mc_ocr.py)")
    args = ap.parse_args()
    d, folder = load_season(args.season, args.version)
    files = pick_files(args.paths, args.files)
    if not files:
        raise SystemExit("Tidak ada screenshot yang cocok.")
    shots = ocr_lines(files, "cache" if args.no_ocr else args.ocr)
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
    rel = lambda f: rel_src(f, folder)
    figs = "".join(f'<figure><a href="{esc(rel(f))}"><img class="shot" src="{esc(rel(f))}" alt="" loading="lazy"></a>'
                   f'<figcaption>{esc(f.name)}</figcaption></figure>' for f in patch_shots)
    body.append(f'<section><h2>Screenshot</h2><div class="shots">{figs}</div></section>')
    md += ["## Screenshot", ""] + [f"- `{shown_path(f)}`" for f in patch_shots]
    out_html, out_md = write_report(folder, f"PATCH_{slug(name)}", page(f"Analisa Patch — {name}", "".join(body), stamp(d)), md)
    print(summary)
    print("Status:", status_summary)
    print(f"Laporan: {out_html}\n         {out_md}")


if __name__ == "__main__":
    main()
