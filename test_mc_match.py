"""Tes mc_match.py: babak frame yang HUD-nya tertutup overlay (pilih Go Go Card) dari tampilan label babak, kotak Gold yang
hanya dibaca bila penghitung Gold tampil (bukan harga jual unit atau dialog), Gold yang terlewat OCR Windows dibaca ulang dari
kotak Gold dengan RapidOCR, dan Gold awal babak. test_data/gold/ = potongan kotak Gold asli dari frame rekaman 21–24 Okt
(ponsel 160x108, PC 144x126); *_lewat = angka yang tidak terbaca OCR Windows.

Jalankan dari folder ini: python -m pytest test_mc_match.py   (atau: python -m unittest test_mc_match)
"""
import tempfile
import unittest
from pathlib import Path

import numpy as np
from PIL import Image

import mc_match
import mc_ocr

GOLD = Path(__file__).resolve().parent / "test_data" / "gold"


def look(seed):
    """An edge map of a round label pill (round_look shape); each seed is a different label."""
    return np.random.default_rng(seed).random((32, 78)).astype(np.float32)


def rec(pill, hud=True):
    """A frame record as read_frames makes it; hud=False = the HP panel, Gold and Level are hidden by an overlay."""
    return {"rows": [{"name": "CinCoeg"}] if hud else [], "gold": 17 if hud else None, "level": 9 if hud else None,
            "look": pill}


class RoundsByLook(unittest.TestCase):
    def test_frame_with_hidden_hud_gets_the_round_its_label_shows(self):
        # Kalea PC 575 s: the Go Go Card pick dims the HUD but its label pill still shows III-3 (13)
        recs = [rec(look(12)), rec(look(12)), rec(look(13), hud=False), rec(look(13))]
        self.assertEqual(mc_match.rounds_by_look(recs, [12, 12, None, 13]), [12, 12, 13, 13])

    def test_frame_with_hidden_hud_and_no_label_pill_stays_open(self):
        # loading or result screens: nothing like a known label
        recs = [rec(look(12)), rec(look(99), hud=False), rec(look(13))]
        self.assertEqual(mc_match.rounds_by_look(recs, [12, None, 13]), [12, None, 13])


class EventRound(unittest.TestCase):
    BOX = {4, 10, 16}  # S7 Go Go Box: I-4, II-6, III-6 (go_go_box.rounds in S7.json)

    def test_go_go_box_seen_after_the_split_belongs_to_the_box_round(self):
        # the "Pilih Hadiah" screen hides the round label; split evenly it landed in II-1 (5) or IV-1 (17)
        self.assertEqual(mc_match.event_round("Go Go Box", 5, self.BOX), 4)
        self.assertEqual(mc_match.event_round("Go Go Box", 17, self.BOX), 16)

    def test_go_go_box_in_its_round_stays(self):
        self.assertEqual(mc_match.event_round("Go Go Box", 10, self.BOX), 10)

    def test_go_go_box_away_from_the_schedule_stays(self):
        self.assertEqual(mc_match.event_round("Go Go Box", 7, self.BOX), 7)

    def test_other_events_keep_their_round(self):
        # Pilih Go Go Card at II-1 is not a Go Go Box
        self.assertEqual(mc_match.event_round("Pilih Go Go Card", 5, self.BOX), 5)

    def test_unknown_round_stays_unknown(self):
        self.assertIsNone(mc_match.event_round("Go Go Box", None, self.BOX))


class GoldShown(unittest.TestCase):
    def test_gold_counter_is_read_also_when_dimmed(self):
        # pc_gold_redup_24 / ponsel_gold_redup_22: an overlay dims the counter, the number is still right
        for name in ("pc_gold_17", "ponsel_gold_12", "pc_gold_redup_24", "ponsel_gold_redup_22"):
            with self.subTest(name):
                self.assertTrue(mc_match.gold_shown(Image.open(GOLD / f"{name}.png")))

    def test_sell_price_and_dialogs_are_not_gold(self):
        # read as Gold 0-15 before: Kalea PC III-2 = 0 (pc_jual_1) and III-4 = 6 (pc_buang_5)
        for name in ("pc_jual_1", "pc_buang_5", "ponsel_jual_15", "ponsel_buang_3", "ponsel_dialog_ok", "ponsel_dialog_biru"):
            with self.subTest(name):
                self.assertFalse(mc_match.gold_shown(Image.open(GOLD / f"{name}.png")))


class ParseGold(unittest.TestCase):
    def test_number_after_the_coin(self):
        # OCR reads the coin as a letter or not at all: "U 75", "e 24", "(e) 44" (21-26 Okt recordings)
        for text, want in (("U 75", 75), ("e 24", 24), ("(e) 44", 44), ("17", 17)):
            with self.subTest(text):
                self.assertEqual(mc_match.parse_gold(text), want)

    def test_no_number_or_too_big(self):
        for text in ("", "Spasi", "999"):
            with self.subTest(text):
                self.assertIsNone(mc_match.parse_gold(text))


@unittest.skipUnless(mc_ocr.rapid_available(), "RapidOCR tidak terpasang")
class GoldLabels(unittest.TestCase):
    def test_gold_missed_by_the_hud_ocr_is_read_from_the_gold_box(self):
        # Kalea PC 510 s and 22 Okt 04-55 165 s: a clear 14 / 11 that OCR Windows did not read
        for name, layout, size, want in (("pc_gold_14_lewat", "pc", (1600, 902), 14),
                                         ("ponsel_gold_11_lewat", "ponsel", (1600, 720), 11)):
            with self.subTest(name), tempfile.TemporaryDirectory() as tmp:
                box = mc_match.LAYOUTS[layout]["gold"]
                frame = Image.new("RGB", size)
                frame.paste(Image.open(GOLD / f"{name}.png"), (int(box[0] * size[0]), int(box[1] * size[1])))
                path = Path(tmp) / "f_00510.png"
                frame.save(path)
                self.assertEqual(mc_match.gold_labels([path], Path(tmp), layout), {"f_00510": want})


class RoundsTableGold(unittest.TestCase):
    @staticmethod
    def frames(golds):
        """One round (IV-5 = 21), a frame every 5 s."""
        return [{"t": 1120 + 5 * i, "round": 21, "gold": g, "level": 9, "hp": {}} for i, g in enumerate(golds)]

    def test_start_gold_includes_an_income_that_comes_just_after_the_label(self):
        # Kalea IV-5: 19 before the income, 38 five seconds later, then spent
        self.assertEqual(mc_match.rounds_table(self.frames([19, 38, 26, 15]), [])[0]["gold"], 38)

    def test_income_at_the_end_of_the_round_is_not_start_gold(self):
        # 24 Okt 02-51 III-1: 37 from the first reading on; 47 at the end is the next round's income
        self.assertEqual(mc_match.rounds_table(self.frames([None, 37, 37, 37, None, 47]), [])[0]["gold"], 37)


if __name__ == "__main__":
    unittest.main()
