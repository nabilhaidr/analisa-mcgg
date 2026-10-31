"""Tes mc_validate.py. (1) Baris patch note "tercatat di server_patch.json": yang dihitung nilai akhir perubahannya, bukan
sekadar nama. Lunox sudah punya entri 20/10, tapi baris "Perolehan Gold: 6 >> 4" dari patch 28/10 belum tercatat.
(2) Layar Toko Spirit Sand: nama + harga per kolom dan kenaikan "ATK/HP rekan" dicocokkan dengan special_store di S7.json.
Data uji toko = OCR asli screenshot/season 7/ocr.json dan S7.json (hanya dibaca).

Jalankan dari folder ini: python -m pytest test_mc_validate.py   (atau: python -m unittest test_mc_validate)
"""
import copy
import json
import tempfile
import unittest
from pathlib import Path

import mc_validate as V

ROOT = Path(__file__).resolve().parent
S7 = json.loads((ROOT / "data" / "1.3.24.344.1" / "S7.json").read_text(encoding="utf-8"))
SHOTS = V.load_ocr(ROOT / "screenshot" / "season 7")

PATCHES = [
    {"patch": "7.2",
     "commanders": [{"name": "Dyrroth", "skill": "Abyssal Favor", "replace": [["2 EXP Commander", "3 EXP Commander"]]}],
     "cards": [{"id": 2015, "name": "Solid Alliance", "removed": True},
               {"id": 3061, "name": "Angela's Power", "replace": [["100 / 190 / 320/540", "100 / 190 / 300 / 500"]]}]},
    {"patch": "20/10",
     "heroes": [{"name": "Lunox", "stat": "Hybrid ATK", "stars": [2], "old": [200], "new": [185]},
                {"name": "Layla", "stat": "Hybrid ATK", "stars": [1, 2], "old": [260, 390], "new": [300, 450]}],
     "commanders": [{"name": "Johnson", "skill": "Johnny, Go!", "text": "Hybrid ATK Dasar Johnny ★3: 285 → 255"}],
     "cards": [{"id": 504, "name": "Turret of Guardians", "text": "Turret ★3: Hybrid ATK 590 → 530; HP Dasar 7.020 → 5.616"}]},
]


def recorded():
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / "server_patch.json"
        path.write_text(json.dumps({"7": PATCHES}), encoding="utf-8")
        return V.recorded_server_changes(7, str.lower, path)


class BarisTercatat(unittest.TestCase):
    def test_patch_baru_pada_hero_lama_belum_tercatat(self):
        self.assertFalse(V.is_recorded(recorded(), "lunox", "4"))

    def test_patch_baru_pada_skill_lama_belum_tercatat(self):
        self.assertFalse(V.is_recorded(recorded(), "dyrroth", "4"))

    def test_nilai_baru_hero_tercatat(self):
        self.assertTrue(V.is_recorded(recorded(), "lunox", "185"))

    def test_nilai_dari_replace_tercatat(self):
        self.assertTrue(V.is_recorded(recorded(), "dyrroth", "3"))

    def test_nilai_lama_dari_replace_tidak_dihitung(self):
        self.assertFalse(V.is_recorded(recorded(), "dyrroth", "2"))

    def test_angka_yang_tidak_berubah_di_replace_ikut_dihitung(self):
        self.assertTrue(V.is_recorded(recorded(), "angela's power", "100/190/300/500"))

    def test_nama_skill_juga_dikenali(self):
        self.assertTrue(V.is_recorded(recorded(), "abyssal favor", "3"))

    def test_nilai_dari_teks_ringkasan_tercatat(self):
        self.assertTrue(V.is_recorded(recorded(), "johnson", "255"))

    def test_nilai_lama_dari_teks_ringkasan_tidak_dihitung(self):
        self.assertFalse(V.is_recorded(recorded(), "johnson", "285"))

    def test_setiap_bagian_teks_ringkasan_dibaca(self):
        self.assertTrue(V.is_recorded(recorded(), "turret of guardians", "5.616"))

    def test_semua_nilai_baris_harus_tercatat(self):
        self.assertTrue(V.is_recorded(recorded(), "layla", "300/450"))
        self.assertFalse(V.is_recorded(recorded(), "layla", "300/999"))

    def test_persen_tidak_membedakan_nilai(self):
        self.assertTrue(V.is_recorded(recorded(), "lunox", "185%"))

    def test_baris_tanpa_angka_cukup_namanya(self):
        self.assertTrue(V.is_recorded(recorded(), "solid alliance", ""))

    def test_nama_yang_tidak_ada_belum_tercatat(self):
        self.assertFalse(V.is_recorded(recorded(), "yin", ""))

    def test_garis_miring_terbaca_angka_satu_tetap_tercatat(self):
        self.assertTrue(V.is_recorded(recorded(), "layla", "3001450"))

    def test_gabungan_nilai_yang_tidak_tercatat_tetap_belum(self):
        self.assertFalse(V.is_recorded(recorded(), "layla", "3001999"))


