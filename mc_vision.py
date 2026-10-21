"""Deteksi ikon game (hero, sinergi, Go Go Card, equipment) di screenshot dengan template matching OpenCV.

Ikon referensi = PNG dari file game (data/<versi>/img, lewat field "icon" di S<n>.json). Ukuran ikon di layar tidak perlu
diketahui: diperkirakan dulu di gambar yang diperkecil, lalu dicocokkan ulang di sekitar ukuran itu. Jadi screenshot PC
(1366x768, 1920x1080) maupun ponsel (2400x1080) bisa. Hanya bagian tengah ikon yang dicocokkan, supaya bingkai, bintang,
dan titik sinergi di bawah potret tidak mengganggu.

Cocok untuk layar yang memakai ikon kepala hero: hasil pertandingan, Rekomendasi Lineup, panel "Hero yang Ditempatkan",
Riwayat. Papan 3D dan Toko (model 3D) tidak bisa dikenali.

Pemakaian debug (Python sistem: opencv-python, numpy, pillow):
  python mc_vision.py <screenshot> [--kind hero|synergy|card|equipment] [--out annotated.png]
"""
import argparse
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

# part of the icon that is compared, relative to the icon centre in icon sizes (x0, y0, x1, y1)
INNER = {"hero": (-0.29, -0.32, 0.29, 0.16), "synergy": (-0.30, -0.32, 0.30, 0.12),
         "card": (-0.32, -0.30, 0.32, 0.30), "equipment": (-0.30, -0.30, 0.30, 0.30)}
ASPECT = {"card": 71 / 52}  # height / width of the small Go Go Card art
THRESHOLD = {"hero": 0.72, "synergy": 0.7, "card": 0.8, "equipment": 0.7}
# Second check: mean absolute colour difference (0-255) between screen patch and icon. Correlation alone also fires on
# smooth backgrounds; on the 2026-10-21 result screen true heroes had 8-20 and false hits 30-75.
MAX_DIFF = {"hero": 27, "synergy": 48, "card": 40, "equipment": 32}  # synergy icons get a tier-coloured backdrop
WORK_WIDTH = 1600  # screenshots are matched at this width (faster; enough detail for 30+ px icons)
WORKERS = os.cpu_count() or 1  # cv2.matchTemplate releases the GIL: icons are matched in parallel threads


def parallel(fn, jobs):
    with ThreadPoolExecutor(WORKERS) as ex:
        return list(ex.map(fn, jobs))


def to_bgr(image):
    if isinstance(image, (str, Path)):
        data = np.fromfile(str(image), dtype=np.uint8)  # cv2.imread cannot open non-ASCII Windows paths
        return cv2.imdecode(data, cv2.IMREAD_COLOR)
    if isinstance(image, Image.Image):
        return cv2.cvtColor(np.asarray(image.convert("RGB")), cv2.COLOR_RGB2BGR)
    return image


def load_icons(d, folder, kind):
    """{name: BGR icon} for one kind of item in the season data."""
    if kind == "hero":
        items = [(h["name"], h.get("icon")) for h in d["heroes"]]
    elif kind == "synergy":
        items = [(s["name"], s.get("icon")) for s in d["synergies"]]
    elif kind == "card":
        items = [(c["name"], c.get("icon")) for c in d["cards"] if c.get("active", True)]
    else:
        items = [(lv["name"], lv.get("icon") or e.get("icon")) for e in d["equipment"] if e.get("active", True) for lv in e["levels"]]
    names = {}  # icon -> names; cards Ⅰ/Ⅱ/Ⅲ and "+" versions share one picture, so they cannot be told apart
    for name, icon in items:
        if icon and (folder / icon).exists() and name not in names.setdefault(icon, []):
            names[icon].append(name)
    return {joined_name(n): to_bgr(folder / icon) for icon, n in names.items()}


def joined_name(names):
    """['Rising Fury Ⅲ', 'Rising Fury Ⅰ', 'Rising Fury Ⅱ'] -> 'Rising Fury Ⅰ / Ⅱ / Ⅲ'."""
    names = sorted(names)
    if len(names) == 1:
        return names[0]
    words = [n.split() for n in names]
    common = 0
    while all(len(w) > common + 1 and w[common] == words[0][common] for w in words):
        common += 1
    head = " ".join(words[0][:common])
    return f"{head} {' / '.join(' '.join(w[common:]) for w in words)}" if common else " / ".join(names)


def template(icon, size, kind):
    """Inner part of the icon scaled to an on-screen size (width in px)."""
    h = int(round(size * ASPECT.get(kind, 1)))
    icon = cv2.resize(icon, (int(round(size)), h), interpolation=cv2.INTER_AREA)
    x0, y0, x1, y1 = INNER[kind]
    cx, cy = size / 2, h / 2
    return icon[int(cy + y0 * h):int(cy + y1 * h), int(cx + x0 * size):int(cx + x1 * size)]


