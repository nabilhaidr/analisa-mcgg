# Validasi otomatis Season 7 (data 1.3.24.344.1)

- Dibuat 2026-10-31T04:58:30 oleh `mc_validate.py` dari `screenshot\season 7\ocr.json`.
- **Selisih** = terbaca jelas tapi beda dengan data. **Cek manual** = kemungkinan salah baca OCR / panel di-scroll; lihat screenshot-nya.

| Bagian | Layar | Selisih | Cek manual | Cakupan |
|---|---|---|---|---|
| Hero | 103 | 0 | 1 | 52 dari 52 hero toko punya screenshot Detail Hero |
| Sinergi | 22 | 0 | 1 | 20 dari 22 sinergi punya screenshot Panduan Sinergi |
| Commander | 45 | 0 | 4 | 40 dari 40 commander punya screenshot detail; 35 nama terbaca di daftar commander |
| Equipment | 134 | 0 | 6 | 110 dari 110 level equipment aktif punya screenshot panel detail |
| Go Go Card | 58 | 0 | 4 | 199 dari 199 kartu aktif terlihat di screenshot Go Go Card |
| Ensiklopedia | 15 | 0 | 2 | 15 screenshot dicocokkan dengan 8 tab Ensiklopedia |
| Toko Spirit Sand | 54 | 0 | 3 | 10 dari 11 item terlihat dengan harga; 11 pembelian sesuai stack data |
| Patch Note | 27 | 0 | 0 | 49 perubahan terbaca dari 27 screenshot patch note |

## Selisih

Tidak ada.

## Cek manual

### Hero (1)

- `hero and synergies\Screenshot (1577).png`: Minotaur ★1 HP: game 030, data 2030

### Sinergi (1)

- `match\commander vexana\Screenshot_2026-10-31-04-15-45-812_com.mobilechess.mi.jpg`: SPECTRE: penjelasan beda
  - game: menyebabkan ledakan. Setelah itu, Alpha Saat mendapatkan Hero SPECTRE memanggil Beta untuk mengejar lawan di sepanjang SPECTRE + Bintang 2 dengan harga yang retakan. Basic ATK Alpha juga menembakkan Force Wave tambahan. ditentukan untuk pertama kali 4 Alpha Bintang 1 bergabung menjadi Alpha Bintang 1 Gold atau 2 Gold 2, dan 4 Alpha Bintang 2 bergabung menjadi Alpha Bintang 3. 3 Gold atau 4 Gold 40% Skill Commander Dyrroth, Vale, dan Alice tidak bisa digunakan pada Alpha. 5 Gold Peluang refresh Alpha di Toko sama dengan Hero 5 5 Gold 400% Gold. t) 11 Saat pertarungan dimulai, endapatkan 1 level Bintang; Hero SPECTRE +400% HP Lihåt RékomendasiILineyp1 •
  - data: Saat pertama kali mendapatkan Hero SPECTRE Bintang 2, kamu akan menerima Hero SPECTRE dengan harga yang lebih tinggi. Hero SPECTRE mendapatkan Peningkatan DMG.

### Commander (4)

- `commander\Screenshot (1460).png`: Lancelot / Golden Legacy: angka game ['213'] tidak ada di data
  - game: Tidak lagi mendapat Keuntungan. Mulai fase 1/11/111 dan seterusnya, mendapatkan 213/3 bonus Gold setiap babak. Pada akhir setiap babak, semua Gold digunakan untuk meningkatkan Lancelot.
  - data: Tidak lagi mendapat Keuntungan. Mulai fase Ⅰ/Ⅱ/Ⅲ dan seterusnya, mendapatkan 2/3/3 bonus Gold setiap babak. Pada akhir setiap babak, semua Gold digunakan untuk meningkatkan Lancelot.
