"""Buat ANALISIS_LINEUP_S7.html dan .md (analisis 5 lineup) dari S7.json, dengan ikon hero/sinergi/kartu/item dari game.

Pemakaian: python analisis_lineup.py   (jalankan setelah mc_data.py; menulis ke data/1.3.24.344.1/)
Angka sinergi, kartu, commander, dan stat hero dibaca dari S7.json; teks analisis (LINEUPS, MECHANICS, ...) ditulis tangan.
Untuk versi game baru: ganti OUT ke folder data versi itu dan periksa ulang teks analisisnya.
"""
import html
import json
from pathlib import Path

OUT = Path(r"F:\Magic Chess\patch-tracker\data\1.3.24.344.1")
d = json.load(open(OUT / "S7.json", encoding="utf-8"))
H = {h["name"]: h for h in d["heroes"]}
S = {s["name"]: s for s in d["synergies"]}
C = {c["name"]: c for c in d["commanders"]}
K = {c["name"]: c for c in d["cards"]}
E = {}
for e in d["equipment"]:
    for lv in e["levels"]:
        if lv["name"] not in E or e["active"]:
            E[lv["name"]] = lv.get("icon") or e["icon"]


def num(n):
    return f"{n:,.0f}".replace(",", ".")


def dec(n):
    return f"{n:.1f}".replace(".", ",")


def stat(hero, star, key, server=True):
    """Hero stat; server=True takes the server patch value (stats_server) when there is one."""
    value = (H[hero].get("stats_server") or {}).get(str(star), {}).get(key) if server else None
    return int(float(value or H[hero]["stats"][str(star)][key]))


def change(hero, star, key):
    return f"{stat(hero, star, key, server=False)} → {stat(hero, star, key)}"


def atk(hero, star):
    return max(stat(hero, star, "Physical ATK"), stat(hero, star, "Magic ATK"))


def tier(syn, count):
    reached = [t for t in S[syn]["tiers"] if t["count"] <= count]
    nxt = [t["count"] for t in S[syn]["tiers"] if t["count"] > count]
    return (reached[-1] if reached else None), (nxt[0] if nxt else None)


def counts(heroes, crystals):
    out = {}
    for h in heroes:
        for s in H[h]["synergies"]:
            out[s] = out.get(s, 0) + 1
    for s, n in crystals.items():
        out[s] = out.get(s, 0) + n
    return sorted(((s, n) for s, n in out.items() if tier(s, n)[0]), key=lambda x: (-tier(x[0], x[1])[0]["count"], x[0]))


def tier10(syn):
    return next(t["effect"] for t in S[syn]["tiers"] if t["count"] >= 10)


# ------------------------------------------------------------------ builds (user's own builds, numbers from S7.json)
O_HP, O_ATK = stat("Odette", 2, "HP"), atk("Odette", 2)
L_HP, L_ATK = stat("Lancelot", 2, "HP"), atk("Lancelot", 2)
ESS_ATK, ESS_HP = round(L_ATK * 0.4), round(L_HP * 0.4)
O_PRE = (O_ATK + ESS_ATK) * (1 + 0.25 + 0.10 + 0.10 + 0.50)  # Lightstick, Winter Crown, Essence Core, Mage 2
FAN = O_PRE * 0.5
O_HP_T = (O_HP + ESS_HP) * 1.2
STARBELLE = ["Fanny", "Lolita", "Edith", "Miya", "Zhuxin"]
LA_ATK = L_ATK * (1 + 0.20 + 0.30 + 0.28)  # Justice Sword, Kagura's Power, Purest Power II
LA_HP = L_HP * (1 + 0.20 + 0.50)           # Nether Claw (+20% Max HP, Arcane +50% HP)
LA_SHIELD, LA_HEAL = LA_HP * 1.25, LA_HP * 0.5

BUILDS = {
    "luoyi": {
        "title": "Build kamu: Odette ★2 sebagai Fan",
        "items": ["Winter Crown", "Lightstick", "Essence Core"],
        "rows": [
            ("Essence Core (dari Lancelot ★2)", f"+40% ATK Lancelot (+{ESS_ATK}), +40% HP (+{num(ESS_HP)}), item Essence Core +10% ATK & +10% HP. "
             "Role Phasewarper: +10% DMG, dan saat HP pertama kali < 40% pindah ke tempat aman & pulih 35% HP"),
            ("Lightstick", "+25% Hybrid ATK; Odette jadi Fan. Saat pertarungan mulai, Fan memberi bonus 50% (Starbelle 6) dari Hybrid ATK-nya ke dirinya dan semua hero Starbelle"),
            ("Winter Crown", "+10% ATK, +10% HP; saat HP < 25% atau terkena DMG mematikan: beku dan pulih 10% HP"),
            ("Mage 2", "+50% Magic ATK (40% hero Mage + 10% semua rekan)"),
            ("Astro 4 (Sovereign)", "+60% DMG dan 10% Lifesteal (Odette pegang item terbanyak)"),
        ],
        "result": [
            f"Odette ★2 dasar: ATK {O_ATK}, HP {num(O_HP)}. Perkiraan ATK sebelum bonus Fan ±{num(O_PRE)}, setelah bonus Fan ±{num(O_PRE + FAN)} "
            f"(Odette ★3 tanpa item: {atk('Odette', 3)}).",
            "Bonus Fan sekitar +" + num(FAN) + " Hybrid ATK ke setiap hero Starbelle: "
            + ", ".join(f"{n} ★2 {atk(n, 2)} → ±{num(atk(n, 2) + FAN)}" for n in STARBELLE) + ".",
            f"HP Odette ±{num(O_HP_T)} + Shield skill {num(1300)} + 2 kesempatan selamat (beku Winter Crown, pindah tempat Phasewarper).",
        ],
    },
    "kagura": {
        "title": "Build kamu: Lancelot ★2 dengan 3 item Kishin Arcane",
        "items": ["Guren Chakram", "Justice Sword", "Nether Claw"],
        "rows": [
            ("Guren Chakram (Arcane)", "+55% DMG, 20% Lifesteal, 20% Spell Vamp"),
            ("Justice Sword (Arcane)", "+20% Hybrid ATK; tiap 5 detik Rain of Swords memberi True DMG 20% ATK ke area dengan lawan terbanyak"),
            ("Nether Claw (Arcane)", "+20% Max HP, +50% HP; stun lawan di depan 2 detik"),
            ("Kishin 6 / Phasewarper 3", "+36 Hybrid DEF / +15% DMG, dan pulih 50% HP saat HP pertama kali < 40%"),
            ("Kagura", "Shield Umbrella Lv2: Shield 125% Max HP saat HP < 50%. Kagura's Power: +30% Hybrid ATK, +20% Lifesteal"),
            ("Purest Power Ⅱ", "+28% Hybrid ATK untuk hero Kishin (Kishin aktif di jumlah 6)"),
        ],
        "result": [
            f"Lancelot ★2 dasar: ATK {L_ATK}, HP {num(L_HP)}. Perkiraan ATK ±{num(LA_ATK)} dan bonus DMG +70%.",
            f"HP ±{num(LA_HP)} + Shield ±{num(LA_SHIELD)} + heal ±{num(LA_HEAL)} = HP efektif ±{num(LA_HP + LA_SHIELD + LA_HEAL)}, "
            "plus Lifesteal 40% dan Spell Vamp 20%.",
            f"Pembanding: hero 4 Gold ★3 punya HP sekitar {num(stat('Lolita', 3, 'HP'))}; "
            f"Lancelot ★3 {num(stat('Lancelot', 3, 'HP'))}, tapi butuh seluruh 9 stok.",
        ],
    },
}

