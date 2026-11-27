# Validasi S8.html terhadap screenshot in-game

- Versi game `1.3.32.354.1` (client PC dipasang 18 Nov), Season 8 "Arena Para Penyihir" (aktif sejak 2026-11-15, Rank
  Season 10 s/d 2027-01-24), diperiksa 2026-11-22. **Diperbarui 2026-11-27**: 119 gambar baru di `match/` (OCR 1 menit 38 detik,
  0 gagal; total 681 gambar) + rekaman 22 Nov 16-26 dan 23 Nov 03-34, untuk Toko Spirit Sand, Go Go Box IV-6 dst., hero
  panggilan, label Alpha, dan Wheel of Fate (bagian bertanda "27 Nov" di bawah). **Tambahan 27 Nov sore**: 51 gambar lagi (OCR 1 menit 3 detik,
  0 gagal; total 732) + rekaman "uji coba commander odette classic": Go Go Box I-4/II-6/III-6, Alpha ★3, commander Odette, ATK Rekan +1%,
  dan Patch Note Penyesuaian Keseimbangan (26/11) (bagian "27 Nov sore").
- Cara: 562 gambar di `patch-tracker/screenshot/season 8/` di-OCR (`ocr_screens.ps1 -Season 8`, 6 menit 52 detik, 0 gagal),
  dicocokkan otomatis (`mc_validate.py --season 8` → `VALIDASI_S8_auto.md`), lalu setiap selisih dan cek manual dilihat dengan mata.
- S8 di data versi lama (`1.3.24.344.1`) adalah data pra-season. Client baru mengubah banyak angka: 42 hero, 6 sinergi,
  14 commander (+ Odette), 23 kartu baru / 5 dihapus / 36 berubah, 7 equipment baru / 27 berubah
  (`data/diff/1.3.24.344.1_vs_1.3.32.354.1_S8.md`). Validasi ini memakai data versi baru.

## Isi folder (dikenali dari OCR, bukan dari nama folder)

