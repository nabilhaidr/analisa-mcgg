"""Tes mc_match.py: babak frame yang HUD-nya tertutup overlay (pilih Go Go Card) dari tampilan label babak, kotak Gold yang
hanya dibaca bila penghitung Gold tampil (bukan harga jual unit atau dialog), Gold yang terlewat OCR Windows dibaca ulang dari
kotak Gold dengan RapidOCR, dan Gold awal babak. test_data/gold/ = potongan kotak Gold asli dari frame rekaman 21–24 Okt
(ponsel 160x108, PC 144x126); *_lewat = angka yang tidak terbaca OCR Windows.

Jalankan dari folder ini: python -m pytest test_mc_match.py   (atau: python -m unittest test_mc_match)
"""
import json
import tempfile
import unittest
from pathlib import Path

import numpy as np
from PIL import Image

import mc_match
import mc_ocr
import mc_vision
import video_frames

GOLD =Path(__file__).resolve().parent / "test_data" / "gold"
RANK = GOLD.parent / "rank"


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


class EventKinds(unittest.TestCase):
    def test_card_pick_with_the_p_cut_off(self):
        # 24 Okt 15-06 825 s: the III-3 pick, its prompt split by OCR Windows
        self.assertIn("Pilih Go Go Card", mc_match.event_kinds("Silakan | sh | ilih 1 Go Go Card. | Bright Sunshine"))

    def test_card_pick_prompt(self):
        self.assertIn("Pilih Go Go Card", mc_match.event_kinds("Silakan pilih 1 Go Go Card. | Fast Promotion"))

    def test_go_go_card_panel_is_no_pick(self):
        # the board info panel (24 Okt 15-06 535 s)
        self.assertNotIn("Pilih Go Go Card", mc_match.event_kinds("Go Go Card | Hero yang Ditempatkan | O.Ne | 014"))


class GameArea(unittest.TestCase):
    def test_portrait_canvas_keeps_the_landscape_game_across_its_middle(self):  # 31 Okt 03-23: 1080x2400, game 1080x486
        canvas = Image.new("RGB", (1080, 2400))
        canvas.paste((255, 255, 255), (0, 957, 1080, 1443))
        game = video_frames.game_area(canvas)
        self.assertEqual(game.size, (1080, 486))
        self.assertEqual(game.getextrema(), ((255, 255), (255, 255), (255, 255)))

    def test_landscape_recording_stays_as_it_is(self):
        frame = Image.new("RGB", (2400, 1080))
        self.assertIs(video_frames.game_area(frame), frame)


class GoGoBoxTitle(unittest.TestCase):
    """OCR rarely reads the title as written: "Piiih Hadiah" 141 times against "Pilih Hadiah" 21 times in 20 recordings."""

    def test_title_with_the_l_read_as_i(self):  # 31 Okt 03-49: every box frame of the match reads like this
        self.assertEqual(mc_match.event_kinds("17 Piiih Hadiah"), ["Go Go Box"])

    def test_title_with_the_l_read_as_a_slash(self):
        self.assertEqual(mc_match.event_kinds("P/lih Hadiah"), ["Go Go Box"])

    def test_title_with_the_start_cut_off(self):
        self.assertEqual(mc_match.event_kinds("ih Hadiah"), ["Go Go Box"])

    def test_title_without_a_space(self):
        self.assertEqual(mc_match.event_kinds("ihHadiah"), ["Go Go Box"])

    def test_round_income_is_no_box(self):
        self.assertEqual(mc_match.event_kinds("Gold: +5 | Hadiah Dasar | Keuntungan"), [])

    def test_card_text_about_a_reward_is_no_box(self):  # Vexana's Power on the card pick screen
        self.assertEqual(mc_match.event_kinds("Box, kamu bisa memilih 1 hadiah | tambahan dari hadiah yang"), [])