# ------------------------------------------------------------------ server balance patch 20/10 (server_patch.json, applied in S7.json)
P2010 = next(p for p in d["server_patches"] if p["patch"] == "20/10")
BADANG = H["Badang"]["skills"][0]
B_OLD, B_NEW = (next(a for a in BADANG[k] if a["label"] == "Peningkatan DMG")["values"] for k in ("attributes", "attributes_server"))
B_HIT = atk("Badang", 2) * int(B_OLD[1].rstrip("%")) / 100  # one ★2 counter-punch
LUNOX_PCT = (stat("Lunox", 2, "Magic ATK") / stat("Lunox", 2, "Magic ATK", server=False) - 1) * 100
PATCH_IMPACT = [  # (hero or commander, chip label, lineup ids, box class, title, text)
    ("Badang", "carry ★2", ["kalea"], "bad", "Nerf terbesar untuk lineup-mu",
     f"Peluang meninju balik saat menerima DMG 50% → 25% (semua bintang). Di ★2 satu tinju balik = {B_OLD[1]} ATK ≈ {num(B_HIT)} Physical DMG, "
     f"jadi rata-rata DMG balasan per serangan yang diterima turun dari ±{num(B_HIT * 0.5)} ke ±{num(B_HIT * 0.25)}. HP, DEF, dan skill aktif "
     f"Fist Crack (8 Fist Wind × 50% ATK) tidak berubah: Badang ★2 tetap tebal, tapi damage-nya turun. Pengali ★3 naik {B_OLD[2]} → {B_NEW[2]}, "
     "tapi ★3 butuh seluruh 9 stok hero 5 Gold."),
    ("Lunox", "pengisi", ["aamon", "kagura"], "bad", "Nerf kecil",
     f"Hybrid ATK ★2 {change('Lunox', 2, 'Magic ATK')} (−{dec(abs(LUNOX_PCT))}%), jadi 3 Chaos Assault (500% Total Magic ATK di ★2) ikut turun "
     f"±{dec(abs(LUNOX_PCT))}%. Di kedua lineup Lunox hanya pengisi (Stargazer di Aamon, Kishin di Kagura); jumlah sinerginya tetap."),
    ("Irithel", "pengisi", ["luoyi", "minotaur"], "", "Buff, hanya di ★3",
     f"Batas Mana ★3 {change('Irithel', 3, 'Batas Mana')}: skill Strafe lebih cepat keluar, tapi hanya di ★3. Di kedua lineup Irithel "
     "pengisi Astro ★1/★2 tanpa item, jadi tidak berpengaruh."),
    ("Vexana", "Commander", [], "good", "Buff commander, bukan hero",
     "Hero Vexana di lineup Minotaur tidak berubah. Yang di-buff commander Vexana: 13 Gold di babak Go Go Box pertama → 10 Gold di tiap "
     "3 babak Go Go Box pertama (total 30 Gold, +17 Gold), di samping hadiah ekstra I Want All of Them! di 3 Go Go Box itu. Jadi Vexana kini "
     "commander ekonomi awal yang kuat. Bonus ini aktif sejak Commander bintang 1 (skill Lv 1 I Want All of Them!); rekaman 31 Okt: "
     "+10 Gold di I-4, II-6, dan III-6."),
]
KIND_LABEL = {"Hero": "hero", "Commander": "commander", "Skill hero": "skill hero", "Sinergi": "sinergi", "Go Go Card": "Go Go Card"}
OTHER_2010 = list(dict.fromkeys(
    f"{c['target'].split(' / ')[0]} ({KIND_LABEL.get(c['kind'], c['kind'])})" for c in P2010["changes"]
    if c["target"].split(" / ")[0] not in {"Badang", "Lunox", "Irithel", "Vexana"}))


# ------------------------------------------------------------------ server balance patch 28/10
P2810 = next(p for p in d["server_patches"] if p["patch"] == "28/10")


def changes_2810(name):
    return "; ".join(c["text"] for c in P2810["changes"] if c["target"].split(" / ")[0] == name) + "."


PATCH_IMPACT_2810 = [
    ("Yin", "pengisi", ["kalea"], "good", "Buff kecil untuk lineup Kalea",
     f"Hybrid ATK ★2 {change('Yin', 2, 'Magic ATK')} dan ★3 {change('Yin', 3, 'Magic ATK')} (+10%). Yin hanya pengisi Dragon Altar di lineup "
     "ini, jadi jaraknya ke lineup lain tidak berubah."),
    ("Lukas", "Commander", [], "good", "Buff commander ekonomi", changes_2810("Lukas") + " Gold dari altar naik, Makhluk Suci ★2 sedikit melemah."),
    ("Dyrroth", "Commander", [], "good", "Buff commander", changes_2810("Dyrroth")),
    ("Lunox", "Commander", [], "bad", "Nerf commander",
     changes_2810("Lunox") + " Angka 3 Hero di file game ada di Power of Order (3 Hero acak dari Sinergi yang diberikan skill-nya), bukan di "
     "Power of Chaos; belum dicek in-game. Lineup SPECTRE + Starbelle dengan commander Lunox ikut melemah."),
]
PATCH_LEAD_2810 = ("Patch note server 28 Oktober (dicatat di server_patch.json; angka di bawah dibaca dari S7.json). Peringkat tidak berubah: "
                   "5 lineup ini tidak memakai commander Lukas, Dyrroth, atau Lunox, dan hanya lineup Kalea yang memakai Yin.")
OTHER_2810 = list(dict.fromkeys(
    f"{c['target']} ({KIND_LABEL.get(c['kind'], c['kind'])})" for c in P2810["changes"]
    if c["target"].split(" / ")[0] not in {x[0] for x in PATCH_IMPACT_2810}))

