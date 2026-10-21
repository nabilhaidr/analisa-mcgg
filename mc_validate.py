"""Validasi laporan season (data/<versi>/S<n>.json, sumber S<n>.html) terhadap screenshot in-game.

Pemakaian (Python biasa, tidak butuh .venv):
  powershell -ExecutionPolicy Bypass -File ocr_screens.ps1 -Season 7   1) OCR screenshot/season 7 -> ocr.json
  python mc_validate.py --season 7                                     2) bandingkan dengan data versi terbaru
  python mc_validate.py --season 7 --version 1.3.24.344.1              data versi tertentu
  python mc_validate.py --season 7 --dump "(1510)"                     teks OCR screenshot yang namanya cocok

Hasil: ringkasan di terminal + data/<versi>/VALIDASI_S<n>_auto.md.

Jenis layar dikenali dari isinya (Detail Hero, Panduan Sinergi, Commander, Equipment, Go Go Card, Ensiklopedia,
Patch Note), jadi pembagian subfolder bebas. Koordinat dinormalkan ke layar 1366x768.
Temuan dibagi dua:
  Selisih     teks/angka terbaca jelas tapi berbeda dengan data -> kemungkinan data perlu diperbaiki
  Cek manual  kemungkinan salah baca OCR, teks terpotong, atau panel di-scroll -> lihat screenshot-nya
Toleransi OCR: angka satu digit diabaikan (1/I, 0/O sering tertukar), "30%" yang terbaca "300/0" dan babak "II-3"
yang terbaca "11-3" dinormalkan, tulisan tombol ("Naikkan Bintang", "Dapatkan") dibuang.
"""
import argparse
import difflib
import json
import re
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
BASE_W, BASE_H = 1366, 768
NUM = re.compile(r"\d+(?:[.,]\d+)?%?")
ROMAN = {"Ⅰ": "I", "Ⅱ": "II", "Ⅲ": "III", "Ⅳ": "IV", "Ⅴ": "V"}
ROUND = re.compile(r"(?<![\w.])[IVXlⅠⅡⅢⅣⅤ1i|]{1,4}\s*-\s*[\dIl](?!\d)")  # babak label I-3 (OCR: 1-3, 11-3, Ill-I)
PHASES = re.compile(r"(?<![\w.])(?:[1Il]{1,3}|[1Il]?V)(?:\s*/\s*(?:[1Il]{1,3}|[1Il]?V))+(?![\w%])")  # fase I/II/III (OCR: 1/11/111)
UI_TEXT = re.compile(r"(Naikkan Bintang|Naik Bintang|Dapatkan|Buka Emblem|Sedang Digunakan|Gunakan)\s*")
HERO_ROWS = ["HP", "Physical ATK", "Magic ATK", "ATK Speed", "Jangkauan ATK", "Batas Mana Awal", "Batas Mana"]
KINDS = {"hero": "Hero", "synergy": "Sinergi", "commander": "Commander", "equipment": "Equipment",
         "card": "Go Go Card", "book": "Ensiklopedia", "patch": "Patch Note"}


# ------------------------------------------------------------------ text helpers

def close(text, names, cutoff=0.8):
    m = difflib.get_close_matches(text, list(names), n=1, cutoff=cutoff)
    return m[0] if m else None


def ratio(a, b):
    return difflib.SequenceMatcher(None, a.lower(), b.lower()).ratio()


def plain(text):
    for k, v in ROMAN.items():
        text = text.replace(k, v)
    return text


def word_cover(ocr_text, ref_text):
    """Share of OCR words (4+ letters) that also appear in the reference text."""
    words = re.findall(r"[a-z]{4,}", ocr_text.lower())
    ref = set(re.findall(r"[a-z]{4,}", plain(ref_text).lower()))
    return sum(w in ref for w in words) / len(words) if words else 1.0


def numbers(text, keep_single=False):
    """Value-like numbers: babak/fase labels dropped, '0/0' read as '%', 5.000 -> 5000; single digits skipped."""
    text = ROUND.sub(" ", plain(text))
    text = PHASES.sub(" ", text)
    text = re.sub(r"(\d+)0/0\b", r"\1%", text)
    text = re.sub(r"(\d)\.(\d{3})\b", r"\1\2", text)
    out = [n.replace(",", ".") for n in NUM.findall(text)]
    return out if keep_single else [n for n in out if n.endswith("%") or len(n.replace(".", "")) > 1]


def missing_numbers(game_text, data_text):
    """(missing, ambiguous): numbers shown in-game that the data lacks. Ambiguous = explainable as OCR merging
    a '/' into '1' (20/25 -> 20125) or a stray leading digit; those go to 'cek manual'."""
    ref = set()
    for n in numbers(data_text, keep_single=True):
        ref |= {n, n.rstrip("%")}
    missing, ambiguous = [], []
    for n in numbers(game_text):
        core = n.rstrip("%")
        if n in ref or core in ref:
            continue
        parts = [p for p in core.split("1") if p]
        dotted = core.split(".")  # list numbering glued to a value: "3. 4 Hero" -> 3.4
        if (("1" in core and parts and all(p in ref for p in parts)) or core[1:] in ref
                or (len(dotted) == 2 and all(p in ref for p in dotted))):
            ambiguous.append(n)
        else:
            missing.append(n)
    return missing, ambiguous