def result_rows(fighting=()):
    return [{"rank": i, "name": n, **({"fighting": True} if i in fighting else {})}
            for i, n in enumerate(("Shalnark", "Cleon", "CinCoeg", "Vuizen"), 1)]


class InterimRanks(unittest.TestCase):
    """A player who is out sees the result screen while the others still play: crossed swords instead of their ranks."""

    def test_rows_with_swords_have_no_rank(self):
        rows = mc_match.interim_ranks(result_rows(fighting=(1, 2)))
        self.assertEqual([r["rank"] for r in rows], [None, None, 3, 4])

    def test_screen_without_swords_keeps_every_rank(self):  # Classic on Riwayat: no points line, yet the ranks are final
        self.assertEqual([r["rank"] for r in mc_match.interim_ranks(result_rows())], [1, 2, 3, 4])


class RankSwords(unittest.TestCase):
    """test_data/rank/ = left 30% of real result screens; the swords were counted by eye."""

    def middles(self, name, pitch):
        return mc_match.sword_ys(mc_vision.to_bgr(RANK / name), pitch)

    def assert_near(self, ys, want):
        self.assertEqual(len(ys), len(want), ys)
        for y, w in zip(ys, want):
            self.assertAlmostEqual(y, w, delta=6)

    def test_points_on_screen_do_not_hide_the_swords(self):  # 31 Okt 20:13: "4791 +28", own rank 4, 3 still playing
        self.assert_near(self.middles("swords_phone.jpg", 106), [152, 259, 366])

    def test_swords_at_pc_scale(self):  # 21 Okt 02:25 Kalea: 1366x768, rows 76 px apart
        self.assert_near(self.middles("swords_pc.jpg", 76), [109, 184])

    def test_no_swords_on_a_final_screen(self):
        self.assertEqual(self.middles("final_phone.jpg", 106), [])

    def test_no_swords_on_a_classic_riwayat_screen(self):  # 31 Okt 03:23: no points line, every rank is final
        self.assertEqual(self.middles("riwayat_classic.jpg", 106), [])


class GridPitch(unittest.TestCase):
    def test_a_missing_row_counts_as_a_step(self):  # rank 3 has no hero row
        self.assertEqual(mc_match.grid_pitch([(1, [], 150.0), (2, [], 256.0), (4, [], 468.0)]), 106.0)

    def test_one_row_has_no_pitch(self):
        self.assertIsNone(mc_match.grid_pitch([(1, [], 150.0)]))


def round_row(label, hp=100):
    return {"label": label, "start": {"CinCoeg": hp}, "delta": {}, "level": 9, "gold": 10}


class NoResultScreen(unittest.TestCase):
    def test_recording_without_a_result_screen_says_where_it_stopped(self):
        notes = [t for _, t in mc_match.insights([round_row("IV-4"), round_row("IV-5", 3)], "CinCoeg", [], None)]
        self.assertIn("Rekaman berhenti di IV-5 tanpa layar hasil: peringkat akhir tidak diketahui.", notes)

    def test_known_rank_needs_no_such_note(self):
        notes = [t for _, t in mc_match.insights([round_row("IV-5")], "CinCoeg", [], 4)]
        self.assertFalse([t for t in notes if "tanpa layar hasil" in t])


class CutRecording(unittest.TestCase):
    """31 Okt 03-49: the recording stops at IV-5 with HP 3, Riwayat later shows rank 3, so IV-5 is not where the player went out."""

    def notes(self):
        return [t for _, t in mc_match.insights([round_row("IV-4"), round_row("IV-5", 3)], "CinCoeg", [], 3, cut=True)]

    def test_note_says_where_the_recording_stopped(self):
        self.assertIn("Rekaman berhenti di IV-5 sebelum pertandingan selesai.", self.notes())

    def test_rank_from_riwayat_is_still_reported(self):
        self.assertIn("Peringkat akhir 3.", self.notes())

    def test_full_recording_has_no_such_note(self):
        notes = [t for _, t in mc_match.insights([round_row("IV-5")], "CinCoeg", [], 3)]
        self.assertFalse([t for t in notes if "sebelum pertandingan selesai" in t])