# ------------------------------------------------------------------ the five lineups, in the order of the no-ultra ranking
LINEUPS = [
    {
        "id": "aamon", "rank": 1, "name": "Dauntless 6 + Stargazer 4 + Mistbender 3", "commander": "Aamon", "label": "tanpa label tier",
        "board": [(0, 0, "Karina", ""), (0, 1, "Lolita", "T ★★"), (0, 2, "Alice", ""), (0, 3, "Franco", ""), (0, 4, "Hilda", ""),
                  (0, 5, "Aldous", ""), (0, 6, "Uranus", ""), (2, 2, "Mathilda", ""), (2, 3, "Nana", "C ★★★"), (2, 4, "Lunox", "")],
        "crystals": {"Dauntless": 1},
        "cards": ["Aamon's Power", "Payday", "Jump the Gun+"],
        "summary": "Paling kuat tanpa ultra: sinergi utamanya memang tidak punya tingkat 10, dan kekuatannya terus bertambah lewat Spirit Sand.",
        "points": [
            "Dauntless 6 (tingkat maksimal): semua rekan Shield 20% Max HP, hero Dauntless Shield tambahan 85% Max HP.",
            "Stargazer 4: hero Stargazer memulihkan 16 Mana per detik, jadi Nana, Lunox, Mathilda, dan Karina sering memakai skill.",
            "Mistbender 3: Aldous, Uranus, dan Nana menghasilkan 2 Spirit Sand setiap memakai skill. Di Toko Spirit Sand, Sand bisa dibelikan buff "
            "ATK/HP permanen seluruh tim (8/16/24 Sand → +1%/+3%/+5% ATK), Nana (60 Sand), atau Mirror Device (80 Sand).",
            "Aamon: 1 Mirror Device di awal dan hingga 2 lagi dari Shard ★2 (+12 Gold tiap Mirror Device). Kartu Power: 4 Gold setiap hero naik ★2 (maks 20).",
            f"Karena itu Nana ★3 realistis: skill 2000% + 1100% ATK Magic DMG, HP {num(stat('Nana', 3, 'HP'))}.",
        ],
        "weak": [
            "Butuh level 10 (10 hero). Versi level 9 ada di bawah.",
            "Lemah di awal game; kekuatannya baru terasa setelah Sand dan Mirror Device terkumpul.",
            "Karina, Hilda, dan Mathilda sering diperebutkan (Karina dan Mathilda dinerf di Patch 7.2). Nana 5 Gold hanya 9 stok.",
            f"Lunox ★2 dinerf kecil di Penyesuaian 20/10 (Hybrid ATK {change('Lunox', 2, 'Magic ATK')}); perannya sebagai pengisi Stargazer tetap.",
        ],
        "tips": [
            "Pasang crystal Pilihan ke hero Dauntless (pilihan Dauntless pasti muncul) dan jangan diganti: crystal Pilihan berikutnya akan menggantikan yang lama.",
            "Di Toko Spirit Sand, item ATK 24 Sand paling efisien (+5% untuk 24 Sand). Angka ini belum dicek ke screenshot toko.",
            "Simpan Mirror Device untuk Nana.",
        ],
        "variant": {"title": "Versi level 9 (9 hero, cukup 1 crystal Pilihan)",
                    "heroes": ["Karina", "Lolita", "Alice", "Franco", "Hilda", "Uranus", "Aldous", "Nana", "Lunox"],
                    "crystals": {"Dauntless": 1},
                    "note": "Mathilda dikeluarkan, jadi Stargazer turun ke 3 (tingkat 2). Kalau dapat kartu Stargazer's Badge/Blessing, "
                            "pasang crystal Stargazer-nya ke hero mana pun untuk kembali ke Stargazer 4."},
        "ultra": "Tidak perlu: Dauntless (maks 6) dan Mistbender (maks 3) sudah di tingkat tertingginya. "
                 "Stargazer bisa ke 6 dengan 2 crystal Stargazer dari kartu Badge/Blessing.",
        "need": "1 crystal (Dauntless) dari crystal Pilihan. Di level 9, Stargazer 4 butuh 1 crystal lagi dari kartu (acak).",
    },
    {
        "id": "luoyi", "rank": 2, "name": "Starbelle 6 + Astro 4", "commander": "Luo Yi", "label": "S",
        "board": [(0, 1, "Fanny", ""), (0, 2, "Hilda", ""), (0, 3, "Edith", ""), (0, 4, "Karina", ""), (0, 5, "Lolita", "T ★★★"),
                  (1, 3, "Odette", "C (kamu: ★2 Fan)"), (2, 1, "Miya", ""), (2, 3, "Irithel", ""), (2, 5, "Zhuxin", "")],
        "crystals": {"Starbelle": 1},
        "cards": ["Luo Yi's Power", "Trust Fund", "Astro Power's Badge", "Legacy of Valor", "Starbelle's Badge", "Fateful Dice", "Payday",
                  "Quaking Blow", "Prime Selection", "Rock Solid", "Uncertain Fortune", "Healing Fountain"],
        "summary": "Damage tim tertinggi di mid game: setiap tambahan ATK Odette ikut dibagi ke seluruh hero Starbelle lewat Lightstick.",
        "points": [
            "Lightstick didapat otomatis dari sinergi Starbelle. Bonusnya dihitung dari Hybrid ATK Fan saat pertarungan dimulai.",
            "Essence Core dari Lancelot ★2 (skill Luo Yi) menaikkan ATK dan HP Odette sekaligus memberi efek bertahan Phasewarper.",
            "Astro 4 menjadikan Odette Sovereign (+60% DMG). Mage 2 menambah +50% Magic ATK.",
            "Jalur kartunya mengambil Astro Power's Badge (crystal Astro + Martis), Starbelle's Badge (crystal Starbelle + Miya), Legacy of Valor, "
            "dan Prime Selection: semuanya sumber crystal di luar crystal Pilihan.",
        ],
        "weak": [
            "Butuh dua hero 5 Gold ★2 (Odette, dan Lancelot untuk Essence Core): masing-masing 3 dari 9 stok, peluang toko 14% di level 9.",
            "Tanpa build Fan, Starbelle 6 sendiri hanya memberi 35 DEF.",
            "Shield skill Odette ★2 hanya 1.300; damage naga berbasis % Max HP (Dragoncaller) tetap berbahaya.",
        ],
        "tips": [
            "Pakaikan item cadangan ke Lancelot sebelum diubah: Essence Core juga mewarisi 40% atribut dasar equipment hero itu.",
            "Lancelot ★2 sudah pilihan terbaik untuk Essence Core (ATK ★2 tertinggi, 365, sama dengan Thamuz). Kalau Lancelot hanya ★1, Essence Core tetap memberi +96 ATK.",
            "Selesaikan item Odette sebelum babak dimulai: bonus Fan dihitung saat pertarungan mulai.",
        ],
        "ultra": "Starbelle 10 (tambah Cici; 6 hero + crystal Pilihan + 3 crystal Starbelle dari kartu Badge/Blessing, Legacy of Valor, "
                 "atau creep IV-3): " + tier10("Starbelle"),
        "need": "1 crystal (Starbelle 6): crystal Pilihan, atau crystal dari Starbelle's Badge.",
    },
    {
        "id": "kagura", "rank": 3, "name": "Kishin 6 + Phasewarper 3 + Shadeweaver 3", "commander": "Kagura", "label": "S (\"Pance kekebalan tubuh\")",
        "board": [(0, 4, "Hylos", ""), (0, 5, "Franco", ""), (0, 6, "Lancelot", "C (kamu: ★2)"), (2, 1, "Lunox", ""), (2, 2, "Angela", ""),
                  (2, 3, "Clint", ""), (2, 4, "Karrie", ""), (2, 5, "Kadita", ""), (2, 6, "Melissa", "")],
        "crystals": {"Kishin": 1},
        "cards": ["Kagura's Power", "Purest Power Ⅱ", "Uncertain Fortune"],
        "summary": "Paling konsisten: dua sinergi sudah maksimal tanpa crystal, dan carry-nya punya HP efektif lebih dari 30.000.",
        "points": [
            "Phasewarper 3 dan Shadeweaver 3 sudah tingkat maksimal hanya dengan 3 hero; Kadita dihitung di keduanya.",
            "Item Kishin naik tingkat dengan membeli duplikat hero Kishin di toko (maksimal Arcane). Ini soal Gold, bukan hoki.",
            "Shadeweaver: angin memberi +50% ATK Speed ke rekan di kolom yang ditempati hero Shadeweaver, dan membuat lawan airborne 1 detik.",
        ],
        "weak": [
            "Semua bergantung pada satu carry. Lancelot ★2 butuh 3 dari 9 stok.",
            "Dua hero 5 Gold (Lancelot, Melissa) mahal.",
            f"Lunox ★2 dinerf kecil di Penyesuaian 20/10 (Hybrid ATK {change('Lunox', 2, 'Magic ATK')}); untuk Kishin 6 jumlah hero yang penting, bukan damage Lunox.",
        ],
        "tips": [
            "Ambil kartu Kishin Unbound kalau muncul: ketiga item jadi versi Diperkuat (Lifesteal/Spell Vamp 30%, ATK +40%, HP +40%) + 5 refresh gratis.",
            "Taruh Lancelot di kolom yang sama dengan hero Shadeweaver (di layout ini: satu kolom dengan Melissa).",
            "Pakai Shield Umbrella dan Kagura's Power ke Lancelot.",
        ],
        "ultra": "Kishin 10 (tambah Dyrroth; 6 hero + crystal Pilihan + 3 crystal Kishin dari Kishin's Blessing/Badge, Legacy of Valor, "
                 "atau creep IV-3): item naik ke Supreme. "
                 "Guren: +150% DMG & +65% HP; Justice Sword: Giant Sword True DMG 500% ATK ke semua lawan di detik ke-3; Nether Claw: +200% HP & stun semua lawan 3 detik.",
        "need": "1 crystal (Kishin 6) dari crystal Pilihan, atau tambah Dyrroth tanpa crystal.",
    },
    {
        "id": "minotaur", "rank": 4, "name": "Astro 6 + Mage 4", "commander": "Minotaur", "label": "S",
        "board": [(0, 1, "Karina", ""), (0, 2, "Atlas", ""), (0, 3, "Odette", "C ★★"), (0, 4, "Hilda", "T ★★"), (0, 5, "Minotaur", ""),
                  (2, 0, "Vexana", ""), (2, 1, "Zhuxin", ""), (2, 5, "Irithel", ""), (2, 6, "Gord", "")],
        "crystals": {"Astro Power": 1, "Stargazer": 1, "Starbelle": 1},
        "cards": ["Minotaur's Power", "Golden Era+", "Divine Execution", "Critical Spellcraft", "Starbelle's Badge", "Stargazer's Badge",
                  "Astro Judgment", "Stargazer's Blessing", "Starbelle's Blessing"],
        "summary": "Stabil dan kuat, tapi Odette hanya menguatkan dirinya sendiri, dan Astro paling sering diperebutkan.",
        "points": [
            "Odette mendapat bonus dua kali: Sovereign Astro 6 (+30% & +90% DMG, 15% Lifesteal) dan Mage 4 (+80% Magic ATK).",
            "Astro Judgment: setiap lawan yang terkena skill Sovereign mendapat True DMG 160% Hybrid ATK (cooldown 3 detik per lawan). Sangat cocok dengan tarian AoE Odette.",
            "Minotaur memperkuat 3 equipment dan memberi 3 Gold untuk setiap penguatan.",
            "Jalur kartunya mengambil Starbelle's Badge/Blessing dan Stargazer's Badge/Blessing: 4 crystal biasa (plus Miya, Luo Yi, Ice Queen Wand, "
            "Peti Equipment). Dari situlah Stargazer 2 dan Starbelle 2, karena crystal Pilihan sudah dipakai untuk Astro 6.",
        ],
        "weak": [
            "Empat sinergi pengisi (Defender 2, Enchanted Tales 2, Stargazer 2, Starbelle 2). Stargazer 2 dan Starbelle 2 hanya aktif kalau kartu Badge/Blessing-nya muncul.",
            "Irithel tanpa item dan tanpa sinergi Marksman hanya menambah jumlah Astro.",
            "Astro diperebutkan (Hilda ada di 4 dari 8 lineup pada pertandingan 20 Oktober), dan lemah melawan Dragoncaller.",
        ],
        "tips": [
            "Variasi Mage 6 + Astro 6: ganti Irithel dan Atlas dengan Vale dan Kadita, lalu pasang crystal Pilihan Astro di Karina atau Hilda "
            "dan 1 crystal Astro dari Astro Power's Badge/Blessing.",
            "Pakai crystal Pilihan untuk Astro atau Mage, bukan Dauntless.",
            "Habiskan penguatan Minotaur lebih awal (setiap penguatan +3 Gold).",
        ],
        "ultra": "Astro 10 (tambah Martis; 6 hero + crystal Pilihan + 3 crystal Astro dari Astro Power's Badge/Blessing, Legacy of Valor, "
                 "atau creep IV-3): " + tier10("Astro Power"),
        "need": "1 crystal (Astro 6) dari crystal Pilihan; Stargazer 2 dan Starbelle 2 butuh 2 crystal lagi dari kartu Badge/Blessing.",
    },
    {
        "id": "kalea", "rank": 5, "name": "Dragon Altar 6 + Dragoncaller 4", "commander": "Kalea", "label": "S",
        "board": [(0, 0, "Zilong", ""), (0, 1, "Yin", ""), (0, 2, "Yi Sun-shin", ""), (0, 3, "Gusion", ""), (0, 4, "Badang", "C ★★"),
                  (0, 5, "Baxia", ""), (0, 6, "Suyou", "T ★★★"), (2, 0, "Luo Yi", ""), (2, 6, "Eudora", "")],
        "crystals": {"Dragon Altar": 1, "Defender": 1},
        "cards": ["Kalea's Power", "Valor's Embrace", "Healing Fountain"],
        "summary": "Paling lemah tanpa ultra, tapi paling berbahaya kalau berhasil ultra Dragoncaller (seperti juara pertandingan 20 Oktober). "
                   "Penyesuaian 20/10 melemahkan carry-nya (Badang ★2), jadi jarak ke lineup lain makin lebar.",
        "points": [
            "Dragon Altar 6: semua petak jadi petak khusus; semua rekan +16% Hybrid ATK & HP, hero Dragon Altar 3 kali lipat (+48%).",
            "Dragoncaller 4: 3 naga × 10% Max HP lawan di area 3×3, hero Dragoncaller +20% DMG.",
            "Kalea untuk ekonomi: Brankas Harta 2–3 kali (hingga 19 Gold atau 9 Gold + hero 5 Gold); Kartu Power 21–35 Gold.",
        ],
        "weak": [
            "Lima sinergi pengisi bernilai kecil. Dragon Altar 6 memakai crystal Pilihan; Defender 2 butuh crystal kedua dari kartu (acak).",
            "Suyou ★3 butuh 9 dari 14 stok. Valor's Embrace (Shield 8% saat rekan tereliminasi) lemah.",
            f"Penyesuaian 20/10: peluang tinju balik Badang 50% → 25%, jadi DMG balasan Badang ★2 tinggal separuh (±{num(B_HIT * 0.25)} per serangan "
            "yang diterima). Pengali ★3-nya naik, tapi Badang ★3 butuh seluruh 9 stok hero 5 Gold.",
        ],
        "tips": [
            "Tentukan satu jalur ultra sejak Fase II. Crystal Pilihan hanya satu yang aktif, jadi ultra butuh 3 crystal dari kartu Badge/Blessing, "
            "Legacy of Valor, atau creep IV-3.",
            "Jalur Dragoncaller paling mudah: tambah Balmond (2 Gold) dan Clint (3 Gold) untuk Dragoncaller 6, lalu crystal.",
            "Setelah 20/10 (saran, belum dites): taruh item damage di Zilong (Dragoncaller + Weapon Master; tiap 3 Basic ATK menyerang 3× "
            "80% ATK dan memulihkan HP) dan beri Badang item bertahan. Badang ★2 tetap tebal di depan, tapi tidak lagi layak jadi pemegang "
            "item damage utama.",
        ],
        "ultra": "Dragoncaller 10 (6 hero + crystal Pilihan + 3 crystal Dragoncaller dari kartu/creep): " + tier10("Dragoncaller")
                 + " — atau Dragon Altar 10 (tambah Wanwan): " + tier10("Dragon Altar"),
        "need": "1 crystal (Dragon Altar 6) dari crystal Pilihan; Defender 2 butuh 1 crystal lagi dari kartu (acak).",
    },
]
NEED_SHORT = {
    "aamon": "1 (crystal Pilihan)",
    "luoyi": "1 (crystal Pilihan atau Starbelle's Badge)",
    "kagura": "1 (crystal Pilihan) atau Dyrroth",
    "minotaur": "1 (crystal Pilihan); +2 dari kartu untuk sinergi pengisi",
    "kalea": "1 (crystal Pilihan); +1 dari kartu untuk Defender 2",
}
RANKING = [  # (lineup id, konsistensi, level, puncak)
    ("aamon", "Sedang", "10 (di level 9: Stargazer 2)", "Sangat tinggi tanpa ultra"),
    ("luoyi", "Sedang–tinggi (2 hero 5 Gold ★2)", "9", "Tinggi; Starbelle 10 menaikkan bonus Fan ke 100%"),
    ("kagura", "Tinggi", "9", "Sangat tinggi di Kishin 10 (item Supreme)"),
    ("minotaur", "Tinggi", "9", "Tinggi; Astro 10 memberi 2 Sovereign"),
    ("kalea", "Sedang", "9", "Sangat tinggi di Dragoncaller 10"),
]
BY_ID = {lu["id"]: lu for lu in LINEUPS}
MECHANICS = [
    "Magic Crystal Pilihan: 1 crystal didapat saat masuk Fase Ⅱ, Ⅲ, dan Ⅳ, tetapi hanya 1 yang bisa aktif. Memakai crystal Pilihan berikutnya "
    "akan menggantikan yang lama, jadi crystal Pilihan hanya menambah +1 sinergi. (Aturan ini dari pengalaman bermain; tidak tertulis di tabel data.)",
    "Saat dipasang, 2 dari 3 pilihan crystal Pilihan selalu sinergi Faction dan Role hero itu sendiri; pilihan ke-3 acak dan tidak termasuk sinergi "
    "kecil (maksimal ≤ 4). Crystal Pilihan berikutnya berguna untuk pindah sinergi kalau rencana berubah.",
    "Crystal sinergi milik hero itu sendiri tetap menambah +1. Terbukti di pertandinganmu 20 Oktober: panel Astro 6/10 dengan 5 hero Astro + crystal Astro di Irithel.",
    "Crystal biasa (satu per hero, bisa banyak) hanya dari sumber acak: kartu Badge/Blessing sinergi, Legacy of Valor, Prime Selection, "
    "crystal Faction dari creep IV-3 (Patch 7.2), Peti Magic Crystal, Blessing commander Lunox, dan Go Go Box mulai akhir Fase Ⅱ "
    "(MCRoundRandomEquip_S7: 1–2 crystal sinergi acak di II-6, 2 di III-6, 3–4 mulai IV-6; terlihat di pertandingan 21 Oktober).",
    "Ultra 10 untuk faksi berisi 6 hero = 6 hero + 1 crystal Pilihan + 3 crystal biasa. Ketiga crystal biasa itu butuh hoki; karena itu jalur "
    "kartu rekomendasi game banyak mengambil kartu Badge/Blessing.",
    "Hero ★3 butuh 9 salinan. Stok pool bersama per harga: " + ", ".join(f"{k} Gold = {v}" for k, v in d["info"]["pool_per_hero"].items() if k != "6")
    + ". Hero 5 Gold ★3 berarti mengambil seluruh stok, kecuali punya Mirror Device.",
    "Peluang toko di level 9: " + ", ".join(f"{g} Gold {p}%" for g, p in zip(range(1, 6), d["info"]["levels"][8]["shop_odds"])) + ".",
]
MATCH = [
    "Pertandingan 20 Oktober 2026 (ID 374683366623511459): kamu (CinCoeg) peringkat 2 dengan Astro 6 + Mage 4 (Minotaur), menyerah di IV-4.",
    "Juara (MANIAC, level 10) sudah mencapai Dragoncaller 10, lalu menjual banyak hero di akhir; layar hasil hanya mencatat 7 hero dan Dragoncaller 6.",
    "Dragoncaller 10: " + tier10("Dragoncaller") + " Damage dihitung dari Max HP, jadi Defender, Dauntless, dan tank tebal tidak membantu.",
    "Pelajaran: begitu lawan terlihat menuju ultra (cek panel X/10 dan crystal di papannya), lihat apakah ultra-mu sendiri masih mungkin. "
    "Waktu itu kamu Astro 6/10: masih butuh Martis (+1) dan 3 crystal Astro lagi. Karena crystal Pilihan hanya satu yang aktif, ketiganya harus "
    "dari kartu Astro Power's Badge/Blessing, Legacy of Valor, atau creep IV-3, jadi ultra Astro memang butuh hoki. Crystal Dauntless di Odette "
    "lebih berguna sebagai Astro.",
]
NOTES = [
    f"Sumber angka: S7.json versi game {d['game_version']}, Season {d['season']} \"{d['info']['name']}\", termasuk perubahan server "
    + " dan ".join(f"Patch {p['patch']}" for p in d["server_patches"]) + " (server_patch.json).",
    "Hero, sinergi, dan Go Go Card di screenshot Rekomendasi Lineup dikenali dengan mencocokkan potret ke ikon asli dari file game. Kartu "
    "Badge/Blessing di lineup Luo Yi dan Minotaur dikonfirmasi dari screenshot Rekomendasi Go Go Card.",
    "Aturan 1 crystal Pilihan aktif berasal dari pengalaman bermain; logikanya ada di kode client, bukan di tabel data.",
    "Angka build adalah perkiraan: semua bonus persen dianggap dijumlahkan dari ATK/HP dasar, karena urutan penumpukannya tidak tertulis di file game.",
    "File game tidak menyimpan win rate; peringkat ini teoretis dari angka game, ditambah pengalaman pertandingan 20 Oktober.",
    "Isi Toko Spirit Sand belum dicek ke screenshot toko.",
]


