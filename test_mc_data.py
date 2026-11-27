"""Tes mc_data.apply_server_patches(): server_patch.json diterapkan di atas data season tanpa mengubah nilai file game.
Data uji = potongan teks asli Abyssal Favor (Dyrroth, S7).

Jalankan dari folder ini: python -m pytest test_mc_data.py   (atau: python -m unittest test_mc_data)
"""
import json
import re
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


class LabelRasioDamage(unittest.TestCase):
    """Detail Hero dan editor lineup menulis (+150% Total Physical ATK) dan (+350% Total Magic ATK); jenis 10100 dan 10101 selalu
    sesuai labelnya di screenshot. Jenis 10502 (Alpha) tertulis (+50% ) Adaptive DMG: tanpa label sama sekali (editor lineup 1 Nov)."""

    def render(self, kind, value):
        return mc_data.FORMULA_KINDS[kind][1](value)

    def s7_skill(self, hero, skill):
        data = json.loads((Path(__file__).resolve().parent / "data" / "1.3.24.344.1" / "S7.json").read_text(encoding="utf-8"))
        return next(s for h in data["heroes"] if h["name"] == hero for s in h["skills"] if s["name"] == skill)

    def test_physical(self):
        self.assertEqual(self.render(10100, 1.5), "150% Total Physical ATK")

    def test_magic(self):
        self.assertEqual(self.render(10101, 3.5), "350% Total Magic ATK")

    def test_adaptif_tanpa_label(self):
        self.assertEqual(self.render(10502, 0.5), "50%")

    def test_data_alpha_tanpa_label(self):
        self.assertIn("50%/70% Adaptive DMG Area", self.s7_skill("Alpha", "Alpha, Charge!")["description"])

    def test_data_tidak_punya_rasio_atk_polos(self):  # "120% ATK Speed" adalah teks asli game
        data = json.loads((Path(__file__).resolve().parent / "data" / "1.3.24.344.1" / "S7.json").read_text(encoding="utf-8"))
        texts = [s.get("description_server") or s["description"] for h in data["heroes"] for s in h["skills"]]
        self.assertEqual([t for t in texts if re.search(r"\d% ATK(?! Speed)", t)], [])

    def test_data_memakai_label_physical(self):  # X.Borg, bukti pertama: editor lineup 1 Nov
        self.assertIn("2000% Total Physical ATK", self.s7_skill("X.Borg", "Last Insanity")["description"])

    def test_data_memakai_label_magic(self):  # Eudora: skill jenis 10101
        self.assertIn("430% Total Magic ATK", self.s7_skill("Eudora", "Forked Lightning")["description"])

    def test_patch_badang_tetap_masuk(self):  # server_patch.json mencari teks persis: 420% -> 800% hilang bila labelnya beda
        self.assertIn("800% Total Physical ATK", self.s7_skill("Badang", "Fist Crack")["description_server"])


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


def hero_data(name, skill, text, attributes):
    return {"heroes": [{"name": name, "stats": {}, "skills": [{"name": skill, "description": text, "attributes": attributes}]}],
            "synergies": [], "cards": [], "commanders": []}


def hero_patch(patch, name, skill, replace, attributes):
    return {"patch": patch, "hero_skills": [{"name": name, "skill": skill, "replace": replace, "attributes": attributes}]}


