"""Tier list Season 8 (comp + commander) -> data/<versi>/TIER_LIST_S8.html + .md, dengan ikon dari img/.

Bukan win rate. Penilaian ditulis tangan di skrip ini dari sumber web yang dibuka 25 Nov 2026 dan dicek lagi 28 Nov (belum
berubah): loadoutgg comps dan commander, mcggdb commander, kitakuji 18 Nov, ditambah daftar Rekomendasi Lineup in-game
(rekaman ponsel 20 Nov 09:33). Sumber itu belum memperhitungkan Penyesuaian Keseimbangan 20/11 dan 26/11
(server_patch.json "8"), jadi efeknya dinilai di sini: comp yang carry atau intinya dinerf turun satu tingkat dari tier
sumbernya ("before"), buff hanya memulihkan sampai tier sumber; commander memakai aturan combined().

Pemakaian (dari folder patch-tracker, setelah mc_data.py):  python tier_list.py
Tes: python -m unittest test_tier_list -v
"""
import sys

from mc_common import chip, esc, load_season, md_table, page, stamp, table, ul, write_report

SEASON = 8
UP, DOWN = "↑", "↓"
VALUE = {"S": 4, "A": 3, "B": 2, "C": 1}
ORDER = "SABC"
P2011, P2611, SERVER = "20/11", "26/11", "server"

# Efek patch = (panah, teks, patch). Panah None = catatan saja, tidak dihitung.
# Penyesuaian Keseimbangan 20/11 (server_patch.json "8")
VALENTINA = (UP, "Valentina ★2: pengali DMG skill 165% → 190%", P2011)
BALMOND = (DOWN, "Balmond ★1/★2: pengali DMG skill 380%/410% → 370%, Shield ★2 6% → 5%; Mana ★3 yang terlalu cepat "
                 "diperbaiki", P2011)
POPOL = (DOWN, "Popol: Freeze 1,0 → 0,3 detik", P2011)
BARBIEL = (DOWN, "Barbiel: stun 1 → 0,5 detik", P2011)
FROST_LOW = (DOWN, "2/4 Frostrider: pewarisan Hybrid ATK Tunggangan 35%/50% → 20%/30%", P2011)
FROST_HP = (DOWN, "Frostrider: pewarisan HP Tunggangan 100% → 80%", P2011)
FROST_SIX = (UP, "6 Frostrider: pewarisan Hybrid ATK Tunggangan 65% → 80%", P2011)
KIMMY = (UP, "Kimmy ★3: pengali DMG skill 1.750% → 1.925% dan 750% → 825%", P2011)
GRAY = (UP, "Gray ★3: jangkauan penargetan skill diperluas", P2011)
DAWN = (UP, "10 Dawnbringer: Supreme Crown 350% → 500% Max HP", P2011)
NANA = (UP, "Nana: jangkauan skill yang terlalu pendek diperbaiki", P2011)
YU_ZHONG = (UP, "Yu Zhong: HP naik ±6% (★3 15.770 → 16.715)", P2011)
LIGHTSTICK = (UP, "Starbelle: bonus Hybrid ATK dasar Lightstick yang hilang dikembalikan", P2011)
LUKAS = (DOWN, "Lukas: Sacred Gift 3–4× → 2–3× Gold", P2011)
VEXANA = (DOWN, "Vexana: hadiah Go Go Box tambahan hanya di 3 Fase pertama; Gold per Fase 4 → 2", P2011)
BRODY = (UP, "Brody: Abyssal Surge bisa dipakai mulai Babak I-1", P2011)
# Penyesuaian Keseimbangan 26/11 (server_patch.json "8"): ★3 hero 4 Gold naik, beberapa hero 5 Gold turun
MELISSA = (UP, "Melissa ★3: DMG Area 205% → 320%, ATK Speed 100% → 200%", P2611)
EUDORA = (UP, "Eudora ★3: pengali DMG 700% → 800% (file 635%), DMG tertunda 345% → 400%", P2611)
KIMMY_3 = (UP, "Kimmy ★3: 1.925% → 2.150% dan 825% → 925%", P2611)
ARGUS = (UP, "Argus ★3: Basic ATK yang Diperkuat 600% → 700%", P2611)
LOLITA = (UP, "Lolita ★3: Physical DMG 1.700% → 1.950% (file 1455%), DMG berbasis HP 12% → 15%", P2611)
YU_ZHONG_3 = (UP, "Yu Zhong ★3: 900% → 1.050%, fase ketiga 1.120% → 1.300%", P2611)
SORA = (UP, "Sora ★3: pengali DMG 1.000% → 1.200%", P2611)
KARINA = (UP, "Karina ★2/★3: pengali DMG skill 450%/500% → 500%/600%", P2611)
ERZA = (UP, "Erza ★2/★3: Shield 750/1.800 → 1.050/2.400, Physical ATK 15%/40% → 20%/50%", P2611)
DAWN_46 = (UP, "4/6 Dawnbringer: stack peningkatan Equipment baru 7/14 → 9/15", P2611)
SWIFT = (UP, "2/4/6 Swiftblade: Hybrid Penetration Hero Swiftblade 25/50/100 → 35/65/130", P2611)
TITAN = (DOWN, "Titan (atribut Balmond): batas HP eksekusi 18% → 15%, DMG Area 200% → 180%", P2611)
BALMOND_3 = (DOWN, "Balmond ★3: Shield per target 9% → 7%, Batas Mana 120 → 170", P2611)
POPOL_2 = (DOWN, "Popol ★1/★2: tombak 27 → 18 lemparan, DMG per lemparan dan saat Freeze berakhir 30%/35% → 50%", P2611)
BANE = (DOWN, "Bane ★2: Freeze 1,8 → 1,2 detik", P2611)
KAGURA = (UP, "Kagura: Shield Bintang 2 125% → 135% Max HP", P2611)
LING = (UP, "Ling: Hybrid ATK permanen per duel 6% → 8%", P2611)
KALEA = (DOWN, "Kalea: hadiah Brankas Harta 5–8 poin berkurang 1–2 Gold", P2611)
GUINEVERE = (DOWN, "Guinevere: Hero gratis Bintang 2 24% → 23%", P2611)
ODETTE = (None, "Odette: tooltip 8–9 sinergi di layar 25%/35% dan 45%/60% HP/Hybrid ATK (file 30%/40% dan 50%/65%), nilai "
                "server tanpa patch note yang tidak diketahui sejak kapan; tidak dihitung", SERVER)