# ------------------------------------------------------------------ HTML
def e(t):
    return html.escape(str(t))


def img(src, cls="", alt="", title=None):
    t = f' title="{e(title)}"' if title else ""
    return f'<img src="{e(src)}" class="{cls}" alt="{e(alt)}" loading="lazy"{t}>' if src else ""


def hero_chip(name, marker=""):
    h = H[name]
    return (f'<span class="hero c{h["cost"]}" title="{e(", ".join(h["synergies"]))}">{img(h["icon"], "hi", name)}'
            f'<span><b>{e(name)}</b><small>{h["cost"]} Gold{(" · " + e(marker)) if marker else ""}</small></span></span>')


def board_html(lu):
    cells = {(r, c): (n, m) for r, c, n, m in lu["board"]}
    out = ['<div class="board" aria-label="Posisi papan">']
    for r in range(3):
        for c in range(7):
            if (r, c) in cells:
                n, m = cells[(r, c)]
                mark = f'<span class="mk">{e(m.split(" (")[0])}</span>' if m else ""
                out.append(f'<div class="cell c{H[n]["cost"]}" title="{e(n)}">{img(H[n]["icon"], "bi", n)}{mark}<span class="bn">{e(n)}</span></div>')
            else:
                out.append('<div class="cell empty"></div>')
    out.append("</div>")
    return "".join(out)