class ReopenedPicks(unittest.TestCase):
    @staticmethod
    def pick(t, rnd, *options):
        return {"t": t, "round": rnd, "kind": "Pilih Go Go Card", "detail": "pilihan: " + ", ".join(options),
                "options": list(options)}

    def test_pick_screen_opened_again_is_marked(self):
        # 23 Okt 21-47: the II-3 pick put off and opened again in II-6 and (after Refresh) III-2; the result screen shows
        # two Go Go Cards, Starbelle's Badge and Echomancer's Badge
        events = [self.pick(375, 7, "Fast Promotion", "Premium Client I"),
                  {"t": 500, "round": 9, "kind": "Go Go Box", "detail": ""},
                  self.pick(545, 10, "Fast Promotion", "Premium Client I"),
                  self.pick(715, 12, "Starbelle's Badge", "Premium Client I"),
                  self.pick(780, 13, "Total Domination", "Echomancer's Badge")]
        self.assertEqual([e["detail"] for e in mc_match.reopened_picks(events)],
                         ["pilihan: Fast Promotion, Premium Client I", "",
                          "dibuka lagi, pilihan II-3: Fast Promotion, Premium Client I",
                          "dibuka lagi, pilihan II-3: Starbelle's Badge, Premium Client I",
                          "pilihan: Total Domination, Echomancer's Badge"])

    def test_separate_picks_stay_separate(self):
        events = [self.pick(430, 7, "Dark Blade", "Rising Fury Ⅰ"), self.pick(825, 13, "Bright Sunshine", "Frontier Blitz")]
        self.assertEqual([e["detail"] for e in mc_match.reopened_picks(events)],
                         ["pilihan: Dark Blade, Rising Fury Ⅰ", "pilihan: Bright Sunshine, Frontier Blitz"])


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
        # Kalea PC 510 s and 22 Okt 04-55 165 s: a clear 14 / 11 that OCR Windows did not read; *_satu: a lone digit
        # (Kalea PC 1165 s, 22 Okt 04-55 65 s) that RapidOCR finds but scores just under its default 0.5
        for name, layout, size, want in (("pc_gold_14_lewat", "pc", (1600, 902), 14),
                                         ("ponsel_gold_11_lewat", "ponsel", (1600, 720), 11),
                                         ("pc_gold_0_satu", "pc", (1600, 902), 0),
                                         ("ponsel_gold_2_satu", "ponsel", (1600, 720), 2)):
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


class HandNames(unittest.TestCase):
    """Names no OCR model reads (kana, ornamental letters), written down by eye per battle ID and row."""

    def rows(self):
        return [{"row": 1, "name": "CinCoeg"}, {"row": 2, "name": "baris 2", "slot": ("hasil.jpg", (0, 0, 9, 9))},
                {"row": 3, "name": "마샤 주나어", "ko": 0.73}]

    def named(self, battle):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "catatan_nama.json"
            path.write_text(json.dumps({"_catatan": "-", "123": {"2": "ブラッカー", "3": "마샤 주니어"}}, ensure_ascii=False), encoding="utf-8")
            return mc_match.hand_names(self.rows(), battle, path)

    def test_a_noted_row_takes_the_written_name(self):
        self.assertEqual(self.named("123")[1]["name"], "ブラッカー")

    def test_it_replaces_the_picture(self):
        self.assertNotIn("slot", self.named("123")[1])

    def test_it_replaces_a_misread_korean_name(self):
        row = self.named("123")[2]
        self.assertEqual((row["name"], row.get("ko")), ("마샤 주니어", None))

    def test_a_noted_row_is_marked_as_unread_by_the_hud_too(self):  # unread_player links it to the HUD player
        self.assertTrue(self.named("123")[1]["hand"])

    def test_rows_without_a_note_stay(self):
        self.assertEqual(self.named("123")[0], {"row": 1, "name": "CinCoeg"})

    def test_another_battle_stays(self):
        self.assertEqual(self.named("999"), self.rows())

    def test_no_id_read_stays(self):
        self.assertEqual(self.named(None), self.rows())