def num_eq(a, b):
    try:
        return abs(float(a.rstrip("%")) - float(b.rstrip("%"))) < 1e-6 and a.endswith("%") == b.endswith("%")
    except ValueError:
        return a == b


def cell_state(game, data):
    """Table cell: 'ok', 'ocr' (dropped digit / blank read as 0) or 'diff'."""
    if num_eq(game, data):
        return "ok"
    g, d = game.rstrip("%"), data.rstrip("%")
    if g in ("0", "") or (len(d) - len(g) == 1 and d.endswith(g)):
        return "ocr"
    return "diff"


# ------------------------------------------------------------------ OCR input

def load_ocr(folder):
    return scale_lines(json.loads((folder / "ocr.json").read_text(encoding="utf-8-sig"))["images"])


def scale_lines(images):
    """{name: lines} with coordinates scaled to the 1366x768 layout the checks are written for."""
    shots = {}
    for name, img in images.items():
        sx, sy = BASE_W / (img.get("w") or BASE_W), BASE_H / (img.get("h") or BASE_H)
        shots[name] = [{"t": l["t"], "x": l["x"] * sx, "y": l["y"] * sy, "r": l["r"] * sx, "b": l["b"] * sy}
                       for l in img["lines"]]
    return shots


def classify(lines):
    texts = [l["t"] for l in lines]
    has = lambda s: any(s in t for t in texts)
    if has("Patch Note") or has("Patch-Note"):
        return "patch"
    if has("Detail Hero"):
        return "hero"
    if any("Panduan Sinergi" in l["t"] and l["y"] < 115 for l in lines):
        return "synergy"
    if has("Peraturan") and (has("Babak") or has("Informasi")):
        return "book"
    if has("Kartu Power") and (has("Kartu Biru") or has("Kartu Ungu") or has("Kartu Oranye")):
        return "card"
    if has("Eksklusif Sinergi") and has("Reguler"):
        return "equipment"
    if has("Persiapan") and (has("Didapatkan") or has("Chessboard")):
        return "commander_list"
    if any(l["t"].startswith("Comman") and l["y"] < 60 and l["x"] < 320 for l in lines):
        return "commander"
    return "other"


def region(lines, y0=0, y1=9999, x0=0, x1=9999):
    return [l for l in sorted(lines, key=lambda l: (l["y"], l["x"])) if y0 <= l["y"] < y1 and x0 <= l["x"] < x1]


class Report:
    def __init__(self):
        self.items = defaultdict(lambda: {"selisih": [], "manual": []})
        self.notes = defaultdict(list)
        self.screens = defaultdict(int)
        self.patch_rows = []

    def add(self, kind, level, shot, msg):
        self.items[kind][level].append((shot, msg))

    def numbers_check(self, kind, shot, label, game_text, data_text, sure=True, show_data=True):
        missing, ambiguous = missing_numbers(game_text, data_text)
        if missing or ambiguous:
            level = "selisih" if missing and sure else "manual"
            self.add(kind, level, shot, f"{label}: angka game {missing + ambiguous} tidak ada di data\n"
                                        f"    game: {game_text}" + (f"\n    data: {data_text}" if show_data else ""))


# ------------------------------------------------------------------ heroes

def table_rows(lines, y0, y1, label_x=(680, 880), value_x=880):
    rows = defaultdict(lambda: ["", []])
    for l in sorted(lines, key=lambda l: l["x"]):
        if not (y0 < l["y"] < y1):
            continue
        key = next((y for y in rows if abs(y - l["y"]) < 12), l["y"])
        if label_x[0] <= l["x"] < label_x[1]:
            rows[key][0] = (rows[key][0] + " " + l["t"]).strip()
        elif l["x"] >= value_x:
            rows[key][1] += [(l["x"], n) for n in numbers(l["t"], keep_single=True)]
    return dict(sorted(rows.items()))


def star_columns(rows):
    full = [v for _, v in rows.values() if len(v) == 3]
    return [sum(v[i][0] for v in full) / len(full) for i in range(3)] if full else [930, 1057, 1183]


def by_star(values, cols):
    return {min(range(3), key=lambda k: abs(cols[k] - x)): n for x, n in values}


