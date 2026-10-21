"""Analisa pertandingan dari rekaman layar (MP4) dan/atau screenshot layar hasil -> data/<versi>/MATCH_<nama>.html/.md.

Pemakaian (Python sistem: av, opencv-python, numpy, pillow; OCR lewat mc_ocr.py = OCR bawaan Windows atau RapidOCR):
  python mc_match.py --video "screenshot\\season 7\\match\\rekaman.mp4" --result hasil1.jpg hasil2.jpg --player CinCoeg --name "21 Okt 15-38"
  python mc_match.py --result hasil.jpg --player CinCoeg            hanya layar hasil
Opsi: --step 5 (detik per frame), --frames <folder> (pakai frame yang sudah diambil), --no-events (lewati OCR frame penuh =
tanpa daftar kejadian), --ocr auto|windows|rapid, --season, --version.
OCR: --ocr auto = OCR Windows untuk frame rekaman (di luar Windows: RapidOCR), dan RapidOCR untuk layar hasil bila terpasang
(di screenshot hasil 21 Okt RapidOCR membaca 8/8 nama pemain, OCR Windows 3/8).

Cara kerja:
- Frame diambil tiap --step detik (video_frames.extract, bisa HEVC ponsel). Cache kerja: cache/match/<nama>/.
- Tata letak HUD dikenali dari rasio layar (ponsel 20:9 atau PC 16:9). Per frame, potongan babak, Gold, Level, dan daftar
  pemain digabung jadi satu gambar lalu di-OCR.
- HP tiap pemain diukur dari PANJANG BAR HP hijau (linear terhadap HP), dikalibrasi otomatis dengan angka HP yang terbaca
  jelas oleh OCR; angka OCR dipakai bila cocok dengan bar (selisih <= 6).
- Kejadian (Go Go Card, Go Go Box, crystal Pilihan, naik level, VICTORY/DEFEAT, panel DMG) dibaca dari OCR frame penuh.
- Layar hasil: hero dan Go Go Card tiap pemain dikenali dari ikon (mc_vision), nama/level dari OCR, sinergi dihitung dari
  hero (crystal tidak terlihat di layar hasil).
Hasil per babak memakai perubahan HP: HP turun = kalah; tetap = menang (lawan pemain atau creep). Angka adalah perkiraan
dari gambar; lihat bagian "Catatan metode" di laporan.
"""
import argparse
import difflib
import json
import re
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from PIL import Image

import mc_ocr
import mc_vision
import video_frames
from mc_common import HERE, ROMAN, chip, esc, load_season, md_table, norm, page, rel_src, round_label, slug, stamp, svg_chart, \
    table, write_report
from mc_lineup import Game

# HUD boxes as fractions of the frame (x0, y0, x1, y1), measured on 2400x1080 phone and 1376x776 PC recordings
LAYOUTS = {
    "ponsel": {"panel": (0.83, 0.07, 1.0, 0.76), "round": (0.34, 0.0, 0.40, 0.05), "gold": (0.87, 0.79, 0.97, 0.94),
               "level": (0.03, 0.83, 0.12, 0.97)},
    "pc": {"panel": (0.855, 0.075, 1.0, 0.75), "round": (0.315, 0.005, 0.36, 0.045), "gold": (0.89, 0.79, 0.98, 0.93),
           "level": (0.01, 0.79, 0.11, 0.93)},
}
UPSCALE = 2  # HUD crops are enlarged before OCR (ocr_screens.ps1 enlarges 2x again)
PARTS = ("round", "round_text", "gold", "level", "panel", "panel_text")  # *_text = white text on black (see text_only)
HUD_DIR = "hud2"  # bump when PARTS changes: sheets are reused from disk
ROUND_RE = re.compile(r"(?<![A-Za-z])([IVXl1|]{1,4})\s*[-–]\s*([1-6Il])(?!\d)")
LEVEL_RE = re.compile(r"Leve[l1I|]\s*(\d{1,2})")
EVENTS = [  # (regex on a frame's OCR text, kind)
    (r"Pilih Kartu Commander Power", "Pilih Kartu Power"),
    (r"pilih 1 Go Go Card", "Pilih Go Go Card"),
    (r"Pilih Hadiah", "Go Go Box"),
    (r"Magic Crystal pilihan aktif", "Crystal Pilihan"),
    (r"Kapasitas Hero \+1|Level Commander ditingkatkan", "Naik level"),
    (r"V[I1l]CTORY", "VICTORY"),
    (r"DEFEAT", "DEFEAT"),
    (r"Win Streak", "Win streak"),
    (r"Lose Streak", "Lose streak"),
    (r"DMG yang Diberikan", "Panel DMG"),
]


def log(*a):
    print(*a, flush=True)


# ------------------------------------------------------------------ OCR helpers

OCR_ENGINE = "auto"  # set from --ocr


def run_ocr(folder, engine=None, files=None):
    return mc_ocr.ocr_folder(folder, engine or OCR_ENGINE, files, log=log)


def crop(im, box):
    W, H = im.size
    return im.crop((int(box[0] * W), int(box[1] * H), int(box[2] * W), int(box[3] * H)))