class FrameRows(unittest.TestCase):
    """Player rows of one frame. Values of 31 Okt 02-51 PC, frame 1065 (1600x902): blackdevil46 has HP 4 + Shield 2, so about 3 px
    of the bar are green and hp_bars finds nothing there, while the name and "02 •4" read fine."""
    W, H = 1600, 902
    BARS = [(558.5, 32, False, 1508, False)]
    NAMES = [("Yann", 530.6, False), ("Plackdevil...", 605.6, False)]
    NUMS = [(569.6, 18, False, 1510.0), (645.1, 4, True, 1511.0)]

    def rows(self, bars=None, names=None, nums=None, mirrors=()):
        return mc_match.frame_rows(self.BARS if bars is None else bars, self.NAMES if names is None else names,
                                   self.NUMS if nums is None else nums, mirrors, self.W, self.H)

    def test_a_bar_under_a_name_is_a_row(self):
        row = self.rows()[0][0]
        self.assertEqual((row["name"], row["bar"], row["ocr"]), ("Yann", 32, 18))

    def test_a_name_without_a_bar_takes_the_number_under_it(self):
        row = self.rows()[0][1]
        self.assertEqual((row["name"], row["bar"], row["ocr"], row["shield"]), ("Plackdevil...", None, 4, True))

    def test_a_name_without_a_bar_or_number_is_no_row(self):  # an eliminated player: the dimmed row
        self.assertEqual([r["name"] for r in self.rows(nums=self.NUMS[:1])[0]], ["Yann"])

    def test_the_number_of_the_next_row_is_not_taken(self):  # 114 px under the name = the row below
        names = [("PRAMUD", 455.6, False), ("Yann", 530.6, False)]
        self.assertEqual([r["name"] for r in self.rows(names=names, nums=self.NUMS[:1])[0]], ["Yann"])

    def test_a_number_under_a_bar_is_not_used_twice(self):  # 21 Okt 22:15: stray text "ell" took OLORENG's 11
        names = [("ell", 523.0, False), ("Yann", 530.6, False)]
        nums = [(569.6, 18, False, 1510.0), (570.6, 18, False, 1510.0)]  # the same number from the panel and panel_text crops
        self.assertEqual([r["name"] for r in self.rows(names=names, nums=nums)[0]], ["Yann"])

    def test_a_dimmed_zero_is_no_row(self):
        nums = self.NUMS[:1] + [(645.1, 0, False, 1511.0)]
        self.assertEqual([r["name"] for r in self.rows(nums=nums)[0]], ["Yann"])

    def test_a_bar_without_a_name_is_kept_apart(self):  # the name is unread: Hangul, symbols
        rows, unnamed = self.rows(names=[("Plackdevil...", 605.6, False)])
        self.assertEqual([(u["bar"], u["ocr"]) for u in unnamed], [(32, 18)])
        self.assertEqual([r["name"] for r in rows], ["Plackdevil..."])

    def test_the_mirror_row_is_no_unnamed_player(self):
        self.assertEqual(self.rows(names=[], mirrors=[530.6])[1], [])