def check_heroes(d, shots, rep):
    heroes = {h["name"]: h for h in d["heroes"]}
    seen = set()
    for name, lines in shots:
        top = next((l["y"] for l in lines if "Atribut" in l["t"] and "Skill" not in l["t"]), 170)
        skill_y = next((l["y"] for l in lines if re.search(r"Atribut [Ss]kill", l["t"])), 480)
        rows = table_rows(lines, top, skill_y)
        cols = star_columns(rows)
        cand = [l["t"].strip() for l in lines if l["y"] < 200 and 150 < l["x"] < 600 and "Detail" not in l["t"]]
        hero = next((close(c, heroes, 0.75) for c in cand if close(c, heroes, 0.75)), None)
        if not hero and rows:  # name missed by OCR: the hero whose stat table matches best
            cells = []
            for i, (_, (label, values)) in enumerate(rows.items()):
                lab = close(label, HERO_ROWS, 0.6) if label else ("HP" if i == 0 else None)
                cells += [(lab, star, v) for star, v in by_star(values, cols).items() if lab and lab != "Jangkauan ATK"]
            hits = {n: sum(h["stats"].get(str(s + 1), {}).get(lab) == v for lab, s, v in cells) for n, h in heroes.items()}
            ranked = sorted(hits.values(), reverse=True)
            if ranked and ranked[0] >= 6 and (len(ranked) == 1 or ranked[0] > ranked[1]):
                hero = max(hits, key=hits.get)
        if not hero:
            rep.add("hero", "manual", name, "nama hero tidak dikenali: " + " | ".join(cand))
            continue
        seen.add(hero)
        h = heroes[hero]
        for i, (_, (label, values)) in enumerate(rows.items()):
            lab = close(label, HERO_ROWS, 0.6) if label else ("HP" if i == 0 else None)
            if not lab or lab == "Jangkauan ATK":
                continue
            for star, v in by_star(values, cols).items():
                ours = h["stats"].get(str(star + 1), {}).get(lab)
                state = cell_state(v, ours) if ours is not None else "ok"
                if state != "ok":
                    rep.add("hero", "selisih" if state == "diff" else "manual", name,
                            f"{hero} ★{star + 1} {lab}: game {v}, data {ours}")
        skills = h["skills"] + ([h["enhanced"]["skill"]] if h.get("enhanced") else [])
        attrs = defaultdict(list)
        for s in skills:
            for a in s["attributes"]:
                attrs[a["label"].lower()].append(a["values"])
        for _, (label, values) in table_rows(lines, skill_y, 800).items():
            if not label or not values:
                continue
            key = close(label.lower(), attrs, 0.7)
            if not key:
                rep.add("hero", "manual", name, f"{hero}: label Atribut Skill '{label}' tidak ada di data {list(attrs)}")
                continue
            got = by_star(values, cols)
            states = [[cell_state(v, vals[i]) for i, v in got.items() if i < len(vals)] for vals in attrs[key]]
            if any(all(s == "ok" for s in st) for st in states):
                continue
            level = "manual" if any(all(s != "diff" for s in st) for st in states) else "selisih"
            rep.add("hero", level, name, f"{hero} '{label}': game {[got.get(i) for i in range(3)]}, data {attrs[key]}")
        names = [s["name"] for s in skills]
        title = [l["t"] for l in lines if 180 < l["x"] < 420 and skill_y - 10 < l["y"] < skill_y + 30]
        if title and not any(close(t, names, 0.7) for t in title):
            rep.add("hero", "manual", name, f"{hero}: nama skill game {title}, data {names}")
    shop = sorted(n for n, h in heroes.items() if not h.get("summoned"))
    rep.notes["hero"].append(f"{len(seen & set(shop))} dari {len(shop)} hero toko punya screenshot Detail Hero")
    missing = sorted(set(heroes) - seen)
    if missing:
        rep.notes["hero"].append("Tanpa screenshot: " + ", ".join(f"{n}{' (panggilan)' if heroes[n].get('summoned') else ''}" for n in missing))


# ------------------------------------------------------------------ synergies

def strip_tier(text, counts):
    """'[2]10%...' -> '10%...'. OCR reads ']' as 1/I/l and 10 as IO: '[21100/0' is '[2]10%'."""
    head = text[1:5].translate(str.maketrans("IlO", "110"))
    for c in sorted(map(str, counts), key=len, reverse=True):
        if head.startswith(c) and len(head) > len(c) and head[len(c)] in "]1|":
            return text[1 + len(c) + 1:].strip()
    return re.sub(r"^[\[|]\S{0,3}\]\s*", "", text)


def check_synergies(d, shots, rep):
    syn = {s["name"]: s for s in d["synergies"]}
    counts = {t["count"] for s in syn.values() for t in s["tiers"]}
    seen = set()
    for name, lines in shots:
        body = region(lines, 300, 700, 100, 1300)
        blocks, explain = [], []
        for l in body:
            if l["t"].startswith(("[", "|")):
                blocks.append(strip_tier(l["t"], counts))
            elif blocks:
                blocks[-1] += " " + l["t"]
            else:
                explain.append(l["t"])
        title = [l["t"] for l in lines if 140 < l["y"] < 190 and 150 < l["x"] < 500]
        sname = next((close(t, syn, 0.7) for t in title if close(t, syn, 0.7)), None)
        if not sname and (blocks or explain):  # title missed: best text match
            text = " ".join(explain + blocks)
            sname = max(syn, key=lambda n: word_cover(text, syn[n]["explain"] + " " + " ".join(t["effect"] for t in syn[n]["tiers"])))
        if not sname:
            rep.add("synergy", "manual", name, "nama sinergi tidak dikenali: " + " | ".join(title))
            continue
        seen.add(sname)
        s = syn[sname]
        if explain and s["explain"] and word_cover(" ".join(explain), s["explain"]) < 0.8:
            rep.add("synergy", "manual", name, f"{sname}: penjelasan beda\n    game: {' '.join(explain)}\n    data: {s['explain']}")
        for b in blocks:
            tier = max(s["tiers"], key=lambda t: word_cover(b, t["effect"]) + 0.5 * (not sum(missing_numbers(b, t["effect"]), [])))
            sure = word_cover(b, tier["effect"]) >= 0.8
            rep.numbers_check("synergy", name, f"{sname} [{tier['count']}]", b, tier["effect"].replace("\n", " "), sure)
    rep.notes["synergy"].append(f"{len(seen)} dari {len(syn)} sinergi punya screenshot Panduan Sinergi")
    if set(syn) - seen:
        rep.notes["synergy"].append("Tanpa screenshot: " + ", ".join(sorted(set(syn) - seen)))