def syn_table_html(heroes, crystals):
    rows = []
    for s, n in counts(heroes, crystals):
        t, nxt = tier(s, n)
        cr = crystals.get(s, 0)
        crs = f" <small>(+{cr} crystal)</small>" if cr else ""
        nx = f" → {nxt}" if nxt else " (maks)"
        rows.append(f'<tr><td class="sn">{img(S[s]["icon"], "si", s)}<b>{e(s)}</b></td>'
                    f'<td class="num">{n}{crs}</td><td class="num">{t["count"]}{nx}</td><td>{e(t["effect"])}</td></tr>')
    return ('<div class="scroll"><table class="list"><tr><th>Sinergi</th><th>Jumlah</th><th>Tingkat aktif</th><th>Efek (data game)</th></tr>'
            + "".join(rows) + "</table></div>")


def cards_html(cards):
    out = []
    for i, n in enumerate(cards):
        if n:
            c = K[n]
            out.append(f'<figure class="gcard">{img(c["icon"], "ci", n, c["description"])}<figcaption>{e(n)}<small>{e(c["tier"])}</small></figcaption></figure>')
        else:
            out.append('<figure class="gcard"><div class="ci unknown">?</div><figcaption>Badge/Blessing<small>sinergi tak terbaca</small></figcaption></figure>')
        if i < len(cards) - 1:
            out.append('<span class="arrow">›</span>')
    return '<div class="cards">' + "".join(out) + "</div>"


def commander_html(name):
    c = C[name]
    skills = "".join(f'<li><b>Lv {s["from_level"]}+ {e(s["type"])}: {e(s["skill"]["name"])}</b> — {e(s["skill"].get("description_server") or s["skill"]["description"])}</li>'
                     for s in c["skills"])
    power = f'<li><b>Kartu Power:</b> {e(c["power_card"]["description"])}</li>' if c.get("power_card") else ""
    return (f'<div class="cmd">{img(c["icon"], "cmi", name)}<div><b>Commander {e(name)}</b> <span class="chip">{e(c["category"])}</span>'
            f'<ul class="tight">{skills}{power}</ul></div></div>')


def build_html(key):
    b = BUILDS[key]
    items = "".join(f'<span class="item">{img(E.get(n), "ii", n)}{e(n)}</span>' for n in b["items"])
    rows = "".join(f"<tr><td><b>{e(a)}</b></td><td>{e(bb)}</td></tr>" for a, bb in b["rows"])
    res = "".join(f"<li>{e(r)}</li>" for r in b["result"])
    return (f'<div class="build"><h4>{e(b["title"])}</h4><div class="items">{items}</div>'
            f'<div class="scroll"><table class="list"><tr><th>Sumber</th><th>Efek</th></tr>{rows}</table></div>'
            f'<p class="label">Perkiraan hasil</p><ul class="tight">{res}</ul></div>')