- `commander\Screenshot (1468).png`: Wanwan / Tiger Pounce: angka game ['4301'] tidak ada di data
  - game: Saat HP Hero lawan di bawah 30% untuk pertama kalinya, Wanwan menyerang Hero lawan dengan HP terendah sebanyak 20 kali, memberikan 180 / 310 1 4301 550 Physical DMG berdasarkan fase saat ini.
  - data: Saat HP Hero lawan di bawah 30% untuk pertama kalinya, Wanwan menyerang Hero lawan dengan HP terendah sebanyak 20 kali, memberikan 180 / 310 / 430 / 550 Physical DMG berdasarkan fase saat ini.
- `commander\Screenshot (1477).png`: Yu Zhong / Soul Grip: angka game ['3.4'] tidak ada di data
  - game: Kualitas Go Go Card pada awal Babak 11-3 meningkat 1 level. Sebagai gantinya, mendapatkan Black Dragon Treasure acak jika sudah mencapai kualitas maksimum. Black Dragon Treasure (Mendapatkan 1 dari pilihan berikut secara acak): 1. 1 Magic Crystal Acak 2. 1 Equipment Acak dan 5 Gold 3.4 Hero acak dari Sinergi dengan jumlah terbanyak (dipengaruhi Oleh probabilitas refresh Toko saat ini) 4. 13 Gold
  - data: Kualitas Go Go Card pada awal Babak II-3 meningkat 1 level. Sebagai gantinya, mendapatkan Black Dragon Treasure acak jika sudah mencapai kualitas maksimum.  Black Dragon Treasure (Mendapatkan 1 dari pilihan berikut secara acak): 1. 1 Magic Crystal Acak 2. 1 Equipment Acak dan 5 Gold 3. 4 Hero acak dari Sinergi dengan jumlah terbanyak (dipengaruhi oleh probabilitas refresh Toko saat ini) 4. 13 Gold  (Penyesuaian Skill di Magic Crystal: Rune: Mendapatkan 1 Black Dragon Treasure secara acak pada awal Babak II-3.)
- `commander\Screenshot (1491).png`: Vale / Shifting Wind: angka game ['51719'] tidak ada di data
  - game: I penggunaan skill tambahan setiap kali Commander mencapai Level 51719.
  - data: Dapatkan 1 penggunaan skill tambahan setiap kali Commander mencapai Level 5/7/9.

### Equipment (6)

- `equipment\Screenshot (1643).png`: Inspire pasif: angka game ['20125'] tidak ada di data
  - game: Inspire: Memberikan 20125/30/ 40% ATK Speed (meningkat seiring berjalannya Fase).
  - data: Inspire: Memberikan 20/25/30/40% ATK Speed (meningkat seiring berjalannya Fase).
- `equipment\Screenshot (1644).png`: Inspire yang Diperkuat pasif: angka game ['20125'] tidak ada di data
  - game: Inspire: Memberikan 20125/30/ 40% ATK Speed (meningkat seiring berjalannya Fase).
  - data: Inspire: Memberikan 20/25/30/40% ATK Speed (meningkat seiring berjalannya Fase).
- `equipment\Screenshot (1674).png`: Holy Crystal yang Diperkuat: jumlah pasif game 0 vs data 1
- `equipment\Screenshot (1719).png`: Lightstick yang Diperkuat: jumlah atribut game ['+15% Max HP'] vs data ['+25% Hybrid ATK', '+15% Max HP']
- `equipment\Screenshot (1748).png`: Magic Crystal Bruiser: jumlah pasif game 0 vs data 1
- `equipment\Screenshot (1766).png`: nama equipment tidak dikenali: Meningkatkan ATK Speed

### Go Go Card (4)

- `go go card\Screenshot (1807).png`: Freya's Power: angka game ['14'] tidak ada di data
  - game: Ketika mengklaim hadiah saat Sinergi yang diperkuat berjumlah 2 14 / 6, mendapatkan IO Gold, 1 Peti Equipment, dan 1 Peti Equipment yang Diperkuat secara berurutan. (Eksklusif untuk Commander Freya)
  - data: Ketika mengklaim hadiah saat Sinergi yang diperkuat berjumlah 2 / 4 / 6, mendapatkan 10 Gold, 1 Peti Equipment, dan 1 Peti Equipment yang Diperkuat secara berurutan. (Eksklusif untuk Commander Freya)