# ------------------------------------------------------------------ commanders

def check_commanders(d, shots, list_shots, rep):
    cmds = {c["name"]: c for c in d["commanders"]}
    seen, in_list = set(), set()
    for _, lines in list_shots:
        for l in lines:
            n = close(re.sub(r"[^A-Za-z&.' ]", "", l["t"]).strip(), cmds, 0.7)
            if n:
                in_list.add(n)
    for name, lines in shots:
        tip = [dict(l, t=UI_TEXT.sub("", l["t"]).strip()) for l in region(lines, 140, 700, 700, 1310)]
        tip = [l for l in tip if l["t"]]
        top = [re.sub(r"[@®]|\s+\w$", "", l["t"]).strip() for l in lines if l["y"] < 140 and l["x"] < 300 and "Comman" not in l["t"]]
        cname = next((close(t, cmds, 0.6) for t in top if close(t, cmds, 0.6)), None)
        if not cname:  # name missed: the commander whose skill names show up in the tooltip
            hits = {c: sum(any(ratio(l["t"], s["skill"]["name"]) > 0.8 for l in tip) for s in cmds[c]["skills"]) for c in cmds}
            cname = max(hits, key=hits.get) if max(hits.values()) else None
        if not cname:
            rep.add("commander", "manual", name, "nama commander tidak dikenali: " + " | ".join(top))
            continue
        seen.add(cname)
        skills = {s["skill"]["name"]: s for s in cmds[cname]["skills"]}
        titles = [l for l in tip if l["x"] > 790 and close(l["t"], skills, 0.75)]
        labels = [l for l in tip if l["t"] in ("Aktif", "Pasif")]
        for i, tl in enumerate(titles):
            sk = skills[close(tl["t"], skills, 0.75)]
            lab = next((l["t"] for l in labels if 0 < l["y"] - tl["y"] < 90), None)
            if lab and sk.get("type") and lab != sk["type"]:
                rep.add("commander", "selisih", name, f"{cname} / {sk['skill']['name']}: game {lab}, data {sk['type']}")
            end = titles[i + 1]["y"] if i + 1 < len(titles) else 700
            body = " ".join(l["t"] for l in tip if tl["y"] < l["y"] < end and l["x"] > 790 and l["t"] not in ("Aktif", "Pasif"))
            desc = sk["skill"]["description"].replace("\n", " ")
            cover = word_cover(body, desc)
            if cover < 0.8:
                rep.add("commander", "selisih" if cover < 0.6 else "manual", name,
                        f"{cname} / {sk['skill']['name']}: teks berbeda ({cover:.0%} kata cocok)\n    game: {body}\n    data: {desc}")
            else:
                rep.numbers_check("commander", name, f"{cname} / {sk['skill']['name']}", body, desc)
    rep.notes["commander"].append(f"{len(seen)} dari {len(cmds)} commander punya screenshot detail; "
                                  f"{len(in_list)} nama terbaca di daftar commander")
    if set(cmds) - seen:
        rep.notes["commander"].append("Tanpa screenshot detail: " + ", ".join(sorted(set(cmds) - seen)))


# ------------------------------------------------------------------ equipment

def equipment_by_body(body, levels):
    """Equipment level whose attributes/unique/passives match the visible panel lines (title not read by OCR)."""
    text = " ".join(l["t"] for l in body)
    if not text.strip():
        return None
    has_passive = "Pasif Unik" in text

    def score(lv):
        lines = lv["attributes"] + [f"Atribut Unik: {u}" for u in lv["unique"]]
        found = sum(re.sub(r"\s+", " ", x).lower() in text.lower() for x in lines)
        return found / max(1, len(lines)) + word_cover(text, " ".join(lv["passives"] + lines)) + (bool(lv["passives"]) == has_passive)
    ranked = sorted(((score(lv), n) for n, (_, lv) in levels.items()), reverse=True)
    if ranked and ranked[0][0] >= 2.5 and (len(ranked) == 1 or ranked[0][0] - ranked[1][0] > 0.2):
        return ranked[0][1]
    return None