class AtributSkillDariPatchServer(unittest.TestCase):
    """Tabel Atribut Skill ikut patch server. Data uji = potongan teks asli Balmond dan Eudora (S8)."""

    BALMOND = "Untuk setiap target yang terkena, dia mendapatkan Shield sebesar 5%/6%/9% dari Max HP-nya selama 4 detik."

    def balmond(self):
        return hero_data("Balmond", "Lethal Counter", self.BALMOND,
                         [{"label": "Bonus Physical", "values": ["380%", "410%", "1200%"]},
                          {"label": "Shield per Serangan", "values": ["5%", "6%", "9%"]}])

    def test_patch_kedua_melanjutkan_atribut_patch_pertama(self):  # 20/11 lalu 26/11 pada Lethal Counter
        d = self.balmond()
        failed = apply_patches(d, [
            hero_patch("20/11", "Balmond", "Lethal Counter", [["Shield sebesar 5%/6%/9%", "Shield sebesar 5%/5%/9%"]],
                       [["Bonus Physical", 1, "370%"], ["Bonus Physical", 2, "370%"], ["Shield per Serangan", 2, "5%"]]),
            hero_patch("26/11", "Balmond", "Lethal Counter", [["Shield sebesar 5%/5%/9%", "Shield sebesar 5%/5%/7%"]],
                       [["Shield per Serangan", 3, "7%"]])])
        self.assertEqual(failed, [])
        skill = d["heroes"][0]["skills"][0]
        self.assertEqual(skill["attributes_server"], [{"label": "Bonus Physical", "values": ["370%", "370%", "1200%"]},
                                                      {"label": "Shield per Serangan", "values": ["5%", "5%", "7%"]}])
        self.assertEqual(skill["attributes"][1]["values"], ["5%", "6%", "9%"])  # nilai file game tetap

    def test_label_kembar_dipilih_dengan_urutan(self):  # Eudora: dua baris "Magic Bonus" (ledakan, DMG tertunda)
        d = hero_data("Eudora", "Thunder's Wrath", "130% Total Magic ATK/345% Total Magic ATK",
                      [{"label": "Magic Bonus", "values": ["245%", "245%", "635%"]},
                       {"label": "Magic Bonus", "values": ["130%", "130%", "345%"]}])
        failed = apply_patches(d, [hero_patch("26/11", "Eudora", "Thunder's Wrath",
                                              [["130% Total Magic ATK/345%", "130% Total Magic ATK/400%"]],
                                              [["Magic Bonus", 3, "800%"], ["Magic Bonus", 3, "400%", 2]])])
        self.assertEqual(failed, [])
        self.assertEqual([a["values"] for a in d["heroes"][0]["skills"][0]["attributes_server"]],
                         [["245%", "245%", "800%"], ["130%", "130%", "400%"]])

    def test_urutan_label_yang_tidak_ada_dilaporkan(self):
        d = self.balmond()
        failed = apply_patches(d, [hero_patch("26/11", "Balmond", "Lethal Counter", [["5%/6%/9%", "5%/6%/7%"]],
                                              [["Shield per Serangan", 3, "7%", 2]])])
        self.assertEqual([c["status"] for c in failed], ["atribut skill tidak ditemukan di file game (perbarui server_patch.json)"])


class SkalaPlaceholder(unittest.TestCase):
    """Kolom ke-5 placeholder [jenis|efek|kolom|unit|skala]: angka tanpa N berarti dikali, sama dengan [kind|...]. Hanya dipakai
    tabel S8 (Elemental Mark FAIRY TAIL); dulu terbaca sebagai konstanta: "0 detik", "-0.01%"."""

    @staticmethod
    def num(spec, row):
        s = mc_data.Season.__new__(mc_data.Season)
        s.skills, s.triggers, s.effects = {}, {}, {(7, 1): row}
        return s.num(spec, 1)

    def test_angka_tanpa_n_adalah_pengali(self):  # FAIRY TAIL 10: freeze 500 ms x 0.001 = 0.5 detik (layar 2039)
        self.assertEqual(self.num("[2|7|Para1|@|0.001|0]", {"m_Para1": 500}), "0.5")

    def test_pengali_negatif(self):
        self.assertEqual(self.num("[2|7|Value0|%|-0.01|0|1]", {"m_Value0": -4000}), "40%")

    def test_rumus_dengan_n_tetap(self):
        self.assertEqual(self.num("[2|7|Value0|%|N*0.01|0]", {"m_Value0": 1500}), "15%")

    def test_kolom_ketujuh_adalah_level_efek(self):  # Gray Ice: Freeze per jumlah Elemental Mark = level efek 4522300
        s = mc_data.Season.__new__(mc_data.Season)
        s.skills, s.triggers = {}, {}
        s.effects = {(7, lv): {"m_Para1": ms} for lv, ms in ((1, 200), (2, 400), (6, 1400))}
        self.assertEqual([s.num(f"[2|7|Para1|@|0.001|0|{mark}]", 1) for mark in (1, 2, 6)], ["0.2", "0.4", "1.4"])
        self.assertEqual(s.num("[2|7|Para1|@|0.001|0|6]", 3), "1.4")  # bintang 3 tetap level efek 6