def ul(xs, cls="tight"):
    return f'<ul class="{cls}">' + "".join(f"<li>{e(x)}</li>" for x in xs) + "</ul>"


def lineup_html(lu):
    heroes = [b[2] for b in lu["board"]]
    hl = "".join(hero_chip(b[2], b[3]) for b in lu["board"])
    variant = ""
    if lu.get("variant"):
        v = lu["variant"]
        variant = (f'<h3>{e(v["title"])}</h3><div class="heroes">{"".join(hero_chip(n) for n in v["heroes"])}</div>'
                   f'<p class="muted">{e(v["note"])}</p>{syn_table_html(v["heroes"], v["crystals"])}')
    syn_badges = "".join(f'<span class="sb">{img(S[s]["icon"], "si", s)}<b>{n}</b></span>' for s, n in counts(heroes, lu["crystals"]))
    build = build_html(lu["id"]) if lu["id"] in BUILDS else ""
    return f"""
<section class="lineup" id="{lu['id']}">
  <h2><span class="rank">#{lu['rank']}</span> {e(lu['name'])} <small>({e(lu['commander'])} · label in-game: {e(lu['label'])})</small></h2>
  <div class="sbs">{syn_badges}</div>
  <p class="lead">{e(lu['summary'])}</p>
  <div class="two">
    <div>{board_html(lu)}<p class="muted small">C = carry, T = tank (target bintang dari layar Rekomendasi Lineup).</p></div>
    <div>{commander_html(lu['commander'])}</div>
  </div>
  <h3>Hero</h3><div class="heroes">{hl}</div>
  <h3>Sinergi aktif</h3>{syn_table_html(heroes, lu['crystals'])}
  <h3>Go Go Card</h3>{cards_html(lu['cards'])}
  {build}
  <div class="grid3">
    <div class="box good"><h4>Kenapa kuat</h4>{ul(lu['points'])}</div>
    <div class="box bad"><h4>Kelemahan</h4>{ul(lu['weak'])}</div>
    <div class="box tip"><h4>Tips</h4>{ul(lu['tips'])}</div>
  </div>
  {variant}
  <p><b>Crystal yang dibutuhkan (tanpa ultra):</b> {e(lu['need'])}</p>
  <p><b>Jalur ultra (opsional):</b> {e(lu['ultra'])}</p>
</section>"""


def short_need(lu):
    return NEED_SHORT[lu["id"]]


PATCH_LEAD = ("Patch note server 20 Oktober (dicatat di server_patch.json; angka di bawah dibaca dari S7.json). Peringkat tidak berubah: "
              "#1–#4 hanya kena nerf kecil Lunox atau tidak terdampak, sedangkan #5 (Kalea) makin tertinggal karena carry-nya dinerf.")


def impact_lineups(ids):
    return "Lineup: " + ", ".join(f"#{BY_ID[i]['rank']} {BY_ID[i]['commander']}" for i in ids) if ids else "Tidak dipakai di 5 lineup"


PATCH_SECTIONS = [("patch2010", "20/10", PATCH_LEAD, PATCH_IMPACT, OTHER_2010),
                  ("patch2810", "28/10", PATCH_LEAD_2810, PATCH_IMPACT_2810, OTHER_2810)]


def patch_html():
    out = []
    for section, patch, lead, impact, other in PATCH_SECTIONS:
        boxes = []
        for name, label, ids, cls, title, text in impact:
            chip = (f'<span class="hero">{img(C[name]["icon"], "hi", name)}<span><b>{e(name)}</b><small>Commander</small></span></span>'
                    if label == "Commander" else hero_chip(name, label))
            links = ", ".join(f'<a href="#{i}">#{BY_ID[i]["rank"]} {e(BY_ID[i]["commander"])}</a>' for i in ids)
            boxes.append(f'<div class="box {cls}"><h4>{e(title)}</h4><p>{chip}</p>'
                         f'<p class="small muted">{("Lineup: " + links) if ids else "Tidak dipakai di 5 lineup"}</p><p>{e(text)}</p></div>')
        out.append(f'<section id="{section}"><h2>Dampak Penyesuaian Keseimbangan {patch}</h2><p class="muted">{e(lead)}</p>'
                   f'<div class="grid3">{"".join(boxes)}</div>'
                   f'<p class="muted small">Tidak berdampak ke 5 lineup ini: {e(", ".join(other))}.</p></section>')
    return "".join(out)


def page_html():
    rank_rows = "".join(
        f'<tr><td class="num"><b>{BY_ID[i]["rank"]}</b></td><td><a href="#{i}">{e(BY_ID[i]["name"])}</a></td>'
        f'<td class="sn">{img(C[BY_ID[i]["commander"]]["icon"], "si round", BY_ID[i]["commander"])}{e(BY_ID[i]["commander"])}</td>'
        f'<td>{e(short_need(BY_ID[i]))}</td><td>{e(lvl)}</td><td>{e(kons)}</td><td>{e(peak)}</td></tr>'
        for i, kons, lvl, peak in RANKING)
    toc = "".join(f'<a href="#{lu["id"]}">#{lu["rank"]} {e(lu["commander"])}</a>' for lu in LINEUPS)
    body = "".join(lineup_html(lu) for lu in LINEUPS)
    match_heroes = "".join(hero_chip(n) for n in ["Zilong", "Gusion", "Badang", "Clint", "Eudora", "Balmond"])
    return TEMPLATE.replace("__BODY__", f"""
<header>
  <h1>Analisis 5 Lineup Magic Chess: Go Go — Season {d['season']} "{e(d['info']['name'])}"</h1>
  <p class="meta">Versi game {e(d['game_version'])} · dibuat 20 Oktober 2026, diperbarui 21 Oktober 2026 (Penyesuaian 20/10) dari data game (S7.json) · gambar hero, sinergi, kartu, dan item dari file game</p>
  <nav class="toc">{toc}<a href="#patch2010">Patch 20/10</a><a href="#patch2810">Patch 28/10</a><a href="#mekanik">Mekanik crystal</a><a href="#pertandingan">Pertandingan 20 Okt</a><a href="#catatan">Catatan</a></nav>
</header>
<main>
<section id="ringkasan">
  <h2>Kesimpulan</h2>
  <div class="grid3">
    <div class="box good"><h4>Terkuat tanpa ultra</h4><p>{hero_chip('Nana', 'carry')}</p><p><b>Aamon</b>: Dauntless 6 + Stargazer 4 + Mistbender 3. Sinerginya sudah maksimal tanpa ultra, dan tim terus menguat lewat Spirit Sand.</p></div>
    <div class="box tip"><h4>Damage tim tertinggi di mid game</h4><p>{hero_chip('Odette', 'Fan')}</p><p><b>Luo Yi</b>: Starbelle 6 dengan Odette ★2 sebagai Fan. Setiap hero Starbelle mendapat sekitar +{num(FAN)} ATK.</p></div>
    <div class="box"><h4>Paling konsisten</h4><p>{hero_chip('Lancelot', 'carry')}</p><p><b>Kagura</b>: Kishin 6 + Phasewarper 3 + Shadeweaver 3. Item Arcane didapat dengan Gold, bukan hoki.</p></div>
  </div>
  <h3>Peringkat tanpa ultra</h3>
  <div class="scroll"><table class="list"><tr><th>#</th><th>Lineup</th><th>Commander</th><th>Crystal wajib</th><th>Level</th><th>Konsistensi</th><th>Puncak (dengan ultra)</th></tr>{rank_rows}</table></div>
  <p class="muted">Selisih kekuatan #2 sampai #4 kecil; pilihannya lebih ditentukan hero yang sedang banyak diambil pemain lain. #3 (Kagura) tidak memakai Karina maupun Hilda, cocok saat lobby penuh pemain Astro. Penyesuaian <a href="#patch2010">20/10</a> dan <a href="#patch2810">28/10</a> tidak mengubah peringkat.</p>
</section>
{patch_html()}
<section id="mekanik"><h2>Mekanik penting: crystal, stok, dan peluang</h2>{ul(MECHANICS, "")}</section>
{body}
<section id="pertandingan"><h2>Pelajaran dari pertandingan 20 Oktober</h2>
  <div class="heroes">{match_heroes}</div>
  <p class="muted small">Hero Dragoncaller (lineup juara). Ikon sinergi: {img(S['Dragoncaller']['icon'], 'si', 'Dragoncaller')}Dragoncaller, {img(S['Astro Power']['icon'], 'si', 'Astro Power')}Astro Power.</p>
  {ul(MATCH, "")}
</section>
<section id="catatan"><h2>Catatan data dan asumsi</h2>{ul(NOTES, "")}</section>
</main>""")