class UnnamedRows(unittest.TestCase):
    """24 Okt 14:43: the HUD never gives the name "1254" (no letters), so that player's bars come without a name. In a frame where
    all other players still alive stand by name, the one bar left over is theirs."""

    def row(self, name, bar=80):
        return {"name": name, "y": 100.0, "bar": bar, "shield": False, "cut": False, "ocr": None}

    def frame(self, names, unnamed=(70,)):
        return {"rows": [self.row(n) for n in names], "unnamed": [{"y": 200.0, "bar": b, "shield": False, "cut": False, "ocr": None}
                                                                  for b in unnamed]}

    def clusters(self, *names):
        return [[n, n.lower(), 10, {n}, set(range(10))] for n in names]

    FINAL = [{"name": n, "row": i} for i, n in enumerate(("Giommy", "1254", "Rapaa"), 1)]

    def linked(self, recs, clusters=None, final=None):
        clusters = self.clusters("Giommy", "Rapaa") if clusters is None else clusters
        mc_match.unnamed_rows(recs, clusters, self.FINAL if final is None else final)
        return [[r["name"] for r in rec["rows"]] for rec in recs]

    def test_the_bar_left_over_is_the_missing_result_row(self):
        self.assertEqual(self.linked([self.frame(["Giommy", "Rapaa"])]), [["Giommy", "Rapaa", "1254"]])

    def test_the_player_joins_the_clusters(self):
        clusters = self.clusters("Giommy", "Rapaa")
        self.linked([self.frame(["Giommy", "Rapaa"])], clusters)
        self.assertEqual([c[0] for c in clusters], ["Giommy", "Rapaa", "1254"])

    def test_a_bar_a_missing_player_can_have_stays_open(self):  # Rapaa, unread here, later has 80: before that HP was higher
        recs = [self.frame(["Giommy"], unnamed=(90,)), self.frame(["Giommy", "Rapaa"], unnamed=())]
        self.assertEqual(self.linked(recs)[0], ["Giommy"])

    def test_a_bar_shorter_than_the_missing_player_has_later_is_not_theirs(self):
        recs = [self.frame(["Giommy"], unnamed=(60,)), self.frame(["Giommy", "Rapaa"], unnamed=())]
        self.assertEqual(self.linked(recs)[0], ["Giommy", "1254"])

    def test_the_missing_player_takes_the_bar_that_fits_them(self):  # Rapaa unread at 80, the other bar is left over
        recs = [self.frame(["Giommy", "Rapaa"], unnamed=()), self.frame(["Giommy"], unnamed=(80, 60)),
                self.frame(["Giommy", "Rapaa"], unnamed=())]
        self.assertEqual(self.linked(recs)[1], ["Giommy", "1254"])
        self.assertEqual(recs[1]["rows"][-1]["bar"], 60)

    def test_two_bars_without_a_name_stay_open(self):
        self.assertEqual(self.linked([self.frame(["Giommy", "Rapaa"], unnamed=(70, 60))]), [["Giommy", "Rapaa"]])

    def test_a_shielded_bar_stays_open_while_a_player_is_unread(self):  # it shows less green than the HP
        recs = [self.frame(["Giommy"], unnamed=(60,)), self.frame(["Giommy", "Rapaa"], unnamed=())]
        recs[0]["unnamed"][0]["shield"] = True
        self.assertEqual(self.linked(recs)[0], ["Giommy"])

    def test_one_stray_low_bar_does_not_stop_the_rest(self):
        recs = [self.frame(["Giommy", "Rapaa"], unnamed=(b,)) for b in (80, 80, 20, 80, 80)]
        self.assertEqual([len(names) for names in self.linked(recs)], [3, 3, 2, 3, 3])

    def test_a_player_who_left_for_good_is_not_waited_for(self):  # Rapaa is out after the first frame
        recs = [self.frame(["Giommy", "Rapaa"], unnamed=()), self.frame(["Giommy"])]
        self.assertEqual(self.linked(recs)[1], ["Giommy", "1254"])

    def test_a_bar_that_rises_is_not_that_player(self):  # HP never rises: the Mirror row after the player is out
        recs = [self.frame(["Giommy", "Rapaa"], unnamed=(40,)), self.frame(["Giommy", "Rapaa"], unnamed=(90,))]
        self.assertEqual(self.linked(recs)[1], ["Giommy", "Rapaa"])

    def test_every_result_row_taken_changes_nothing(self):
        clusters = self.clusters("Giommy", "1254", "Rapaa")
        self.assertEqual(self.linked([self.frame(["Giommy", "1254", "Rapaa"])], clusters), [["Giommy", "1254", "Rapaa"]])

    def test_two_players_without_a_cluster_stay_open(self):
        self.assertEqual(self.linked([self.frame(["Rapaa"])], self.clusters("Rapaa")), [["Rapaa"]])

    def test_without_a_result_screen_nothing_changes(self):
        self.assertEqual(self.linked([self.frame(["Giommy", "Rapaa"])], final=[]), [["Giommy", "Rapaa"]])

    def test_an_empty_key_does_not_catch_other_names(self):  # "" starts every name: a Hangul player has no key
        clusters = self.clusters("Giommy", "Rapaa")
        final = [{"name": "Giommy", "row": 1}, {"name": "마샤 주니어", "row": 2}, {"name": "Rapaa", "row": 3}]
        self.linked([self.frame(["Giommy", "Rapaa"])], clusters, final)
        self.assertIsNone(mc_match.player_of("Zzzzzz", clusters))

    def test_the_own_yellow_row_counts_by_its_colour(self):  # "CirCoeg" read in the yellow row
        recs = [{"rows": [dict(self.row("CirCoeg"), yellow=True), self.row("Rapaa")],
                 "unnamed": [{"y": 200.0, "bar": 70, "shield": False, "cut": False, "ocr": None}]}]
        clusters = self.clusters("CinCoeg", "Rapaa")
        final = [{"name": "CinCoeg", "row": 1}, {"name": "1254", "row": 2}, {"name": "Rapaa", "row": 3}]
        mc_match.unnamed_rows(recs, clusters, final, "CinCoeg")
        self.assertEqual([r["name"] for r in recs[0]["rows"]], ["CirCoeg", "Rapaa", "1254"])


