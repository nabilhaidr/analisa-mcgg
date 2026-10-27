"""OCR untuk alat analisa (mc_patch.py, mc_match.py): satu fungsi, dua mesin, format hasil sama dengan ocr_screens.ps1.

Mesin:
- "windows": OCR bawaan Windows lewat ocr_screens.ps1 -> <folder>/ocr.json (perilaku lama; ocr.json juga dipakai
  mc_validate.py). Hanya di Windows.
- "rapid": RapidOCR (model PP-OCR, offline; Windows/Linux/macOS; `pip install rapidocr_onnxruntime`) -> <folder>/ocr_rapid.json.
  Di layar hasil pertandingan PC (screenshot 1873) membaca 8/8 nama pemain, OCR Windows 3/8.
- "auto" (default): Windows bila ada PowerShell; selain itu ocr.json yang sudah ada bila mencakup semua gambar yang diminta
  (hasil OCR Windows yang ikut di repo, jadi hasilnya sama dengan di Windows), lalu RapidOCR.

Hasil: {"<path relatif, pemisah \\>": {"stamp", "w", "h", "lines": [{"t", "x", "y", "r", "b"}]}} dalam piksel gambar asli.
Gambar yang tidak berubah (ukuran + waktu ubah sama) diambil dari cache, seperti ocr_screens.ps1.
"""
import importlib.util
import json
import os
import shutil
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
ENGINES = ("auto", "windows", "rapid")
SUFFIXES = (".png", ".jpg", ".jpeg")
RAPID_SCALE = 2  # small text is enlarged first, like ocr_screens.ps1
_rapid = None


def images_in(folder):
    return sorted(p for p in Path(folder).rglob("*") if p.is_file() and p.suffix.lower() in SUFFIXES)


def key_of(folder, path):
    """'match\\Screenshot (1873).png': the key ocr_screens.ps1 writes, on every OS."""
    return "\\".join(Path(path).resolve().relative_to(Path(folder).resolve()).parts)


def windows_available():
    return os.name == "nt" and shutil.which("powershell") is not None


def rapid_available():
    return importlib.util.find_spec("rapidocr_onnxruntime") is not None


def describe(engine):
    """Engine name for reports: what "auto" becomes on this computer (ocr.json from elsewhere is used only if complete)."""
    return engine if engine != "auto" else "windows" if windows_available() else "rapid"


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig")).get("images", {}) if path.exists() else {}


def covers(images, folder, files):
    """True when every file has an entry of the same file size (stamp = "<size>-<time>")."""
    return all(str(f.stat().st_size) == str(images.get(key_of(folder, f), {}).get("stamp", "")).split("-")[0] for f in files)


def run_windows(folder, quiet=True):
    subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", str(HERE / "ocr_screens.ps1"), "-Folder", str(folder)],
                   check=True, stdout=subprocess.DEVNULL if quiet else None)
    return load_json(Path(folder) / "ocr.json")


def run_rapid(folder, files, log=print):
    global _rapid
    out = Path(folder) / "ocr_rapid.json"
    images = load_json(out)
    todo = []
    for f in files:
        st = f.stat()
        if images.get(key_of(folder, f), {}).get("stamp") != f"{st.st_size}-{st.st_mtime_ns}":
            todo.append(f)
    if todo:
        from rapidocr_onnxruntime import RapidOCR
        _rapid = _rapid or RapidOCR()
        log(f"RapidOCR {len(todo)} gambar ...")
    for i, f in enumerate(todo, 1):
        st = f.stat()
        with Image.open(f) as im:
            w, h = im.size
            big = im.convert("RGB").resize((w * RAPID_SCALE, h * RAPID_SCALE), Image.LANCZOS)
        result, _ = _rapid(np.ascontiguousarray(np.asarray(big)[..., ::-1]))  # BGR, like cv2.imread
        lines = []
        for box, text, _score in result or []:
            xs, ys = [p[0] for p in box], [p[1] for p in box]
            lines.append({"t": text, "x": int(min(xs) / RAPID_SCALE), "y": int(min(ys) / RAPID_SCALE),
                          "r": int(max(xs) / RAPID_SCALE), "b": int(max(ys) / RAPID_SCALE)})
        lines.sort(key=lambda l: (l["y"], l["x"]))
        images[key_of(folder, f)] = {"stamp": f"{st.st_size}-{st.st_mtime_ns}", "w": w, "h": h, "lines": lines}
        if i % 25 == 0 or i == len(todo):
            out.write_text(json.dumps({"version": 1, "engine": "rapid", "images": images}, ensure_ascii=False), encoding="utf-8")
            if i % 25 == 0:
                log(f"  {i}/{len(todo)} gambar di-OCR ...")
    return images


KOREAN_REC = HERE / "cache" / "models" / "korean" / "korean_PP-OCRv5_rec_mobile.onnx"
_korean = None


def read_korean(images):
    """[(text, score)] for one-line text pictures (PIL) read by RapidOCR's Korean recognizer (PP-OCRv5 mobile: Hangul and
    Latin), or None without the model file or RapidOCR 1.2. The page OCR has only Chinese and English models, so a Hangul
    name gives no text at all. The model is onnx/PP-OCRv5/rec/korean_PP-OCRv5_rec_mobile.onnx of ModelScope
    RapidAI/RapidOCR v3.10.0 (13.5 MB); cache/ is not in git, so download it again after a clone."""
    global _korean
    if _korean is None:
        try:
            from rapidocr_onnxruntime.ch_ppocr_v3_rec.text_recognize import TextRecognizer
        except ImportError:
            return None
        if not KOREAN_REC.exists():
            return None
        _korean = TextRecognizer({"model_path": str(KOREAN_REC), "rec_img_shape": [3, 48, 320], "rec_batch_num": 6,
                                  "use_cuda": False})
    result, _ = _korean([np.ascontiguousarray(np.asarray(im.convert("RGB"))[..., ::-1]) for im in images])  # BGR
    return [(text, float(score)) for text, score in result]


def ocr_folder(folder, engine="auto", files=None, log=print):
    """OCR of the images in `folder` (all, or only `files`) as {key: {"stamp", "w", "h", "lines"}} (see module doc)."""
    folder = Path(folder)
    files = [Path(f) for f in files] if files is not None else images_in(folder)
    if engine == "auto":
        if windows_available():
            engine = "windows"
        else:
            cached = load_json(folder / "ocr.json")
            if files and covers(cached, folder, files):
                return cached
            engine = "rapid"
    if engine == "windows":
        if not windows_available():
            raise SystemExit("Mesin OCR 'windows' butuh Windows + PowerShell. Pakai --ocr rapid "
                             "(pip install rapidocr_onnxruntime).")
        return run_windows(folder)
    if engine != "rapid":
        raise SystemExit(f"Mesin OCR tidak dikenal: {engine} (pilihan: {', '.join(ENGINES)})")
    if not rapid_available():
        raise SystemExit("OCR tidak tersedia: tidak ada PowerShell (OCR Windows) dan RapidOCR belum terpasang. "
                         "Jalankan: pip install rapidocr_onnxruntime")
    return run_rapid(folder, files, log)


def lines_of(images, folder, path):
    """OCR lines of one image from an ocr_folder() result ([] when the image is not in it)."""
    return images.get(key_of(folder, path), {}).get("lines", [])