def comp(tier, name, synergies, carries, heroes, commanders, sources, patch=(), note="", before=None, was=None):
    """synergies: [(nama, jumlah atau None)]; before: tier sumber bila tier di sini lebih rendah karena nerf;
    was: tier sebelum patch 26/11 bila patch itu mengubahnya."""
    return {"tier": tier, "name": name, "synergies": synergies, "carries": carries, "heroes": heroes,
            "commanders": commanders, "sources": sources, "patch": list(patch), "note": note, "before": before,
            "was": was}


COMPS = [
    comp("S", "6 SPECTRE + Mage + Stargazer", [("SPECTRE", 6), ("Mage", None), ("Stargazer", None)], ["Valentina"],
         ["Valentina", "Alpha", "Atlas", "Mathilda", "Hilda", "Yi Sun-shin", "Lucy", "Pharsa", "Nana"], ["Brody"],
         ["loadoutgg S, urutan pertama (kartu SPECTRE's Badge, Neon Zenith)",
          "in-game \"6 SPECTRE & 4 Mage\" (Kelvin), tersimpan di Lineup Saya milikmu",
          "in-game \"Mage & Stargazer\" 56.763 (Radjagogo), varian tanpa 6 SPECTRE"],
         [VALENTINA, BRODY], "Alpha (7 Gold) terbuka saat Hero SPECTRE 5 Gold, yaitu Valentina, naik ke ★2."),
    comp("S", "6 SPECTRE + Starbelle", [("SPECTRE", 6), ("Starbelle", 4)], ["Valentina"],
         ["Valentina", "Alpha", "Atlas", "Hilda", "Mathilda", "Yi Sun-shin", "Edith", "Lolita", "Cici", "Miya"], ["Alice"],
         ["loadoutgg S (kartu Alice's Power, SPECTRE's Badge)"], [VALENTINA, LIGHTSTICK, LOLITA]),
    comp("S", "6 Titan + 4 Mage", [("Titan", 6), ("Mage", 4)], ["Pharsa"],
         ["Pharsa", "Argus", "Valentina", "Balmond", "Sora", "Bruno", "Helcurt", "Grock"], ["Brody", "Zilong"],
         ["in-game \"Titan & Mage\" 1.573.314, paling populer (Jake Plays Magic Chess; carry Pharsa ★3, tank Argus ★3; "
          "commander ALL)",
          "loadoutgg A \"6 Titan 4 SPECTRE\" (Brody) dan \"6 Titan Deadeye Bruno\" (Zilong)",
          "in-game \"Lineup Berfokus pada 6 Titan\" 48.342 (Jetskayy)"],
         [BALMOND, VALENTINA, ARGUS, SORA, TITAN, BALMOND_3],
         "Nerf Balmond (20/11, 26/11) dan atribut Titan-nya tidak mengenai inti versi in-game (carry Pharsa, tank Argus); "
         "Argus ★3 dan Sora ★3 justru naik 26/11."),
    comp("S", "6 FAIRY TAIL + 4 Swiftblade / Mage / Weapons Master",
         [("FAIRY TAIL", 6), ("Swiftblade", 4), ("Mage", 4), ("Weapons Master", 4)], ["Gray", "Lucy", "Erza"],
         ["Natsu", "Gray", "Lucy", "Erza", "Juvia", "Wendy", "Fanny", "Ling", "Kimmy", "Karina", "Valentina", "Pharsa",
          "Argus", "Leomord"], ["Karina", "Guinevere"],
         ["in-game \"6 FAIRY TAIL & 4 Swiftblade\" 822.718 (Amri; carry Gray ★3, tank Natsu ★2)",
          "in-game \"6 FAIRY TAIL & 4 Mage\" 643.185 (B.CO; carry Lucy ★3, tank Natsu ★3)",
          "kitakuji #2 FAIRY TAIL + Weapons Master (carry Erza ★3 dengan Argus dan Leomord; commander Karina)",
          "loadoutgg A \"6 FAIRY TAIL\" (carry Natsu; Guinevere)"],
         [GRAY, ERZA, SWIFT, KIMMY_3, KARINA, ARGUS],
         "Pasangan 4 mengikuti carry ★3 yang didapat: Gray → Swiftblade, Lucy → Mage, Erza → Weapons Master. "
         "kitakuji: waspadai lawan dengan banyak Deadeye."),
    comp("S", "Dawnbringer: 6 Stargazer + 6 Dawnbringer / ultra 10 Dawnbringer", [("Dawnbringer", 6), ("Stargazer", 6)],
         ["Eudora", "Valentina"],
         ["Eudora", "Terizla", "Nana", "Yu Zhong", "Valir", "Mathilda", "Karina", "Selena", "Ling", "Valentina", "Angela",
          "Lapu-Lapu"], ["Aamon", "Zilong", "Brody", "Harley"],
         ["in-game \"6 Stargazer & 6 Dawnbringer\" 640.951 (GO1 MCGG; carry Eudora ★3, tank Terizla ★2)",
          "loadoutgg S \"10 Dawnbringer Ultra\" (carry Valentina; Aamon)",
          "loadoutgg A \"Dawnbringer Swiftblade Karina\" (Zilong) dan \"Dawnbringer Titan\" (Brody)",
          "kitakuji #4 Terizla + Thamuz, transisi ke 6 Defender + Dawnbringer (Harley)"],
         [DAWN, YU_ZHONG, DAWN_46, EUDORA, YU_ZHONG_3, KARINA],
         "Ultra 10 butuh Magic Crystal Dawnbringer dan kini memberi Shield 500% Max HP. Patch 26/11 menaikkan "
         "4/6 Dawnbringer dan carry Eudora ★3."),
    comp("A", "6 Frostrider + 4 Weapons Master", [("Frostrider", 6), ("Weapons Master", 4)], ["Leomord"],
         ["Leomord", "Kupa", "Barbiel", "Popol", "Irithel", "Thamuz", "Argus", "Harley", "Bane"], ["Lukas"],
         ["loadoutgg S \"Frostrider Weapons Master Leomord\" (Lukas)",
          "in-game \"6 Frostrider & 4 Weapon Master\" 628.427 (officialmjgaming; carry Leomord ★3, tank Argus ★3)"],
         [FROST_SIX, FROST_HP, BARBIEL, LUKAS, POPOL_2, BANE, ARGUS],
         "Efek patch campuran: serangan 6 Frostrider naik, tetapi HP warisan, Barbiel, dan commander utamanya turun "
         "(20/11); 26/11 menurunkan Popol dan Bane, menaikkan tank Argus ★3. Carry Leomord tidak berubah.",
         before="S"),
    comp("A", "Dragonslayer + SPECTRE", [("Dragonslayer", 6), ("SPECTRE", 6)], ["Ling", "Kimmy", "Valentina"],
         ["Valentina", "Kimmy", "Ling", "Atlas", "Alpha", "Mathilda", "Yi Sun-shin", "Natsu", "Moskov"], ["Lukas", "Dyrroth"],
         ["kitakuji #1 (carry Ling, Kimmy, Valentina; commander Lukas)",
          "loadoutgg A \"6 SPECTRE Dragonslayer\" (Lukas; kartu Neon Zenith)",
          "loadoutgg A \"6 Dragonslayer Bruiser Kimmy\" (Dyrroth)"],
         [KIMMY, VALENTINA, LUKAS, KIMMY_3],
         "Tiap pertandingan 1 hero 1 Gold dan 1 hero 5 Gold acak ikut menjadi Dragonslayer; paling enak bila Valentina "
         "yang terpilih (menyalakan Dragonslayer dan SPECTRE sekaligus)."),
    comp("B", "Titan + Swiftblade (Balmond)", [("Titan", None), ("Swiftblade", None)], ["Balmond"],
         ["Balmond", "Ling", "Fanny", "Argus", "Gray", "Valentina", "Thamuz"], ["Aamon"],
         ["loadoutgg S \"Titan Swiftblade Balmond\" (Aamon)"], [BALMOND, BALMOND_3, TITAN, SWIFT, ARGUS],
         "Carry-nya Balmond, dinerf 20/11 lalu lagi 26/11 (Batas Mana ★3 120 → 170, atribut Titan); buff Swiftblade "
         "tidak menutupinya.", before="S", was="A"),
    comp("A", "Stargazer + Mistbender / Dauntless (Nana)", [("Stargazer", 6), ("Mistbender", 3), ("Dauntless", None)],
         ["Nana"], ["Nana", "Uranus", "Aldous", "Eudora", "Valir", "Juvia", "Lapu-Lapu", "Balmond", "Popol"],
         ["Lunox", "Cyclops"],
         ["loadoutgg A \"Stargazer Dauntless Mistbender Nana\" (Lunox)",
          "loadoutgg A \"Dragonslayer Dauntless Stargazer\" (carry Popol; Cyclops)",
          "in-game \"6 Stargazer & 3 Mistbender\" 108.653 (ShineJonZoie)",
          "kitakuji #5 Dauntless + Stargazer, \"opsi aman\""], [NANA, EUDORA, BALMOND_3, POPOL_2]),
    comp("A", "Ultra 10 Starbelle", [("Starbelle", 10)], ["Valentina"],
         ["Valentina", "Alpha", "Balmond", "Karina", "Miya"], ["Vexana"],
         ["loadoutgg S \"10 Starbelle Ultra\" (carry Valentina; Vexana)"], [VEXANA, LIGHTSTICK, KARINA, BALMOND_3],
         "Jalan ke 10 Starbelle mengandalkan hadiah Go Go Box tambahan Vexana, yang kini dibatasi.", before="S"),
    comp("C", "Popol & Kupa Frostrider + Phasewarper (4-4-3-3)", [("Frostrider", 4), ("Defender", 4), ("Phasewarper", 3)],
         ["Popol"], ["Popol", "Kupa", "Leomord", "Barbiel", "Kadita", "Harley", "Thamuz", "Melissa"], ["Vexana"],
         ["loadoutgg S \"Popol Kupa Frostrider (4-4-3-3)\" (Vexana; kartu Kalea's Power)",
          "in-game \"Frostrider & Phasewarper\" 367.733 (Radjagogo; carry Popol ★2, tank Leomord ★3)",
          "in-game \"4 Frostrider, 4 Defender, & 3 Phasewarper\" 70.299 (Jetskayy) dan \"4 Frostrider & 3 Phasewarper\" "
          "54.847 (Paduka GoGo)"],
         [POPOL, FROST_LOW, FROST_HP, BARBIEL, VEXANA, POPOL_2, MELISSA],
         "Hampir semua bagiannya dinerf 20/11, dan carry Popol dinerf lagi 26/11. Lineup tersimpanmu Defender 4 + "
         "Frostrider 4 + Phasewarper 3 termasuk di sini.", before="S", was="B"),
    comp("B", "Reroll Irithel (Zilong low-roll)", [("Bruiser", None), ("Frostrider", None), ("Deadeye", None)], ["Irithel"],
         ["Irithel", "Kupa", "Aldous", "Masha", "Yu Zhong", "Miya", "Natsu"], ["Zilong"],
         ["loadoutgg S \"Zilong Irithel Kupa (low-roll)\" (Zilong)",
          "kitakuji #3 reroll Irithel ★3: Irithel menunggangi Kupa agar ikut efek Bruiser"],
         [FROST_LOW, FROST_HP, YU_ZHONG, YU_ZHONG_3], "Menekan HP lawan di awal, perlu transisi menjelang akhir (kitakuji).",
         before="S"),
    comp("B", "6 Bruiser (Popol & Kupa / Melissa)", [("Bruiser", 6), ("Phasewarper", None)], ["Popol", "Melissa"],
         ["Popol", "Kupa", "Yu Zhong", "Masha", "Aldous", "Jawhead", "Natsu", "Melissa", "Gatotkaca", "Leomord"],
         ["Lylia", "Yu Zhong"],
         ["loadoutgg A \"6 Bruiser Popol Kupa\" (Lylia) dan \"6 Bruiser Melissa\" (Yu Zhong)",
          "in-game \"6 Bruiser & 3 Phasewarper\" 47.310 (Paduka GoGo)"],
         [POPOL, YU_ZHONG, POPOL_2, MELISSA, YU_ZHONG_3],
         "26/11: varian Melissa naik (★3 DMG Area dan ATK Speed), varian Popol turun lagi; tetap B.", before="A"),
    comp("B", "Echomancer + Weapons Master / ultra 10 Echomancer (Thamuz)", [("Echomancer", 6), ("Weapons Master", 6)],
         ["Thamuz"], ["Thamuz", "Argus", "Leomord", "Erza", "Johnson", "Selena", "Sora", "Lapu-Lapu"], ["Cyclops", "Vexana"],
         ["in-game \"6 Echomancer & 6 Weapon Master\" 266.154 (Bass; carry Thamuz ★2), kamu menyimpannya",
          "loadoutgg A \"Echomancer into Popol Weapons Master\" (carry Popol; Cyclops, kartu Cyclops's Power)",
          "loadoutgg B \"10 Echomancer Ultra\" (carry Thamuz; Vexana)"],
         [POPOL, VEXANA, ARGUS, ERZA, SORA, POPOL_2],
         "Nerf Popol mengenai varian loadoutgg (carry Popol), bukan versi in-game (carry Thamuz). 26/11 menaikkan Argus, "
         "Erza, dan Sora di comp ini."),
    comp("B", "Echomancer + Starbelle (Thamuz)", [("Echomancer", None), ("Starbelle", None)], ["Thamuz"],
         ["Thamuz", "Lolita", "Fanny", "Cici", "Vale", "Sora"], ["Lukas"],
         ["loadoutgg B \"6 Echomancer Starbelle\" (Lukas)"], [LUKAS, LIGHTSTICK, LOLITA, SORA],
         "Paling dekat dengan resep terbaikmu di S7 (Fanny + Starbelle 6 + Echomancer)."),
    comp("B", "6 Dragonslayer + Swiftblade (Ling)", [("Dragonslayer", 6), ("Swiftblade", None)], ["Ling"],
         ["Ling", "Popol", "Gray", "Fanny", "Karina", "Harley", "Eudora", "Kupa"], ["Aurora"],
         ["loadoutgg B \"6 Dragonslayer Swiftblade\" (Aurora)"], [SWIFT, KARINA, EUDORA, POPOL_2],
         "Buff Swiftblade 26/11 tidak menaikkannya di atas tier sumber (loadoutgg B)."),
    comp("A", "6 Defender low-roll (Melissa)", [("Defender", 6)], ["Melissa"], ["Melissa", "Hylos", "Edith", "Barbiel"],
         ["Angela"], ["loadoutgg A \"6 Defender (low-roll)\" (Angela)"], [BARBIEL, MELISSA],
         "Barbiel dinerf 20/11 (A → B), tetapi carry Melissa ★3 dibuff besar 26/11, jadi kembali ke tier sumber.", was="B"),
    comp("C", "3 Phasewarper (Thamuz, Kadita)", [("Phasewarper", 3)], ["Thamuz"],
         ["Thamuz", "Kadita", "Harley", "Popol", "Johnson"], ["Cyclops"],
         ["loadoutgg C \"3 Phasewarper Thamuz Kadita\" (Cyclops)"], [POPOL, POPOL_2]),
]