class BarlessRows(unittest.TestCase):
    """A row found from its name and number alone (FrameRows) has no bar to measure."""

    def recs(self):
        full = [{"name": "Yann", "y": 100.0, "bar": 100, "shield": False, "cut": False, "ocr": 100 - i} for i in range(10)]
        return [{"t": 5 * i, "round": "IV-1", "gold": None, "level": None, "look": None,
                 "rows": [full[i], {"name": "blackdevil", "y": 200.0, "bar": None, "shield": True, "cut": False, "ocr": 4}]} for i in range(10)]

    def test_the_number_stands_without_a_bar(self):
        recs = self.recs()
        clusters = mc_match.cluster_players(recs)
        tl = mc_match.timeline(recs, clusters, mc_match.calibrate(recs))
        self.assertEqual(tl[0]["hp"]["blackdevil"], 4)

    def test_calibration_skips_them(self):
        self.assertGreater(mc_match.calibrate(self.recs())[0], 0)


class NumbersOutvoteTheBar(unittest.TestCase):
    """31 Okt 02-51 PC IV-2: readings 12, 13, 12, of which only the 13 is a number on the screen; the screen shows 13."""

    def frames(self, values):
        return [{"t": 5 * i, "round": 18, "gold": None, "level": None, "hp": {"A": v}, "read": ["A"] if number else []}
                for i, (v, number) in enumerate(values)]

    def test_a_read_number_beats_more_bar_estimates(self):
        table = mc_match.rounds_table(self.frames([(12, False), (13, True), (12, False), (12, False), (12, False)]), ["A"])
        self.assertEqual(table[0]["start"]["A"], 13)

    def test_bar_estimates_stand_without_a_number(self):
        table = mc_match.rounds_table(self.frames([(12, False), (12, False), (11, False)]), ["A"])
        self.assertEqual(table[0]["start"]["A"], 12)

    def test_the_most_common_number_wins(self):
        table = mc_match.rounds_table(self.frames([(18, True), (13, True), (13, True), (13, True), (12, False)]), ["A"])
        self.assertEqual(table[0]["start"]["A"], 13)

    def test_a_later_number_next_to_the_estimate_is_the_same_hp(self):  # the bar wobbles 25-26 px, 13 shows at the end of the round
        values = [(12, False), (13, False), (12, False), (12, False), (12, False), (13, True)]
        self.assertEqual(mc_match.rounds_table(self.frames(values), ["A"])[0]["start"]["A"], 13)

    def test_a_later_number_further_off_is_after_the_fight(self):  # a lost fight takes at least 3 HP
        values = [(40, False), (40, False), (40, False), (40, False), (40, False), (30, True)]
        self.assertEqual(mc_match.rounds_table(self.frames(values), ["A"])[0]["start"]["A"], 40)