- `go go card\Screenshot (1811).png`: Freya's Power: angka game ['14'] tidak ada di data
  - game: Ketika mengklaim hadiah saat Sinergi yang diperkuat berjumlah 2 14 / 6, mendapatkan IO Gold, 1 Peti Equipment, dan 1 Peti Equipment yang Diperkuat secara berurutan. (Eksklusif untuk Commander Freya)
  - data: Ketika mengklaim hadiah saat Sinergi yang diperkuat berjumlah 2 / 4 / 6, mendapatkan 10 Gold, 1 Peti Equipment, dan 1 Peti Equipment yang Diperkuat secara berurutan. (Eksklusif untuk Commander Freya)
- `go go card\Screenshot (1834).png`: Trust Fund: angka game ['8116'] tidak ada di data
  - game: Mendapatkan 8116 / 25 Gold secara berurutan saat mencapai Commander level 8 1 9 / 10.
  - data: Mendapatkan 8 / 16 / 25 Gold secara berurutan saat mencapai Commander level 8 / 9 / 10.
- `go go card\Screenshot (1842).png`: Rising Fury Ⅱ: angka game ['125%'] tidak ada di data
  - game: DMG rekan meningkat 2.5% untuk setiap detik mereka bertahan di pertarungan, hingga 125%.
  - data: DMG rekan meningkat 2.5% untuk setiap detik mereka bertahan di pertarungan, hingga 25%.

### Ensiklopedia (2)

- `ensiklopedia\Screenshot (1785).png`: Ensiklopedia: angka game ['70'] tidak ada di data
  - game: Level 5 Level 6 Level 7 Level 8 Level 9 Level 10 uu 70 34% 16% 13% 22% 40% 35% 25% 1% 50/0 100/0 26% 35% 1% 5% 14% 'Peluang Refresh Toko dalam Pertandingan
- `ensiklopedia\Screenshot (1787).png`: Ensiklopedia: angka game ['114', '1114'] tidak ada di data
  - game: oommanuer. 'Biaya Peningkatan Level 3 4 Gold yang @ 3 Dibutuhkan: 'DMG Commander @ 20 @ 32 @ 40 @ 54 10 9 (Maks) 74 DMG Commander: Setelah setiap babak, Commander yang menang memberikan sejumlah DMG ke Commander yang kalah. DMG bervariasi berdasarkan babak dan jumlah unit yang masih bertahan. DMG Commander = DMG Dasar Babak + Total Level Bintang Unit yang Masih Bertahan Babak 1-2 14 II-1 114 11-5 11-6 111-1 0>111-3 1114>111-6 tv-1>tv-3 >tv-6 V-1 •y V-5 DMG Dasar 3 5 6 7 11 13 14 15 Kasus Khusus: Unit non-Hero tertentu yang masih bertahan meningkatkan DMG Commander sebanyak 1. Jika babak berakhir seri, kedua belah pihak memberikan DMG satu sama Iain.

### Toko Spirit Sand (3)

- `match\spirit sand\Screenshot (1918).png`: HP rekan naik 1%, item yang dibeli ? memberi ? stack
- `match\spirit sand\Screenshot_2026-10-31-03-33-32-699_com.mobilechess.mi.jpg`: ATK rekan naik 1%, item yang dibeli ? memberi ? stack
- `match\spirit sand\Screenshot_2026-10-31-03-35-54-171_com.mobilechess.mi.jpg`: ATK rekan naik 5%, item yang dibeli ? memberi ? stack

## Patch note vs data