def check_equipment(d, shots, rep):
    levels = {lv["name"]: (e, lv) for e in d["equipment"] if e.get("active", True) for lv in e["levels"]}
    inactive = {lv["name"] for e in d["equipment"] if not e.get("active", True) for lv in e["levels"]} - set(levels)
    seen = set()
    for name, lines in shots:
        head = [l for l in region(lines, 175, 335, 1000, 1300) if l["t"] not in ("Dasar", "Ditingkatkan")]
        if head and head[0]["t"].endswith(" yang"):  # OCR often drops the wrapped "Diperkuat" line
            head[0] = dict(head[0], t=head[0]["t"] + " Diperkuat")
            if len(head) > 1 and head[1]["t"] == "Diperkuat":
                head.pop(1)
        best = (0, None, 0)
        for k in (1, 2, 3):
            if k > len(head):
                break
            cand = " ".join(l["t"] for l in head[:k])
            for n in list(levels) + list(inactive):
                r = ratio(cand, n)
                if r > best[0] + 0.02:
                    best = (r, n, k)
        if best[0] < 0.8:
            lname = equipment_by_body(region(lines, 360, 760, 895, 1300), levels)
            if not lname:
                if head:
                    rep.add("equipment", "manual", name, "nama equipment tidak dikenali: " + " | ".join(l["t"] for l in head))
                continue
            best = (1, lname, len(head))  # title missed by OCR: the panel body identified it
        lname, used = best[1], best[2]
        if lname in inactive:
            rep.add("equipment", "selisih", name, f"{lname} tampil di game tapi ditandai nonaktif di data")
            continue
        seen.add(lname)
        _, lv = levels[lname]
        summary = " ".join(l["t"] for l in head[used:])
        if summary and lv["summary"] and word_cover(summary, lv["summary"]) < 1 and ratio(summary, lv["summary"]) < 0.8:
            rep.add("equipment", "manual", name, f"{lname}: ringkasan game '{summary}' vs data '{lv['summary']}'")
        body = region(lines, head[-1]["y"] + 30 if head else 360, 760, 895, 1300)
        attrs = [re.sub(r"\s+", " ", l["t"]) for l in body if l["t"].startswith("+")]
        scrolled = bool(body) and not attrs and not body[0]["t"].startswith(("Pasif", "Atribut"))
        for a in attrs:
            same = [x for x in lv["attributes"] if word_cover(a, x) >= 0.99]
            if not same:
                rep.add("equipment", "selisih", name, f"{lname}: atribut game '{a}' tidak ada di data {lv['attributes']}")
            elif not any(numbers(a) == numbers(x) for x in same):
                rep.add("equipment", "selisih", name, f"{lname}: atribut game '{a}' vs data {same}")
        if attrs and len(attrs) != len(lv["attributes"]):
            rep.add("equipment", "manual", name, f"{lname}: jumlah atribut game {attrs} vs data {lv['attributes']}")
        text = " ".join(l["t"] for l in body if not l["t"].startswith("+"))
        for u in re.findall(r"Atribut Unik:\s*(.+?)(?=Pasif Unik|Atribut Unik|$)", text):
            rep.numbers_check("equipment", name, f"{lname} atribut unik", u.strip(), " ".join(lv["unique"]))
        passives = [p.strip() for p in re.split(r"Pasif Unik\s*-\s*", text)[1:]]
        if not passives and text and not attrs:  # panel scrolled: the visible part must be in the passive text
            ref = " ".join(lv["passives"])
            if word_cover(text, ref) < 0.8:
                rep.add("equipment", "manual", name, f"{lname} (panel di-scroll): teks tidak cocok\n    game: {text}\n    data: {ref}")
            continue
        for p in passives:
            ref = next((x for x in lv["passives"] if x.split(":")[0].lower() in p.lower()[:40]), None)
            if not ref:
                rep.add("equipment", "selisih", name, f"{lname}: pasif game '{p[:70]}' tidak ada di data "
                                                     f"{[x.split(':')[0] for x in lv['passives']]}")
            else:
                rep.numbers_check("equipment", name, f"{lname} pasif", p, ref.replace("\n", " "))
        if len(passives) != len(lv["passives"]) and not scrolled:
            rep.add("equipment", "manual", name, f"{lname}: jumlah pasif game {len(passives)} vs data {len(lv['passives'])}")
    rep.notes["equipment"].append(f"{len(seen)} dari {len(levels)} level equipment aktif punya screenshot panel detail")
    if set(levels) - seen:
        rep.notes["equipment"].append("Tanpa screenshot panel detail: " + ", ".join(sorted(set(levels) - seen)))


# ------------------------------------------------------------------ go go cards

def card_blocks(lines):
    """Split the 4-column card grid into (title, description) pairs; cards cut off at the top have no title."""
    cols = defaultdict(list)
    for l in lines:
        if l["y"] > 140 and l["x"] > 260:
            cols[min(3, max(0, round((l["x"] - 282) / 283)))].append(l)
    out = []
    for col in cols.values():
        col.sort(key=lambda l: l["y"])
        blocks = []
        for l in col:
            if blocks and l["y"] - blocks[-1][-1]["y"] <= 22:
                blocks[-1].append(l)
            else:
                blocks.append([l])
        i = 0
        while i < len(blocks):
            b, nxt = blocks[i], blocks[i + 1] if i + 1 < len(blocks) else None
            if len(b) <= 2 and nxt and 0 < nxt[0]["y"] - b[-1]["y"] < 60:
                out.append((" ".join(l["t"] for l in sorted(b, key=lambda l: l["x"])), " ".join(l["t"] for l in nxt)))
                i += 2
            else:
                out.append(("", " ".join(l["t"] for l in b)))
                i += 1
    return out


