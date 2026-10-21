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

## Catatan

- Aturan equipment aktif (`m_DropState`) disimpulkan dari data + screenshot (cocok 67/67), bukan dibaca dari kode game.
  Aturan kartu aktif (`m_Value1–3`) dibaca dari kode galeri in-game.
- X.Borg Bintang 3 kini "total 2000% ATK … sebanyak 10 serangan" (rumus `N*10` yang sama dengan Rising Fury); belum bisa
  dicek karena tidak ada screenshot X.Borg.
- "Jangkauan ATK" hero tidak dibandingkan karena tidak tersimpan sebagai kolom tabel.
