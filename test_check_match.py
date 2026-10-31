"""Tes check_match.py untuk pemeriksaan yang diambil dari check.py lama: peringatan HP sendiri kosong di timeline,
peringatan laporan tanpa papan akhir, dan baris ringkasan per laporan. Laporan uji = laporan MATCH asli di
data/1.3.24.344.1 (hanya dibaca) atau salinannya di folder sementara yang diubah sedikit.

Jalankan dari folder ini: python -m pytest test_check_match.py   (atau: python -m unittest test_check_match)
"""
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import check_match

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "1.3.24.344.1"
SEASONS = {}  # data season dimuat sekali untuk semua tes


def warnings_of(md):
    return check_match.check(md, SEASONS)[1]


def copy_report(name, folder, md_edits=(), html_edits=()):
    """Salin MATCH_<name>.md/.html dan match_<name>/ ke folder, lalu terapkan (pola regex, pengganti); setiap pola harus
    ditemukan tepat sekali."""
    for suffix, edits in ((".md", md_edits), (".html", html_edits)):
        src = DATA / f"MATCH_{name}{suffix}"
        text = src.read_text(encoding="utf-8")
        for pattern, repl in edits:
            text, n = re.subn(pattern, repl, text, flags=re.S | re.M)
            assert n == 1, f"pola {pattern!r} ditemukan {n} kali di {src.name}"
        (folder / src.name).write_text(text, encoding="utf-8")
    shutil.copytree(DATA / f"match_{name}", folder / f"match_{name}")
    return folder / f"MATCH_{name}.md"


def hp_empty(warn):
    return [w for w in warn if "HP sendiri kosong" in w]


class HpSendiriKosong(unittest.TestCase):
    def test_hp_kosong_sebelum_tereliminasi_diperingatkan(self):
        # rusak: HP sendiri di II-1 tidak terbaca (24 Okt 02-51 tereliminasi di IV-5), tidak boleh lolos tanpa catatan
        with tempfile.TemporaryDirectory() as tmp:
            md = copy_report("24_Okt_02_51", Path(tmp),
                             md_edits=[(r"^\| II-1 \| 89 \|", "| II-1 | - |")],
                             html_edits=[(r"<td><b>II-1</b></td><td>89</td>", "<td><b>II-1</b></td><td>-</td>")])
            warn = warnings_of(md)
        self.assertTrue([w for w in hp_empty(warn) if "II-1" in w], warn)

    def test_laporan_tanpa_hp_kosong_tidak_diperingatkan(self):
        self.assertEqual(hp_empty(warnings_of(DATA / "MATCH_24_Okt_02_51.md")), [])

    def test_hp_kosong_setelah_tereliminasi_tidak_diperingatkan(self):
        # 23 Okt 21-47: tereliminasi di IV-1, baris IV-2 sesudahnya memang tanpa HP sendiri
        self.assertEqual(hp_empty(warnings_of(DATA / "MATCH_23_Okt_21_47.md")), [])


class TanpaPapanAkhir(unittest.TestCase):
    def test_laporan_tanpa_papan_akhir_diperingatkan(self):
        with tempfile.TemporaryDirectory() as tmp:
            md = copy_report("24_Okt_02_51", Path(tmp),
                             md_edits=[(r"^## Papan akhir \(layar hasil\)\n.*?(?=^## )", "")],
                             html_edits=[(r"<section><h2>Papan akhir \(layar hasil\)</h2>.*?</section>", "")])
            warn = warnings_of(md)
        self.assertTrue([w for w in warn if "tanpa papan akhir" in w], warn)

    def test_laporan_dengan_papan_akhir_tidak_diperingatkan(self):
        self.assertEqual([w for w in warnings_of(DATA / "MATCH_24_Okt_02_51.md") if "tanpa papan akhir" in w], [])


class TanpaLayarHasil(unittest.TestCase):
    """Rekaman yang berhenti sebelum layar hasil menyatakannya sendiri di Catatan otomatis."""

    def test_keterbatasan_yang_tertulis_tidak_diperingatkan(self):
        self.assertEqual(warnings_of(DATA / "MATCH_31_Okt_03_49_Vexana.md"), [])

    def test_hp_kosong_di_babak_terakhir_rekaman_tidak_diperingatkan(self):
        self.assertEqual(warnings_of(DATA / "MATCH_31_Okt_02_51_PC.md"), [])

    def test_hp_kosong_sebelum_babak_terakhir_tetap_diperingatkan(self):
        with tempfile.TemporaryDirectory() as tmp:
            md = copy_report("31_Okt_03_49_Vexana", Path(tmp),
                             md_edits=[(r"^\| IV-4 \| 30 \|", "| IV-4 | - |")],
                             html_edits=[(r"<td><b>IV-4</b></td><td>30</td>", "<td><b>IV-4</b></td><td>-</td>")])
            warn = warnings_of(md)
        self.assertTrue([w for w in warn if "HP sendiri kosong" in w], warn)


class LayarHasilSementara(unittest.TestCase):
    """Saat tersingkir lebih dulu, baris di atas barismu masih berikon pedang: tanpa peringkat dan tanpa poin."""

    def test_baris_tanpa_peringkat_tidak_diperingatkan(self):
        self.assertEqual(warnings_of(DATA / "MATCH_31_Okt_03_23.md"), [])

    def test_baris_tanpa_peringkat_bukan_kesalahan(self):
        self.assertEqual(check_match.check(DATA / "MATCH_31_Okt_03_23.md", SEASONS)[0], [])

    def test_baris_tanpa_peringkat_padahal_ada_poin_jadi_kesalahan(self):
        with tempfile.TemporaryDirectory() as tmp:
            md = copy_report("31_Okt_03_23", Path(tmp),
                             md_edits=[(r"· poin -", "· poin 4000 (+10)")],
                             html_edits=[(r"· poin -", "· poin 4000 (+10)")])
            errors = check_match.check(md, SEASONS)[0]
        self.assertTrue([e for e in errors if "tanpa peringkat" in e], errors)


class BarisRingkasan(unittest.TestCase):
    # dibaca tangan dari laporannya: kotak Peringkat, HP akhir, Babak terbaca, dan nama di papan akhir
    WANT = {
        "24_Okt_02_51": {"pkt": "4", "HP": "0", "babak": "I-1–IV-5", "n": "21", "kalah": "8", "nama": "8/8"},
        "24_Okt_15_06": {"pkt": "4", "HP": "0", "babak": "I-1–IV-5", "n": "21", "kalah": "7", "nama": "7/8"},  # peringkat 1 = gambar
        "21_Okt_15_38_Minotaur": {"pkt": "1", "HP": "32", "babak": "I-1–V-1", "n": "23", "kalah": "7", "nama": "8/8"},
    }

    def test_ringkasan_dari_isi_laporan(self):
        for name, want in self.WANT.items():
            with self.subTest(name):
                self.assertEqual(check_match.check(DATA / f"MATCH_{name}.md", SEASONS)[2], want)

    def test_cli_mencetak_baris_ringkasan(self):
        run = subprocess.run([sys.executable, "check_match.py", "24_Okt_02_51"], cwd=ROOT, capture_output=True,
                             encoding="utf-8")
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertRegex(run.stdout, r"(?m)^OK\s+24_Okt_02_51\s+4\s+0\s+I-1–IV-5\s+21\s+8\s+8/8\s*$")


if __name__ == "__main__":
    unittest.main()
