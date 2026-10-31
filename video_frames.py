"""Ambil frame dari rekaman pertandingan (MP4) dengan PyAV, termasuk rekaman layar ponsel HEVC (H.265) yang tidak bisa
dibaca video_frames.ps1. Hanya keyframe yang di-decode (cepat; rekaman ponsel punya keyframe ±tiap 1 detik), jadi waktu
frame bisa bergeser ±1 detik. Frame yang sudah ada (bukan 0 byte) tidak diambil ulang. Setelah itu bisa di-OCR:
ocr_screens.ps1 -Folder <out>. Juga dipakai mc_match.py (fungsi extract).

Pemakaian (dari folder patch-tracker; butuh paket av + pillow di Python sistem):
  python video_frames.py "screenshot\\season 7\\match\\<rekaman>.mp4" <folder_out> [--step 5] [--width 1600]
Hasil: <folder_out>\\f_<detik, 5 digit>.jpg
"""
import argparse
import time
from pathlib import Path

import av


def game_area(img):
    """A recording started with the phone upright has a portrait canvas with the landscape game across its middle and black
    above and below (31 Okt 03-23: 1080x2400, game 1080x486): keep that band. The game has the screen's own shape, turned."""
    w, h = img.size
    if h <= w:
        return img
    band = round(w * w / h)
    top = (h - band) // 2
    return img.crop((0, top, w, top + band))


def extract(video, out, step=5, width=1600, log=print):
    """Save one frame every `step` seconds as <out>/f_<second>.jpg; returns the number of new frames."""
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    with av.open(str(video)) as container:
        stream = container.streams.video[0]
        stream.thread_type = "AUTO"
        stream.codec_context.skip_frame = "NONKEY"
        dur = float(stream.duration * stream.time_base) if stream.duration else container.duration / 1e6
        log(f"{stream.codec_context.name} {stream.width}x{stream.height}, durasi {dur:.1f} detik")
        nxt, n = 0.0, 0
        for frame in container.decode(stream):
            if frame.time is None or frame.time < nxt:
                continue
            path = out / f"f_{int(nxt):05d}.jpg"
            if not path.exists() or path.stat().st_size == 0:
                img = game_area(frame.to_image())
                img.resize((width, round(width * img.height / img.width))).save(path, quality=88)
                n += 1
            while nxt <= frame.time:
                nxt += step
    log(f"{n} frame baru di {out} ({time.time() - t0:.0f} detik)")
    return n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("out", type=Path)
    ap.add_argument("--step", type=float, default=5)
    ap.add_argument("--width", type=int, default=1600)
    args = ap.parse_args()
    extract(args.video, args.out, args.step, args.width)


if __name__ == "__main__":
    main()