# Tier commander sumber, nama seperti di data (sumber menulis "Popol and Kupa"). Dicek lagi 28 Nov: belum berubah.
MCGGDB = {
    "S": ["Alice", "Fanny", "Harley", "Lukas"],
    "A": ["Aamon", "Brody", "Chou", "Dyrroth", "Franco", "Freya", "Kalea", "Lancelot", "Ling", "Lunox", "Luo Yi", "Minotaur",
          "Miya", "Moskov", "Nana", "Paquito", "Popol & Kupa", "Vale", "Valir", "Vexana", "Zilong"],
    "B": ["Alucard", "Angela", "Aurora", "Cyclops", "Diggie", "Johnson", "Kagura", "Karina", "Layla", "Lylia", "Ruby",
          "Yu Zhong"],
    "C": ["Guinevere", "Gusion", "Wanwan"],
}
LOADOUTGG = {
    "S": ["Fanny", "Freya", "Kalea", "Lukas", "Nana", "Vexana", "Yu Zhong", "Zilong"],
    "A": ["Alice", "Alucard", "Angela", "Brody", "Chou", "Dyrroth", "Harley", "Johnson", "Kagura", "Karina", "Lancelot",
          "Layla", "Lunox", "Luo Yi", "Minotaur", "Odette", "Paquito", "Ruby", "Valir", "Wanwan"],
    "B": ["Aamon", "Aurora", "Diggie", "Franco", "Guinevere", "Gusion", "Ling", "Lylia", "Moskov", "Popol & Kupa", "Vale"],
    "C": ["Cyclops", "Miya"],
}
CMD_PATCH = {"Brody": [BRODY], "Lukas": [LUKAS], "Vexana": [VEXANA], "Kagura": [KAGURA], "Ling": [LING],
             "Kalea": [KALEA], "Guinevere": [GUINEVERE], "Odette": [ODETTE]}