def text_only(im):
    """White/yellow text on black, green HP bars and hearts removed (hearts were read as 0/9/e before the HP number)."""
    a = np.asarray(im.convert("RGB")).astype(int)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    keep = ((r > 170) & (g > 170) & (b > 170)) | ((r > 180) & (g > 150) & (b < 120))
    keep &= ~((g > r + 35) & (g > b + 15))
    out = np.zeros(a.shape, np.uint8)
    out[keep] = 255
    return Image.fromarray(out)


def hud_sheet(im, layout, out):
    """One image per frame with the HUD crops stacked; returns {part: (y offset, height)} in sheet pixels."""
    parts = {}
    for name in PARTS:
        c = crop(im, LAYOUTS[layout][name.replace("_text", "")])
        c = c.resize((c.width * UPSCALE, c.height * UPSCALE), Image.LANCZOS)
        parts[name] = text_only(c) if name.endswith("_text") else c
    offsets, y = {}, 0
    for name, p in parts.items():
        offsets[name] = (y, p.height)
        y += p.height + 30
    if not out.exists():
        sheet = Image.new("RGB", (max(p.width for p in parts.values()), y), (0, 0, 0))
        for name, p in parts.items():
            sheet.paste(p, (0, offsets[name][0]))
        sheet.save(out)
    return offsets


def hp_bars(im, layout):
    """[(y in frame px, bar length px, shield)] of the green HP bars in the player list (bars fill from the right).
    shield = white segment touching the green one: the green part is then shorter than the HP, so the bar is not used."""
    W, H = im.size
    x0, y0, x1, y1 = LAYOUTS[layout]["panel"]
    a = np.asarray(im.crop((int(x0 * W), int(y0 * H), int(x1 * W), int(y1 * H)))).astype(int)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    green = (g > 150) & (g > r + 40) & (g > b + 40)
    white = (r > 200) & (g > 200) & (b > 200)
    rows, out, y = green.sum(1), [], 0
    while y < len(rows):
        if rows[y] >= 0.15 * green.shape[1]:
            y2 = y
            while y2 + 1 < len(rows) and rows[y2 + 1] >= 0.15 * green.shape[1]:
                y2 += 1
            xs = np.where(green[y:y2 + 1].any(0))[0]
            runs, start = [], xs[0]
            for p, q in zip(xs, xs[1:]):
                if q != p + 1:
                    runs.append((start, p))
                    start = q
            runs.append((start, xs[-1]))
            a0, a1 = max(runs, key=lambda t: t[1] - t[0])
            band = white[max(0, y - 1):y2 + 2]
            shield = band[:, max(0, a0 - 40):a0].sum() + band[:, a1 + 1:a1 + 41].sum() >= 4
            out.append((int(y0 * H) + (y + y2) / 2, int(a1 - a0 + 1), bool(shield)))
            y = y2 + 1
        y += 1
    return out


def clean_name(t):
    t = re.sub(r"^[^\w]+", "", t.strip())
    t = re.sub(r"\s+\d{1,2}$", "", t)  # level badge glued to the name: "adikagacor 8"
    return t.strip(" .:")


def parse_round(text):
    m = ROUND_RE.search(text or "")
    if not m:
        return None
    roman = m.group(1).replace("1", "I").replace("l", "I").replace("|", "I")
    n = 1 if m.group(2) in "Il" else int(m.group(2))
    return f"{roman}-{n}" if roman in ROMAN else None


def round_number(label):
    """I-1 -> 1, II-1 -> 5, III-1 -> 11, IV-1 -> 17, V-1 -> 23 (phase IV and later 6 rounds), like mc_common.round_label."""
    roman, n = label.split("-")
    i = ROMAN.index(roman)
    return [0, 4, 10][i] + int(n) if i < 3 else 16 + (i - 3) * 6 + int(n)


# ------------------------------------------------------------------ video timeline

