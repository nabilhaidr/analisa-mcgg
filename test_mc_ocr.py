"""Tes mc_ocr.py: ambang skor RapidOCR per panggilan (run_rapid text_score). RapidOCR menyimpan ambang terakhir yang
diberikan, jadi panggilan dengan ambang rendah (kotak Gold mc_match) tidak boleh mengubah panggilan biasa sesudahnya.
Tes ocr_screens.ps1: gambar yang gagal di-OCR tidak boleh tersimpan memakai hasil gambar sebelumnya.

Jalankan dari folder ini: python -m pytest test_mc_ocr.py   (atau: python -m unittest test_mc_ocr)
"""
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

import mc_ocr

GOLD = Path(__file__).resolve().parent / "test_data" / "gold"


def texts(images):
    return [l["t"] for v in images.values() for l in v["lines"]]


@unittest.skipUnless(mc_ocr.rapid_available(), "RapidOCR tidak terpasang")
class RapidTextScore(unittest.TestCase):
    def test_low_score_call_reads_a_lone_digit_and_does_not_leak(self):
        # ponsel_gold_2_satu: a lone "2" scored ~0.5, dropped at RapidOCR's default text_score 0.5
        with tempfile.TemporaryDirectory() as low, tempfile.TemporaryDirectory() as default:
            for folder in (low, default):
                shutil.copy(GOLD / "ponsel_gold_2_satu.png", Path(folder) / "gold.png")
            self.assertIn("2", texts(mc_ocr.run_rapid(Path(low), [Path(low) / "gold.png"], log=lambda *a: None,
                                                      text_score=0.1)))
            self.assertEqual(texts(mc_ocr.run_rapid(Path(default), [Path(default) / "gold.png"], log=lambda *a: None)), [])


@unittest.skipUnless(mc_ocr.windows_available(), "OCR Windows hanya ada di Windows")
class WindowsFailedImage(unittest.TestCase):
    # 1 Nov: out of memory on 6 of 72 images; the script went on and saved the previous image's text under the next name
    def run_script(self, folder):
        return subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", str(mc_ocr.HERE / "ocr_screens.ps1"),
                               "-Folder", str(folder)], capture_output=True, text=True, encoding="utf-8", errors="replace")

    def test_failed_image_is_not_saved_and_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            shutil.copy(GOLD / "ponsel_gold_2_satu.png", folder / "a_baik.png")
            (folder / "b_rusak.jpg").write_bytes(b"bukan gambar")
            run = self.run_script(folder)
            self.assertEqual(run.returncode, 1)
            self.assertIn("b_rusak.jpg", run.stderr)
            self.assertEqual(sorted(mc_ocr.load_json(folder / "ocr.json")), ["a_baik.png"])

    def test_failed_image_is_tried_again_next_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            shutil.copy(GOLD / "ponsel_gold_2_satu.png", folder / "a_baik.png")
            (folder / "b_rusak.jpg").write_bytes(b"bukan gambar")
            self.run_script(folder)
            again = self.run_script(folder)
            self.assertEqual(again.returncode, 1)
            self.assertIn("0 baru di-OCR, 1 dari cache, 1 gagal", again.stdout)
            shutil.copy(GOLD / "ponsel_gold_2_satu.png", folder / "b_rusak.jpg")
            fixed = self.run_script(folder)
            self.assertEqual(fixed.returncode, 0, fixed.stderr)
            self.assertIn("1 baru di-OCR, 1 dari cache)", fixed.stdout)
            self.assertEqual(sorted(mc_ocr.load_json(folder / "ocr.json")), ["a_baik.png", "b_rusak.jpg"])


if __name__ == "__main__":
    unittest.main()