class TabelPanduanSinergiS8(unittest.TestCase):
    """Panduan Sinergi client 1.3.32.354.1 (S8): tombol Lite/Penuh dan tabel angka per tingkat. Harapan dibaca dari screenshot
    season 8: 2113 (Deadeye), 2021 (Shadeweaver, 1 kolom), 2024/2025/2026 (Titan Lite/Penuh/tooltip Super Mecha)."""

    @classmethod
    def setUpClass(cls):
        path = Path(__file__).resolve().parent / "data" / "1.3.32.354.1" / "S8.json"
        cls.syn = {s["name"]: s for s in json.loads(path.read_text(encoding="utf-8"))["synergies"]}

    def test_judul_kolom(self):
        self.assertEqual(self.syn["Deadeye"]["table"]["header"],
                         ["Perolehan Critical Chance oleh Semua Rekan", "Perolehan Critical Chance Tambahan oleh Hero Deadeye",
                          "DMG Critical Tambahan yang Didapatkan Hero Deadeye"])

    def test_sel_per_tingkat(self):
        self.assertEqual([(r["count"], r["cells"]) for r in self.syn["Deadeye"]["table"]["rows"]],
                         [(2, ["5%", "15%", "30%"]), (4, ["10%", "25%", "60%"]), (6, ["20%", "40%", "120%"])])

    def test_sel_sebanyak_judul_kolom(self):  # Shadeweaver punya mNumDescribeTag2, tapi layarnya 1 kolom
        self.assertEqual([r["cells"] for r in self.syn["Shadeweaver"]["table"]["rows"]], [["25%"], ["50%"]])

    def test_baris_teks_selebar_tabel(self):  # Titan 10: mNumDescribeTag1 "##" = mSpecialDescription
        last = self.syn["Titan"]["table"]["rows"][-1]
        self.assertEqual(last["count"], 10)
        self.assertTrue(last["text"].endswith("Mereka juga mendapatkan 50% dan 300%."), last["text"])

    def test_teks_penuh_memakai_kata_kunci(self):
        self.assertIn("Hero Titan mendapatkan Peningkatan DMG. Super Mecha mendapatkan Peningkatan DMG dan Pengurangan DMG.",
                      self.syn["Titan"]["explain_full"])

    def test_tooltip_kata_kunci(self):
        details = {k["keyword"]: k["text"] for k in self.syn["Titan"]["details"]}
        self.assertTrue(details["Super Mecha"].startswith("Super Mecha mendapatkan Atribut Mecha dari Hero Titan."))

    def test_teks_lite_dari_baris_tingkat(self):  # mSkillDescriptionNew, sama persis dengan layar 2113
        self.assertEqual(self.syn["Deadeye"]["explain_lite"],
                         "Semua rekan mendapatkan Critical Chance. Hero Deadeye mendapatkan Critical Chance dan Critical DMG tambahan.")

    def test_angka_teks_baris_dari_daftar_angkanya_sendiri(self):  # FAIRY TAIL 10 di layar 2039: m_NumDescribeTag tanpa durasi
        text = self.syn["FAIRY TAIL"]["table"]["rows"][-1]["text"]
        self.assertIn("freeze ke lawan selama 0.5 detik dan memberikan True DMG sebesar 10%", text)
        self.assertIn("hujan api memberikan True DMG sebesar 20%", text)

    def test_baris_dengan_sel_dan_teks(self):  # Starbelle 10 di layar 2069: 300 | 100%, lalu teks sinar
        last = self.syn["Starbelle"]["table"]["rows"][-1]
        self.assertEqual((last["count"], last["cells"]), (10, ["300", "100%"]))
        self.assertTrue(last["text"].endswith("memberikan True DMG sebesar 12% HP."), last["text"])