| Folder | Gambar | Isi |
|---|---|---|
| hero and synergies | 217 + 11 MP4 | 102 Detail Hero, 113 Panduan Sinergi (tata letak baru S8), 2 galeri hero. MP4: 6 rekaman PC video pratinjau sinergi (Deadeye: Critical Chance 20/35/60% dan Critical DMG 130/160/220% = tabel 5+15, 10+25, 20+40 dan +30/60/120%), 5 video YouTube |
| commander | 51 | 41 layar detail (PC 18 Nov + Vexana di ponsel 20 Nov 21:20 dan 21 Nov 03:41), 3 layar Ganti Commander (Lucky Commander), 4 layar Odette ponsel 27 Nov 16:56–16:57 (dengan 3 tooltip kata kunci) |
| equipment | 131 | panel detail semua tab |
| go go card | 54 | galeri; S8 tidak punya tab "Kartu Power" lagi (Semua / Oranye / Ungu / Biru) |
| ensiklopedia | 16 | 8 tab |
| update patch | 57 + 4 MP4 | 18 Patch Note Season 8.0 (PC 18 Nov), 5 layar ponsel 20 Nov (Penyesuaian Keseimbangan 20/11 + pengumuman skor leaderboard), 27 layar Panduan Season (Ringkasan Sinergi sinergi baru, tab Lineup Kuat), 7 layar ponsel 27 Nov 16:21–16:22 (Penyesuaian Keseimbangan 26/11). MP4 = video YouTube |
| match | 194 + 8 MP4 | layar hasil: 33 bertanggal 1–7 Nov (masih S7), 14 bertanggal 16–21 Nov dan 24 bertanggal 22–27 Nov (S8, efek Wheel of Fate di pojok kanan atas). 27 Nov: 10 layar Wheel of Fate (4 roda berputar, 6 teks hasil), 57 panel unit dalam pertandingan (Alpha, Gatotkaca, Moskov, Bane, Terizla, Thamuz; sebagian mode Custom lawan Computer), 3 tooltip sinergi (Chrono Wanderer, Fan yang Bersorak), 2 layar Achievement. 3 frame VLC PC (2480–2482) = hitung mundur Go Go Box rekaman 20 Nov. `spirit sand/`: 20 layar Toko Spirit Sand 23 Nov + rekamannya. MP4: 5 rekaman ponsel 20 Nov, 22 Nov 16-26 (Commander's Power), 23 Nov 03-34 (toko). **27 Nov sore (+28 gambar, +1 MP4):** 16 frame VLC PC "Go Go Box setelah I-4/II-6/III-6 (n)" dari 6 rekaman, 4 panel Alpha ★3 (IV-6, 16:55), 4 layar skill Odette dalam pertandingan, 2 tooltip SPECTRE, 1 layar hasil (Gold Galore), papan; `spirit sand/` +12 layar toko 17:24–17:41; rekaman "uji coba commander odette classic.mp4" (23:40, Classic, roda Gold Galore) |

## Hasil per bagian

| Bagian | Layar | Cakupan | Hasil |
|---|---|---|---|
| Hero (Detail Hero) | 102 | 52 dari 52 hero toko | Stat ★1–★3 dan tabel Atribut Skill cocok (Zhuxin dicek mata: judul terbaca "Zhuxm"). 7 teks Elemental Mark cocok setelah perbaikan |
| Hero panggilan (panel dalam pertandingan, 27 Nov) | 59 | 4 dari 4: Alpha ★1–★3, Gatotkaca/Moskov/Bane ★1–★3 | HP, mana awal, ATK, DEF, ATK Speed, jangkauan, tabel skill, dan semua (+N) di tooltip cocok (dicek mata, lihat bawah). `mc_validate.py` hanya mengenali Detail Hero, jadi tetap menulisnya "Tanpa screenshot" |
| Sinergi (Panduan Sinergi) | 113 + 3 | 22 dari 22 sinergi | 318 baris tabel tingkat cocok. Teks Lite/Penuh cocok kecuali 3 teks yang diganti server (lihat bawah). Chrono Wanderer dan Fan yang Bersorak (tanpa Panduan Sinergi) cocok kata per kata lewat tooltip dalam pertandingan 27 Nov |
| Commander | 48 | 41 dari 41 | Nama skill, Aktif/Pasif, angka cocok. 6 cek manual = salah baca OCR ("/" jadi "1", judul skill Lv 2 Aamon tidak terbaca). Odette (27 Nov sore): teks skill dan tooltip cocok, kecuali tooltip "melebihi 6" tingkat 8–9 (nilai server, lihat bawah) |
| Equipment | 131 | 113 dari 113 level aktif | Cocok. 8 cek manual dicek mata (Inspire 20/25/30/40%, Guardian Helmet yang Diperkuat 2 pasif, Spellblade Talisman 1 pasif) |
| Go Go Card | 54 | 195 dari 200 kartu aktif | Cocok. Tidak terlihat: Journey's Windfall, Fury's Edge (Bisa Berubah Sewaktu-waktu), Victory's Blessing, Odette's Power ×2 (semuanya kartu baru client ini) |
| Ensiklopedia | 16 | 8 tab | Cocok (tabel DMG Commander 3/5/6/7/11/13/14/15, biaya naik level, Magic Crystal Pilihan, Wheel of Fate) |
| Patch Note 26/11 (27 Nov sore) | 7 | 25 baris + Kalea, Karina, Bane (terlewat OCR, dibaca mata) | Semua dicatat di `server_patch.json` ("26/11"); client PC tidak berubah sejak 22 Nov. 2 nilai lama patch note tidak cocok file: Eudora ★3 700% (file 635%), Lolita ★3 1.700% (file 1455%) |
| Patch Note | 23 | Season 8.0 + 20/11 | 9 baris sudah di file game, 7 baris diterapkan server (semua tercatat di `server_patch.json`), 2 tak bisa dipastikan otomatis (Frostrider rasio Hybrid ATK, Shield Balmond; keduanya tercatat), 2 judul rusak OCR ("S_ Frostrider" ganda; "Vale's Power" terbaca "Yaelned'aSpaPtOkaWne1r k", kartunya di file sudah 2 Gold) |
| Toko Spirit Sand (23 dan 27 Nov) | 29 + rekaman | **11 dari 11 item** dengan harga (ATK Rekan +1% 27 Nov) | Semua harga cocok; 12 pembelian bertumpuk sesuai stack data (HP +1/+2/+3, ATK +1/+3/+5). Auto: 1 selisih + 2 cek manual = dua pembelian di antara dua screenshot (terlihat di rekaman) dan kolom yang tidak terbaca OCR (lihat bawah). S8 kini `STORE_VERIFIED` |
| Go Go Box (6 rekaman 20–22 Nov) | 19 | I-4 ×6, II-6 ×6, III-6 ×4, IV-6 ×2, V-6 | Semua cocok data S8: I-4 = 8 equipment; II-6 = 5–6 + 1–2 crystal + 1 Kapasitas +1; III-6 = 4 + 2 + 2; IV-6/V-6 = 5 + 2 + 1 (aturan S7 3–4 + 3–4 + 1 tidak mungkin). Babak dari isi orb + posisi rekaman/HUD; label nama file tertukar di 3 rekaman (lihat bawah) |

## Kesalahan yang ditemukan dan sudah diperbaiki di `mc_data.py`

| Temuan | Sebelum | Sesudah (= game) | Penyebab |
|---|---|---|---|
| Teks Elemental Mark FAIRY TAIL: Gray, Wendy, Juvia, Erza, Lucy, Natsu, Magic Crystal FAIRY TAIL (Mystic) | "Freeze 0/0/0/0/0/0 detik", "-1 / -1 / …", "-0.01% / …" | Gray 0.2/0.4/0.6/0.75/1.05/1.4 detik, Wendy 5/15/20/25/40/50, Juvia 20%/25%/30%/35%/40%/40%, Erza 10/20/25/30/45/55, Lucy 25%/35%/40%/45%/50%/50%, Natsu 30%/…/215%, crystal 40% (layar 2144–2222, 2330) | kolom ke-5 placeholder berisi angka saja (`0.001`, `-1`, `-0.01`, `100`) dibaca sebagai konstanta, padahal pengali; kolom ke-7 (`|0|1` … `|0|6`) = level efek per jumlah Elemental Mark, dulu diabaikan. Hanya dipakai tabel S8; ekspor S7 identik |
| Baris teks FAIRY TAIL 10 | "freeze … selama 10% detik … sebesar ?" | "freeze … 0.5 detik … True DMG 10% HP … 20%" (layar 2039) | teks baris memakai daftar angka tabel (`m_NumDescribeTag`, tanpa durasi); seharusnya `m_SpecialNumDescribe` → `m_NumDescribeNew` |
| Panduan Sinergi S8 tidak tergambar | hanya teks lama `mRelationExplain` + teks per tingkat | ditambah `explain_lite` (tombol Lite = `mSkillDescriptionNew` baris tingkat), `explain_full` (tombol Penuh = `mRelationExplainNew`, `${TagN}$` = nama kata kunci), `table` (judul kolom `DescriptionIcon.mIconDescription` dari `m_RelationEffectTag`, sel `mNumDescribeTag1..n` + `m_NumDescribeTag`, teks baris `mSpecialDescription`), `details` (tooltip kata kunci) | UI baru client 1.3.32.354.1; tampil di tab Sinergi S8.html dan S8.md |
| (27 Nov) Catatan Go Go Box di S8.md | "Catatan data: ID 1054 …" tercetak di bawah tabel Wheel of Fate | di bagian Go Go Box | baris catatan ikut masuk blok Wheel of Fate saat bagian itu ditambahkan (riwayat 59); S8.json dan S8.html tidak terpengaruh |
| (27 Nov) `m_SpecialRules` Commander's Power | `[1, 1, 1]` mentah, tidak tampil di laporan | `special_rules` = putaran 1 slot 1: Kartu Power Commander sendiri; tampil di kolom "Aturan data" S8.md/S8.html | arti dibuktikan dari rekaman (lihat Wheel of Fate) |
| (27 Nov sore) Tabel Atribut Skill dari patch server | patch kedua pada skill yang sama mulai lagi dari tabel file, jadi perubahan atribut patch pertama hilang; baris kedua yang labelnya sama (Eudora/Kimmy "Magic Bonus", Popol "Bonus Physical") tidak bisa diubah | atribut melanjutkan `attributes_server` patch sebelumnya, seperti teksnya; `attributes` boleh `[label, bintang, nilai, urutan]` | ditemukan saat mencatat 26/11 (Balmond 20/11 lalu 26/11). Kimmy 20/11 kini juga punya atribut 1925%/825% |

Perbaikan alat pemeriksa (`mc_validate.py`): galeri kartu S8 tanpa tab Kartu Power, layar Commander ponsel ("+ Commander"),
judul Commander rusak OCR (Nana "Cc uma de"), tabel Panduan Sinergi (baris dicocokkan lewat isinya karena label tingkat
2/4/6 tidak terbaca; "%" terbaca "0/0"; ikon di belakang angka terbaca satu digit tambahan), judul sinergi "+ Stargazer",
teks commander dari server (`description_server`), pecahan atribut yang dipotong panel, baris lanjutan patch note. 27 Nov sore: di layar toko,
persen ATK/HP yang turun berarti pertandingan baru (stack tidak pernah turun dalam satu pertandingan), jadi tidak dibandingkan dengan layar sebelumnya.
`check_match.py` kini memeriksa semua folder versi yang punya laporan MATCH (42 laporan S7 tetap di `1.3.24.344.1`).

## Kartu Power = Go Go Card emas (sejak S8)

- Info pengguna, terbukti di data dan layar: di `MCSuperCrystalKey_S8` semua kartu Power ber-`m_Level` 3 (= Oranye/emas); di S7
  `m_Level` 4 dengan tab galeri sendiri "Kartu Power" dan hanya di putaran 1. Galeri S8 tidak punya tab Kartu Power: kartu Power
  tampil berbingkai emas di tab Kartu Oranye (2399, 2408). Di pertandingan, pilihan Go Go Card babak I-2 mencampur kartu Power dengan
  kartu emas lain (rekaman 20 Nov 08-02: Shield of Fortune + Franco's Power).
- 53 kartu aktif bertanda Power (`m_CardTag` 2); 9 di antaranya juga bisa muncul di putaran 2–3 (Kagura's, Cyclops', Nana's, Fanny's,
  Gusion's, dan versi umum Lunox's, Alice's, Ruby's, Freya's).
- `m_CardTag` = jenis kartu yang dipakai Wheel of Fate: 1 Kartu finansial (47 kartu aktif, 12 di antaranya juga kartu Power),
  2 Kartu Power (53), 3 Kartu Badge Sinergi (28, Badge + Blessing), 4 Kartu peningkatan Sinergi (15), 0 = kartu biasa (69).
- Ekspor diperbaiki: tier "Oranye" + `power: true`, `tags` = nama jenis kartu. S8.html: chip "Power" di kartu dan filter "Kartu
  Power"; `mc_diff.py` mencatat 51 perubahan "Tier: Power → Oranye" (bukan kartu dihapus + kartu baru). Ekspor S7 tidak berubah.

## Wheel of Fate (diperiksa 22 Nov)

- **Kapan:** upacara pembuka setelah semua player memilih commander, sebelum babak I-1 (kelas `MCLogicOpenCeremonyComp_GoGoRoulette`).
  Hanya battle config S8 yang punya `<AOpeningCeremonyInfo iOpenType="1" iMapId="1900751" …>` dengan 4 fase 2 + 6,5 + 4 + 3 =
  15,5 detik. Rekaman 07-39: layar loading 57 detik → roda berputar 60 detik → hasil 66 detik → papan 72 detik.
- **Cara memilih (nama fungsi di `GameAssembly.pdb`):** `CollectRouletteConfigs` → `PrepareRouletteList` → `RandomConfig` dengan
  `GetRouletteWeight` (`m_Weight`, atau `m_NewPlayerWeight` bila `ShouldUseNewPlayerWeight`); tabel berurutan `m_Order`, tapi roda di
  layar tidak mengikuti urutan itu (lihat 27 Nov). Efek
  diterapkan lewat `SetGoGoCardFilter`/`IsCardTagAllowed` (tag kartu), `ModifyGoGoCardQuality` (kualitas), `ModifyGoGoCardRoundData`
  (babak), `CreateShareGoGoCard` (kartu sama untuk semua), `MCLogicGoGoCardRouletteSpecialRules` (`TryGetRules`, `IsRoundMatch`,
  `IsSlotMatch`, `TryPickSelfCommander`: aturan per slot). Id terpilih disimpan di `MCLogicGlobalComp.m_iGoGoRouletteId`.
- **Isi `MCRoulette` (12 baris, 9 aktif, total bobot 15; pemain baru total 4):**

| Efek | Peluang (bobot) | Pemain baru | Aturan |
|---|---|---|---|
| Crystal Legend | 13,3% (2) | 25% (1) | putaran 1: hanya Kartu Badge Sinergi, kualitas Ungu |
| Commander's Power | 13,3% (2) | – | putaran 1: hanya Kartu Power, kualitas Oranye; slot 1 = Kartu Power Commander sendiri (`m_SpecialRules` [1,1,1], terbukti 27 Nov) |
| Gold Galore | 6,7% (1) | 25% (1) | putaran 1–3: kualitas Oranye |
| Tycoon | 13,3% (2) | 25% (1) | putaran 1–3: hanya Kartu finansial, kualitas Oranye |
| Synergy Awakening | 13,3% (2) | – | putaran 2: hanya Kartu peningkatan Sinergi, kualitas Ungu |
| Fate Sync | 13,3% (2) | – | semua player ditawari kartu yang sama |
| Oracle Vision | 6,7% (1) | – | kualitas Go Go Card pertandingan diungkap lebih awal |
| Hero Reinforcement | 13,3% (2) | – | setelah tiap pilihan Go Go Card: 1 Hero 3, 4, lalu 5 Gold (skill 90001–90003) |
| Early Reinforcement | 6,7% (1) | 25% (1) | Go Go Card muncul di babak I-2, I-3, I-4 |
| Tycoon (varian), Hero Awakening, Promotion Rewards | nonaktif (0) | – | varian Tycoon kualitas Ungu/Oranye/Oranye; hanya kartu peningkatan Hero di putaran 1; babak Go Go Card tambahan di Level Commander 4, 6, 7 |

- **Bukti layar:** video resmi "Wheel of Fate" (`update patch/`) menampilkan tepat 9 efek aktif di atas. Hasil roda di rekaman 20 Nov:
  07-39 **Early Reinforcement** (teks sama persis), 08-02 **Tycoon** (pilihan I-2: Shield of Fortune + Franco's Power, keduanya kartu
  finansial emas), 08-22 **Gold Galore** (pilihan I-2: Box of Holy Objects + Golden Era, keduanya Oranye). Rekaman 09-33 dan 18-30
  dimulai di tengah pertandingan. Teks efek di layar = `MCRoulette.mDesc`.
- **Ensiklopedia** (2250) hanya menyebut 4 efek (Crystal Legend, Commander's Power, Gold Galore, Tycoon), padahal roda memakai 9.
- Diekspor ke S8.json (`wheel_of_fate`), S8.md, dan tab Info Season S8.html.

### Wheel of Fate: segmen roda, `m_SpecialRules`, dan hasil (27 Nov)

- **Roda di layar = 12 segmen.** Kamera hanya memperlihatkan separuh atas lingkaran: di 05-26-40 (roda berhenti) tampak 7 segmen,
  yang paling kiri dan paling kanan sejajar pusat roda, jadi 7 segmen = 180° = 30° per segmen = 12 segmen. Isi segmen **berbeda
  tiap pertandingan** dan satu efek bisa tampil 2 kali: 04-25-11 Crystal Legend, Gold Galore, Tycoon, Synergy Awakening, Fate Sync,
  Oracle Vision, Hero Reinforcement, Early Reinforcement (semua beda); 05-23-17 Tycoon 2 kali; 05-26-40 Crystal Legend, Commander's
  Power, dan Gold Galore masing-masing 2 kali di antara 7 segmen. Gold Galore berbobot 1 tapi tampil 2 kali, jadi dugaan lama "tiap
  efek tampil sebanyak bobotnya" **salah**: segmen tidak menunjukkan bobot. Ikon segmen = `Atlas_McRoulette_MC/RouletteNN` efek aktif;
  ikon efek nonaktif (Hero Awakening, Promotion Rewards) tidak pernah terlihat. Roda yang masih berputar menyorot segmen lain dari
  hasil akhirnya (04-25-11 menyorot Fate Sync, hasil Commander's Power).
- **`m_SpecialRules` [1,1,1] = jenis 1, putaran Go Go Card 1, slot 1.** Nama fungsi di PDB: `MCLogicGoGoCardRouletteSpecialRules`
  `TryGetRules`, `IsRoundMatch`, `IsSlotMatch`, `HasType1ForRound`, `TryPickSelfCommander`/`PickSelfCommander`. Bukti rekaman 22 Nov
  16-26 (hasil roda Commander's Power, commander Lukas): pilihan I-2 menawarkan 2 kartu, **slot kiri Lukas's Power** ("Eksklusif untuk
  Commander Lukas"), slot kanan Aurora's Power; setelah 2 kali refresh slot kiri tetap Lukas's Power, slot kanan menjadi Guinevere's lalu
  Franco's Power. Putaran 2 (II-3: Knockout Punch, …) dan 3 (III-3: Rising Fury II, Magic Surge, Vanguard Leader) berisi kartu Ungu biasa
  tanpa Lukas's Power, jadi [1,1,1] bukan "jenis 1 di putaran 1–3". Urutan field [jenis, putaran, slot] belum teruji karena ketiganya 1.
  Di rekaman ini setiap putaran menawarkan 2 kartu, masing-masing Refresh ×2.
- **Hasil roda.** Nama efek tampil di pojok kanan atas layar hasil S8 (layar hasil 1–7 Nov tidak punya, karena masih S7). 21 pertandingan
  biasa (19 layar hasil 16–27 Nov + rekaman 20 Nov 08-02 dan 08-22 tanpa layar hasil) dan 5 roda pertandingan latihan 27 Nov:

| Efek | Peluang data | Pertandingan biasa | Latihan 27 Nov |
|---|---|---|---|
| Fate Sync | 13,3% | 6 (21 Nov 22:02, 22 Nov 15:56, 24 Nov 03:14, 24 Nov 11:10, 26 Nov 11:16, 26 Nov 18:40) | 1 (05:28) |
| Tycoon | 13,3% | 6 (16 Nov 23:44, 17 Nov 22:32, rekaman 20 Nov 08-02, 24 Nov 04:52, 25 Nov 19:05, 27 Nov 04:06; roda 03:39) | – |
| Commander's Power | 13,3% | 2 (22 Nov 16:48, 25 Nov 01:12) | 2 (04:25, 05:25) |
| Gold Galore | 6,7% | 2 (rekaman 20 Nov 08-22, 26 Nov 05:23) | – |
| Crystal Legend | 13,3% | 1 (21 Nov 20:15) | 1 (05:23) |
| Hero Reinforcement | 13,3% | 1 (20 Nov 04:57) | 1 (05:26) |
| Synergy Awakening | 13,3% | 1 (24 Nov 16:35) | – |
| Oracle Vision | 6,7% | 1 (20 Nov 09:57, rekaman 09-33) | – |
| Early Reinforcement | 6,7% | 1 (20 Nov 08:00, rekaman 07-39) | – |

  Jam = jam layar hasil (akhir pertandingan); untuk latihan = jam layar roda. Fate Sync dan Tycoon masing-masing 6 dari 21 (29%, data
  13,3%), tapi untuk 21 pertandingan itu masih wajar: uji χ² terhadap bobot data 11,5, p ≈ 0,18 (simulasi 200.000 kali; peluang ada
  satu efek yang muncul ≥ 6 kali ≈ 30%). Belum ada bukti peluang berbeda dari tabel; kumpulkan terus dari layar hasil berikutnya.

## Hero panggilan S8 (panel dalam pertandingan, 27 Nov)

Panel unit dan tooltip skill menulis nilai mutlak, jadi persentase skill dibuktikan dengan menghitung balik dari ATK di panel yang
sama (dibulatkan ke bawah). Semua cocok dengan S8.json; ★3 Gatotkaca, Moskov, dan Bane baru pertama kali terbukti.

| Hero | ★ (screenshot) | HP | Mana | ATK fisik / magic | DEF, ATK Speed, jangkauan | Tooltip skill |
|---|---|---|---|---|---|---|
| Alpha | ★1 (03-55-06/12, III-5) | 5.400 | 0/40 | 295 / 295 | 48 (29%), 0,75, 2 | 50% → +147, 135% → +398 (retakan, chase), 120% → +354 (Force Wave), ★3 1620% → +4779 True DMG; tabel 50/70/–, 135/160/–, 135/160/–, 120/145/735 |
| Alpha | ★2 (03-56-26/30, 03-59-03/11/14) | 10.260 | 0/40 | 604 / 488 (dasar 390 + item) | 48 (29%), 0,75, 2 | 70% × 604 (Hybrid ATK tertinggi) → +422 |
| Gatotkaca | ★1 (04-32-50/54) | 4.335 | 0/80 | 250 / 250 | 48 (29%), 0,65, 1 | 185% → +462, 250% → +625, 165% → +412, ★3 175% → +437, pulih 700 HP, airborne 1,2 detik |
| Gatotkaca | ★2 (04-39-10/14, 04-47-10/13) | 7.805 | 0/80 | 469 / 544 (dasar 375) | 68 (36%), 0,65, 1 | 265% × 544 → +1441, 250% → +1360, 165% → +897, 175% → +952, pulih 1.200 HP |
| Gatotkaca | ★3 (04-52-22/26, 04-53-10/14) | 53.760 | 0/20 | 925 / 1.073 (dasar 740) | 68 (36%), 0,65, 1 | 1135% × 1073 → +12178, 900% → +9657, 600% → +6438, 175% → +1877, pulih 6.000 HP, airborne 1,32 detik |
| Moskov | ★1 (05-03-38/42) | 3.565 | 0/60 | 220 / 220 | 24 (17%), 0,80, 4 | 260% → +572, ATK Speed +20%, ★3 1000% → +2200; 05-04-02/07: 341 → +886, mana 33/80 |
| Moskov | ★2 (05-10-09/14, 05-10-26/32) | 6.417 | 0/60 | 330 / 330 | 24 (17%), 0,80, 4 | 275% → +907 (462 → +1270), +25%, 1000% → +3300 |
| Moskov | ★3 (05-21-09/13) | 44.205 | 0/20 | 987 / 705 (dasar 705) | 24 (17%), 0,90, 4 | teks ★3 "memberikan / Physical DMG" (tabel ★3 "/", sama dengan data), +40%, 1000% × 987 → +9870 |
| Bane | ★1 (05-36-44/48, 05-37-49/54) | 4.985 | 0/80 | 230 / 230 | 48 (29%), 0,65, 1 | 240% → +552 (magic 310 → +744), airborne + freeze 1,2 detik |
| Bane | ★2 (05-43-45/49, 05-49-49/53) | 8.975 | 0/80 | 345 / 466 | 48 (29%), 0,65, 1 | 260% × 466 → +1211, 1,8 detik |
| Bane | ★3 (05-51-44/48, 05-53-25/28) | 61.825 | 0/20 | 740 / 999 | 48 (29%), 0,65, 1 | 1100% × 999 → +10989 (05-53-28 magic 899 → +9889), 2,5 detik |

- Mana "0/N" = Batas Mana Awal; setelah skill pertama batasnya menjadi Batas Mana (Moskov ★1 33/80, Gatotkaca ★2 0/100), sesuai data.
- **Label Alpha S8:** tooltip menulis "(+147) **Physical DMG** Area" (merah), sama dengan S8.json (`50%/70% Physical DMG Area`); S7 menulis
  "Adaptive DMG". Tooltip dalam pertandingan tidak memperlihatkan label persennya (nilai mutlak), jadi bahwa persennya tanpa label
  "Total … ATK" di S8 tetap hanya dari data, seperti S7.
- Sinergi tanpa Panduan Sinergi, dicek lewat tooltip dalam pertandingan: **Chrono Wanderer** (04-33-16) "Hero 5 Gold yang dipanggil oleh
  Echomancer.", kolom "Efek Khusus", baris "Dapatkan Bonus Sinergi Echomancer"; **Fan yang Bersorak** (04-39-02/06) "Hero yang menggunakan
  Lightstick mendapatkan efek bonus Starbelle dan memberikan bonus ke Hero Starbelle.", baris "Dapatkan bonus Sinergi Starbelle", tooltip
  Lightstick "Equipment Khusus. Bisa digunakan oleh Hero apa pun. Menggunakannya akan memberikan Sinergi Cheering Fan." Semua sama
  persis dengan S8.json (termasuk nama Inggris "Cheering Fan" di tooltip).

## Toko Spirit Sand S8 (23 Nov 03:35, `match/spirit sand/`)

Satu pertandingan: 20 screenshot + rekaman 28:50 (`Screenrecorder-2026-11-23-03-34-54-845.mp4`). Rekaman dipindai per 0,25 detik; tiap
kali toko terbuka dan isinya berubah, bagian toko disimpan (72 potongan), jadi pembelian di antara dua screenshot ikut terlihat.

| Waktu rekaman | Babak | Dibeli (harga) | ATK / HP rekan | Spirit Sand di robot (sebelum → sesudah) |
|---|---|---|---|---|
| 9:06 → 9:10 | II-4 | Nana (60) | 0% / 0% | 60 → 0 |
| 10:02 → 10:07 | II-5 | HP Rekan +1% ×2 (8 + 8) | HP 0 → 2% | 16 → (tertutup) |
| 10:12 → 10:14 | II-5 | ATK Rekan +2% (16) | ATK 0 → **3%** | (tertutup) → 6 |
| 14:06 → 14:08 | III-2 | Magic Crystal Acak (80) | – | 86 → (tertutup) |
| 14:23 → 14:26 | III-2 | HP Rekan +3% (24) | HP 2 → 5% | 30 → 8 |
| 14:29 → 14:32 | III-2 | HP Rekan +1% (8) | HP 5 → 6% | 14 → 6 |
| 16:40 → 16:43 | III-4 | Mirror Device (80) | – | 80 → (tertutup) |
| 17:58 → 18:29 | III-5/III-6 | Hero 4 Gold Bintang 1 Acak (30) | – | 32 → 2 |
| 19:18 → 21:05 | III-6/IV-1 | ATK Rekan +2% (16) | ATK 3 → **6%** | 17 → … |
| 21:05 → 21:09 | IV-1 | ATK Rekan +3% (24) | ATK 6 → **11%** | 31 → 8 |
| 22:24 → 22:27 | IV-2 | HP Rekan +2% (16) | HP 6 → 8% | 20 → (tertutup) |
| 24:06 → 24:09 | IV-4 | HP Rekan +2% (16) | HP 8 → 10% | 19 → 3 |

- 10 dari 11 item terlihat dengan harga sama dengan data (ATK Rekan +1% tidak pernah ditawarkan di pertandingan ini; datanya sama dengan
  S7, yang sudah terverifikasi). 9 pembelian bertumpuk cocok: HP +1% = +1, HP +2% = +2, HP +3% = +3, **ATK +2% = +3, ATK +3% = +5**
  (sama dengan temuan S7). Di 4 pembelian yang terekam tanpa jeda (Nana 60 → 0, HP +1% 14 → 6, Hero 4 Gold 32 → 2, HP +2%
  19 → 3) angka robot turun tepat sebesar harga; di pembelian lain angkanya ikut bertambah selama pertarungan berjalan (30 → 8 untuk
  harga 24).
- Aturan toko sama dengan S7: 3 slot; isi tidak berganti antarbabak (HP +1%, Magic Crystal Acak, Nana bertahan I-2 s/d II-4); hanya slot
  yang dibeli diganti; item yang sama bisa ada di 2 slot (HP +1% ×2) dan muncul lagi di slot yang baru dibeli (HP +2% di IV-2); Nana dan
  Mirror Device tidak muncul lagi setelah dibeli. Sejak IV-4 ketiga slot berisi 1 Equipment Acak yang Diperkuat (80) dan tidak dibeli.
- `VALIDASI_S8_auto.md`: 1 selisih (`03-56-04`: ATK naik 8% = ATK +2% lalu ATK +3%, keduanya di antara screenshot III-6 dan IV-1) dan
  1 cek manual (`03-49-23`: HP naik 3% = HP Rekan +3% yang muncul setelah Magic Crystal Acak dibeli). Keduanya terjelaskan oleh rekaman.
  OCR hanya membaca 7 dari 11 nama + harga (nama Nana tidak terbaca di 2 layar, baris HP 10% di `03-59-05` tidak terbaca).
- Notifikasi kiri atas di `03-49-23` (Magic Crystal Titan, FAIRY TAIL, Weapon Master) = item yang baru diterima, bukan layar pilihan.
- `mc_data.py`: `STORE_VERIFIED = {7, 8}`, jadi catatan "Belum terverifikasi" hilang dari tabel toko S8.html/S8.md, dan catatan
  ATK +2%/+3% menyebut "Cocok dengan kenaikan baris ATK rekan di layar toko".

## Go Go Box S8 mulai IV-6 (rekaman 20 Nov, frame VLC PC)

| Layar | Rekaman (posisi) | Babak (HUD sebelum kotak) | Equipment biasa | Crystal sinergi | Kapasitas +1 |
|---|---|---|---|---|---|
| 2480 | 18-30 (22:39) | IV-6 | Taunt & DEF, DMG Tambahan, Spell Vamp, Magic Penetration, Pemulihan Mana Tank | Dawnbringer, Stargazer | 1 |
| 2481 | 09-33 (22:40) | IV-6 | Lifesteal, Penggunaan Skill Cepat, CC Tunggal, Pemulihan Mana Tank, Magic Penetration | Weapon Master, Dawnbringer | 1 |
| 2482 | 18-30 (28:30) | **V-6** | DMG Tank, ATK Speed Super Cepat, Memantulkan Physical DMG, DMG Tambahan, CC Tunggal | SPECTRE, FAIRY TAIL | 1 |

- Ketiganya hitung mundur "1 Segera Dimulai" dengan 8 orb utuh (tinggal 2 pemain). 5 + 2 + 1 cocok dengan data S8 IV-6 dst. (equipment
  4–6, crystal 1–3, Kapasitas +1 1) dan tidak mungkin dengan aturan S7 (3–4 + 3–4 + 1). Semua label ada di pool babaknya; `mc_validate.py`
  dengan RapidOCR: 3 dari 3 layar 8 orb utuh, 0 selisih (susunan ini juga cocok II-6, jadi babaknya dibaca dari HUD rekaman).
- V-6 baru pertama kali terekam (S7 hanya sampai IV-6). Hero di kotak belum dicek. I-4, II-6, III-6 S8: lihat 27 Nov sore.

## 27 Nov sore: Go Go Box I-4/II-6/III-6, Alpha ★3, Odette, ATK Rekan +1%

### Go Go Box I-4, II-6, III-6 (16 frame VLC PC dari 6 rekaman)

| Rekaman | I-4 | II-6 | III-6 |
|---|---|---|---|
| 20 Nov 07-39 (Vexana) | 05:24 "III-6 (4)": 8 equipment | 11:44 "II-6 (6)": 5 + Bruiser, Dauntless + 1 | 18:12 "I-4 (6)": 4 + SPECTRE, Defender + 2 |
| 20 Nov 08-02 | 04:52 "II-6 (5)": 8 equipment (Spell Vamp ×2) | 11:25 "I-4 (5)": 6 + Titan + 1 | – |
| 20 Nov 08-22 | 04:31 "II-6 (4)": 8 equipment | 11:04 "I-4 (4)": 6 + FAIRY TAIL + 1 | – |
| 20 Nov 09-33 | 02:46 "I-4 (3)": 8 equipment | 09:01 "II-6 (3)": 6 + Starbelle + 1 | 16:13 "III-6 (3)": 4 + Bruiser, Mage + 2 |
| 20 Nov 18-30 | 03:14 "I-4": 8 equipment | 09:31 "II-6": 5 + Swiftblade, Titan + 1 | 16:22 "III-6": 4 + FAIRY TAIL, Mage + 2 |
| 22 Nov 16-26 | 05:16 "I-4 (2)": 8 equipment | 12:00 "II-6 (2)": 6 + Bruiser + 1 | 19:30 "III-6 (2)": 4 + Deadeye, Titan + 2 |

- Sel = posisi di rekaman, "nama file", lalu equipment biasa + crystal + Kapasitas +1. Babak ditentukan dari isi orb dan urutan waktu (Go Go Box
  berikutnya ±6½ menit kemudian), bukan dari nama file: di rekaman 07-39, 08-02, dan 08-22 label nama file tertukar (mis. "I-4 (4)" di 11:04 berisi
  crystal FAIRY TAIL + Kapasitas +1 = II-6, sedangkan "II-6 (4)" di 04:31 berisi 8 equipment = I-4). Isinya tetap cocok data, tanpa selisih. Nama
  file tidak diubah.
- Semua label orb ada di pool babaknya (`mc_validate.py` dengan RapidOCR: 19 dari 19 layar 8 orb utuh, 0 selisih). Rekaman 07-39 menampilkan pita
  "Pilih satu dari semua opsi setelah semua Commander selesai memilih." (Vexana, I Want All of Them!) di I-4, II-6, dan III-6. Hero di kotak belum dicek.

### Alpha ★3 (16:55, IV-6, mode Custom lawan Computer)

- Panel: HP 100.000/100.000, mana 0/40, ATK 2689 / 2169 (dasar 1735 + item/sinergi), DEF 48 (29%), ATK Speed 0,75, jangkauan 2: cocok data ★3.
- Tooltip ★3 memakai teks ★3 sendiri: "Alpha menjadi tidak bisa ditargetkan … masing-masing memberikan (+43561) True DMG. Menggunakan skill satu
  kali saat pertarungan dimulai." = 1620% × 2689, lalu "Pasif: Basic ATK menembakkan Force Wave … (+19764) Physical DMG Area … berdasarkan nilai
  Hybrid ATK-nya yang lebih tinggi." = 735% × 2689 (kolom ★3 DMG Force Wave). Di data kalimat Pasif ★3 tidak ada di teks (nilainya hanya di tabel,
  735%), dan teks ★1–★2 menulis "didasarkan pada". Tabel 50/70/–, 135/160/–, 135/160/–, 120/145/735 sama. ★4 belum terlihat.

### Commander Odette (ponsel 27 Nov 16:56–16:57, Odette ★★)

- "Blessing" (Aktif) dan "Supplication" (Pasif) sama persis dengan data, termasuk tooltip "Sinergi Faction" (Titan; Echomancer; FAIRY TAIL;
  SPECTRE; Starbelle; Dawnbringer;) dan "Jumlah Sinergi" 2–6 (2%/5%, 4%/6%, 8%/10%, 10%/12%, 12%/15%). "Swan Princess" = nama skin.
- **Tooltip "melebihi 6" berbeda:** 7: 15% HP; 20% Hybrid ATK (sama), **8: 25% HP; 35% Hybrid ATK** (file 30%/40%), **9: 45% HP; 60% Hybrid ATK**
  (file 50%/65%). Angka file dari efek 45060600/45060601 level 8–9 (`MCEffect` 3000/4000, 5000/6500; tidak ada baris S8 yang menimpa). Levelnya
  = jumlah sinergi, bukan level commander. Client PC tidak berubah sejak 22 Nov dan Patch Note 26/11 tidak menyebut Odette, jadi nilainya dari
  server tanpa patch note (seperti Vexana Unrestricted 20 Nov). Dicatat di `server_patch.json` sebagai "27/11 tanpa patch note" (catatan).
- Dalam pertandingan (17:00, I-2): Blessing menawarkan 2 sinergi, "Pilih satu Sinergi untuk menambah Jumlah Sinergi tersebut sebanyak 1." Rekaman
  Classic: roda Gold Galore; pilihan Go Go Card I-2 (Technological Revolution, Sharp Arrow, Fully Armed), II-3, III-3 semuanya emas, dan Odette's
  Power tidak muncul (kedua kartu itu tetap belum terlihat).

### ATK Rekan +1% (toko S8, 27 Nov 17:24–17:41)

- Pertandingan kedua dengan toko: Nana dibeli (II-5 → III-1), ATK Rekan +2% (ATK 0 → 3%), 2 Hero 4 Gold, ATK Rekan +3% (3 → 8%, +5), lalu **ATK
  Rekan +1% seharga 8** muncul di slot itu dan dibeli: ATK 8 → 9% (**+1 stack**). Jadi 11 dari 11 item terlihat dengan harga sama dengan data
  dan semua aturan stack terbukti di S8 (HP +1/+2/+3, ATK +1/+3/+5).
- Auto: cek manual `27-17-37-35` = kolom yang tidak terbaca OCR (yang dibeli ATK Rekan +2%, +3 stack, sesuai). "ATK naik -11%" antara layar
  23 Nov dan 27 Nov hilang setelah perbaikan pemeriksa (pertandingan baru).

## Yang memang berbeda (bukan kesalahan ekstraksi)

### Penyesuaian Keseimbangan 20/11 (diterapkan server, tercatat di `server_patch.json` kunci "8")

| Bagian | Item | Perubahan | Catatan |
|---|---|---|---|
| Commander | Brody / Abyssal Surge | kini bisa digunakan mulai Babak I-1 | tidak ada angka di teks file |
| Commander | Lukas / Sacred Gift | 3–4 kali lipat → 2–3 kali lipat | |
| Commander | Vexana / I Want All of Them! | kini hanya pada 3 Fase Go Go Box pertama | teks baru terlihat di layar ponsel 20 dan 21 Nov |
| Commander | Vexana / Unrestricted | 4 → 2 Gold per Fase Go Go Box | file game 6. Layar PC 18 Nov (1980) 6, ponsel 20 Nov 21:20 **4**, ponsel 21 Nov 03:41 **2**: nilai 4 berasal dari server sebelum 20/11 tanpa patch note |
| Sinergi | Frostrider | pewarisan HP Tunggangan 100% → 80%; pewarisan Hybrid ATK 2/4/6: 35/50/65% → 20/30/80% | angka 80% dicek dengan memperbesar layar |
| Skill hero | Barbiel / Quaking Stomp | stun 1 → 0,5 detik | |
| Sinergi | Dawnbringer | 10 Dawnbringer: Supreme Crown 350% → 500% Max HP | |
| Skill hero | Gray | ★3 jangkauan penargetan skill diperluas | tanpa angka |
| Skill hero | Valentina / Arcane Shade | pengali DMG Skill ★2 165% → 190% | file game dan layar Detail Hero 18 Nov menulis **140%** di ★2 |
| Skill hero | Kimmy / Traction Pulse | ★3: 1.750% → 1.925%, 750% → 825% | |
| Hero | Yu Zhong | HP 3.545/6.380/15.770 → 3.760/6.765/16.715 | |
| Skill hero | Popol / Icefield Strike | Freeze 1,0 → 0,3 detik | |
| Skill hero | Balmond / Lethal Counter | ★1/★2 380%/410% → 370%; Shield ★2 6% → 5% | |
| Lainnya | — | perbaikan bonus Hybrid ATK dasar Lightstick, Mana Balmond ★3, jangkauan skill Nana | catatan |

### Penyesuaian Keseimbangan 26/11 (diterapkan server, tercatat di `server_patch.json` kunci "8")

7 layar ponsel 27 Nov 16:21–16:22, dibaca mata (OCR melewatkan Kalea, Karina, dan Bane). Client PC tidak berubah sejak 22 Nov
(`patch_tracker.py snapshot`). Panel Bane ★2 dalam pertandingan 27 Nov 05:43–05:53 masih freeze 1,8 detik, jadi patch ini belum berlaku pagi
itu (20/11 juga baru berlaku beberapa jam setelah catatannya tampil). `PATCH_Penyesuaian_26_11.html|md` = analisa otomatis `mc_patch.py`;
drafnya tidak dipakai mentah (Lolita "12% → 15%" terbaca sebagai stat HP, Balmond/Kimmy perlu teks hasil 20/11, angka ribuan bertitik).

| Bagian | Item | Perubahan | Catatan |
|---|---|---|---|
| Commander | Kagura / Yin Yang Gathering | Shield Bintang 2: 125% → 135% Max HP | |
| Commander | Ling / Transcendent Stance | Hybrid ATK permanen per duel yang dimenangkan: 6% → 8% | |
| Commander | Kalea / Serpent's Favor | hadiah bonus Brankas Harta 5–8 poin berkurang 1–2 Gold | angka baru tidak disebut (catatan) |
| Commander | Guinevere / Mystic Evolution | peluang Hero gratis saat refresh Toko (Bintang 2): 24% → 23% | |
| Sinergi | Dawnbringer | 4/6: stack peningkatan Equipment baru 7/14 → 9/15 | catatan |
| Sinergi | Swiftblade | 2/4/6: Hybrid Penetration tambahan Hero Swiftblade 25/50/100 → 35/65/130 | catatan |
| Sinergi | Titan | Atribut Balmond: batas HP eksekusi 18% → 15%, DMG Area setelah eksekusi 200% → 180% | teks skill Balmond ikut diganti |
| Skill hero | Melissa / Eyes on You! | ★3 DMG Area 205% → 320%, ATK Speed 100% → 200% | |
| Skill hero | Eudora / Thunder's Wrath | ★3 700% → 800%, DMG tertunda 345% → 400% | file dan Detail Hero 18 Nov: **635%** |
| Skill hero | Kimmy / Traction Pulse | ★3 1.925% → 2.150%, 825% → 925% | melanjutkan 20/11 |
| Skill hero | Argus / Warmonger | ★3 600% → 700% | |
| Skill hero | Lolita / Noumenon Blast | ★3 1.700% → 1.950%, DMG berbasis HP 12% → 15% | file: **1455%** |
| Skill hero | Yu Zhong / Soul Grip | ★3 900% → 1.050%, fase ketiga 1.120% → 1.300% | |
| Skill hero | Sora / Sundering Strike | ★3 1.000% → 1.200% | |
| Skill hero | Karina / Dance of Death | ★2/★3 450%/500% → 500%/600% | |
| Skill hero | Erza / Heaven's Wheel Armor | Shield ★2/★3 750/1.800 → 1.050/2.400; Physical ATK ★2/★3 15%/40% → 20%/50% | |
| Skill hero | Balmond / Lethal Counter | Shield per target ★3 9% → 7%; Batas Mana ★3 120 → 170 | melanjutkan 20/11 |
| Skill hero | Popol / Icefield Strike | ★1/★2: tombak 27 → 18, DMG per serangan dan saat Freeze berakhir 30%/35% → 50% | melanjutkan 20/11 |
| Skill hero | Bane / Deadly Catch | Freeze ★2 1,8 → 1,2 detik | panel 27 Nov pagi masih 1,8 |

`mc_validate.py`: 46 baris patch note terbaca dari 30 layar, tidak ada lagi yang "belum dicatat". Titan "18% → 15%" berstatus "sudah di data"
karena angka 15% kebetulan ada di teks Titan; Lolita "12% → 15%" "tidak bisa dipastikan". Keduanya tercatat lewat skill Balmond dan Lolita.

### Teks yang diganti server (tidak ada di file game, tanpa perubahan angka)

- **Titan, mode Lite** (2024): "Saat pertarungan dimulai, Hero Titan di Mech Platform berubah menjadi Super Mecha untuk
  bertarung dan mendapatkan efek atribut dari Hero Titan lainnya." File: "Hero Titan di Mech Platform berubah menjadi Super
  Mecha pada awal pertarungan. Super Mecha juga mendapatkan Atribut Mecha dari Hero Titan."
- **Frostrider, mode Lite** (2058): "Setelah Penunggang menaiki Tunggangan, keduanya bertarung sebagai satu unit. Penunggang
  mendapatkan atribut dan peningkatan skill dari Tunggangan." File: "Hero Frostrider mendapatkan skill dan atribut yang
  diperkuat saat dipasangkan dengan Tunggangan."
- **Dawnbringer** (2089–2098): teks Lite ("… melalui **Peningkatan**", file "Pertumbuhan"), teks Penuh ("Mendapatkan 1 Equipment
  Dawnbringer setiap kali Jumlah Sinergi mencapai 2, 4, atau 6. …"), judul kolom ("Total Jumlah Equipment Dawnbringer" /
  "Stack Peningkatan Equipment Dawnbringer Baru", file "Jumlah Equipment Dawnbringer" / "Jumlah Baru") dan baris 10
  ("… mendapatkan 32 stack Peningkatan. Makin banyak stack peningkatan, makin kuat pula efek Equipment Dawnbringer."). Angka
  tabel (1/2/3, 7/14/32) sama dengan file.
- Teks Lite tidak ada di `RelationSkillTip`: sumbernya `mSkillDescriptionNew` di `RelationSkill_MC_S8` (Deadeye 2113 sama persis).
  Ketiga teks di atas tidak ada di tabel mana pun di client (dicari langsung di semua file tabel), jadi dikirim server,
  sama seperti teks commander Vexana/Lukas/Dyrroth/Lunox di S7.

### Lainnya

- Equipment Dawnbringer yang Diperkuat (Skywrath Spear, Horn of Prosperity, Direwolf's Devastator): tabel 22.5%
  (2250 × 0,0001), panel menampilkan 22%. Data tetap 22.5%; `mc_validate.py` mencatatnya di Cakupan, bukan Selisih.
- Swiftblade (2122–2125): ikon di belakang angka terbaca "1530", "2530", "1004"; dicek mata: 10/25, 15/50, 25/100 cocok.
- Layar Vexana ponsel 20 Nov 21:20 tetap tercatat Selisih di `VALIDASI_S8_auto.md`: Unrestricted menulis 4 Gold, bukan nilai
  file (6) maupun nilai server terakhir (2). Lylia (1986) = "Shop" terbaca "S.b22".
- 2 rujukan ikon kartu tidak ada di atlas game (`GOGO_Icon_2022_mini`, `GOGO_Icon_503_mini`); atlas hotfix
  `mini_patch/…/Atlas_GoGoCard_04_MC` juga tidak memuat 503 (yang ada `GOGO_Icon_1503_mini`).
- Belum ada screenshot (per 27 Nov sore): 5 kartu di atas (Odette's Power ×2 juga tidak muncul di rekaman Odette), Alpha ★4, angka baru
  Kalea 26/11, hero di dalam Go Go Box. Hero panggilan, Chrono Wanderer, Fan yang Bersorak, Toko Spirit Sand S8 (11/11), Go Go Box I-4 s/d
  V-6, commander Odette, dan Patch Note 26/11 sudah dicek 27 Nov (bagian di atas).