FOR_YOU = [
    "Commander terbaikmu di S7, <b>Fanny</b> (30 pertandingan, juara 11, rata-rata peringkat 3,6), dinilai S oleh kedua "
    "sumber S8 dan tidak tersentuh patch 20/11 maupun 26/11.",
    "Resep terbaikmu di S7, Fanny + Starbelle 6 + Echomancer (juara 8 dari 17 papan), paling dekat dengan comp B "
    "Echomancer + Starbelle. Bila ingin tetap memakai hero Starbelle, comp S <b>6 SPECTRE + Starbelle</b> lebih kuat "
    "(Lolita ★3 naik 26/11); Fanny sebagai commander bisa dipasang di comp mana pun.",
    "Lineup tersimpanmu Defender 4 + Frostrider 4 + Phasewarper 3 (+ Shadeweaver) memakai Popol dan Barbiel, yang dinerf "
    "20/11 bersama pewarisan 4 Frostrider; Popol dinerf lagi 26/11, jadi comp ini kini C. Lineup tersimpan lain, "
    "6 SPECTRE & 4 Mage (Kelvin), termasuk comp S.",
    "Lineup favoritmu di S7, Aamon + Dauntless 6 + Stargazer 4 + Mistbender 3 (Nana ★3), sejalan dengan comp A "
    "Stargazer + Mistbender / Dauntless; jangkauan skill Nana diperbaiki 20/11, Eudora ★3 naik 26/11.",
]