def s8_data():
    return json.loads((Path(__file__).resolve().parent / "data" / "1.3.32.354.1" / "S8.json").read_text(encoding="utf-8"))


class KartuPowerS8(unittest.TestCase):
    """Sejak S8 kartu Power commander adalah Go Go Card emas: m_Level 3 (S7: 4, tab Kartu Power), tampil di tab Kartu Oranye
    galeri (screenshot go go card 2399, 2408). m_CardTag: 1 finansial, 2 Power, 3 Badge Sinergi, 4 peningkatan Sinergi."""

    @classmethod
    def setUpClass(cls):
        cls.cards = [c for c in s8_data()["cards"] if c.get("active")]

    def card(self, cid):
        return next(c for c in self.cards if c["id"] == cid)

    def test_kartu_power_berkualitas_emas(self):
        lunox = self.card(3017)  # Lunox's Power (khusus Commander Lunox)
        self.assertEqual((lunox["tier"], lunox["power"], lunox["commander"]), ("Oranye", True, "Lunox"))

    def test_tidak_ada_tier_power_lagi(self):
        self.assertEqual([c["name"] for c in self.cards if c["tier"] == "Power"], [])

    def test_kartu_power_umum_juga_ditandai(self):  # Lunox's Power umum 3045: tanpa commander, muncul di putaran 1-3
        self.assertTrue(self.card(3045)["power"])

    def test_jenis_kartu_dari_tag(self):
        self.assertEqual(self.card(3019)["tags"], ["Kartu Power", "Kartu finansial"])  # Aamon's Power
        self.assertEqual(self.card(2001)["tags"], ["Kartu finansial"])  # Excellent Recruit
        self.assertNotIn("power", self.card(2001))