def check_cards(d, shots, rep):
    cards = d["cards"]
    seen = set()
    alltext = []
    for name, lines in shots:
        alltext.append(" ".join(l["t"] for l in lines))
        for title, desc in card_blocks(lines):
            if not title or len(desc) < 15:
                continue

            def score(c):  # number-aware: twins such as Purest Power I differ only in their numbers
                return (0.4 * ratio(title, plain(c["name"])) + 0.6 * word_cover(desc, c["description"])
                        + 0.05 * (not sum(missing_numbers(desc, c["description"]), [])) + 0.01 * c.get("active", True))
            best = max(cards, key=score)
            if score(best) < 0.6:
                rep.add("card", "manual", name, f"kartu tidak dikenali: '{title}' / {desc[:80]}")
                continue
            seen.add(best["id"])
            sure = ratio(title, plain(best["name"])) >= 0.8
            if not best.get("active", True):
                rep.add("card", "selisih" if sure else "manual", name,
                        f"{best['name']} ({best['tier']}) tampil di game tapi ditandai nonaktif di data")
            rep.numbers_check("card", name, best["name"], desc, best["description"].replace("\n", " "), sure)
    # cards whose title OCR failed: look for their description (its words, numbers left out) in the card screens
    corpus = " ".join(re.findall(r"[a-z]{3,}", " ".join(alltext).lower()))
    unseen = []
    for c in cards:
        if not c.get("active", True) or c["id"] in seen:
            continue
        words = re.findall(r"[a-z]{3,}", plain(c["description"]).lower())
        grams = [" ".join(words[i:i + 3]) for i in range(max(1, len(words) - 2))]
        if grams and sum(g in corpus for g in grams) / len(grams) >= 0.5:
            seen.add(c["id"])
        else:
            unseen.append(f"{c['name']} ({c['tier']})")
    active = sum(c.get("active", True) for c in cards)
    rep.notes["card"].append(f"{active - len(unseen)} dari {active} kartu aktif terlihat di screenshot Go Go Card")
    if unseen:
        rep.notes["card"].append("Tidak terlihat: " + ", ".join(unseen))


# ------------------------------------------------------------------ ensiklopedia

def check_book(d, shots, rep):
    ref = " ".join(s.get("title", "") + " " + s.get("text", "") + " " + s.get("note", "") + " "
                   + " ".join(s.get("table", {}).get("header", [])) + " "
                   + " ".join(" ".join(map(str, r)) for r in s.get("table", {}).get("rows", []))
                   for t in d.get("encyclopedia", []) for s in t["sections"])
    if not ref.strip():
        rep.notes["book"].append("Data tidak punya Ensiklopedia")
        return
    for name, lines in shots:
        body = " ".join(l["t"] for l in lines if l["x"] > 280 and l["y"] > 170)
        cover = word_cover(body, ref)
        if cover < 0.9:
            rep.add("book", "manual", name, f"hanya {cover:.0%} kata cocok dengan teks Ensiklopedia\n    game: {body[:300]}")
        rep.numbers_check("book", name, "Ensiklopedia", body, ref, sure=False, show_data=False)
    rep.notes["book"].append(f"{len(shots)} screenshot dicocokkan dengan {len(d.get('encyclopedia', []))} tab Ensiklopedia")


# ------------------------------------------------------------------ patch notes

def entity_texts(d):
    """name key -> text holding the values the game shows for that hero/commander/card/synergy/equipment."""
    out = defaultdict(str)
    key = lambda n: re.sub(r"[^a-z0-9]", "", plain(n).lower())
    for h in d["heroes"]:
        out[key(h["name"])] += " ".join(v for st in h["stats"].values() for v in st.values()) + " " + \
            " ".join(s["description"] for s in h["skills"])
    for c in d["commanders"]:
        out[key(c["name"])] += " ".join(s["skill"]["description"] for s in c["skills"])
        for s in c["skills"]:
            out[key(s["skill"]["name"])] += s["skill"]["description"]
    for c in d["cards"]:
        out[key(c["name"])] += " " + c["description"]
    for s in d["synergies"]:
        out[key(s["name"])] += s["explain"] + " " + " ".join(t["effect"] for t in s["tiers"])
    for e in d["equipment"]:
        for lv in e["levels"]:
            out[key(lv["name"])] += " ".join(lv["attributes"] + lv["unique"] + lv["passives"])
    return out, key


def recorded_server_changes(season, key):
    """Names (hero / commander / skill / synergy / card) already noted in server_patch.json for this season."""
    path = HERE / "server_patch.json"
    if not path.exists():
        return set()
    names = set()
    for p in json.loads(path.read_text(encoding="utf-8")).get(str(season), []):
        for ch in sum((p.get(k, []) for k in ("heroes", "commanders", "hero_skills", "synergies", "cards")), []):
            names |= {key(ch["name"])} | ({key(ch["skill"])} if ch.get("skill") else set())
    return names