TIPS = [
    "<b>Wheel of Fate</b> (9 efek aktif) mengubah babak Go Go Card tiap pertandingan. <b>Crystal Legend</b> (putaran 1 "
    "hanya Kartu Badge Sinergi) dan <b>Synergy Awakening</b> (putaran 2 hanya kartu peningkatan Sinergi) membantu comp "
    "ultra 10; <b>Hero Reinforcement</b> (hero 3, 4, lalu 5 Gold acak setelah tiap pemilihan) membantu comp yang butuh "
    "carry 5 Gold.",
    "Sejak S8 Kartu Power adalah Go Go Card emas dan tidak dijamin muncul, karena itu loadoutgg menaikkan commander yang "
    "tetap menghasilkan tanpa Kartu Power: Kalea, Lukas, Nana. Pengecualian: efek <b>Commander's Power</b> membuat putaran 1 "
    "hanya berisi Kartu Power, dan slot pertamanya selalu Kartu Power commander sendiri (terbukti di rekaman 22 Nov).",
    "<b>Tycoon</b> (semua kartu finansial emas) dan <b>Gold Galore</b> (semua kartu emas) mempercepat ekonomi; <b>Early "
    "Reinforcement</b> memajukan Go Go Card ke Babak I-2, I-3, I-4. <b>Fate Sync</b> memberi semua pemain kartu yang sama: "
    "hindari berebut Magic Crystal yang sama (saran kitakuji).",
    "Patch 20/11 menaikkan Valentina ★2, Gray ★3, Kimmy ★3, Yu Zhong, 10 Dawnbringer, serangan 6 Frostrider, dan Brody, "
    "serta memperbaiki Nana dan Lightstick; yang turun Balmond, Popol, Barbiel, 2/4 Frostrider, HP warisan Frostrider, "
    "Lukas, dan Vexana.",
    "Patch 26/11 menaikkan ★3 hero 4 Gold (Melissa, Eudora, Kimmy, Argus, Lolita, Yu Zhong, Sora), Karina, Erza, "
    "4/6 Dawnbringer, Swiftblade, Kagura, dan Ling; yang turun Balmond (★3 dan atribut Titan), Popol, Bane, Kalea, dan "
    "Guinevere. Panel Bane di pertandingan 27 Nov pagi masih memakai nilai lama, jadi waktu berlakunya belum pasti.",
    "Data pertandinganmu di S8 (23 laporan MATCH 16–27 Nov, hampir semuanya sebelum patch 26/11 berlaku): dari 20 "
    "pertandingan dengan layar hasil kamu juara 13 kali, peringkat 2 lima kali, lalu peringkat 4 dan 7 sekali. Papan "
    "Dawnbringer 5–6 juara 4 dari 4; papan SPECTRE 5–7 juara 4 kali dan peringkat 2 tiga kali. Di 132 papan berperingkat "
    "pemain lain, Titan >= 4 hero ada di 28% papan peringkat 1–4 vs 12% papan 5–8 (Balmond belum kena nerf 26/11), "
    "sedangkan SPECTRE hanya 6% vs 17%. Sampel kecil, bukan win rate.",
]

