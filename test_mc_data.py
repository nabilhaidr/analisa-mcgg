"""Tes mc_data.apply_server_patches(): server_patch.json diterapkan di atas data season tanpa mengubah nilai file game.
Data uji = potongan teks asli Abyssal Favor (Dyrroth, S7).

Jalankan dari folder ini: python -m pytest test_mc_data.py   (atau: python -m unittest test_mc_data)
"""
import json
import tempfile
import unittest
from pathlib import Path

import mc_data

FAVOR_FILE = "Dyrroth mendapatkan 2 EXP Commander setiap kali melahap. Setelah setiap 2 kali melahap, lahapan berikutnya memberikan 2 Hero."


def season_data():
    skill = {"name": "Abyssal Favor", "description": FAVOR_FILE, "attributes": []}
    return {"heroes": [], "synergies": [], "cards": [],
            "commanders": [{"name": "Dyrroth", "skills": [{"from_level": 2, "type": "Pasif", "skill": skill}]}]}


def favor(patch, *replace):
    return {"patch": patch, "commanders": [{"name": "Dyrroth", "skill": "Abyssal Favor", "replace": list(replace)}]}


def apply_patches(d, patches):
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / "server_patch.json"
        path.write_text(json.dumps({"7": patches}), encoding="utf-8")
        return mc_data.apply_server_patches(d, 7, path)


def favor_entry(d):
    return d["commanders"][0]["skills"][0]


class DuaPatchPadaSkillYangSama(unittest.TestCase):
    """Patch 7.2 dan 28/10 sama-sama mengubah Abyssal Favor."""

    def test_patch_kedua_melanjutkan_angka_patch_pertama(self):
        d = season_data()
        failed = apply_patches(d, [favor("7.2", ["2 EXP Commander", "3 EXP Commander"]),
                                   favor("28/10", ["3 EXP Commander", "4 EXP Commander"])])
        self.assertEqual(failed, [])
        self.assertEqual(favor_entry(d)["skill"]["description_server"],
                         "Dyrroth mendapatkan 4 EXP Commander setiap kali melahap. Setelah setiap 2 kali melahap, "
                         "lahapan berikutnya memberikan 2 Hero.")

    def test_patch_kedua_tidak_menghapus_perubahan_patch_pertama(self):
        d = season_data()
        apply_patches(d, [favor("7.2", ["2 EXP Commander", "3 EXP Commander"]),
                          favor("28/10", ["Setelah setiap 2 kali", "Setelah setiap 1 kali"])])
        self.assertEqual(favor_entry(d)["skill"]["description_server"],
                         "Dyrroth mendapatkan 3 EXP Commander setiap kali melahap. Setelah setiap 1 kali melahap, "
                         "lahapan berikutnya memberikan 2 Hero.")

    def test_teks_file_game_tetap_utuh(self):
        d = season_data()
        apply_patches(d, [favor("7.2", ["2 EXP Commander", "3 EXP Commander"]),
                          favor("28/10", ["3 EXP Commander", "4 EXP Commander"])])
        self.assertEqual(favor_entry(d)["skill"]["description"], FAVOR_FILE)

    def test_setiap_patch_tercatat_di_catatan_server(self):
        d = season_data()
        apply_patches(d, [favor("7.2", ["2 EXP Commander", "3 EXP Commander"]),
                          favor("28/10", ["3 EXP Commander", "4 EXP Commander"])])
        self.assertEqual([n["patch"] for n in favor_entry(d)["server"]], ["7.2", "28/10"])

    def test_teks_lama_yang_tidak_ada_dilaporkan(self):
        d = season_data()
        failed = apply_patches(d, [favor("7.2", ["2 EXP Commander", "3 EXP Commander"]),
                                   favor("28/10", ["9 EXP Commander", "4 EXP Commander"])])
        self.assertEqual([c["status"] for c in failed], ["teks lama tidak ditemukan di file game (perbarui server_patch.json)"])
        self.assertIn("3 EXP Commander", favor_entry(d)["skill"]["description_server"])


if __name__ == "__main__":
    unittest.main()
