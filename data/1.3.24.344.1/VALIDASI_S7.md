# Validasi S7.html terhadap screenshot in-game

- Versi game `1.3.24.344.1`, Season 7 "Chrono Echoes", diperiksa 2026-10-20.
- Cara: teks ke-422 screenshot di `patch-tracker/screenshot/season 7/` dibaca dengan OCR bawaan Windows lalu
  dicocokkan otomatis dengan `S7.json` (sumber S7.html). Setiap selisih dicek ulang dengan melihat screenshot-nya.
- Selisih yang ternyata hanya salah baca OCR (mis. `II-3` terbaca `11-3`, `30%` terbaca `300/0`, panel yang di-scroll)
  tidak dihitung sebagai kesalahan.

## Hasil per bagian

| Bagian | Screenshot | Cakupan | Hasil |
|---|---|---|---|
| Hero (Detail Hero) | 136 | 52 dari 52 hero toko | Stat ★1–★3, nama skill, tabel Atribut Skill cocok (setelah perbaikan) |
| Sinergi (Panduan Sinergi) | 21 | 20 dari 22 sinergi | Penjelasan & angka tiap tier cocok |
| Commander | 60 | 40 dari 40 commander | Nama skill, label Aktif/Pasif, deskripsi cocok (setelah perbaikan) |
| Detail tooltip commander | 10 (dikirim di chat) | 10 tooltip di 8 commander (semua yang ada di S7) | Alucard, Diggie ×2, Franco, Freya ×2, Johnson (15 ikon sinergi), Kalea, Luo Yi, Lylia: teks & angka cocok |
| Equipment | 136 | 110 dari 110 level equipment aktif | Ringkasan, atribut, atribut unik, pasif cocok (setelah perbaikan; Haas' Claws dasar/diperkuat di screenshot 1665/1666) |
| Go Go Card | 58 | 199 dari 199 kartu aktif | Deskripsi cocok; tidak ada kartu "nonaktif" yang tampil di game |
| Ensiklopedia | 15 | 8 tab | Teks, peluang toko, biaya level, tabel DMG Commander cocok |
| Update Patch | 17 | Patch Note 7.2 | Lihat bagian "Yang memang berbeda" |

Tidak ada screenshot untuk: hero panggilan (Alpha, Gatotkaca, Layla, Moskov, Novaria, X.Borg) serta sinergi Chrono Wanderer
dan Fan yang Bersorak. (Kagura, Popol & Kupa, dan Haas' Claws ternyata ada; judulnya hanya tidak terbaca OCR.)
Pengecekan otomatis yang sama kini bisa diulang dengan `ocr_screens.ps1` + `mc_validate.py` (hasil: `VALIDASI_S7_auto.md`).

## Kesalahan yang ditemukan dan sudah diperbaiki di `mc_data.py`

| Temuan | Sebelum | Sesudah (= game) | Penyebab |
|---|---|---|---|
| Baxia "Persentase Shield" | 10000%/10000%/12000% | 10%/10%/12% | faktor skala `0.001` di placeholder diabaikan |
| Vexana "DMG Berkelanjutan" | 22.5%/22.5%/50% | 450%/450%/1000% | rumus `N*20` di placeholder diabaikan |
| Fanny "Bonus Physical" ke-3, Lancelot "Bonus Physical"/"DMG Jalur" | 0%/0%/0% | 270/270/670%, 140/160/450% | efek rasio biasa menyimpan nilai di `FPara1`, bukan kolom yang ditunjuk |
| Rising Fury Ⅰ/Ⅱ/Ⅲ | "… hingga 1.5%/2.5%/5%" | "… hingga 15%/25%/50%" | rumus `N*10` diabaikan |
| Solid Alliance Ⅱ | 2% Hybrid ATK | 3% Hybrid ATK | kartu memakai level skill 2, skrip selalu level 1 |
| Deskripsi skill commander (Alice, Johnson, Ling, Zilong, Angela, Dyrroth, Valir, Yu Zhong, Luo Yi, Lunox, Gusion, Lukas) | versi pendek | versi panjang seperti di layar Commander | layar Commander memakai `SkillExtraDesc_MC` |
| Teks dengan kutip CSV (Johnson "Spanner Spin", Starbelle "Lightstick") | `""Spanner Spin""` | `"Spanner Spin"` | kutip CSV tidak dibersihkan |
| Atribut equipment | "+10% Physical ATK; +10% Magic ATK" | "+10% Hybrid ATK" (juga Hybrid DEF) | game menggabungkan nilai Physical + Magic yang sama |
| Equipment yang tampil | 94 (termasuk Lightstick & Choice Magic Crystal ganda) | 67 aktif + 27 ditandai nonaktif | hanya `m_DropState = 1` yang muncul di game (67/67 cocok) |
| Hero panggilan | tampil seperti hero toko | diberi label "Hero panggilan" / `*` | game tidak menjual mereka di Toko dan tidak menampilkan Chrono Wanderer di daftar hero sinergi Role |

Perbaikan sebelumnya di sesi yang sama (sudah dicek ke screenshot juga): skill hero lama yang kosong (Eudora, Angela, Hilda,
Karrie, Zilong, Minotaur) dan teks pasif Supreme Blades.

## Yang memang berbeda (bukan kesalahan ekstraksi)

Patch Note 7.2 (layar Update Patch) mencantumkan perubahan angka yang tidak ada di file game lokal. Menu in-game di
screenshot juga masih menampilkan angka lama, yang sama dengan file game; angka baru diterapkan dari server saat bertanding.
Perubahan ini dicatat di `server_patch.json` dan ditampilkan di S7.html sebagai catatan oranye "Patch 7.2 (server)": angka hero
di tab Hero, deskripsi kartu/skill commander sudah memakai nilai baru, dan ringkasannya ada di tab "Patch Server".

| Item | Laporan / menu in-game | Patch Note 7.2 |
|---|---|---|
| Alpha HP ★1/★2 | 5000 / 9500 | 5400 / 10260 |
| X.Borg Hybrid ATK ★1/★2 | 240 / 365 | 260 / 395 |
| Gatotkaca Hybrid ATK ★1/★2 | 230 / 345 | 250 / 375 |
| Karina Hybrid ATK ★2/★3 | 215 / 285 | 200 / 260 |
| Mathilda Hybrid ATK ★2/★3 | 155 / 210 | 145 / 195 |
| Dyrroth Abyssal Devourer / Abyssal Favor | mulai Babak I-4 / 2 EXP | mulai I-3 / 3 EXP |
| Aurora Frost Treasures | minimal 7 Gold | minimal 8 Gold |
| Dimensional Shot Ⅰ / Ⅱ | 4% / 6% per petak | 5% / 8% |
| Death Oracle | 30 Shield | 35 Shield |
| Lunox's Power | 10 Gold, +20 Gold | 8 Gold, +18 Gold |
| Angela's Power | 100/190/320/540 Magic DMG | 100/190/300/500 |
| Divine Execution | HP di bawah 16% | 14% |
| Healing Fountain | 6 Gold | 4 Gold |
| Transmutation | setelah 4 babak | setelah 5 babak |
| Solid Alliance Ⅰ & Ⅱ | masih aktif (juga masih tampil di menu Go Go Card) | dihapus sementara |

Konten baru di patch yang sama sudah ada di laporan: 8 Go Go Card sinergi Role baru (Knockout Punch, Aftershock, Blazing Valor,
Whirl of Carnage, Hail of Shots, Star Chorus, Shrouded Blade, Critical Spellcraft), Equipment Reforger, Chrono Wanderer
(Layla, Novaria), revamp Lukas, Vexana's Power, Novel Equipment 3 Equipment, Magic Surge 100% Mana.

## Toko Spirit Sand (31 Okt, 54 layar toko dari 3 pertandingan)

Semua 11 item terlihat dan harganya cocok dengan `special_store`. Kenaikan baris "ATK/HP rekan meningkat sebesar X%" setelah membeli:

| Item | Kenaikan in-game | Contoh screenshot | Data |
|---|---|---|---|
| ATK Rekan +1% | +1 | 1903→1904 (0→1), 1916→1917 (10→11) | 1 stack |
| ATK Rekan +2% | **+3** | 1908→1909 (1→4), 1923→1924 (14→17) | 3 stack |
| ATK Rekan +3% | **+5** | 1914→1915 (5→10), ponsel 03-35-48→03-35-54 (1→6) | 5 stack |
| HP Rekan +1% | +1 | 1917→1918 (4→5), ponsel 03-38-09→03-38-12 (5→6) | 1 stack |
| HP Rekan +2% | +2 | 1909→1910 (0→2), 1925→1926 (5→7) | 2 stack |
| HP Rekan +3% | +3 | ponsel 03-39-17→03-39-21 (6→9) | 3 stack |

Harga merah 1 Equipment Acak yang Diperkuat (80) tidak terbaca OCR dan dicek langsung di screenshot ponsel 03-38-09.

## Hero panggilan (31 Okt, panel unit dalam pertandingan di `match/`)

Layar Detail Hero toko tidak menampilkan hero panggilan, jadi dicek dari panel unit saat bertanding, dengan mata (OCR tidak membaca
angka HP di atas bar; `mc_validate.py` tetap menulisnya "Tanpa screenshot"). Semua cocok dengan S7.json + `server_patch.json`.

| Hero | Bintang | HP | Mana awal | Hybrid ATK | DEF | ATK Speed | Jangkauan | Bukti |
|---|---|---|---|---|---|---|---|---|
| Alpha | ★1 | 5400 (server) | 40 | 295 | 48 | 0,75 | 2 | 04-45-54 |
| Alpha | ★2 | 10260 (server) | 40 | ada bonus equipment | ada bonus | ada bonus | 2 | 04-53-39 |
| Novaria | ★1 | 3565 | 30 | 195 (server) | 24 | 0,75 | 4 | 13-44-08 |
| Novaria | ★2 | 7059 (6417 + bonus 10%) | 30 | 413 = 295 × 1,4 | 24 | 0,75 | 4 | 13-53-51 |
| Gatotkaca | ★1 | 4335 | 80 | 250 (server) | 48 | 0,65 | 1 | 15-27-41 |
| Gatotkaca | ★2 | 7805 | 80 | 488 = 375 × 1,3 | 48 | 0,65 | 1 | 15-32-16 |
| X.Borg | ★1 | 4075 | 80 | 260 (server) | 42 | 0,75 | 1 | 15-57-21 |
| X.Borg | ★2 | 7335 | 80 | 395 (server) | 42 | 0,75 | 1 | 16-04-06 |
| Layla | ★1 | 3565 | 30 | 300 (server) | 24 | 0,80 | 4 | 16-14-34 |
| Layla | ★2 | 6417 | 30 | 562 = 450 × 1,25 | 24 | 0,80 | 4 | 16-26-00 |
| Moskov | ★1 | 3565 | 60 | 275 = 220 × 1,25 | 24 | 0,95 dengan bonus (Layla sama di 16-40-22) | 4 | 19-31-00 |
| Moskov | ★2 | 6417 | 60 | 412 = 330 × 1,25 | 24 | 0,95 dengan bonus | 4 | 19-35-46 |

Panel menampilkan "mana/Batas Mana Awal" (0/30, 0/80), jadi angkanya sama dengan kolom Batas Mana Awal. Hero panggilan ★3 pertama: Novaria, 31 Okt 23:31 (tabel berikutnya).

Tooltip skill menampilkan nilai mutlak (dibulatkan ke bawah), jadi persentase data terbukti lewat hitungan:

| Hero | Layar | Tooltip | Hitungan dari data |
|---|---|---|---|
| Layla ★1 | 19-56-51 | (+405), (+585), (+480) | 135%, 195%, 160% × ATK 300 |
| Layla ★2 | 20-04-23 | (+912), (+1276), (+1094) | 150%, 210%, 180% × ATK 608 |
| Alpha ★1 | 04-48-35 | (+398), teks ★3 (+4779) | 135%, 1620% × ATK 295 |
| Alpha ★1 | 04-52-19 | (+866), teks ★3 (+11696) | 120%, 1620% × ATK 722 |
| Moskov ★2 | 19-35-51 | (+1314), teks ★3 (+4780) | 275%, 1000% × ATK 478 |

Teks skill Alpha, Layla, Moskov sama dengan data, selain salah baca OCR. Layla ★3 "3600% Physical ATK" juga cocok.

### Tooltip Novaria, Gatotkaca, X.Borg (31 Okt 22:54 – 1 Nov 03:10, `match/` dan `match/practice bot/`)

Semua angka (+N) tooltip baru dihitung balik dari persentase S7.json: tiap layar hanya pas dengan satu pasang bintang dan ATK. Kalimat skill, tabel
Atribut Skill, Shield 10%/12%, pulih 700/1200 HP, airborne 1,2 detik, dan ATK Speed Moskov 20%/25% juga sama dengan data.

| Hero | Layar | Tooltip | Hitungan dari data |
|---|---|---|---|
| Novaria ★1 | 23-15-03 | (+1521), (+105) | 650%, 45% × Magic ATK 234 |
| Novaria ★1 | 23-15-17 | (+1651), (+114) | 650%, 45% × Magic ATK 254 |
| Novaria ★2 | 23-29-56 | (+2996), (+214) | 700%, 50% × Magic ATK 428, bukan Physical ATK 324 |
| Novaria ★3 | 23-31-45 | (+32760), (+16380) | 4000%, 2000% × Magic ATK 819 |
| X.Borg ★1 | 23-21-17, 02-09-25 | (+65), (+1040), teks ★3 (+5200) | 25%, 400%, 2000% × ATK 260 |
| X.Borg ★2 | 23-23-19 | (+94), (+1705), teks ★3 (+7580) | 25%, 450%, 2000% × ATK 379 (panel 395 di 23-23-15, sudah 363 saat tooltip dibuka; ketiga angka hanya pas dengan 379) |
| X.Borg ★2 | 02-11-30 | (+98), (+1777), teks ★3 (+7900) | 25%, 450%, 2000% × ATK 395 |
| Gatotkaca ★1 | 02-48-18 | (+462), (+625), (+412), teks ★3 (+437) | 185%, 250%, 165%, 175% × Magic ATK 250 |
| Gatotkaca ★1 | 02-49-48 | (+555), (+750), (+495), teks ★3 (+525) | persentase sama × Magic ATK 300 |
| Gatotkaca ★2 | 02-55-38 | (+1094), (+1032), (+681), teks ★3 (+722) | 265%, 250%, 165%, 175% × Magic ATK 413 |
| Gatotkaca ★2 | 02-56-14 | (+1340), (+1265), (+834), teks ★3 (+885) | persentase sama × Magic ATK 506, bukan Physical ATK 413 |
| Moskov ★1 | 22-54-23, 02-04-25 | (+572), (+2200); (+772), (+2970) | 260%, teks ★3 1000% × ATK 220 dan 297 |
| Moskov ★2 | 02-09-06 | (+1226), teks ★3 (+4460) | 275%, 1000% × ATK 446 |
| Layla ★1 | 02-25-43, 02-31-09 | (+567), (+819), (+672) | 135%, 195%, 160% × ATK 420 |

**X.Borg ★3 terbukti tanpa harus punya X.Borg ★3.** Tooltip dalam pertandingan menulis (+7580)/(+7900) = 2000% × ATK dan tabelnya "Bonus Physical
2000% 2000% 2000%". Editor lineup (`practice bot/` 03-10-03) menulis rumusnya: "memberikan total (+2000% Total Physical ATK) Physical DMG sebanyak 10
serangan dalam 2 detik". S7.json menulis "2000% ATK": nilainya benar, labelnya lebih pendek. Label umum itu datang dari `FORMULA_KINDS` dan dipakai 30 skill
hero; dibiarkan karena baru X.Borg yang terlihat di editor lineup. Gatotkaca "175% ATK" ternyata Magic ATK, bukti (+885) dengan Physical ATK 413.

**Sinergi Chrono Wanderer** (13-46-02, 13-46-07): "Hero 5 Gold yang dipanggil oleh Echomancer." sama dengan `explain`; efek in-game
"Dapatkan bonus Sinergi Echomancer", data "Mendapatkan bonus atribut dari Sinergi Echomancer." (kalimat ini juga tampil di panel kecil 13-46-02).

## Go Go Box (31 Okt, layar Pilih Hadiah 17-05-38 sampai 17-05-48)

Layar sisa 20 detik: 8 orb utuh = 6 equipment + Dapatkan Sinergi Dragoncaller + Kapasitas +1, ditambah 3 hero. `mc_validate.py` memeriksanya
otomatis sejak 31 Okt: layar tidak punya label babak, jadi babaknya dikenali dari susunan orb, dan hasilnya hanya cocok dengan II-6. Dua layar
berikutnya menampilkan orb tersisa setelah pemain lain memilih, tanpa selisih.

## Go Go Box (1 Nov, layar hitung mundur "Segera Dimulai", 16 gambar)

Layar sebelum Pilih Hadiah, jadi semua orb masih ada: 8 frame rekaman 21 Okt yang dijeda di VLC (`match/Go Go Box <n> …`), 5 layar pertandingan 1 Nov
(`match/Go Go Box setelah …`), 3 layar lawan bot (`match/practice bot/`). `mc_validate.py` mengenalinya sejak 1 Nov. OCR Windows hanya membaca 5–7 dari 8
label, jadi layar Go Go Box dibaca ulang dengan RapidOCR: 8 dari 8, sama dengan bacaan mata. Label baru memudar masuk di hitungan 2; di hitungan 3 belum ada.

| Babak | Data (equipment + crystal + Kapasitas) | Label terbaca RapidOCR | Tanpa label utuh (mata, sebagian dikonfirmasi ikon) |
|---|---|---|---|
| I-4 | 8 + 0 + 0 | 2 frame VLC: 8 + 0 + 0 | `setelah I-4`, `setelah I-4 (2)`, bot: 8 + 0 + 0 |
| II-6 | 5–6 + 1–2 + 1 | frame VLC 6 + 1 + 1 dan 5 + 2 + 1, `setelah II-6 (2)` dan bot 6 + 1 + 1 | `setelah II-6`: 6 + 1 + 1 |
| III-6 | 4 + 2 + 2 | 2 frame VLC: 4 + 2 + 2 | `setelah III-6`, bot: 4 + 2 + 2 |
| IV-6 | 3–4 + 3–4 + 1 | 2 frame VLC: 4 + 3 + 1 | – |

- Semua label ada di pool babaknya. Orb merah muda bergambar kucing = Feline Blade "CC Tunggal", orb teal di `setelah III-6` = Magic Crystal Echomancer.
- Pencocokan ikon (`mc_vision`, 3–7 dari 8 orb per layar) tidak bertentangan dengan bacaan mata di 6 layar tanpa label utuh. Jumlah per jenisnya tetap bacaan mata.
  Satu orb di `setelah III-6` tertutup crystal: bagian yang terlihat bergambar equipment, bukan koin crystal, tapi namanya tidak bisa dipastikan.
- Hero III-6 dan IV-6 di 4 frame VLC (12 slot, dibaca dari lencana sinergi): Odette, Badang, Baxia, Alice, Thamuz, Fanny, Nana. Semua 5 Gold, sesuai data.
  Hero I-4 dan II-6 tidak dicek ulang di sini.
- V-6 dst. punya jumlah yang sama dengan IV-6 dan layarnya tanpa label babak, jadi catatan otomatis ikut menyebut babak itu. Pertandingan terekam baru sampai IV-6.

## Commander Lukas, Dyrroth, Lunox (31 Okt, layar Commander ponsel)

Teks skill di ponsel sudah memuat Penyesuaian 28/10: Lukas Sacred Gift "3 hingga 4 kali lipat", Dyrroth "Mulai Babak I-3", "4 EXP Commander",
"Setelah setiap 1 kali melahap", Lunox Power of Order "2 Hero acak ... dan 4 Gold". Teks Power of Chaos tidak berubah. Jadi baris Patch Note
"Power of Chaos: Jumlah Hero dengan Blessing 3 >> 2" sebenarnya mengubah jumlah Hero acak di Power of Order.

## Catatan

- Aturan equipment aktif (`m_DropState`) disimpulkan dari data + screenshot (cocok 67/67), bukan dibaca dari kode game.
  Aturan kartu aktif (`m_Value1–3`) dibaca dari kode galeri in-game.
- X.Borg Bintang 3 "total 2000% ATK … sebanyak 10 serangan" (rumus `N*10` yang sama dengan Rising Fury) terbukti 1 Nov, lihat bagian Hero panggilan.
- "Jangkauan ATK" hero tidak dibandingkan karena tidak tersimpan sebagai kolom tabel.