SOURCES = [
    ("loadoutgg: Best Comps & Lineups (November 2026)", "https://loadoutgg.com/magic-chess-gogo/teams/",
     "25 comp bertanda RANKED S8 atau LOW-ROLL, S sampai C. Dibuka 25 Nov 2026 dan dicek lagi 28 Nov: belum berubah,"
     "belum memuat Penyesuaian 20/11 dan 26/11."),
    ("loadoutgg: Commander Tier List (November 2026)", "https://loadoutgg.com/magic-chess-gogo/commanders/",
     "41 commander S8. Halamannya menulis \"tiers updated 27 Sep 2026\" padahal isinya sudah S8 (Odette baru, perubahan "
     "15 Nov). Vexana diletakkan pertama karena hadiah Go Go Box tambahan di setiap tahap, yang dibatasi patch 20/11. "
     "Dicek lagi 28 Nov: belum berubah."),
    ("mcggdb: Commander tier list S8", "https://mcggdb.com/commanders/",
     "\"Our take\" untuk ranked Legend ke atas, dari angka commander dan pilihan pro; bukan win rate. Odette tidak dinilai. "
     "Dicek lagi 28 Nov: belum berubah."),
    ("kitakuji: Sinergi Magic Chess Terkuat (Update Season 8)",
     "https://kitakuji.id/blog/sinergi-magic-chess-terkuat-dan-update-terbaru/",
     "18 Nov 2026, lima combo meta awal ranked Mythic, sebelum patch 20/11. Ada klaim yang tidak cocok dengan data game: "
     "\"tidak ada commander baru\", padahal Odette baru di S8 (40 → 41 commander)."),
    ("In-game: Rekomendasi Lineup", "",
     "Rekaman ponsel 20 Nov 09:33, sebelum patch 20/11. Semua lineup bernilai S; angka = popularitas (ikon api), bukan "
     "win rate. Hero dikenali dari ikon (mc_vision.py); tanda C/T di layar = carry/tank."),
]


def combined(grades, arrows=None):
    """Tier gabungan commander dari tier sumber (S/A/B/C) dan efek patch (satu panah atau daftar panah UP/DOWN/None);
    None bila tak ada sumber.

    S 4, A 3, B 2, C 1, dirata-rata, ±0,5 untuk tiap buff/nerf (panah None = catatan, tidak dihitung). S butuh skor
    >= 3,5, paling tidak satu sumber S, dan tidak ada sumber di bawah A; A >= 2,75; B >= 1,75; sisanya C."""
    if not grades:
        return None
    arrows = arrows if isinstance(arrows, (list, tuple)) else [arrows]
    score = sum(VALUE[g] for g in grades) / len(grades) + sum({UP: 0.5, DOWN: -0.5}.get(a, 0) for a in arrows)
    if score >= 3.5 and "S" in grades and min(VALUE[g] for g in grades) >= VALUE["A"]:
        return "S"
    return "A" if score >= 2.75 else "B" if score >= 1.75 else "C"


def commander_grades(d):
    """Semua commander di data season dengan tier sumber, efek patch, tier gabungan, dan tier sebelum patch 26/11
    ("prev"); urut S → C lalu nama."""
    by_mcggdb = {n: t for t, names in MCGGDB.items() for n in names}
    by_loadout = {n: t for t, names in LOADOUTGG.items() for n in names}
    out = []
    for c in d["commanders"]:
        n, patch = c["name"], CMD_PATCH.get(c["name"], [])
        grades = [g for g in (by_mcggdb.get(n), by_loadout.get(n)) if g]
        out.append({"name": n, "icon": c.get("icon"), "mcggdb": by_mcggdb.get(n), "loadoutgg": by_loadout.get(n),
                    "patch": patch, "tier": combined(grades, [a for a, _, _ in patch]),
                    "prev": combined(grades, [a for a, _, p in patch if p != P2611])})
    return sorted(out, key=lambda g: (ORDER.index(g["tier"]) if g["tier"] else len(ORDER), g["name"]))