def read_frames(frames, work, layout):
    """Per frame: round, gold, level, player rows [{name, y, bar, ocr}] from the HUD sheets and HP bars."""
    hud = work / HUD_DIR
    hud.mkdir(exist_ok=True)
    info = {}
    for f in frames:
        im = Image.open(f).convert("RGB")
        info[f.stem] = (hud_sheet(im, layout, hud / f"{f.stem}.png"), im.size[1], hp_bars(im, layout))
    log(f"OCR {len(frames)} potongan HUD ...")
    ocr = run_ocr(hud)
    recs = []
    for f in frames:
        off, H, bars = info[f.stem]
        lines = ocr.get(f"{f.stem}.png", {}).get("lines", [])
        sheet = np.asarray(Image.open(hud / f"{f.stem}.png").convert("RGB")).astype(int)
        part = lambda name: [l for l in lines if off[name][0] <= l["y"] < off[name][0] + off[name][1]]
        text = lambda name: " ".join(l["t"] for l in part(name))
        gold = next((int(m) for m in re.findall(r"\d{1,3}", text("gold")) if int(m) <= 300), None)
        lv = LEVEL_RE.search(text("level"))
        py0 = LAYOUTS[layout]["panel"][1] * H
        to_frame = lambda l, name: py0 + (l["y"] - off[name][0]) / UPSCALE

        def yellow(l):  # own name is drawn in yellow
            box = sheet[int(l["y"]):int(l["b"]) + 1, int(l["x"]):int(l["r"]) + 1]
            r, g, b = box[..., 0], box[..., 1], box[..., 2]
            bright = (r > 170) & (g > 150)
            return bool(bright.sum() > 10 and ((b < 120) & bright).sum() > 0.5 * bright.sum())
        names = [(clean_name(l["t"]), to_frame(l, "panel"), yellow(l)) for l in part("panel")
                 if len(re.findall(r"[A-Za-z]", l["t"])) >= 3 and "Mirror" not in l["t"] and "Level" not in l["t"]]
        nums = []  # (y, hp, shield shown): "•10 •86" = shield 10 + HP 86
        for name in ("panel", "panel_text"):
            for l in part(name):
                found = re.findall(r"\d{1,3}", l["t"])
                if 1 <= len(found) <= 2 and not re.search(r"[A-Za-z]{2}", l["t"]) and int(found[-1]) <= 100:
                    nums.append((to_frame(l, name), int(found[-1]), len(found) == 2))
        rows = []
        for y, length, shield in bars:
            above = [n for n in names if 0 < y - n[1] < 0.06 * H]
            below = sorted((v for v in nums if 0 <= v[0] - y < 0.05 * H), key=lambda v: (not v[2], v[0] - y))
            if above:
                top = max(above, key=lambda n: n[1])
                rows.append({"name": top[0], "yellow": top[2], "y": y, "bar": length, "shield": shield or bool(below and below[0][2]),
                             "ocr": below[0][1] if below else None})
        recs.append({"t": int(f.stem[2:]), "round": parse_round(text("round") + " " + text("round_text")), "gold": gold,
                     "level": int(lv.group(1)) if lv and 1 <= int(lv.group(1)) <= 10 else None, "rows": rows})
    return recs


def name_key(name):
    for a, b in (("æ", "ae"), ("œ", "oe"), ("ø", "o"), ("...", "")):
        name = name.replace(a, b)
    return norm(name)


def same_player(k, ref, ratio=0.7):
    return k.startswith(ref[:5]) or ref.startswith(k[:5]) or difflib.SequenceMatcher(None, k, ref).ratio() >= ratio


def player_of(name, clusters):
    """Cluster for an OCR'd list name: prefix / similarity, looser (0.6) than when building clusters."""
    k = name_key(name)
    if len(k) < 3:
        return None
    best = max(clusters, key=lambda c: difflib.SequenceMatcher(None, k, c[1]).ratio(), default=None)
    hit = next((c for c in clusters if same_player(k, c[1])), None) or \
        (best if best and difflib.SequenceMatcher(None, k, best[1]).ratio() >= 0.6 else None)
    return hit[0] if hit else None


def cluster_players(recs, known=()):
    """Canonical player names from the (often truncated) list names: clusters of similar names, top 8 by frequency."""
    counts = Counter(r["name"] for rec in recs for r in rec["rows"])
    clusters = []  # [display name, key, count]
    for name, n in counts.most_common():
        k = name_key(name)
        if len(k) < 3:
            continue
        hit = next((c for c in clusters if same_player(k, c[1])), None)
        if hit:
            hit[2] += n
        else:
            clusters.append([name, k, n])
    clusters = sorted((c for c in clusters if c[2] >= 3), key=lambda c: -c[2])[:8]
    for c in clusters:  # full names from the result screen when the list shows "musuhkoru..."
        c[0] = next((k for k in known if same_player(norm(k), c[1])), c[0])
    return clusters


def calibrate(recs):
    """(a, b, n): bar = a * HP + b, fitted on rows whose OCR'd HP number is clean; fallback: longest bar = 100 HP."""
    pairs = np.array([(r["bar"], r["ocr"]) for rec in recs for r in rec["rows"] if r["ocr"] and 5 <= r["ocr"] <= 100], float)
    if len(pairs) >= 8:
        keep = np.ones(len(pairs), bool)
        for _ in range(3):
            a, b = np.polyfit(pairs[keep, 1], pairs[keep, 0], 1)
            keep = np.abs(pairs[:, 0] - (a * pairs[:, 1] + b)) < 5
        if a > 0.3 and keep.sum() >= 6:
            return float(a), float(b), int(keep.sum())
    longest = max((r["bar"] for rec in recs for r in rec["rows"]), default=100)
    return longest / 100, 0.0, 0


def accept_rounds(times, numbers):
    """Round numbers kept from the OCR'd labels (None = not read): the longest chain that never goes back and moves at most
    2 rounds + 1 per 40 s ahead. Unlike taking labels one by one, a misread label that jumps ahead (II-3 read during II-2,
    or a wrong first label) cannot make the correct labels after it look like steps back."""
    idx = [i for i, n in enumerate(numbers) if n]
    length, prev = {}, {}
    for j, i in enumerate(idx):
        length[i], prev[i] = 1, None
        for k in idx[:j]:
            if 0 <= numbers[i] - numbers[k] <= 2 + (times[i] - times[k]) // 40 and length[k] + 1 > length[i]:
                length[i], prev[i] = length[k] + 1, k
    keep, i = set(), max(idx, key=lambda i: length[i]) if idx else None
    while i is not None:
        keep.add(i)
        i = prev[i]
    return [n if i in keep else None for i, n in enumerate(numbers)]