def store_shot(name):
    """Baris OCR asli satu layar (screenshot/season 7/ocr.json) dalam koordinat 1366x768."""
    return SHOTS[next(k for k in SHOTS if k.endswith(name))]


class LayarToko(unittest.TestCase):
    def test_layar_toko_dikenali(self):
        self.assertEqual(V.classify(store_shot("Screenshot (1909).png")), "store")

    def test_panel_mistbender_bukan_layar_toko(self):
        self.assertNotEqual(V.classify(store_shot("Screenshot (1630).png")), "store")

    def test_layar_ponsel_tanpa_judul_terbaca_tetap_dikenali(self):
        self.assertEqual(V.classify(store_shot("03-35-54-171_com.mobilechess.mi.jpg")), "store")

    def test_nama_dan_harga_tiap_kolom(self):
        self.assertEqual(V.store_slots(store_shot("Screenshot (1909).png"), S7["special_store"]["items"]),
                         [("Magic Crystal Acak", 80), ("HP Rekan +2%", 16), ("ATK Rekan +3%", 24)])

    def test_dua_nama_dalam_satu_baris_ocr_dipisah(self):
        self.assertEqual(V.store_slots(store_shot("Screenshot (1926).png"), S7["special_store"]["items"]),
                         [("Magic Crystal Acak", 80), ("Hero 4 Gold Bintang 1 Acak", 30), ("ATK Rekan +3%", 24)])

    def test_nama_tanpa_persen_dari_harganya(self):
        self.assertEqual(V.store_slots(store_shot("Screenshot (1908).png"), S7["special_store"]["items"]),
                         [("Magic Crystal Acak", 80), ("ATK Rekan +2%", 16), ("ATK Rekan +3%", 24)])

    def test_layar_ponsel_dibaca_per_kolom(self):
        self.assertEqual(V.store_slots(store_shot("03-37-03-863_com.mobilechess.mi.jpg"), S7["special_store"]["items"]),
                         [("Hero 4 Gold Bintang 1 Acak", 30), ("HP Rekan +1%", 8), ("Magic Crystal Acak", 80)])

    def test_persen_atk_dan_hp_terbaca(self):
        self.assertEqual(V.store_percent(store_shot("Screenshot (1910).png")), {"ATK": 4, "HP": 2})

    def test_persen_dengan_tanda_persen_terbaca_nol_garis_nol(self):
        self.assertEqual(V.store_percent(store_shot("2026-10-22-06-38-48-171_com.mobilechess.mi.jpg"))["HP"], 1)


def run_store(names, data=None):
    rep = V.Report()
    V.check_store(data or S7, [(n, store_shot(n)) for n in names], rep)
    return rep


class CocokkanToko(unittest.TestCase):
    PAIR = ["Screenshot (1908).png", "Screenshot (1909).png"]  # beli ATK +2%: ATK 1% -> 4%

    def test_harga_dan_stack_sesuai_data_tanpa_selisih(self):
        rep = run_store(self.PAIR)
        self.assertEqual(rep.items["store"]["selisih"], [])
        self.assertEqual(rep.items["store"]["manual"], [])

    def test_harga_beda_dengan_data_jadi_selisih(self):
        data = copy.deepcopy(S7)
        next(i for i in data["special_store"]["items"] if i["name"] == "Magic Crystal Acak")["price"] = 70
        self.assertEqual(len(run_store(self.PAIR[:1], data).items["store"]["selisih"]), 1)

    def test_stack_beda_dengan_data_jadi_selisih(self):
        data = copy.deepcopy(S7)
        item = next(i for i in data["special_store"]["items"] if i["name"] == "ATK Rekan +2%")
        item["effect"] = item["effect"].replace("+3 stack", "+2 stack")
        self.assertEqual(len(run_store(self.PAIR, data).items["store"]["selisih"]), 1)

    def test_pembelian_dihitung_di_catatan(self):
        self.assertIn("1 pembelian", " ".join(run_store(self.PAIR).notes["store"]))

    def test_item_yang_tidak_terlihat_dilaporkan(self):
        self.assertTrue(any(n.startswith("Tanpa screenshot") and "Nana" in n for n in run_store(self.PAIR).notes["store"]))

    def test_item_tanpa_harga_terbaca_bukan_tanpa_screenshot(self):
        notes = run_store(["03-38-12-747_com.mobilechess.mi.jpg"]).notes["store"]
        unread = "1 Equipment Acak yang Diperkuat"
        self.assertTrue(any(n.startswith("Tidak terbaca harganya") and unread in n for n in notes))
        self.assertFalse(any(n.startswith("Tanpa screenshot") and unread in n for n in notes))


