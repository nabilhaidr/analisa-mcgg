"""Tes mc_patch.entity_chip(): ikon baris laporan Patch mengikuti jenis barisnya.
Data uji = path ikon asli Lunox di S7.json; namanya ada di daftar hero dan daftar commander.

Jalankan dari folder ini: python -m pytest test_mc_patch.py   (atau: python -m unittest test_mc_patch)
"""
import unittest

import mc_patch

ICON_HERO = "img/Atlas_HeroHeadIcon_S7/SkinHead068_08.png"
ICON_COMMANDER = "img/Atlas_HeroHeadIcon_New_MC/HeroHead45226.png"


def season_data():
    return {"heroes": [{"name": "Lunox", "icon": ICON_HERO}], "commanders": [{"name": "Lunox", "icon": ICON_COMMANDER}],
            "synergies": [], "cards": []}


def chip_html(kind):
    return mc_patch.entity_chip(season_data(), {"data_name": "Lunox", "kind": kind})


class IkonMengikutiJenisBaris(unittest.TestCase):
    """Penyesuaian Commander 28/10 menampilkan ikon hero Lunox, bukan ikon commander-nya."""

    def test_baris_commander_memakai_ikon_commander(self):
        html = chip_html("Commander")
        self.assertIn(ICON_COMMANDER, html)
        self.assertNotIn(ICON_HERO, html)

    def test_baris_hero_memakai_ikon_hero(self):
        html = chip_html("Hero")
        self.assertIn(ICON_HERO, html)
        self.assertNotIn(ICON_COMMANDER, html)

    def test_bagian_tanpa_daftar_sendiri_tetap_berikon(self):
        self.assertIn(ICON_HERO, chip_html("Lainnya"))


if __name__ == "__main__":
    unittest.main()