def timeline(recs, clusters, cal, me=None):
    """Per frame: round number, gold, level, {player: HP}. HP = OCR number when it agrees with the bar (or the bar shows a
    shield), else the bar estimate. Rounds: labels outside the longest consistent chain are OCR slips (accept_rounds);
    frames between two kept labels are split evenly (half/half, or thirds when one label in between was never read)."""
    a, b, _ = cal
    out, numbers = [], []
    for rec in recs:
        hp = {}
        for r in rec["rows"]:
            p = me if (me and r.get("yellow")) else player_of(r["name"], clusters)
            if not p or p in hp:  # first row wins ("<name> Mirror" copies come later in the list)
                continue
            est = max(0.0, min(100.0, (r["bar"] - b) / a))
            if r["ocr"] is not None and (r["shield"] or abs(r["ocr"] - est) <= 6):
                hp[p] = r["ocr"]
            elif not r["shield"]:
                hp[p] = round(est)
        numbers.append(round_number(rec["round"]) if rec["round"] else None)
        out.append({"t": rec["t"], "round": None, "gold": rec["gold"], "level": rec["level"], "hp": hp})
    accepted = accept_rounds([x["t"] for x in out], numbers)
    idx = [i for i, n in enumerate(accepted) if n]
    for i in idx:
        out[i]["round"] = accepted[i]
    for i1, i2 in zip(idx, idx[1:]):
        n1, n2, gap = accepted[i1], accepted[i2], i2 - i1
        for j in range(i1 + 1, i2):
            step = (j - i1) * (n2 - n1 + 1) // gap if n2 > n1 else 0
            out[j]["round"] = min(n1 + step, n2)
    for i in range(idx[-1] + 1 if idx else 0, len(out)):
        out[i]["round"] = accepted[idx[-1]] if idx else None
    return out


