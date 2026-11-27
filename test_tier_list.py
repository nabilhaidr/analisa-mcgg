"""Tes tier_list.py: aturan gabungan tier commander, dan semua nama di tier list harus ada di data S8.

Jalankan: python -m unittest test_tier_list -v
"""
import unittest

import tier_list as T
from mc_common import load_season


class Gabungan(unittest.TestCase):
    def test_dua_s_jadi_s(self):
        self.assertEqual(T.combined(["S", "S"]), "S")

    def test_s_dan_a_jadi_s(self):
        self.assertEqual(T.combined(["S", "A"]), "S")

    def test_s_dan_b_tidak_bisa_s(self):
        self.assertEqual(T.combined(["B", "S"]), "A")

    def test_nerf_menurunkan_s_dan_a_ke_a(self):
        self.assertEqual(T.combined(["S", "A"], T.DOWN), "A")

    def test_nerf_tidak_menurunkan_dua_s(self):
        self.assertEqual(T.combined(["S", "S"], T.DOWN), "S")

    def test_buff_tanpa_sumber_s_tetap_a(self):
        self.assertEqual(T.combined(["A", "A"], T.UP), "A")

    def test_satu_sumber(self):
        self.assertEqual(T.combined(["A"]), "A")

    def test_a_dan_b_jadi_b(self):
        self.assertEqual(T.combined(["A", "B"]), "B")

    def test_a_dan_c_jadi_b(self):
        self.assertEqual(T.combined(["A", "C"]), "B")

    def test_b_dan_c_jadi_c(self):
        self.assertEqual(T.combined(["B", "C"]), "C")

    def test_tanpa_sumber(self):
        self.assertIsNone(T.combined([]))


class GabunganBeberapaPatch(unittest.TestCase):
    """Commander bisa kena lebih dari satu patch (20/11, 26/11): tiap buff/nerf ±0,5."""

    def test_dua_buff_naik_satu_tingkat(self):
        self.assertEqual(T.combined(["B", "B"], [T.UP, T.UP]), "A")

    def test_buff_dan_nerf_saling_menghapus(self):
        self.assertEqual(T.combined(["S", "A"], [T.UP, T.DOWN]), "S")

    def test_catatan_tanpa_panah_tidak_dihitung(self):  # Odette: nilai server tanpa patch note
        self.assertEqual(T.combined(["A"], [None]), "A")


class DataS8(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d, _ = load_season(8)

    def test_semua_nama_ada_di_data(self):
        self.assertEqual(T.unknown_names(self.d), [])

    def test_carry_termasuk_hero_comp(self):
        for c in T.COMPS:
            self.assertEqual([h for h in c["carries"] if h not in c["heroes"]], [], c["name"])

    def test_tiap_commander_s8_dinilai(self):
        graded = T.commander_grades(self.d)
        self.assertEqual(len(graded), len(self.d["commanders"]))
        self.assertNotIn(None, [g["tier"] for g in graded])

    def test_urutan_commander_dari_s(self):
        tiers = [g["tier"] for g in T.commander_grades(self.d)]
        self.assertEqual(tiers, sorted(tiers, key=T.ORDER.index))

    def test_efek_patch_berlabel(self):  # (panah, teks, patch): 20/11, 26/11, atau catatan server
        effects = [e for c in T.COMPS for e in c["patch"]] + [e for es in T.CMD_PATCH.values() for e in es]
        self.assertEqual({e[2] for e in effects} - {"20/11", "26/11", "server"}, set())

    def test_comp_di_bawah_tier_sumber_punya_nerf(self):
        for c in T.COMPS:
            if c["before"]:
                self.assertTrue(any(e[0] == T.DOWN for e in c["patch"]), c["name"])
                self.assertLess(T.ORDER.index(c["before"]), T.ORDER.index(c["tier"]), c["name"])


class Patch2611(unittest.TestCase):
    """Penyesuaian Keseimbangan 26/11 (server_patch.json "8"); sumber web belum berubah saat dicek 27 Nov."""

    @classmethod
    def setUpClass(cls):
        d, _ = load_season(8)
        cls.cmd = {g["name"]: g for g in T.commander_grades(d)}
        cls.comps = {c["name"]: c for c in T.COMPS}

    def test_kalea_turun_ke_a(self):  # mcggdb A + loadoutgg S = 3,5, nerf Brankas Harta -0,5
        self.assertEqual(self.cmd["Kalea"]["tier"], "A")

    def test_kagura_dan_ling_naik_ke_a(self):  # B + A = 2,5, buff +0,5
        self.assertEqual((self.cmd["Kagura"]["tier"], self.cmd["Ling"]["tier"]), ("A", "A"))

    def test_odette_tetap_a(self):  # catatan server tidak dihitung
        self.assertEqual(self.cmd["Odette"]["tier"], "A")

    def test_comp_carry_popol_dan_balmond_turun(self):
        self.assertEqual(self.comps["Popol & Kupa Frostrider + Phasewarper (4-4-3-3)"]["tier"], "C")
        self.assertEqual(self.comps["Titan + Swiftblade (Balmond)"]["tier"], "B")

    def test_buff_melissa_memulihkan_tier_sumber(self):  # loadoutgg A, turun ke B karena Barbiel 20/11
        c = self.comps["6 Defender low-roll (Melissa)"]
        self.assertEqual((c["tier"], c["before"]), ("A", None))


if __name__ == "__main__":
    unittest.main()