def estimate_size(img, icons, kind):
    """Best on-screen icon width (px at img scale): try sizes 3.5-11% of the image height on a half-size copy."""
    small = cv2.resize(img, (img.shape[1] // 2, img.shape[0] // 2), interpolation=cv2.INTER_AREA)
    sizes = [small.shape[0] * f for f in np.geomspace(0.035, 0.11, 16)]
    best = (0, None)

    def score(job):
        s, icon = job
        t = template(icon, s, kind)
        return None if t.shape[0] < 8 or t.shape[1] < 8 else float(cv2.matchTemplate(small, t, cv2.TM_CCOEFF_NORMED).max())
    for s in sizes:
        scores = [x for x in parallel(score, [(s, icon) for icon in icons.values()]) if x is not None]
        top = float(np.mean(sorted(scores)[-6:])) if scores else 0
        if top > best[0]:
            best = (top, s * 2)
    return best[1]


def detect(image, icons, kind="hero", size=None, threshold=None):
    """[{name, x, y, size, score}] of icons found in the image (coordinates of the original image), best match per spot."""
    img = to_bgr(image)
    scale = min(1.0, WORK_WIDTH / img.shape[1])
    if scale < 1:
        img = cv2.resize(img, (int(img.shape[1] * scale), int(img.shape[0] * scale)), interpolation=cv2.INTER_AREA)
    size = size * scale if size else estimate_size(img, icons, kind)
    if not size:
        return []
    threshold = threshold or THRESHOLD[kind]
    x0f, y0f = INNER[kind][0], INNER[kind][1]

    def match(job):
        s, name, icon = job
        h = s * ASPECT.get(kind, 1)
        t = template(icon, s, kind)
        res = cv2.matchTemplate(img, t, cv2.TM_CCOEFF_NORMED)
        peaks = (res >= threshold) & (res == cv2.dilate(res, np.ones((max(3, int(s / 2)),) * 2, np.uint8)))
        out = []
        for y, x in zip(*np.nonzero(peaks)):
            patch = img[y:y + t.shape[0], x:x + t.shape[1]]
            if np.abs(patch.astype(np.int16) - t.astype(np.int16)).mean() > MAX_DIFF[kind]:
                continue
            out.append((float(res[y, x]), name, (x - x0f * s) / scale, (y - y0f * h) / scale, s / scale))
        return out
    jobs = [(s, name, icon) for s in (size * 0.95, size, size * 1.05) for name, icon in icons.items()]
    found = [f for part in parallel(match, jobs) for f in part]
    found.sort(reverse=True)  # the order of the threads does not matter
    kept = []
    for score, name, x, y, s in found:  # one icon per spot: keep the best score
        if all((x - k["x"]) ** 2 + (y - k["y"]) ** 2 > (0.6 * min(s, k["size"])) ** 2 for k in kept):
            kept.append({"name": name, "x": round(x), "y": round(y), "size": round(s), "score": round(score, 3)})
    return sorted(kept, key=lambda k: (k["y"], k["x"]))


def rows(found, tol=0.5):
    """Group detections into horizontal rows (result screen: one row per player), each sorted left to right."""
    out = []
    for f in sorted(found, key=lambda f: f["y"]):
        if out and abs(f["y"] - np.mean([g["y"] for g in out[-1]])) < tol * f["size"]:
            out[-1].append(f)
        else:
            out.append([f])
    return [sorted(r, key=lambda f: f["x"]) for r in out]


def annotate(image, found, out):
    img = to_bgr(image).copy()
    for f in found:
        r = f["size"] // 2
        cv2.rectangle(img, (f["x"] - r, f["y"] - r), (f["x"] + r, f["y"] + r), (0, 220, 255), 2)
        cv2.putText(img, f"{f['name']} {f['score']:.2f}", (f["x"] - r, f["y"] - r - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.45,
                    (0, 220, 255), 1, cv2.LINE_AA)
    cv2.imencode(Path(out).suffix or ".png", img)[1].tofile(str(out))


def main():
    from mc_common import load_season
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Deteksi ikon game di screenshot")
    ap.add_argument("image", type=Path)
    ap.add_argument("--kind", default="hero", choices=list(INNER))
    ap.add_argument("--season", type=int)
    ap.add_argument("--out", type=Path, help="simpan gambar dengan kotak deteksi")
    args = ap.parse_args()
    d, folder = load_season(args.season)
    found = detect(args.image, load_icons(d, folder, args.kind), args.kind)
    for i, row in enumerate(rows(found), 1):
        print(f"baris {i} (y≈{row[0]['y']}): " + ", ".join(f"{f['name']} {f['score']:.2f}" for f in row))
    if args.out:
        annotate(args.image, found, args.out)
        print("gambar:", args.out)


if __name__ == "__main__":
    main()