TEMPLATE = """<!doctype html>
<html lang="id">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light dark">
<title>Analisis Lineup S7</title>
<style>
:root { --bg:#f5f6f8; --card:#fff; --text:#1c2230; --muted:#5d6879; --line:#e2e6ed; --accent:#3366e6; --chip:#eef1f6;
  --good:#2b9a61; --bad:#c2410c; --tip:#2a77cf; --c1:#7d8798; --c2:#2b9a61; --c3:#2a77cf; --c4:#8d55d9; --c5:#d48a12; --c7:#d93d72; }
@media (prefers-color-scheme: dark) { :root { --bg:#0e1117; --card:#161b24; --text:#e6ebf2; --muted:#98a3b4; --line:#283040;
  --accent:#7ea1ff; --chip:#212837; --good:#4cc38a; --bad:#ff8a5c; --tip:#6aa8ff; } }
* { box-sizing: border-box; }
body { margin:0; background:var(--bg); color:var(--text); font:15px/1.55 system-ui, "Segoe UI", Roboto, sans-serif; }
header, main { max-width: 1180px; margin: 0 auto; padding: 0 16px; }
header { padding-top: 22px; }
h1 { font-size: 24px; margin: 0 0 4px; } h2 { font-size: 20px; margin: 0 0 10px; } h3 { font-size: 16px; margin: 18px 0 8px; } h4 { margin: 0 0 6px; font-size: 15px; }
h2 small { font-weight: 400; color: var(--muted); font-size: 14px; }
.meta, .muted { color: var(--muted); } .small { font-size: 12.5px; }
.toc { display:flex; flex-wrap:wrap; gap:6px; margin:12px 0 0; position: sticky; top: 0; background: var(--bg); padding: 8px 0; z-index: 2; }
.toc a { border:1px solid var(--line); background:var(--card); border-radius:999px; padding:4px 12px; text-decoration:none; color:var(--text); font-size:13.5px; }
section { background:var(--card); border:1px solid var(--line); border-radius:14px; padding:18px; margin:16px 0; scroll-margin-top: 60px; }
.rank { display:inline-block; background:var(--accent); color:#fff; border-radius:8px; padding:0 8px; margin-right:4px; }
.lead { font-size: 16px; }
a { color: var(--accent); }
.two { display:grid; grid-template-columns: minmax(0, 560px) minmax(0, 1fr); gap:16px; align-items:start; }
@media (max-width: 860px) { .two { grid-template-columns: minmax(0, 1fr); } }
.grid3 { display:grid; gap:12px; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); margin-top: 14px; }
.box { border:1px solid var(--line); border-left:4px solid var(--accent); border-radius:10px; padding:10px 12px; }
.box p { margin: 6px 0; }
.box.good { border-left-color: var(--good); } .box.bad { border-left-color: var(--bad); } .box.tip { border-left-color: var(--tip); }
ul.tight { margin: 4px 0; padding-left: 18px; } ul.tight li { margin: 3px 0; }
.board { display:grid; grid-template-columns: repeat(7, minmax(0, 1fr)); gap:4px; background: var(--chip); padding:6px; border-radius:10px; max-width: 560px; }
.cell { aspect-ratio: 1; border-radius: 8px; position: relative; display:flex; flex-direction:column; align-items:center; justify-content:center; background: var(--card); border:2px solid var(--line); overflow:hidden; }
.cell.empty { background: transparent; border-style: dashed; opacity: .5; }
.cell .bi { width: 72%; aspect-ratio: 1; border-radius: 50%; object-fit: cover; }
.cell .bn { font-size: 10px; line-height: 1.1; text-align: center; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 100%; }
.cell .mk { position:absolute; top:2px; left:2px; font-size:9.5px; font-weight:700; background:#000b; color:#ffd54a; border-radius:4px; padding:0 3px; }
.c1 { border-color: var(--c1); } .c2 { border-color: var(--c2); } .c3 { border-color: var(--c3); } .c4 { border-color: var(--c4); } .c5 { border-color: var(--c5); } .c7 { border-color: var(--c7); }
.heroes { display:flex; flex-wrap:wrap; gap:8px; }
.hero { display:inline-flex; align-items:center; gap:6px; border:2px solid var(--line); border-radius:999px; padding:2px 10px 2px 2px; background: var(--chip); }
.hero .hi { width:34px; height:34px; border-radius:50%; object-fit:cover; }
.hero small { display:block; color: var(--muted); font-size: 11.5px; line-height: 1.1; }
.hero b { font-size: 13.5px; line-height: 1.1; }
.sbs { display:flex; flex-wrap:wrap; gap:6px; margin-bottom: 6px; }
.sb { display:inline-flex; align-items:center; background: var(--chip); border-radius: 999px; padding: 2px 10px 2px 2px; }
.si { width:26px; height:26px; vertical-align:middle; margin-right:6px; } .si.round { border-radius:50%; }
.list { width:100%; border-collapse:collapse; font-size:14px; }
.list th, .list td { text-align:left; vertical-align:top; padding:6px 8px; border-bottom:1px solid var(--line); }
.list .num { white-space:nowrap; } .list .sn { white-space:nowrap; }
.scroll { overflow-x:auto; }
.cards { display:flex; flex-wrap:wrap; align-items:center; gap:4px; }
.gcard { margin:0; width: 78px; text-align:center; font-size: 11.5px; }
.gcard .ci { width: 52px; height: 71px; border-radius: 6px; object-fit: cover; display:block; margin: 0 auto 3px; }
.gcard .unknown { display:flex; align-items:center; justify-content:center; background: var(--chip); border:1px dashed var(--line); font-size: 22px; color: var(--muted); }
.gcard small { display:block; color: var(--muted); }
.arrow { color: var(--muted); font-size: 18px; }
.cmd { display:flex; gap:10px; align-items:flex-start; }
.cmi { width:56px; height:56px; border-radius:50%; flex:none; }
.chip { display:inline-block; background: var(--chip); border-radius:999px; padding:0 8px; font-size:12px; }
.build { border:1px solid var(--line); border-radius: 10px; padding: 12px; margin-top: 14px; }
.items { display:flex; flex-wrap:wrap; gap:8px; margin-bottom: 8px; }
.item { display:inline-flex; align-items:center; gap:6px; background: var(--chip); border-radius: 8px; padding: 3px 10px 3px 3px; font-size: 13.5px; }
.ii { width: 32px; height: 32px; border-radius: 6px; }
.label { font-weight: 700; margin: 10px 0 2px; }
</style>
</head>
<body>__BODY__
</body>
</html>
"""


# ------------------------------------------------------------------ Markdown
def mimg(src, w=28, alt=""):
    return f'<img src="{src}" width="{w}" alt="{alt}">' if src else ""


