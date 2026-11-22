# Validasi S8.html terhadap screenshot in-game

- Versi game `1.3.32.354.1` (client PC dipasang 18 Nov), Season 8 "Arena Para Penyihir" (aktif sejak 2026-11-15, Rank
  Season 10 s/d 2027-01-24), diperiksa 2026-11-22.
- Cara: 562 gambar di `patch-tracker/screenshot/season 8/` di-OCR (`ocr_screens.ps1 -Season 8`, 6 menit 52 detik, 0 gagal),
  dicocokkan otomatis (`mc_validate.py --season 8` → `VALIDASI_S8_auto.md`), lalu setiap selisih dan cek manual dilihat dengan mata.
- S8 di data versi lama (`1.3.24.344.1`) adalah data pra-season. Client baru mengubah banyak angka: 42 hero, 6 sinergi,
  14 commander (+ Odette), 23 kartu baru / 5 dihapus / 36 berubah, 7 equipment baru / 27 berubah
  (`data/diff/1.3.24.344.1_vs_1.3.32.354.1_S8.md`). Validasi ini memakai data versi baru.

## Isi folder (dikenali dari OCR, bukan dari nama folder)

| Folder | Gambar | Isi |
|---|---|---|
| hero and synergies | 217 + 11 MP4 | 102 Detail Hero, 113 Panduan Sinergi (tata letak baru S8), 2 galeri hero. MP4: 6 rekaman PC video pratinjau sinergi (Deadeye: Critical Chance 20/35/60% dan Critical DMG 130/160/220% = tabel 5+15, 10+25, 20+40 dan +30/60/120%), 5 video YouTube |
| commander | 47 | 41 layar detail (PC 18 Nov + Vexana di ponsel 20 Nov 21:20 dan 21 Nov 03:41), 3 layar Ganti Commander (Lucky Commander) |
| equipment | 131 | panel detail semua tab |
| go go card | 54 | galeri; S8 tidak punya tab "Kartu Power" lagi (Semua / Oranye / Ungu / Biru) |
| ensiklopedia | 16 | 8 tab |
| update patch | 50 + 4 MP4 | 18 Patch Note Season 8.0 (PC 18 Nov), 5 layar ponsel 20 Nov (Penyesuaian Keseimbangan 20/11 + pengumuman skor leaderboard), 27 layar Panduan Season (Ringkasan Sinergi sinergi baru, tab Lineup Kuat). MP4 = video YouTube |
| match | 47 + 5 MP4 | layar hasil: 33 bertanggal 1–7 Nov (masih S7), 14 bertanggal 16–21 Nov (S8). 5 rekaman ponsel 20 Nov (11 GB, disalin 22 Nov) belum diproses |

## Hasil per bagian

| Bagian | Layar | Cakupan | Hasil |
|---|---|---|---|
| Hero (Detail Hero) | 102 | 52 dari 52 hero toko | Stat ★1–★3 dan tabel Atribut Skill cocok (Zhuxin dicek mata: judul terbaca "Zhuxm"). 7 teks Elemental Mark cocok setelah perbaikan |
| Sinergi (Panduan Sinergi) | 113 | 20 dari 22 sinergi | 318 baris tabel tingkat cocok. Teks Lite/Penuh cocok kecuali 3 teks yang diganti server (lihat bawah) |
| Commander | 44 | 40 dari 41 (Odette tanpa screenshot) | Nama skill, Aktif/Pasif, angka cocok. 6 cek manual = salah baca OCR ("/" jadi "1", judul skill Lv 2 Aamon tidak terbaca) |
| Equipment | 131 | 113 dari 113 level aktif | Cocok. 8 cek manual dicek mata (Inspire 20/25/30/40%, Guardian Helmet yang Diperkuat 2 pasif, Spellblade Talisman 1 pasif) |
| Go Go Card | 54 | 195 dari 200 kartu aktif | Cocok. Tidak terlihat: Journey's Windfall, Fury's Edge (Bisa Berubah Sewaktu-waktu), Victory's Blessing, Odette's Power ×2 (semuanya kartu baru client ini) |
| Ensiklopedia | 16 | 8 tab | Cocok (tabel DMG Commander 3/5/6/7/11/13/14/15, biaya naik level, Magic Crystal Pilihan, Wheel of Fate) |
| Patch Note | 23 | Season 8.0 + 20/11 | 9 baris sudah di file game, 7 baris diterapkan server (semua tercatat di `server_patch.json`), 2 tak bisa dipastikan otomatis (Frostrider rasio Hybrid ATK, Shield Balmond; keduanya tercatat), 2 judul rusak OCR ("S_ Frostrider" ganda; "Vale's Power" terbaca "Yaelned'aSpaPtOkaWne1r k", kartunya di file sudah 2 Gold) |
| Toko Spirit Sand, Go Go Box | 0 | — | Belum ada screenshot S8 |