def check_patch(d, shots, rep):
    texts, key = entity_texts(d)
    recorded = recorded_server_changes(d.get("season"), key)
    active = {}  # card/equipment name -> active in this season's data
    for item in d["cards"]:
        active[key(item["name"])] = active.get(key(item["name"]), False) or item.get("active", True)
    for e in d["equipment"]:
        for lv in e["levels"]:
            active[key(lv["name"])] = active.get(key(lv["name"]), False) or e.get("active", True)
    header = re.compile(r"^(.+?)\s*\(\s*([^()]{0,10})\s*\)\s*$")
    change = re.compile(r"(\d[\d.,/% ]*)\s*(?:>>|»)\s*(\d[\d.,/% ]*)")
    done = set()
    for name, lines in shots:
        entity = None
        for l in region(lines, 160, 800, 420, 1366):
            t = l["t"].strip()
            m = header.match(t)
            if m and len(m.group(1)) <= 40:
                entity = m.group(1).strip()
                if "Baru" in m.group(2) and (entity, "baru") not in done:
                    done.add((entity, "baru"))
                    rep.patch_rows.append((entity, "(baru)", "ada di data" if key(entity) in texts else "tidak ditemukan di data"))
                continue
            if key(t) in texts and len(t) <= 40:  # header whose "(x)" marker OCR dropped
                entity = t
                continue
            ctx = t.split(":", 1)
            target = key(ctx[0]) if len(ctx) > 1 and key(ctx[0]) in texts else key(entity or "")
            if entity and "dihapus" in t.lower() and (entity, "dihapus") not in done:
                done.add((entity, "dihapus"))
                state = active.get(key(entity))
                rep.patch_rows.append((entity, t, "item tidak ditemukan di data" if state is None else
                                       "belum: masih aktif di data (dihapus lewat server)" if state else "sudah: nonaktif di data"))
                continue
            pairs = change.findall(t)
            if not pairs and entity and "/" in t:  # ">>" dropped: "240/365 260/395"
                groups = re.findall(r"\d[\d.,]*(?:/\d[\d.,]*)+%?", t)
                if len(groups) == 2 and len(groups[0].split("/")) == len(groups[1].split("/")):
                    pairs = [tuple(groups)]
            if not pairs or not entity:
                continue
            uid = (entity, re.sub(r"\W+", "", t.lower())[:60])
            if uid in done:
                continue
            done.add(uid)
            data_text = texts.get(target, "")
            label = re.search(r"(?<![\w.])([IVXl1|]{1,4}-\d)\s*(?:>>|»)\s*([IVXl1|]{1,4}-\d)", t)
            if label and data_text:  # babak label change ("Mulai Babak I-4 >> I-3"): compare the labels themselves
                old_l, new_l = (re.sub(r"[1l|]", "I", x) for x in label.groups())
                in_data = lambda lab: re.search(rf"(?<![IVX]){re.escape(lab)}(?!\d)", plain(data_text)) is not None
                status = ("sudah di data" if in_data(new_l) and not in_data(old_l) else
                          "belum: data masih nilai lama (diterapkan server)" if in_data(old_l) and not in_data(new_l) else
                          "tidak bisa dipastikan")
                rep.patch_rows.append((entity, t, status))
                continue
            # digits around ">>" read reliably, so single digits count here ("7 >> 8 Gold")
            old = {n for a, _ in pairs for n in numbers(a, keep_single=True)}
            new = {n for _, b in pairs for n in numbers(b, keep_single=True)}
            removed, added = old - new, new - old
            ref = set(numbers(data_text, keep_single=True))
            ref |= {n.rstrip("%") for n in ref}
            has = lambda vals: bool(vals) and all(v in ref or v.rstrip("%") in ref for v in vals)
            # both values occur in the text (Death Oracle: "30 Shield ... hingga 35 kali"): look at the word after it
            word = re.search(r"(?:>>|»)\s*[\d.,/% ]+\s*([A-Za-z]{3,})", t)
            near = lambda vals: word and any(re.search(rf"(?<![\d.]){re.escape(v)}\s+{word.group(1)}", data_text, re.I) for v in vals)
            if not data_text:
                status = "item tidak ditemukan di data"
            elif added and not has(added):
                status = "belum: angka baru tidak ada di data (diterapkan server)"
            elif has(added) and not has(removed):
                status = "sudah di data"
            elif near(added) and not near(removed):
                status = "sudah di data"
            elif near(removed) and not near(added):
                status = "belum: data masih nilai lama (diterapkan server)"
            else:
                status = "tidak bisa dipastikan"
            rep.patch_rows.append((entity, t, status))
    # server-only changes: are they already noted in server_patch.json (shown in the report as "Patch x (server)")?
    rep.patch_rows = [(e, t, s + (" · tercatat di server_patch.json" if key(e) in recorded else " · belum dicatat di server_patch.json")
                       if s.startswith("belum") else s) for e, t, s in rep.patch_rows]
    unrecorded = sum(s.endswith("belum dicatat di server_patch.json") for _, _, s in rep.patch_rows)
    rep.notes["patch"].append(f"{len(rep.patch_rows)} perubahan terbaca dari {len(shots)} screenshot patch note"
                              + (f"; {unrecorded} perubahan server belum dicatat di server_patch.json" if unrecorded else ""))