def unknown_names(d):
    """Nama hero/sinergi/commander di tier list yang tidak ada di data season (salah ketik, atau data berubah)."""
    heroes = {h["name"] for h in d["heroes"]}
    synergies = {s["name"] for s in d["synergies"]}
    commanders = {c["name"] for c in d["commanders"]}
    missing = set()
    for c in COMPS:
        missing |= {n for n, _ in c["synergies"] if n not in synergies}
        missing |= {h for h in c["heroes"] + c["carries"] if h not in heroes}
        missing |= {m for m in c["commanders"] if m not in commanders}
    for tiers in (MCGGDB, LOADOUTGG):
        missing |= {m for names in tiers.values() for m in names if m not in commanders}
    missing |= {m for m in CMD_PATCH if m not in commanders}
    return sorted(missing)


def tally(tiers):
    return ", ".join(f"{t} {tiers.count(t)}" for t in ORDER)


def md_text(text):
    return text.replace("<b>", "**").replace("</b>", "**")


def render(d):
    """(html, md lines) halaman tier list."""
    heroes = {h["name"]: h for h in d["heroes"]}
    syn_icon = {s["name"]: s.get("icon") for s in d["synergies"]}
    cmd_icon = {c["name"]: c.get("icon") for c in d["commanders"]}
    grades = commander_grades(d)
    title = f"Tier List Season {d['season']} — {d.get('info', {}).get('name', '')}"

    def hero_chip(name, carry=False):
        cost = heroes[name]["cost"]
        return chip(name, heroes[name].get("icon"), f"c{cost} on" if carry else f"c{cost}",
                    f"{cost} Gold" + (", carry" if carry else ""))

    def syn_chip(name, count):
        return chip(f"{count} {name}" if count else name, syn_icon[name])

    def cmd_chip(name):
        return chip(name, cmd_icon[name])

    def arrow(a):
        if a is None:
            return '<span class="muted">·</span>'
        return f'<span class="{"buff" if a == UP else "nerf"}">{a}</span>'

    def effect(e, html=True):
        a, t, p = e
        return f"{arrow(a)} {esc(t)} ({p})" if html else f"{a or '·'} {t} ({p})"

    def notes(c, html=True):
        fx = [effect(e, html) for e in c["patch"]]
        return fx + ([esc(c["note"]) if html else c["note"]] if c["note"] else [])

    s_comps = [c for c in COMPS if c["tier"] == "S"]
    dropped = [c for c in COMPS if c["before"]]
    s_cmds = [g for g in grades if g["tier"] == "S"]
    moved_comps = [c for c in COMPS if c["was"]]
    moved_cmds = [g for g in grades if g["prev"] != g["tier"]]
    cmd_moves = "; ".join(f"{g['name']} {''.join(a for a, _, _ in g['patch'] if a)} ({g['tier']})"
                          for g in grades if any(a for a, _, _ in g["patch"]))
    intro = ("Bukan win rate. Gabungan sumber web (dibuka 25 Nov 2026, dicek lagi 28 Nov) dan daftar <b>Rekomendasi "
             "Lineup</b> in-game (rekaman 20 Nov), lalu dikoreksi dengan <b>Penyesuaian Keseimbangan 20/11 dan 26/11</b> "
             "yang belum diperhitungkan sumber-sumber itu.")
    rule = ("Gabungan = rata-rata dua sumber (S 4, A 3, B 2, C 1; satu sumber bila hanya satu yang menilai), ±0,5 untuk "
            "tiap buff/nerf commander di patch 20/11 dan 26/11 (catatan server tanpa panah tidak dihitung). S butuh "
            "rata-rata ≥ 3,5, paling tidak satu sumber S, dan tidak ada sumber di bawah A; A ≥ 2,75; B ≥ 1,75; sisanya C.")
    comp_rule = ("Tier comp = penilaian dari sumbernya (kolom Sumber). Koreksi patch: carry atau inti yang dinerf turun "
                 "satu tingkat dari tier sumber (\"X di sumber\"); buff hanya memulihkan sampai tier sumber, tidak "
                 "melampauinya.")
    comp_heads = ["Tier", "Comp", "Hero", "Commander", "Sumber", "Patch dan catatan"]
    cmd_heads = ["Gabungan", "Commander", "mcggdb", "loadoutgg", "Patch"]

    # ---- HTML
    s_items = [esc(c["name"]) + "<br>" + "".join(hero_chip(h, True) for h in c["carries"]) for c in s_comps]
    move_items = ([f"{esc(c['name'])}: {c['was']} → {c['tier']}" for c in moved_comps]
                  + [f"{cmd_chip(g['name'])} {g['prev']} → {g['tier']}" for g in moved_cmds])
    summary = ('<section><h2>Ringkasan</h2><div class="grid3">'
               f'<div class="box good"><h4>Comp S</h4>{ul(s_items)}</div>'
               f'<div class="box good"><h4>Commander S</h4>{"".join(cmd_chip(g["name"]) for g in s_cmds)}'
               f'<p class="small muted">Patch: {esc(cmd_moves)}</p></div>'
               f'<div class="box bad"><h4>Berubah karena patch 26/11</h4>{ul(move_items)}</div>'
               "</div></section>")
    rows = []
    for c in COMPS:
        before = f'<br><span class="small muted">{c["before"]} di sumber</span>' if c["before"] else ""
        was = f'<br><span class="small muted">{c["was"]} sebelum 26/11</span>' if c["was"] else ""
        rows.append([f"<b>{c['tier']}</b>{before}{was}",
                     f"<b>{esc(c['name'])}</b><br>" + "".join(syn_chip(n, k) for n, k in c["synergies"]),
                     "".join(hero_chip(h, h in c["carries"]) for h in c["heroes"]),
                     "".join(cmd_chip(m) for m in c["commanders"]),
                     ul([esc(s) for s in c["sources"]], "small"),
                     ul(notes(c), "small")])
    crows = [[f"<b>{g['tier']}</b>" + (f'<br><span class="small muted">{g["prev"]} sebelum 26/11</span>'
                                       if g["prev"] != g["tier"] else ""),
              cmd_chip(g["name"]), g["mcggdb"] or "–", g["loadoutgg"] or "–",
              "<br>".join(effect(e) for e in g["patch"])] for g in grades]
    sources = [f"<b>{esc(t)}</b>" + (f' — <a href="{esc(u)}">{esc(u)}</a>' if u else "")
               + f'<br><span class="small muted">{esc(n)}</span>' for t, u, n in SOURCES]
    legend = (f"{arrow(UP)} buff, {arrow(DOWN)} nerf, {arrow(None)} catatan; label di belakang efek = asal perubahan "
              "(20/11, 26/11, atau server tanpa patch note). Hero bergaris hijau = carry; warna bingkai hero = harga (abu 1, "
              "hijau 2, biru 3, ungu 4, emas 5, merah muda 7 Gold).")
    body = "".join([
        f'<section><p>{intro}</p><p class="small muted">{legend}</p></section>',
        summary,
        f"<section><h2>Untukmu</h2>{ul(FOR_YOU)}</section>",
        f'<section><h2>Comp</h2><p class="small muted">{esc(comp_rule)}</p>{table(comp_heads, rows)}</section>',
        f'<section><h2>Commander</h2><p class="small muted">{esc(rule)}</p>{table(cmd_heads, crows)}</section>',
        f"<section><h2>Cara membaca season ini</h2>{ul(TIPS)}</section>",
        f"<section><h2>Sumber</h2>{ul(sources)}</section>",
    ])
    html_text = page(title, body, stamp(d))

    # ---- Markdown
    md_rows = [[c["tier"] + (f" ({c['before']} di sumber)" if c["before"] else "")
                + (f" ({c['was']} sebelum 26/11)" if c["was"] else ""),
                f"**{c['name']}** (" + ", ".join(f"{k} {n}" if k else n for n, k in c["synergies"]) + ")",
                ", ".join(f"**{h}**" if h in c["carries"] else h for h in c["heroes"]),
                ", ".join(c["commanders"]), "; ".join(c["sources"]), "; ".join(notes(c, html=False))] for c in COMPS]
    cmd_md = [[g["tier"] + (f" ({g['prev']} sebelum 26/11)" if g["prev"] != g["tier"] else ""), g["name"],
               g["mcggdb"] or "–", g["loadoutgg"] or "–", "; ".join(effect(e, html=False) for e in g["patch"])]
              for g in grades]
    md = [f"# {title}", "", f"_{stamp(d)}_", "", md_text(intro), "",
          "↑ buff, ↓ nerf, · catatan; label di belakang efek = asal perubahan (20/11, 26/11, server). Hero tebal = carry.", "",
          "## Ringkasan", "",
          "- **Comp S:** " + "; ".join(f"{c['name']} (carry {', '.join(c['carries'])})" for c in s_comps),
          "- **Commander S:** " + ", ".join(g["name"] for g in s_cmds) + f" (patch: {cmd_moves})",
          "- **Berubah karena patch 26/11:** " + "; ".join([f"{c['name']} {c['was']} → {c['tier']}" for c in moved_comps]
                                                         + [f"{g['name']} {g['prev']} → {g['tier']}" for g in moved_cmds]),
          "- **Di bawah tier sumber karena patch:** " + "; ".join(f"{c['name']} {c['before']} → {c['tier']}"
                                                                for c in dropped),
          "", "## Untukmu", ""]
    md += [f"- {md_text(x)}" for x in FOR_YOU]
    md += ["", "## Comp", "", f"_{comp_rule}_", ""] + md_table(comp_heads, md_rows)
    md += ["", "## Commander", "", f"_{rule}_", ""] + md_table(cmd_heads, cmd_md)
    md += ["", "## Cara membaca season ini", ""] + [f"- {md_text(t)}" for t in TIPS]
    md += ["", "## Sumber", ""] + [f"- **{t}**" + (f" — {u}" if u else "") + f": {n}" for t, u, n in SOURCES]
    return html_text, md


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    d, folder = load_season(SEASON)
    missing = unknown_names(d)
    if missing:
        sys.exit("Nama tidak ada di data S8, perbaiki tier_list.py: " + ", ".join(missing))
    html_text, md = render(d)
    out_html, _ = write_report(folder, "TIER_LIST_S8", html_text, md)
    grades = commander_grades(d)
    print(f"{len(COMPS)} comp ({tally([c['tier'] for c in COMPS])}), {len(grades)} commander "
          f"({tally([g['tier'] for g in grades])}) -> {out_html} (+ .md)")


if __name__ == "__main__":
    main()