## Kesalahan yang ditemukan dan sudah diperbaiki di `mc_data.py`

| Temuan | Sebelum | Sesudah (= game) | Penyebab |
|---|---|---|---|
| Teks Elemental Mark FAIRY TAIL: Gray, Wendy, Juvia, Erza, Lucy, Natsu, Magic Crystal FAIRY TAIL (Mystic) | "Freeze 0/0/0/0/0/0 detik", "-1 / -1 / …", "-0.01% / …" | Gray 0.2/0.4/0.6/0.75/1.05/1.4 detik, Wendy 5/15/20/25/40/50, Juvia 20%/25%/30%/35%/40%/40%, Erza 10/20/25/30/45/55, Lucy 25%/35%/40%/45%/50%/50%, Natsu 30%/…/215%, crystal 40% (layar 2144–2222, 2330) | kolom ke-5 placeholder berisi angka saja (`0.001`, `-1`, `-0.01`, `100`) dibaca sebagai konstanta, padahal pengali; kolom ke-7 (`|0|1` … `|0|6`) = level efek per jumlah Elemental Mark, dulu diabaikan. Hanya dipakai tabel S8; ekspor S7 identik |
| Baris teks FAIRY TAIL 10 | "freeze … selama 10% detik … sebesar ?" | "freeze … 0.5 detik … True DMG 10% HP … 20%" (layar 2039) | teks baris memakai daftar angka tabel (`m_NumDescribeTag`, tanpa durasi); seharusnya `m_SpecialNumDescribe` → `m_NumDescribeNew` |
| Panduan Sinergi S8 tidak tergambar | hanya teks lama `mRelationExplain` + teks per tingkat | ditambah `explain_lite` (tombol Lite = `mSkillDescriptionNew` baris tingkat), `explain_full` (tombol Penuh = `mRelationExplainNew`, `${TagN}$` = nama kata kunci), `table` (judul kolom `DescriptionIcon.mIconDescription` dari `m_RelationEffectTag`, sel `mNumDescribeTag1..n` + `m_NumDescribeTag`, teks baris `mSpecialDescription`), `details` (tooltip kata kunci) | UI baru client 1.3.32.354.1; tampil di tab Sinergi S8.html dan S8.md |

Perbaikan alat pemeriksa (`mc_validate.py`): galeri kartu S8 tanpa tab Kartu Power, layar Commander ponsel ("+ Commander"),
judul Commander rusak OCR (Nana "Cc uma de"), tabel Panduan Sinergi (baris dicocokkan lewat isinya karena label tingkat
2/4/6 tidak terbaca; "%" terbaca "0/0"; ikon di belakang angka terbaca satu digit tambahan), judul sinergi "+ Stargazer",
teks commander dari server (`description_server`), pecahan atribut yang dipotong panel, baris lanjutan patch note.
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
  `GetRouletteWeight` (`m_Weight`, atau `m_NewPlayerWeight` bila `ShouldUseNewPlayerWeight`), urutan tampil menurut `m_Order`; efek
  diterapkan lewat `SetGoGoCardFilter`/`IsCardTagAllowed` (tag kartu), `ModifyGoGoCardQuality` (kualitas), `ModifyGoGoCardRoundData`
  (babak), `CreateShareGoGoCard` (kartu sama untuk semua). Id terpilih disimpan di `MCLogicGlobalComp.m_iGoGoRouletteId`.
- **Isi `MCRoulette` (12 baris, 9 aktif, total bobot 15; pemain baru total 4):**

| Efek | Peluang (bobot) | Pemain baru | Aturan |
|---|---|---|---|
| Crystal Legend | 13,3% (2) | 25% (1) | putaran 1: hanya Kartu Badge Sinergi, kualitas Ungu |
| Commander's Power | 13,3% (2) | – | putaran 1: hanya Kartu Power, kualitas Oranye (`m_SpecialRules` [1,1,1], artinya belum diketahui) |
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
- **Belum diketahui dari data:** berapa segmen yang tampil di roda (ikon terlihat berulang, mis. ikon merah muda di kiri dan kanan)
  dan arti `m_SpecialRules` Commander's Power. Diekspor ke S8.json (`wheel_of_fate`), S8.md, dan tab Info Season S8.html.

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
- Belum ada screenshot: commander Odette, 5 kartu di atas, hero panggilan (Alpha, Bane, Gatotkaca, Moskov), sinergi Chrono
  Wanderer dan Fan yang Bersorak, Toko Spirit Sand S8, Go Go Box S8.