# ------------------------------------------------------------------ main

def latest_version():
    versions = [p.name for p in DATA.iterdir() if p.is_dir() and p.name != "diff"]
    return max(versions, key=lambda v: tuple(int(x) if x.isdigit() else 0 for x in re.split(r"[._]", v)))


def to_markdown(rep, season, version, ocr_path):
    lines = [f"# Validasi otomatis Season {season} (data {version})", "",
             f"- Dibuat {datetime.now().isoformat(timespec='seconds')} oleh `mc_validate.py` dari `{ocr_path}`.",
             "- **Selisih** = terbaca jelas tapi beda dengan data. **Cek manual** = kemungkinan salah baca OCR / panel "
             "di-scroll; lihat screenshot-nya.", "",
             "| Bagian | Layar | Selisih | Cek manual | Cakupan |", "|---|---|---|---|---|"]
    for kind, label in KINDS.items():
        it = rep.items[kind]
        cover = "; ".join(n for n in rep.notes[kind] if not n.startswith(("Tanpa", "Tidak")))
        lines.append(f"| {label} | {rep.screens[kind]} | {len(it['selisih'])} | {len(it['manual'])} | {cover} |")
    lines.append("")
    for level, title in (("selisih", "Selisih"), ("manual", "Cek manual")):
        lines += [f"## {title}", ""]
        anything = False
        for kind, label in KINDS.items():
            items = rep.items[kind][level]
            if items:
                anything = True
                lines += [f"### {label} ({len(items)})", ""]
                for shot, msg in items:
                    first, *rest = msg.split("\n")
                    lines.append(f"- `{shot}`: {first}")
                    lines += [f"  - {r.strip()}" for r in rest]
                lines.append("")
        if not anything:
            lines += ["Tidak ada.", ""]
    if rep.patch_rows:
        lines += ["## Patch note vs data", "", "| Item | Patch note | Status di data |", "|---|---|---|"]
        lines += [f"| {e} | {t.replace('|', '/')} | {s} |" for e, t, s in rep.patch_rows]
        lines.append("")
    gaps = [f"- {KINDS[k]}: {n}" for k in KINDS for n in rep.notes[k] if n.startswith(("Tanpa", "Tidak"))]
    if gaps:
        lines += ["## Belum ada screenshot", ""] + gaps + [""]
    return "\n".join(lines)


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Validasi laporan season terhadap screenshot in-game (OCR)")
    ap.add_argument("--season", type=int, required=True)
    ap.add_argument("--version", help="folder data/<versi>; default versi terbaru")
    ap.add_argument("--screens", type=Path, help="folder screenshot; default screenshot/season <n>")
    ap.add_argument("--dump", help="tampilkan teks OCR screenshot yang namanya mengandung teks ini")
    args = ap.parse_args()

    folder = (args.screens or HERE / "screenshot" / f"season {args.season}").resolve()
    if not (folder / "ocr.json").exists():
        sys.exit(f"{folder / 'ocr.json'} belum ada. Jalankan dulu: "
                 f"powershell -ExecutionPolicy Bypass -File ocr_screens.ps1 -Season {args.season}")
    shots = load_ocr(folder)
    if args.dump:
        for name, lines in shots.items():
            if args.dump in name:
                print(f"===== {name}  [{classify(lines)}]")
                for l in sorted(lines, key=lambda l: (l["y"], l["x"])):
                    print(f"{l['x']:6.0f},{l['y']:5.0f}  {l['t']}")
        return
    version = args.version or latest_version()
    path = DATA / version / f"S{args.season}.json"
    if not path.exists():
        sys.exit(f"{path} belum ada. Jalankan mc_data.py dulu.")
    d = json.loads(path.read_text(encoding="utf-8"))

    groups = defaultdict(list)
    for name, lines in shots.items():
        groups[classify(lines)].append((name, lines))
    rep = Report()
    for kind in KINDS:
        rep.screens[kind] = len(groups[kind])
    check_heroes(d, groups["hero"], rep)
    check_synergies(d, groups["synergy"], rep)
    check_commanders(d, groups["commander"], groups["commander_list"], rep)
    check_equipment(d, groups["equipment"], rep)
    check_cards(d, groups["card"], rep)
    check_book(d, groups["book"], rep)
    check_patch(d, groups["patch"], rep)

    out = DATA / version / f"VALIDASI_S{args.season}_auto.md"
    ocr_rel = folder.relative_to(HERE) / "ocr.json" if folder.is_relative_to(HERE) else folder / "ocr.json"
    out.write_text(to_markdown(rep, args.season, version, ocr_rel), encoding="utf-8")
    print(f"Season {args.season}, data {version}: {len(shots)} screenshot "
          f"({', '.join(f'{len(v)} {k}' for k, v in sorted(groups.items()))})")
    for kind, label in KINDS.items():
        it = rep.items[kind]
        print(f"  {label:13} {len(it['selisih']):3} selisih, {len(it['manual']):3} cek manual | " + "; ".join(rep.notes[kind]))
    print(f"  Laporan: {out}")


if __name__ == "__main__":
    main()
