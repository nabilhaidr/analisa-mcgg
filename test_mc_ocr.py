"""Tes mc_ocr.py: ambang skor RapidOCR per panggilan (run_rapid text_score). RapidOCR menyimpan ambang terakhir yang
diberikan, jadi panggilan dengan ambang rendah (kotak Gold mc_match) tidak boleh mengubah panggilan biasa sesudahnya.

Jalankan dari folder ini: python -m pytest test_mc_ocr.py   (atau: python -m unittest test_mc_ocr)
"""
import shutil
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


if __name__ == "__main__":
    unittest.main()