def non_increasing(values):
    """Closest non-increasing sequence (HP never goes up), by pooling neighbours that break the order into one value, their
    lower median (isotonic regression, L1). One misread value is outvoted by its neighbours: 60 41 60 60 47 -> 60 60 60 60
    47, where replacing every rise by the previous value would give 60 41 41 41 41."""
    med = lambda b: sorted(b)[(len(b) - 1) // 2]
    blocks = []
    for v in values:
        blocks.append([v])
        while len(blocks) > 1 and med(blocks[-2]) < med(blocks[-1]):
            last = blocks.pop()
            blocks[-1] += last
    return [med(b) for b in blocks for _ in b]


def rounds_table(tl, players):
    """Per round: HP at the start (most common reading in the round's first 60%, made non-increasing per player), gold,
    level; delta = next start - start."""
    by_round = defaultdict(list)
    for x in tl:
        if x["round"]:
            by_round[x["round"]].append(x)
    rows = []
    for n in sorted(by_round):
        xs = by_round[n]
        head = xs[:max(1, int(len(xs) * 0.6))]
        start = {}
        for p in players:
            vals = [x["hp"][p] for x in head if p in x["hp"]]
            if vals:
                start[p] = Counter(vals).most_common(1)[0][0]
        golds = [x["gold"] for x in xs if x["gold"] is not None]
        levels = [x["level"] for x in xs if x["level"]]
        rows.append({"round": n, "label": round_label(n), "start": start, "gold": golds[0] if golds else None,
                     "level": max(levels) if levels else None, "delta": {}})
    for p in players:
        have = [r for r in rows if p in r["start"]]
        for r, v in zip(have, non_increasing([r["start"][p] for r in have])):
            r["start"][p] = v
    for cur, nxt in zip(rows, rows[1:]):
        cur["delta"] = {p: nxt["start"][p] - v for p, v in cur["start"].items() if p in nxt["start"]}
    return rows


def read_events(frames, d, by_time):
    ocr = run_ocr(frames[0].parent)
    cards = sorted((c["name"] for c in d["cards"] if c.get("active", True)), key=len, reverse=True)
    syns = [s["name"] for s in d["synergies"]]
    heroes = [h["name"] for h in d["heroes"]]
    events, seen = [], {}
    for f in frames:
        lines = ocr.get(f.name, {}).get("lines", [])
        text = " | ".join(l["t"] for l in lines)
        t = int(f.stem[2:])
        flat = norm(text)
        for pattern, kind in EVENTS:
            if not re.search(pattern.replace(" ", r"\s*"), text, re.I):  # RapidOCR may drop spaces ("GoGo Card")
                continue
            repeat = kind in seen and t - seen[kind] <= 15  # the same event on consecutive frames
            seen[kind] = t
            if repeat:
                continue
            detail = ""
            if kind in ("Pilih Kartu Power", "Pilih Go Go Card"):
                found = list(dict.fromkeys(c for c in cards if norm(c) in flat))
                found = [c for c in found if not any(norm(c) in norm(o) and c != o for o in found)]  # Rising Fury Ⅰ in Ⅱ
                detail = "pilihan: " + ", ".join(found) if found else ""
            elif kind == "Crystal Pilihan":
                m = re.search(r"Sinergi:\s*([A-Za-z ]+)", text)
                detail = next((s for s in syns if m and norm(s) in norm(m.group(1))), m.group(1).strip() if m else "")
            elif kind in ("VICTORY", "DEFEAT"):
                m = re.search(r"Gold:\s*\+?\s*(\d+)", text)
                detail = f"Gold +{m.group(1)}" if m else ""
            elif kind in ("Win streak", "Lose streak"):
                m = re.search(r"(\d+)\s*(?:Win|Lose)\s*Streak", text, re.I)
                detail = f"{m.group(1)} beruntun" if m else ""
            elif kind == "Panel DMG":
                pairs = []
                for i, l in enumerate(lines):
                    h = next((h for h in heroes if norm(l["t"]).startswith(norm(h))), None)
                    num = next((int(n) for n in re.findall(r"\b\d{3,6}\b", " ".join(x["t"] for x in lines[i:i + 3]))), None)
                    if h and num and h not in [p[0] for p in pairs]:
                        pairs.append((h, num))
                detail = ", ".join(f"{h} {n:,}".replace(",", ".") for h, n in pairs[:5])
            events.append({"t": t, "round": by_time.get(t), "kind": kind, "detail": detail, "frame": f})
    return events


# ------------------------------------------------------------------ result screen

def read_result(paths, d, folder, engine=None):
    """Rows of the result screen(s): rank order, name, level, heroes, cards. Several screenshots of the same screen
    (scrolled hero list) are merged per row; the icon size found on the first one is reused."""
    hero_icons, card_icons = mc_vision.load_icons(d, folder, "hero"), mc_vision.load_icons(d, folder, "card")
    tmp = HERE / "cache" / "match" / "_result"  # OCR copies here so no ocr.json lands in the screenshot folder
    tmp.mkdir(parents=True, exist_ok=True)
    for p in paths:
        copy = tmp / p.name
        if not copy.exists() or copy.stat().st_size != p.stat().st_size:
            copy.write_bytes(p.read_bytes())
    ocr = run_ocr(tmp, engine, [tmp / p.name for p in paths])
    rows, meta, sizes = {}, {}, {}
    for p in paths:
        found_h = mc_vision.detect(p, hero_icons, "hero", size=sizes.get("hero"))
        found_c = mc_vision.detect(p, card_icons, "card", size=sizes.get("card"))
        for kind, found in (("hero", found_h), ("card", found_c)):
            if found and kind not in sizes:
                sizes[kind] = statistics.median(f["size"] for f in found)
        heroes = [r for r in mc_vision.rows(found_h) if len(r) >= 2]
        cards = mc_vision.rows(found_c)
        lines = ocr.get(p.name, {}).get("lines", [])
        text = " ".join(l["t"] for l in lines)
        meta.setdefault("id", next(iter(re.findall(r"\b\d{15,20}\b", text)), None))
        pts = re.search(r"(\d{3,5})\s*([+-]\d{1,3})\b", text)
        if pts:
            meta.setdefault("points", f"{pts.group(1)} ({pts.group(2)})")
        x_left = min((f["x"] for r in heroes for f in r), default=0)
        level_ys = sorted((l["y"] + l["b"]) / 2 for l in lines if LEVEL_RE.search(l["t"]) and l["r"] < x_left)
        for i, r in enumerate(heroes, 1):
            y, size = sum(f["y"] for f in r) / len(r), r[0]["size"]
            if len(heroes) <= len(level_ys) <= 8:  # rank = order of the "Level N" lines, so a row without heroes shifts nothing
                i = 1 + min(range(len(level_ys)), key=lambda k: abs(level_ys[k] - y))
            x_first = min(f["x"] for f in r)
            near = [l for l in lines if abs((l["y"] + l["b"]) / 2 - y) < size * 0.9 and l["r"] < x_first - size]
            name = next((clean_name(l["t"]) for l in sorted(near, key=lambda l: l["y"])  # "AJ11" has 2 letters, badge "39" none
                         if len(re.findall(r"[A-Za-z]", l["t"])) >= 2 and not LEVEL_RE.search(l["t"])), f"baris {i}")
            lv = next((int(m.group(1)) for l in near if (m := LEVEL_RE.search(l["t"]))), None)
            row_cards = next((c for c in cards if abs(sum(f["y"] for f in c) / len(c) - y) < size * 0.6), [])
            cur = rows.setdefault(i, {"rank": i, "name": name, "level": lv, "heroes": [], "cards": []})
            if cur["name"].startswith("baris ") or (norm(name) == norm(cur["name"]) and len(name) > len(cur["name"])):
                cur["name"] = name  # the fullest reading over the screenshots ("TT:jawirGG", not "TTjawirGG")
            cur["heroes"] = list(dict.fromkeys(cur["heroes"] + [f["name"] for f in r]))
            cur["cards"] = list(dict.fromkeys(cur["cards"] + [f["name"] for f in row_cards]))
            cur["level"] = cur["level"] or lv
    return [rows[k] for k in sorted(rows)], meta


# ------------------------------------------------------------------ insights

def insights(rounds, me, events, final_rank):
    out = []
    if final_rank:
        out.append(("good" if final_rank <= 3 else "warn", f"Peringkat akhir {final_rank}."))
    phases = {}
    for r in rounds:
        d = r["delta"].get(me)
        if d is not None and d < 0:
            phase = r["label"].split("-")[0]
            phases[phase] = phases.get(phase, 0) - d
    if phases:
        worst = max(phases, key=phases.get)
        out.append(("warn" if phases[worst] >= 25 else "", "HP hilang per fase: " + ", ".join(f"Fase {k} −{v}" for k, v in phases.items())
                    + f". Terbanyak di Fase {worst}."))
    streak, best, lose, worst_lose = 0, (0, None), 0, (0, None)
    for r in rounds:
        d = r["delta"].get(me)
        if d is None:
            continue
        if d < 0:
            lose, streak = lose + 1, 0
            if lose > worst_lose[0]:
                worst_lose = (lose, r["label"])
        else:
            streak, lose = streak + 1, 0
            if streak > best[0]:
                best = (streak, r["label"])
    if best[0] >= 3:
        out.append(("good", f"{best[0]} babak beruntun tanpa kehilangan HP (sampai {best[1]})."))
    if worst_lose[0] >= 2:
        out.append(("bad", f"{worst_lose[0]} kekalahan beruntun (sampai {worst_lose[1]})."))
    for lv in (7, 8, 9):
        first = next((r["label"] for r in rounds if (r["level"] or 0) >= lv), None)
        if first:
            out.append(("", f"Level {lv} pertama terlihat di {first}."))
    for phase in ("II", "III"):
        golds = [r["gold"] for r in rounds if r["label"].startswith(phase + "-") and r["gold"] is not None]
        if golds:
            avg = sum(golds) / len(golds)
            out.append(("good" if avg >= 45 else "warn" if avg < 20 else "",
                        f"Rata-rata Gold di awal babak Fase {phase}: {avg:.0f}" +
                        (" (bunga hampir maksimal)" if avg >= 45 else " (bunga kecil)" if avg < 20 else "") + "."))
    gone = {}
    for r in rounds:
        for p, v in r["start"].items():
            if v == 0 and p not in gone and p != me:
                gone[p] = r["label"]
    if gone:
        out.append(("", "Tereliminasi: " + ", ".join(f"{p} ({lab})" for p, lab in gone.items()) + "."))
    for e in events:
        if e["kind"] == "Panel DMG" and e["detail"]:
            out.append(("", f"Panel DMG {round_label(e['round']) if e['round'] else ''}: {e['detail']}."))
    return out


# ------------------------------------------------------------------ main

def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Analisa pertandingan dari rekaman dan/atau screenshot hasil")
    ap.add_argument("--video", type=Path)
    ap.add_argument("--result", type=Path, nargs="*", default=[])
    ap.add_argument("--player", help="nama kamu di game (untuk timeline dan peringkat)")
    ap.add_argument("--name")
    ap.add_argument("--step", type=float, default=5)
    ap.add_argument("--frames", type=Path, help="folder frame f_<detik>.jpg yang sudah ada")
    ap.add_argument("--no-events", action="store_true")
    ap.add_argument("--ocr", default="auto", choices=mc_ocr.ENGINES, help="mesin OCR (lihat mc_ocr.py)")
    ap.add_argument("--season", type=int)
    ap.add_argument("--version")
    args = ap.parse_args()
    if not (args.video or args.frames or args.result):
        ap.error("isi --video/--frames dan/atau --result")
    global OCR_ENGINE
    OCR_ENGINE = args.ocr
    result_engine = "rapid" if args.ocr == "auto" and mc_ocr.rapid_available() else args.ocr
    d, folder = load_season(args.season, args.version)
    game = Game(d)
    name = args.name or (args.video or args.frames or args.result[0]).stem
    work = HERE / "cache" / "match" / slug(name)
    work.mkdir(parents=True, exist_ok=True)
    assets = folder / f"match_{slug(name)}"

    final, meta = read_result([p.resolve() for p in args.result], d, folder, result_engine) if args.result else ([], {})
    if final:
        log(f"Layar hasil: {len(final)} pemain dikenali")
    names = [r["name"] for r in final]
    me = None
    if args.player:
        me = next((n for n in names if norm(n) == norm(args.player)), None) or \
             next((n for n in names if difflib.SequenceMatcher(None, norm(n), norm(args.player)).ratio() > 0.7), args.player)

    rounds, events, players, cal, layout = [], [], [], (1.0, 0.0, 0), None
    if args.video or args.frames:
        frames_dir = args.frames or work / "frames"
        if args.video and not args.frames:
            video_frames.extract(args.video, frames_dir, args.step, 1600, log)
        frames = [f for f in sorted(Path(frames_dir).glob("f_*.jpg"), key=lambda p: int(p.stem[2:])) if f.stat().st_size]
        w, h = Image.open(frames[0]).size
        layout = "ponsel" if w / h >= 2.0 else "pc"
        log(f"{len(frames)} frame, tata letak {layout}")
        recs = read_frames(frames, work, layout)
        clusters = cluster_players(recs, names)
        players = [c[0] for c in clusters]
        if args.player and me not in players:
            me = next((p for p in players if same_player(norm(p), norm(args.player))), me)
        cal = calibrate(recs)
        tl = timeline(recs, clusters, cal, me if me in players else None)
        (work / "timeline.json").write_text(json.dumps(tl, ensure_ascii=False), encoding="utf-8")
        rounds = rounds_table(tl, players)
        if not args.no_events:
            log("OCR frame penuh untuk kejadian ...")
            events = read_events(frames, d, {x["t"]: x["round"] for x in tl})
    final_rank = next((r["rank"] for r in final if me and norm(r["name"]) == norm(me)), None)
    title = f"Analisa Pertandingan — {name}"
    body, md = [], [f"# {title}", "", f"_{stamp(d)}_", ""]

    me_hp = [r["start"][me] for r in rounds if me in r["start"]]
    losses = sum(1 for r in rounds if (r["delta"].get(me) or 0) < 0)
    boxes = [("Peringkat", str(final_rank) if final_rank else "-"),
             ("HP akhir", str(me_hp[-1]) if me_hp else "-"),
             ("Babak terbaca", f"{rounds[0]['label']} – {rounds[-1]['label']} ({len(rounds)} babak), kehilangan HP di {losses} babak"
              if rounds else "-"),
             ("Pertandingan", f"ID {meta.get('id') or '-'} · poin {meta.get('points') or '-'}")]
    if not rounds:  # result screen only: no HP timeline
        boxes = [x for x in boxes if x[0] not in ("HP akhir", "Babak terbaca")]
    body.append('<section><h2>Ringkasan</h2><div class="grid3">' +
                "".join(f'<div class="box"><h4>{esc(k)}</h4><p>{esc(v)}</p></div>' for k, v in boxes) +
                f'</div><p class="muted small">Pemain: {esc(me or "-")}' + (f" · tata letak {esc(layout)}" if layout else "") + "</p></section>")
    md += [f"- **{k}:** {v}" for k, v in boxes] + [f"- Pemain: {me or '-'}", ""]

    notes = insights(rounds, me, events, final_rank) if (rounds or final_rank) else []
    if notes:
        body.append("<section><h2>Catatan otomatis</h2><ul>" + "".join(
            f'<li class="{c}">{esc(t)}</li>' if c else f"<li>{esc(t)}</li>" for c, t in notes) + "</ul></section>")
        md += ["## Catatan otomatis", ""] + [f"- {t}" for _, t in notes] + [""]

    if rounds:
        series = {p: [r["start"].get(p) for r in rounds] for p in players}
        body.append(f'<section><h2>HP per babak</h2>{svg_chart(series, [r["label"] for r in rounds], highlight=me)}</section>')
        ev_by_round = defaultdict(list)
        for e in events:
            if e["round"] and e["kind"] not in ("Panel DMG", "Win streak", "Lose streak"):
                ev_by_round[e["round"]].append(e["kind"] + (f" ({e['detail']})" if e["detail"] else ""))
        cells, md_rows = [], []
        for r in rounds:
            hp, dlt = r["start"].get(me), r["delta"].get(me)
            res = "" if dlt is None else ("kalah" if dlt < 0 else "tidak kehilangan HP")
            cls = "nerf" if dlt is not None and dlt < 0 else "buff" if dlt == 0 else "muted"
            evs = "; ".join(dict.fromkeys(ev_by_round.get(r["round"], [])))
            cells.append([f"<b>{r['label']}</b>", esc(hp if hp is not None else "-"),
                          f'<span class="{cls}">{dlt:+d}</span> {esc(res)}' if dlt is not None else "-",
                          esc(r["gold"] if r["gold"] is not None else "-"), esc(r["level"] or "-"), esc(evs)])
            md_rows.append([r["label"], hp if hp is not None else "-", f"{dlt:+d} {res}" if dlt is not None else "-",
                            r["gold"] if r["gold"] is not None else "-", r["level"] or "-", evs])
        heads = ["Babak", "HP awal", "Perubahan", "Gold awal", "Level", "Kejadian"]
        body.append(f'<section><h2>Timeline ({esc(me or "pemain")})</h2>{table(heads, cells)}</section>')
        md += [f"## Timeline ({me or 'pemain'})", ""] + md_table(heads, md_rows) + [""]
        heads = ["Pemain"] + [r["label"] for r in rounds]
        grid = [[p] + [r["start"].get(p, "") for r in rounds] for p in players]
        body.append(f'<section><h2>HP semua pemain</h2>{table(heads, [[esc(c) for c in row] for row in grid])}</section>')
        md += ["## HP semua pemain", ""] + md_table(heads, grid) + [""]
    if events:
        rows = [[f"{e['t'] // 60:02d}:{e['t'] % 60:02d}", round_label(e["round"]) if e["round"] else "-", e["kind"], e["detail"]]
                for e in events]
        body.append(f'<section><h2>Kejadian</h2>{table(["Waktu", "Babak", "Kejadian", "Detail"], [[esc(c) for c in r] for r in rows])}</section>')
        md += ["## Kejadian", ""] + md_table(["Waktu", "Babak", "Kejadian", "Detail"], rows) + [""]
    if final:
        rows, md_rows = [], []
        for r in final:
            known = [h for h in r["heroes"] if h in game.H]
            counts, active = game.counts(known, []), game.active_tiers(known, [])
            mine = bool(me and norm(r["name"]) == norm(me))
            rows.append([f"<b>{r['rank']}</b>", esc(r["name"]) + (" <b>(kamu)</b>" if mine else ""), esc(r["level"] or "-"),
                         " ".join(chip(h, game.H[h].get("icon"), f"c{game.H[h]['cost']}") for h in known),
                         " ".join(chip(c) for c in r["cards"]),
                         " ".join(chip(f"{s} {counts[s]}", game.S[s].get("icon")) for s in active)])
            md_rows.append([r["rank"], r["name"] + (" (kamu)" if mine else ""), r["level"] or "-", ", ".join(known),
                            ", ".join(r["cards"]), ", ".join(f"{s} {counts[s]}" for s in active)])
        heads = ["#", "Pemain", "Level", "Hero", "Go Go Card", "Sinergi dari hero"]
        body.append(f'<section><h2>Papan akhir (layar hasil)</h2>{table(heads, rows)}'
                    '<p class="muted small">Sinergi dihitung dari hero yang terlihat; crystal tidak tampil di layar hasil, jadi angka '
                    'sebenarnya bisa lebih tinggi. Satu baris layar hasil memuat 9 hero (geser untuk hero ke-10). Kartu Ⅰ/Ⅱ/Ⅲ dengan '
                    'gambar sama tidak bisa dibedakan.</p></section>')
        md += ["## Papan akhir (layar hasil)", ""] + md_table(heads, md_rows) + [""]
    figs = []
    for e in [e for e in events if e["kind"] in ("Pilih Kartu Power", "Pilih Go Go Card", "Go Go Box", "Crystal Pilihan", "Panel DMG")][:24]:
        assets.mkdir(exist_ok=True)
        out = assets / f"{e['frame'].stem}.jpg"
        if not out.exists():
            im = Image.open(e["frame"])
            im.resize((640, round(640 * im.height / im.width))).save(out, quality=82)
        cap = f"{e['t'] // 60:02d}:{e['t'] % 60:02d} · {round_label(e['round']) if e['round'] else '-'} · {e['kind']}"
        figs.append(f'<figure><img class="shot" src="{esc(rel_src(out, folder))}" alt="" loading="lazy">'
                    f'<figcaption>{esc(cap)}</figcaption></figure>')
    if figs:
        body.append(f'<section><h2>Frame kunci</h2><div class="shots">{"".join(figs)}</div></section>')
    a, b, n = cal
    method = []
    if layout:
        method += [f"Tata letak: {layout}; frame tiap {args.step:g} detik; OCR: {mc_ocr.describe(OCR_ENGINE)}.",
                   f"HP dari panjang bar: HP = (panjang − {b:.1f}) / {a:.3f}" +
                   (f", dikalibrasi dari {n} angka HP yang terbaca OCR." if n else ", tanpa kalibrasi OCR (bar terpanjang = 100 HP)."),
                   "HP awal babak = nilai terbanyak di 60% awal babak, lalu dibuat tidak pernah naik (nilai yang melanggar urutan "
                   "digabung dengan tetangganya, diambil mediannya).",
                   "Label babak dipakai bila termasuk rantai terpanjang yang tidak pernah mundur (maks. 2 babak + 1 per 40 detik ke "
                   "depan); frame di antara dua label dibagi rata.",
                   "Pilihan Go Go Card = kartu yang tampil di layar pilihan; kartu yang akhirnya diambil terlihat di layar hasil.",
                   "Teks Win/Lose Streak hanya dicatat di daftar Kejadian (tidak di timeline): teks itu bisa milik lawan yang sedang "
                   "tampil, jadi tidak dipakai untuk menentukan hasil babak."]
    if final:
        method.append(f"Layar hasil: hero dan Go Go Card dari ikon (mc_vision), nama dan level dari OCR "
                      f"({mc_ocr.describe(result_engine)}); "
                      "peringkat = urutan baris.")
    body.append(f'<section><h2>Catatan metode</h2><ul>{"".join(f"<li>{esc(m)}</li>" for m in method)}</ul></section>')
    md += ["## Catatan metode", ""] + [f"- {m}" for m in method]
    out_html, out_md = write_report(folder, f"MATCH_{slug(name)}", page(title, "".join(body), stamp(d)), md)
    log(f"Laporan: {out_html}\n         {out_md}")


if __name__ == "__main__":
    main()