BOX_FULL ="31-17-05-38-617_com.mobilechess.mi.jpg"  # II-6, sisa 20 detik: 8 orb masih utuh (dibaca dari gambarnya)
BOX_PICKED = "31-17-05-48-931_com.mobilechess.mi.jpg"  # sisa 10 detik: 3 pemain sudah mengambil orbnya


class LayarPilihHadiah(unittest.TestCase):
    def test_layar_dikenali(self):
        self.assertEqual(V.classify(store_shot(BOX_FULL)), "go_go_box")

    def test_judul_dengan_l_terbaca_i_tetap_dikenali(self):  # 141 dari 197 judul di 20 rekaman terbaca begini
        self.assertEqual(V.classify([{"t": "17 Piiih Hadiah", "x": 500, "y": 10, "r": 600, "b": 30}]), "go_go_box")

    def test_rincian_gold_babak_bukan_go_go_box(self):
        self.assertNotEqual(V.classify([{"t": "Hadiah Dasar", "x": 500, "y": 10, "r": 600, "b": 30}]), "go_go_box")

    def test_orb_dibaca_per_jenis(self):
        self.assertEqual(V.box_orbs(store_shot(BOX_FULL), S7["go_go_box"]),
                         {"equipment": ["Counter Lifesteal", "DMG Tambahan", "DMG Tank", "Memantulkan Physical DMG",
                                        "Pembunuh Tank", "Spell Vamp"],
                          "crystals": ["Dapatkan Sinergi Dragoncaller"], "special": ["Kapasitas +1"]})

    def test_nama_pemain_bukan_orb(self):
        orbs = V.box_orbs(store_shot(BOX_PICKED), S7["go_go_box"])
        self.assertFalse({"CinCoeg", "PARANOIA", "L.O.L"} & set(sum(orbs.values(), [])))


def run_box(names, data=None):
    rep = V.Report()
    V.check_go_go_box(data or S7, [(n, store_shot(n)) for n in names], rep)
    return rep


class CocokkanGoGoBox(unittest.TestCase):
    def test_delapan_orb_cocok_dengan_satu_babak(self):
        rep = run_box([BOX_FULL])
        self.assertEqual(rep.items["go_go_box"]["selisih"], [])
        self.assertIn("II-6", " ".join(rep.notes["go_go_box"]))

    def test_susunan_yang_tidak_ada_di_data_jadi_selisih(self):
        data = copy.deepcopy(S7)
        for r in data["go_go_box"]["rounds"]:
            r["special"]["count"] = 0  # 1 Kapasitas +1 di layar, 0 di data
        self.assertEqual(len(run_box([BOX_FULL], data).items["go_go_box"]["selisih"]), 1)

    def test_jumlah_equipment_beda_dengan_data_jadi_selisih(self):
        data = copy.deepcopy(S7)
        next(r for r in data["go_go_box"]["rounds"] if r["label"] == "II-6")["equipment"]["min"] = 7
        self.assertEqual(len(run_box([BOX_FULL], data).items["go_go_box"]["selisih"]), 1)

    def test_orb_yang_sudah_diambil_bukan_selisih(self):
        self.assertEqual(run_box([BOX_PICKED]).items["go_go_box"]["selisih"], [])

    def test_layar_sebagian_tidak_diklaim_cocok_babak(self):
        self.assertNotIn("cocok babak", " ".join(run_box([BOX_PICKED]).notes["go_go_box"]))


if __name__ == "__main__":
    unittest.main()