def md_syn_table(heroes, crystals):
    lines = ["| Sinergi | Jumlah | Tingkat aktif | Efek (data game) |", "|---|---|---|---|"]
    for s, n in counts(heroes, crystals):
        t, nxt = tier(s, n)
        cr = crystals.get(s, 0)
        crs = f" (+{cr} crystal)" if cr else ""
        nx = f" → {nxt}" if nxt else " (maks)"
        lines.append(f"| {mimg(S[s]['icon'], 24, s)} **{s}** | {n}{crs} | {t['count']}{nx} | {t['effect']} |")
    return lines


def md_board(lu):
    cells = {(r, c): (n, m) for r, c, n, m in lu["board"]}
    lines = ["| " + " | ".join(f"K{c + 1}" for c in range(7)) + " |", "|" + "---|" * 7]
    for r in range(3):
        row = []
        for c in range(7):
            if (r, c) in cells:
                n, m = cells[(r, c)]
                mark = "<br>**" + m.split(" (")[0] + "**" if m else ""
                row.append(f"{mimg(H[n]['icon'], 40, n)}<br>{n}{mark}")
            else:
                row.append(" ")
        lines.append("| " + " | ".join(row) + " |")
    return lines


def md_lineup(lu):
    heroes = [b[2] for b in lu["board"]]
    c = C[lu["commander"]]
    badges = " ".join(f"{mimg(S[s]['icon'], 24, s)} {s} {n}" for s, n in counts(heroes, lu["crystals"]))
    out = [f"## #{lu['rank']} {lu['name']} — {lu['commander']}", "",
           f"*Label in-game: {lu['label']}.* {badges}", "",
           f"**{lu['summary']}**", "", "### Posisi papan", "", *md_board(lu), "", "_C = carry, T = tank (target bintang dari layar Rekomendasi Lineup)._", "",
           f"### Commander {mimg(c['icon'], 32, lu['commander'])} {lu['commander']} ({c['category']})", ""]
    out += [f"- **Lv {s['from_level']}+ {s['type']}: {s['skill']['name']}** — {(s['skill'].get('description_server') or s['skill']['description']).replace(chr(10), ' ')}"
            for s in c["skills"]]
    if c.get("power_card"):
        out.append(f"- **Kartu Power:** {c['power_card']['description'].replace(chr(10), ' ')}")
    out += ["", "### Hero", "", "| Hero | Harga | Sinergi | Peran |", "|---|---|---|---|"]
    out += [f"| {mimg(H[n]['icon'], 32, n)} **{n}** | {H[n]['cost']} Gold | {', '.join(H[n]['synergies'])} | {m} |" for _, _, n, m in lu["board"]]
    out += ["", "### Sinergi aktif", "", *md_syn_table(heroes, lu["crystals"]), "", "### Go Go Card", ""]
    out.append(" › ".join((f"{mimg(K[n]['icon'], 36, n)} {n}" if n else "Badge/Blessing (sinergi tak terbaca)") for n in lu["cards"]))
    out += [""] + [f"- **{n}** ({K[n]['tier']}): {K[n]['description'].replace(chr(10), ' ')}" for n in dict.fromkeys(x for x in lu["cards"] if x)]
    if lu["id"] in BUILDS:
        b = BUILDS[lu["id"]]
        out += ["", f"### {b['title']}", "", " ".join(f"{mimg(E.get(n), 32, n)} {n}" for n in b["items"]), "", "| Sumber | Efek |", "|---|---|"]
        out += [f"| **{a}** | {bb} |" for a, bb in b["rows"]]
        out += ["", "**Perkiraan hasil:**", ""] + [f"- {r}" for r in b["result"]]
    out += ["", "### Kenapa kuat", ""] + [f"- {x}" for x in lu["points"]]
    out += ["", "### Kelemahan", ""] + [f"- {x}" for x in lu["weak"]]
    out += ["", "### Tips", ""] + [f"- {x}" for x in lu["tips"]]
    if lu.get("variant"):
        v = lu["variant"]
        out += ["", f"### {v['title']}", "", " ".join(f"{mimg(H[n]['icon'], 32, n)} {n}" for n in v["heroes"]), "", f"_{v['note']}_", "",
                *md_syn_table(v["heroes"], v["crystals"])]
    out += ["", f"**Crystal yang dibutuhkan (tanpa ultra):** {lu['need']}", "", f"**Jalur ultra (opsional):** {lu['ultra']}", "", "---", ""]
    return out


def page_md():
    out = [f"# Analisis 5 Lineup Magic Chess: Go Go — Season {d['season']} \"{d['info']['name']}\"", "",
           f"Versi game {d['game_version']} · dibuat 20 Oktober 2026, diperbarui 21 Oktober 2026 (Penyesuaian 20/10) dari data game (S7.json)"
           " · gambar dari file game (folder `img/`)", "",
           "## Kesimpulan", "",
           f"- **Terkuat tanpa ultra:** {mimg(C['Aamon']['icon'], 28, 'Aamon')} Aamon — Dauntless 6 + Stargazer 4 + Mistbender 3. Sinerginya sudah maksimal tanpa ultra, dan tim terus menguat lewat Spirit Sand.",
           f"- **Damage tim tertinggi di mid game:** {mimg(C['Luo Yi']['icon'], 28, 'Luo Yi')} Luo Yi — Starbelle 6 dengan Odette ★2 sebagai Fan (setiap hero Starbelle sekitar +{num(FAN)} ATK).",
           f"- **Paling konsisten:** {mimg(C['Kagura']['icon'], 28, 'Kagura')} Kagura — Kishin 6 + Phasewarper 3 + Shadeweaver 3. Item Arcane didapat dengan Gold, bukan hoki.", "",
           "### Peringkat tanpa ultra", "", "| # | Lineup | Commander | Crystal wajib | Level | Konsistensi | Puncak (dengan ultra) |", "|---|---|---|---|---|---|---|"]
    for i, kons, lvl, peak in RANKING:
        lu = BY_ID[i]
        out.append(f"| {lu['rank']} | {lu['name']} | {mimg(C[lu['commander']]['icon'], 24, lu['commander'])} {lu['commander']} | "
                   f"{short_need(lu)} | {lvl} | {kons} | {peak} |")
    out += ["", "_Selisih kekuatan #2 sampai #4 kecil; pilihannya lebih ditentukan hero yang sedang banyak diambil pemain lain._", ""]
    for _, patch, lead, impact, other in PATCH_SECTIONS:
        out += [f"## Dampak Penyesuaian Keseimbangan {patch}", "", f"_{lead}_", ""]
        for name, label, ids, _, title, text in impact:
            icon = C[name]["icon"] if label == "Commander" else H[name]["icon"]
            out.append(f"- **{title}** — {mimg(icon, 28, name)} **{name}** ({label}; {impact_lineups(ids)}): {text}")
        out += ["", f"_Tidak berdampak ke 5 lineup ini: {', '.join(other)}._", ""]
    out += ["## Mekanik penting: crystal, stok, dan peluang", ""] + [f"- {x}" for x in MECHANICS] + ["", "---", ""]
    for lu in LINEUPS:
        out += md_lineup(lu)
    out += ["## Pelajaran dari pertandingan 20 Oktober", ""] + [f"- {x}" for x in MATCH]
    out += ["", "## Catatan data dan asumsi", ""] + [f"- {x}" for x in NOTES] + [""]
    return "\n".join(out)


(OUT / "ANALISIS_LINEUP_S7.html").write_text(page_html(), encoding="utf-8")
(OUT / "ANALISIS_LINEUP_S7.md").write_text(page_md(), encoding="utf-8")
missing = sorted({n for lu in LINEUPS for _, _, n, _ in lu["board"] if not H[n].get("icon")}
                 | {n for lu in LINEUPS for n in lu["cards"] if n and not K[n].get("icon")})
print("selesai; ikon hilang:", missing or "tidak ada")
print(f"Odette pre-Fan {O_PRE:.0f}, Fan {FAN:.0f}, total {O_PRE + FAN:.0f}, HP {O_HP_T:.0f}; Lancelot ATK {LA_ATK:.0f}, EHP {LA_HP + LA_SHIELD + LA_HEAL:.0f}")