class LastReadingAboveTheLine(unittest.TestCase):
    """21 Okt 22:15: EiRaCantik (rank 8) stood at 15, then a partly read copy of another player's name gave 43 in IV-4. HP never
    rises, so that reading is not theirs and must not keep them in the table."""

    def table(self, values):
        return mc_match.rounds_table([{"t": 5 * i, "round": 17 + i, "gold": None, "level": None, "hp": {"A": v} if v else {}, "read": ["A"]}
                                      for i, v in enumerate(values)], ["A"])

    def test_it_is_dropped(self):
        self.assertEqual([r["start"].get("A") for r in self.table([30, 15, 43])], [30, 15, None])

    def test_a_high_reading_inside_the_series_is_still_evened_out(self):
        self.assertEqual([r["start"].get("A") for r in self.table([60, 90, 60, 47])], [60, 60, 60, 47])

    def test_a_series_that_falls_stays(self):
        self.assertEqual([r["start"].get("A") for r in self.table([30, 15, 4])], [30, 15, 4])

    def test_a_last_reading_seen_in_many_frames_is_not_stray(self):
        tl = [{"t": 5 * i, "round": n, "gold": None, "level": None, "hp": {"A": v}, "read": ["A"]}
              for i, (n, v) in enumerate([(17, 30), (18, 15), (19, 43), (19, 43), (19, 43)])]
        self.assertEqual([r["start"].get("A") for r in mc_match.rounds_table(tl, ["A"])], [30, 15, 15])


class HealingFountainRise(unittest.TestCase):
    """The card gives 3 HP every round, so HP can rise: 22 Okt 06:16 CinCoeg 7, 10, 13 ... 28, YXGC 37, 40, 43 ... The holders
    went flat in the table (all at 19 from V-1 on) while a misread number must still be evened out."""

    def starts(self, values, heal=None):
        tl = [{"t": 5 * i, "round": 17 + i, "gold": None, "level": None, "hp": {"A": v}, "read": ["A"]} for i, v in enumerate(values)]
        return [r["start"].get("A") for r in mc_match.rounds_table(tl, ["A"], {"A": 3} if heal is None else heal)]

    def test_the_rise_stays(self):
        self.assertEqual(self.starts([7, 10, 13, 16]), [7, 10, 13, 16])

    def test_a_loss_between_rises_stays(self):
        self.assertEqual(self.starts([40, 43, 30, 33]), [40, 43, 30, 33])

    def test_flat_rounds_before_the_card_stay(self):
        self.assertEqual(self.starts([50, 50, 50, 53, 56]), [50, 50, 50, 53, 56])

    def test_a_misread_spike_is_still_evened_out(self):
        self.assertEqual(self.starts([7, 10, 40, 16]), [7, 10, 13, 16])

    def test_without_the_card_hp_does_not_rise(self):
        got = [v for v in self.starts([30, 15, 20, 18, 12], heal={}) if v is not None]
        self.assertEqual(got, sorted(got, reverse=True))


class HealOf(unittest.TestCase):
    def test_only_holders_of_the_card_count(self):
        final = [{"name": "YXGC", "cards": ["Lunox's Power", "Healing Fountain"]}, {"name": "CinCoeg", "cards": ["Fanny's Power"]}]
        self.assertEqual(mc_match.heal_of(final), {"YXGC": 3})


if __name__ == "__main__":
    unittest.main()