class WheelOfFateS8(unittest.TestCase):
    """Wheel of Fate (MCRoulette): diputar setelah memilih commander, sebelum babak I-1. 9 efek berbobot > 0 = 9 efek di video
    resmi; hasil di rekaman 20 Nov: Early Reinforcement (07-39), Tycoon (08-02), Gold Galore (08-22)."""

    @classmethod
    def setUpClass(cls):
        cls.wof = s8_data()["wheel_of_fate"]
        cls.fx = {e["name"] + ("" if e["active"] else " (nonaktif)"): e for e in cls.wof["effects"]}

    def test_sembilan_efek_aktif(self):
        self.assertEqual(sorted(n for n, e in self.fx.items() if e["active"]),
                         ["Commander's Power", "Crystal Legend", "Early Reinforcement", "Fate Sync", "Gold Galore",
                          "Hero Reinforcement", "Oracle Vision", "Synergy Awakening", "Tycoon"])
        self.assertEqual(self.wof["total_weight"], 15)

    def test_peluang_dari_bobot(self):
        self.assertEqual((self.fx["Crystal Legend"]["chance"], self.fx["Gold Galore"]["chance"]), (13.3, 6.7))
        self.assertEqual(self.fx["Crystal Legend"]["new_player_chance"], 25.0)  # pemain baru: 4 efek berbobot 1

    def test_teks_sama_dengan_rekaman(self):
        self.assertEqual(self.fx["Early Reinforcement"]["description"],
                         "Go Go Card di pertandingan ini muncul pada Babak I-2, I-3, dan I-4.")
        self.assertEqual(self.fx["Gold Galore"]["description"], "Semua Go Go Card di pertandingan ini Berkualitas Emas.")

    def test_aturan_per_putaran(self):
        self.assertEqual(self.fx["Crystal Legend"]["rounds"], [{"round": 1, "cards": "Kartu Badge Sinergi", "quality": "Ungu"}])
        self.assertEqual(self.fx["Synergy Awakening"]["rounds"], [{"round": 2, "cards": "Kartu peningkatan Sinergi", "quality": "Ungu"}])
        self.assertEqual([r["quality"] for r in self.fx["Gold Galore"]["rounds"]], ["Oranye"] * 3)
        self.assertEqual(self.fx["Early Reinforcement"]["trigger_rounds"], ["I-2", "I-3", "I-4"])

    def test_efek_khusus(self):
        self.assertTrue(self.fx["Fate Sync"]["shared_cards"])
        self.assertTrue(self.fx["Oracle Vision"]["foresight"])
        self.assertEqual(len(self.fx["Hero Reinforcement"]["post_select_skills"]), 3)

    def test_efek_nonaktif_tetap_tercatat(self):
        self.assertEqual(sorted(n for n, e in self.fx.items() if not e["active"]),
                         ["Hero Awakening (nonaktif)", "Promotion Rewards (nonaktif)", "Tycoon (nonaktif)"])

    def test_aturan_khusus_commanders_power(self):
        # m_SpecialRules [1,1,1] = jenis 1 (MCLogicGoGoCardRouletteSpecialRules.TryPickSelfCommander), putaran 1, slot 1.
        # Rekaman 22 Nov 16-26 (Lukas): slot kiri I-2 tetap Lukas's Power setelah 2 kali refresh, slot kanan berganti
        # Aurora's -> Guinevere's -> Franco's Power; putaran 2 (II-3) dan 3 (III-3) tanpa kartu Power Lukas.
        self.assertEqual(self.fx["Commander's Power"]["special_rules"],
                         [{"type": 1, "round": 1, "slot": 1, "text": "Kartu Power Commander sendiri"}])

    def test_catatan_roda_dua_belas_segmen(self):  # screenshot 27 Nov: 7 segmen terlihat = setengah lingkaran
        self.assertTrue(any("12 segmen" in n for n in self.wof["notes"]))


class TokoSpiritSandS8(unittest.TestCase):
    """Toko S8 dicek ke 20 layar + rekaman 23 Nov 03-34: 10 dari 11 item dengan harga (ATK Rekan +1% tidak muncul),
    9 pembelian sesuai stack (ATK +2% = +3 stack, ATK +3% = +5 stack, seperti S7)."""

    def test_toko_s8_terverifikasi(self):
        store = s8_data()["special_store"]
        self.assertTrue(store["verified"])
        atk3 = next(i for i in store["items"] if i["name"] == "ATK Rekan +3%")
        self.assertIn("Cocok dengan kenaikan baris ATK rekan", " ".join(atk3["notes"]))


def s8_md():
    return (Path(__file__).resolve().parent / "data" / "1.3.32.354.1" / "S8.md").read_text(encoding="utf-8")


class MarkdownS8(unittest.TestCase):
    def test_catatan_go_go_box_di_bagian_go_go_box(self):  # dulu tercetak di bawah tabel Wheel of Fate
        md = s8_md()
        box, wheel = md.index("## Go Go Box"), md.index("## Wheel of Fate")
        self.assertIn("ID 1054", md[box:wheel])
        self.assertNotIn("ID 1054", md[wheel:md.index("## ", wheel + 3)])

    def test_aturan_khusus_di_tabel_wheel_of_fate(self):
        row = next(l for l in s8_md().splitlines() if l.startswith("| Commander's Power |"))
        self.assertIn("putaran 1 slot 1: Kartu Power Commander sendiri", row)


if __name__ == "__main__":
    unittest.main()