| Item | Patch note | Status di data |
|---|---|---|
| Dyrroth | Abyssal Devourer: Mulai Babak 1-4 >> 1-3, Dyrroth bisa melahap Hero Bintang 1 setiap 3 | belum: data masih nilai lama (diterapkan server) · tercatat di server_patch.json |
| Dyrroth | Abyssal Favor: Dyrroth mendapatkan 1 >> 3 EXP saat melahap Hero. | belum: angka baru tidak ada di data (diterapkan server) · tercatat di server_patch.json |
| Aurora | acak senilai minimal 7 >> 8 Gold. | belum: angka baru tidak ada di data (diterapkan server) · tercatat di server_patch.json |
| Chrono Wanderer | (baru) | ada di data |
| X.Borg | Hybrid ATK Dasar pada Bintang 112: 240/365 260/395 | belum: angka baru tidak ada di data (diterapkan server) · tercatat di server_patch.json |
| Gatotkaca | Hybrid ATK Dasar pada Bintang 112: 230/345 >> 250/375 | belum: angka baru tidak ada di data (diterapkan server) · tercatat di server_patch.json |
| Alpha | HP Dasar pada Bintang 1/2: 5.000/9.500 >> 5.400/10.260 | belum: angka baru tidak ada di data (diterapkan server) · tercatat di server_patch.json |
| Karina | Hybrid ATK Dasar pada Bintang 213: 215/285 >> 200/260 | belum: angka baru tidak ada di data (diterapkan server) · tercatat di server_patch.json |
| Mathilda | Hybrid ATK Dasar pada Bintang 213: 155/210 >> 145/195 | belum: angka baru tidak ada di data (diterapkan server) · tercatat di server_patch.json |
| Knockout Punch | (baru) | ada di data |
| Aftershock | (baru) | ada di data |
| Blazing Valor | (baru) | ada di data |
| Whirl of Carnage | (baru) | ada di data |
| Hail of Shots | (baru) | ada di data |
| Star Chorus | (baru) | ada di data |
| Shrouded Blade | (baru) | ada di data |
| Critical Spellcraft | (baru) | ada di data |
| Novel Equipment | Mendapatkan 2 >> 3 Equipment Acak yang Diperkuat | sudah di data |
| Magic Surge | Hero baris belakang mendapatkan 80% >> 100% Mana saat pertarungan dimulai. | sudah di data |
| Dimensional Shot I | DMG yang diberikan ke target meningkat sebesar 4% >> 5% untuk setiap 1 petak antara | belum: angka baru tidak ada di data (diterapkan server) · tercatat di server_patch.json |
| Dimensional Shot II | DMG yang diberikan ke target meningkat sebesar 6% >> 8% untuk setiap 1 petak antara | belum: angka baru tidak ada di data (diterapkan server) · tercatat di server_patch.json |
| Death Oracle | Commander mendapatkan 30 >> 35 Shield. | belum: data masih nilai lama (diterapkan server) · tercatat di server_patch.json |
| Lunox's Power | Lunox's Power: Mendapatkan 10 >> 8 Gold. Saat pertama kali mengaktifkan Sinergi | belum: angka baru tidak ada di data (diterapkan server) · tercatat di server_patch.json |
| Lunox's Power | hingga berjumlah 6, mendapatkan 20 >> 18 Gold tambahan. | belum: angka baru tidak ada di data (diterapkan server) · tercatat di server_patch.json |
| Angela's Power | 1640 >> 100/190/300/500 Magic DMG ke lawan di sepanjang jalurnya berdasarkan fase. | belum: angka baru tidak ada di data (diterapkan server) · tercatat di server_patch.json |
| Divine Execution | Langsung mengeliminasi lawan dengan HP di bawah 16% >> 14%. | belum: angka baru tidak ada di data (diterapkan server) · tercatat di server_patch.json |
| Healing Fountain | Mendapatkan 6 >> 4 Gold. | belum: angka baru tidak ada di data (diterapkan server) · tercatat di server_patch.json |
| Solid Alliance I | Dihapus sementara pada season ini. | belum: masih aktif di data (dihapus lewat server) · tercatat di server_patch.json |
| Transmutation | Setelah 4 >> 5 babak, Go Go Card ini berubah menjadi Go Go Card Kualitas Oranye acak. | belum: angka baru tidak ada di data (diterapkan server) · tercatat di server_patch.json |
| Solid Alliance II | Dihapus sementara pada season ini. | belum: masih aktif di data (dihapus lewat server) · tercatat di server_patch.json |
| Equipment Reforger | (baru) | ada di data |
| Layla | untuk menembus lawan, memberikan 340 >> 400 Physical DMG. | belum: angka baru tidak ada di data (diterapkan server) · tercatat di server_patch.json |
| Johnson | Hybrid ATK Dasar Johnny pada Bintang 3: 285 >> 255 | belum: angka baru tidak ada di data (diterapkan server) · tercatat di server_patch.json |
| Layla | Hybrid ATK Dasar pada Bintang 112: 260/390 >> 3001450 | belum: angka baru tidak ada di data (diterapkan server) · tercatat di server_patch.json |
| Layla | Hybrid ATK Dasar pada Bintang 112: 260/390 >> 300/450 | belum: angka baru tidak ada di data (diterapkan server) · tercatat di server_patch.json |
| Novaria | Hybrid ATK Dasar pada Bintang 112: 175/265 >> 195/295 | belum: angka baru tidak ada di data (diterapkan server) · tercatat di server_patch.json |
| Thamuz | Batas Mana pada Bintang 112: 70 >> 50 | tidak bisa dipastikan |
| Irithel | Batas Mana pada Bintang 3: 100 >> 90 | belum: angka baru tidak ada di data (diterapkan server) · tercatat di server_patch.json |
| Lunox | Hybrid ATK Dasar pada Bintang 2: 200 >> 185 | belum: angka baru tidak ada di data (diterapkan server) · tercatat di server_patch.json |
| Badang | Saat menerima DMG, Badang berpeluang 50% >> 25% untuk meninju target satu kali. | belum: angka baru tidak ada di data (diterapkan server) · tercatat di server_patch.json |
| Badang | Pengali DMG Serangan Balik pada Bintang 3: 420% >> 800% | belum: angka baru tidak ada di data (diterapkan server) · tercatat di server_patch.json |
| Turret of Guardians | Hybrid ATK Turret pada Bintang 3: 590 >> 530; HP Dasar Turret pada Bintang 3: 7.020 >> | belum: angka baru tidak ada di data (diterapkan server) · tercatat di server_patch.json |
| Dyrroth | Abyssal Favor: Dyrroth mendapatkan 3 >> 4 EXP Commander setiap kali melahap Hero. | belum: angka baru tidak ada di data (diterapkan server) · tercatat di server_patch.json |
| Dyrroth | Setiap selesai melahap 2 >> 1 kali, lahapan berikutnya memberikan 2 Hero yang memiliki | belum: data masih nilai lama (diterapkan server) · tercatat di server_patch.json |
| Lunox | Power of Chaos - Jumlah Hero dengan Blessing: 3 >> 2 | belum: angka baru tidak ada di data (diterapkan server) · tercatat di server_patch.json |
| Lunox | Power of Order - Perolehan Gold: 6 >> 4 | belum: angka baru tidak ada di data (diterapkan server) · tercatat di server_patch.json |
| Yin | Hybrid ATK Dasar pada Bintang 2/3: 250/370 >> 275/410 | belum: angka baru tidak ada di data (diterapkan server) · tercatat di server_patch.json |
| Forbidden Power | Mendapatkan 25% >> 30% Peningkatan DMG. | belum: angka baru tidak ada di data (diterapkan server) · tercatat di server_patch.json |
| Lukas | Hybrid ATK Makhluk Suci Bintang 2: 165 >> 145. | belum: angka baru tidak ada di data (diterapkan server) · tercatat di server_patch.json |

## Belum ada screenshot

- Hero: Tanpa screenshot: Alpha (panggilan), Gatotkaca (panggilan), Layla (panggilan), Moskov (panggilan), Novaria (panggilan), X.Borg (panggilan)
- Sinergi: Tanpa screenshot: Chrono Wanderer, Fan yang Bersorak
- Toko Spirit Sand: Tidak terbaca harganya (angka merah): 1 Equipment Acak yang Diperkuat
