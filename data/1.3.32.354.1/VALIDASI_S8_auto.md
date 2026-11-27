# Validasi otomatis Season 8 (data 1.3.32.354.1)

- Dibuat 2026-11-27T19:21:37 oleh `mc_validate.py` dari `screenshot\season 8\ocr.json`.
- **Selisih** = terbaca jelas tapi beda dengan data. **Cek manual** = kemungkinan salah baca OCR / panel di-scroll; lihat screenshot-nya.

| Bagian | Layar | Selisih | Cek manual | Cakupan |
|---|---|---|---|---|
| Hero | 102 | 0 | 1 | 51 dari 52 hero toko punya screenshot Detail Hero |
| Sinergi | 113 | 0 | 7 | 20 dari 22 sinergi punya screenshot Panduan Sinergi; 318 baris tabel tingkat cocok dengan data |
| Commander | 48 | 2 | 6 | 41 dari 41 commander punya screenshot detail; 0 nama terbaca di daftar commander |
| Equipment | 131 | 0 | 8 | 113 dari 113 level equipment aktif punya screenshot panel detail; Angka di belakang koma tidak tampil di panel (bukan selisih): Direwolf's Devastator yang Diperkuat +22.5% Hybrid ATK; Horn of Prosperity yang Diperkuat +22.5% ATK Speed; Skywrath Spear yang Diperkuat +22.5% Hybrid ATK |
| Go Go Card | 54 | 0 | 0 | 195 dari 200 kartu aktif terlihat di screenshot Go Go Card |
| Ensiklopedia | 16 | 0 | 2 | 16 screenshot dicocokkan dengan 8 tab Ensiklopedia |
| Toko Spirit Sand | 29 | 1 | 2 | 10 dari 11 item terlihat dengan harga; 5 pembelian sesuai stack data |
| Go Go Box | 19 | 0 | 0 | 19 dari 19 layar menampilkan 8 orb utuh, cocok babak I-4, II-6, III-6, IV-6, V-6, VI-6, VII-6, VIII-6 |
| Patch Note | 30 | 0 | 0 | 46 perubahan terbaca dari 30 screenshot patch note |

## Selisih

### Commander (2)

- `commander\Screenshot (1986).png`: Lylia / Go, Tharz!: angka game ['22'] tidak ada di data
  - game: Bisa digunakan setelah Kapasitas mencapai 8: Tharz melahap Toko dan menggantinya dengan Little Witch's S.b22, di mana kamu bisa menggunakan Witch Coin untuk membeli hero yang telah ditempatkan. Hero yang sudah tidak tersisa di Hero Pool Bersama tidak bisa dibeli. Mendapatkan 7 Witch Coin pada awal setiap babak.
  - data: Bisa digunakan setelah Kapasitas mencapai 8: Tharz melahap Toko dan menggantinya dengan Little Witch's Shop, di mana kamu bisa menggunakan Witch Coin untuk membeli hero yang telah ditempatkan. Hero yang sudah tidak tersisa di Hero Pool Bersama tidak bisa dibeli. Mendapatkan 7 Witch Coin pada awal setiap babak.
- `commander\Screenshot_2026-11-20-21-20-50-864_com.mobilechess.mi.jpg`: Vexana / Unrestricted: angka game ['117'] tidak ada di data
  - game: Vexana mendapatkan 4 Gold pada setiap Fase Go Go Box. Slaug 117
  - data: Vexana mendapatkan 6 Gold pada setiap Fase Go Go Box.

### Toko Spirit Sand (1)

- `match\spirit sand\Screenshot_2026-11-23-03-56-04-899_com.mobilechess.mi.jpg`: ATK rekan naik 8%, item yang dibeli ['ATK Rekan +2%'] memberi [3] stack

## Cek manual

### Hero (1)

- `hero and synergies\Screenshot (2218).png`: nama hero tidak dikenali: Zhuxm

### Sinergi (7)

- `hero and synergies\Screenshot (2122).png`: Swiftblade tabel, baris 2: game ['1530'], data ['10', '25']
- `hero and synergies\Screenshot (2123).png`: Swiftblade tabel, baris 2: game ['1530'], data ['10', '25']
- `hero and synergies\Screenshot (2124).png`: Swiftblade tabel, baris 2: game ['1530'], data ['10', '25']
- `hero and synergies\Screenshot (2125).png`: Swiftblade tabel, baris 6: game ['2530', '1004'], data ['25', '100']
- `hero and synergies\Screenshot (2095).png`: Dawnbringer: penjelasan di 2 layar tidak cocok dengan teks Lite, Penuh, maupun teks lama di data (juga `hero and synergies\Screenshot (2097).png`)
  - game: Mendapatkan 1 Equipment Dawnbrinqer setiap kali Jumlah Sinergi mencapai 2, 4, atau 6. Equipment Dawnbrinqer menjadi lebih kuat seiring bertambahnya stack Peninqkatan. Saat Jumlah Sinergi mencapai 4 atau 6, Equipment Dawnbrinqer yang baru diperoleh mendapatkan stack Peninqkatan tambahan.
  - data Lite: Mendapatkan Equipment Dawnbringer yang bisa menjadi lebih kuat melalui Pertumbuhan.
  - data Penuh: Mendapatkan Equipment Dawnbringer. menjadi lebih kuat setelah mendapatkan Pertumbuhan.
- `hero and synergies\Screenshot (2058).png`: Frostrider: penjelasan di 1 layar tidak cocok dengan teks Lite, Penuh, maupun teks lama di data
  - game: Setelah Penunggang menaiki Tunggangan, keduanya bertarung sebagai satu unit. Penunggang mendapatkan atribut dan peningkatan skill dari Tunggangan.
  - data Lite: Hero Frostrider mendapatkan skill dan atribut yang diperkuat saat dipasangkan dengan Tunggangan.
  - data Penuh: Tempatkan Penunggang dan pasangkan dengan Tunggangan. Pada awal pertarungan, setiap Penunggang mendapatkan seluruh HP dan sebagian Hybrid ATK dari Tunggangan pasangannya. Skill setiap Penunggang diperkuat sesuai Tunggangan pasangannya (Leo, Barbiel, atau Kupa). Hero Frostrider mendapatkan ATK Speed.
- `hero and synergies\Screenshot (2024).png`: Titan: penjelasan di 1 layar tidak cocok dengan teks Lite, Penuh, maupun teks lama di data
  - game: Saat pertarungan dimulai, Hero Titan di Mech Platform berubah menjadi Super Mecha untuk bertarung dan mendapatkan efek atribut dari Hero Titan Iainnya.
  - data Lite: Hero Titan di Mech Platform berubah menjadi Super Mecha pada awal pertarungan. Super Mecha juga mendapatkan Atribut Mecha dari Hero Titan.
  - data Penuh: Menciptakan Mech Platform di Chessboard yang bisa ditempati Hero Titan. Pada awal pertarungan, Hero Titan yang ditempatkan berubah menjadi Super Mecha. Hero Titan mendapatkan Peningkatan DMG. Super Mecha mendapatkan Peningkatan DMG dan Pengurangan DMG. Pada awal pertarungan, Hero Titan memperkuat Super Mecha.

### Commander (6)

- `commander\Screenshot (1964).png`: Lancelot / Golden Legacy: angka game ['213'] tidak ada di data
  - game: Tidak lagi mendapat Keuntungan. Mulai fase 1/11/111 dan seterusnya, mendapatkan 213/3 bonus Gold setiap babak. Pada akhir setiap babak, semua Gold digunakan untuk meningkatkan Lancelot.
  - data: Tidak lagi mendapat Keuntungan. Mulai fase Ⅰ/Ⅱ/Ⅲ dan seterusnya, mendapatkan 2/3/3 bonus Gold setiap babak. Pada akhir setiap babak, semua Gold digunakan untuk meningkatkan Lancelot.
- `commander\Screenshot (1967).png`: Wanwan / Tiger Pounce: angka game ['4301'] tidak ada di data
  - game: Saat HP Hero lawan di bawah 30% untuk pertama kalinya, Wanwan menyerang Hero lawan dengan HP terendah sebanyak 20 kali, memberikan 180 / 310 1 4301 550 Physical DMG berdasarkan fase saat ini.
  - data: Saat HP Hero lawan di bawah 30% untuk pertama kalinya, Wanwan menyerang Hero lawan dengan HP terendah sebanyak 20 kali, memberikan 180 / 310 / 430 / 550 Physical DMG berdasarkan fase saat ini.
- `commander\Screenshot (1971).png`: Angela / Love's Protection: angka game ['3201'] tidak ada di data
  - game: Pilih rekan untuk dilindungi. Hero yang dipilih akan menembakkan Love Energy setiap 3 detik, memulihkan HP sebesar 5% dari Max HP mereka ke rekan di jalurnya dan memberikan 100 / 190 1 3201 540 Magic DMG berdasarkan Fase ke lawan di jalurnya.
  - data: Pilih rekan untuk dilindungi. Hero yang dipilih akan menembakkan Love Energy setiap 3 detik, memulihkan HP sebesar 5% dari Max HP mereka ke rekan di jalurnya dan memberikan 100 / 190 / 320 / 540 Magic DMG berdasarkan Fase ke lawan di jalurnya.
- `commander\Screenshot (1978).png`: Yu Zhong / Soul Grip: angka game ['3.4'] tidak ada di data
  - game: Kualitas Go Go Card pada awal Babak 11-3 meningkat 1 level. Sebagai gantinya, mendapatkan Black Dragon Treasure acak jika sudah mencapai kualitas maksimum. Black Dragon Treasure (Mendapatkan 1 dari pilihan berikut secara acak): 1. 1 Magic Crystal Acak 2. 1 Equipment Acak dan 5 Gold 3.4 Hero acak dari Sinergi dengan jumlah terbanyak (dipengaruhi Oleh probabilitas refresh Toko saat ini) 4. 13 Gold
  - data: Kualitas Go Go Card pada awal Babak II-3 meningkat 1 level. Sebagai gantinya, mendapatkan Black Dragon Treasure acak jika sudah mencapai kualitas maksimum.  Black Dragon Treasure (Mendapatkan 1 dari pilihan berikut secara acak): 1. 1 Magic Crystal Acak 2. 1 Equipment Acak dan 5 Gold 3. 4 Hero acak dari Sinergi dengan jumlah terbanyak (dipengaruhi oleh probabilitas refresh Toko saat ini) 4. 13 Gold  (Penyesuaian Skill di Magic Crystal: Rune: Mendapatkan 1 Black Dragon Treasure secara acak pada awal Babak II-3.)
- `commander\Screenshot (1987).png`: Aamon / Blade of Resonance: angka game ['12'] tidak ada di data
  - game: Mendapatkan 1 Mirror Device pada awal pertandingan. Saat Hero mencapai Bintang 2, kamu akan mendapatkan 1 Shard. 7 Shard akan otomatis dikonversi menjadi I Mirror Device. Kamu bisa mendapatkan hingga 2 Mirror Device. Mendapatkan 12 Gold tambahan setiap kali Mirror Device
  - data: Mendapatkan 1 Mirror Device pada awal pertandingan. Saat Hero mencapai Bintang 2, kamu akan mendapatkan 1 Shard. 7 Shard akan otomatis dikonversi menjadi 1 Mirror Device. Kamu bisa mendapatkan hingga 2 Mirror Device.
- `commander\Screenshot (1991).png`: Vale / Shifting Wind: angka game ['51719'] tidak ada di data
  - game: I penggunaan skill tambahan setiap kali Commander mencapai Level 51719. aikkan Bintang
  - data: Dapatkan 1 penggunaan skill tambahan setiap kali Commander mencapai Level 5/7/9.

### Equipment (8)

- `equipment\Screenshot (2253).png`: Inspire pasif: angka game ['20125'] tidak ada di data
  - game: Inspire: Memberikan 20125/30/ 40% ATK Speed (meningkat seiring berjalannya Fase).
  - data: Inspire: Memberikan 20/25/30/40% ATK Speed (meningkat seiring berjalannya Fase).
- `equipment\Screenshot (2254).png`: Inspire pasif: angka game ['20125'] tidak ada di data
  - game: Inspire: Memberikan 20125/30/ 40% ATK Speed (meningkat seiring berjalannya Fase).
  - data: Inspire: Memberikan 20/25/30/40% ATK Speed (meningkat seiring berjalannya Fase).
- `equipment\Screenshot (2255).png`: nama equipment tidak dikenali: Meningkatkan ATK Speed
- `equipment\Screenshot (2256).png`: Inspire pasif: angka game ['20125'] tidak ada di data
  - game: Inspire: Memberikan 20125/30/ 40% ATK Speed (meningkat seiring berjalannya Fase).
  - data: Inspire: Memberikan 20/25/30/40% ATK Speed (meningkat seiring berjalannya Fase).
- `equipment\Screenshot (2264).png`: Inspire pasif: angka game ['20125'] tidak ada di data
  - game: Inspire: Memberikan 20125/30/ 40% ATK Speed (meningkat seiring berjalannya Fase).
  - data: Inspire: Memberikan 20/25/30/40% ATK Speed (meningkat seiring berjalannya Fase).
- `equipment\Screenshot (2265).png`: Inspire yang Diperkuat pasif: angka game ['20125'] tidak ada di data
  - game: Inspire: Memberikan 20125/30/ 40% ATK Speed (meningkat seiring berjalannya Fase).
  - data: Inspire: Memberikan 20/25/30/40% ATK Speed (meningkat seiring berjalannya Fase).
- `equipment\Screenshot (2299).png`: Guardian Helmet yang Diperkuat: jumlah pasif game 1 vs data 2
- `equipment\Screenshot (2310).png`: Spellblade Talisman: jumlah pasif game 0 vs data 1

### Ensiklopedia (2)

- `ensiklopedia\Screenshot (2246).png`: Ensiklopedia: angka game ['114', '1114'] tidak ada di data
  - game: @ 20 oommanuer. 'Biaya Peningkatan Level 3 4 Gold yang @ 3 Dibutuhkan: 'DMG Commander 32 @ 40 @ 54 10 9 (Maks) 74 DMG Commander: Setelah setiap babak, Commander yang menang memberikan sejumlah DMG ke Commander yang kalah. DMG bervariasi berdasarkan babak dan jumlah unit yang masih bertahan. DMG Commander = DMG Dasar Babak + Total Level Bintang Unit yang Masih Bertahan Babak 1-2 14 II-1 114 11-5 11-6 Ill-1 0>111-3 1114>111-6 tv-1>tv-3 >tv-6 V-1 -y V-5 DMG Dasar 3 5 6 7 11 13 14 15 Kasus Khusus: Unit non-Hero tertentu yang masih bertahan meningkatkan DMG Commander sebanyak 1. Jika babak berakhir seri, kedua belah pihak memberikan DMG satu sama Iain.
- `ensiklopedia\Screenshot (2250).png`: Ensiklopedia: angka game ['3.2'] tidak ada di data
  - game: 'Magic Crystal Pilihan 1. Mendapatkan 1 Magic Crystal Pilihan saat memasuki Fase II, III, dan IV. 2. Saat pertama kali kamu menggunakannya ke rekan, 3 pilihan Sinergi berdasarkan Sinergi Hero target akan tersedia untuk dipilih. 3.2 pilihan pertama dipilih dari Sinergi Faction dan Role Hero. Pilihan ke-3 bersifat acak. Sinergi Minor (Sinergi berjumlah maksimal <4) tidak muncul. 4. Setelah dikonfirmasi, Magic Crystal Pilihan menempati slot Magic Crystal dan menjadi terkunci. 5. Jika kamu tidak menginginkan satu pun dari 3 Sinergi tersebut, kamu bisa membatalkan pilihan untuk mempertahankan efek Magic Crystal awal Hero. 6. Jika Hero dengan Magic Crystal tersebut dijual, kamu bisa mengembalikan efek Magic Crystal dengan membeli lagi Hero yang sama. 'Wheel of Fate Pada awal pertandingan, Wheel of Fate akan memilih efek secara acak yang membawa perubahan baru bagi sistem Go Go Card dalam pertandingan. 1. Crystal Legend: Babak pemilihan Go Go Card pertama hanya menawarkan Kartu Badge Sinergi. 2. Commander's Power: Babak pemilihan Go Go Card pertama hanya menawarkan Kartu Power. 3. Gold Galore: Semua Go Go Card dalam pertandingan ini memiliki Kualitas Emas. 4. Tycoon: Semua Go Go Card dalam pertandingan ini adalah Kartu finansial.

### Toko Spirit Sand (2)

- `match\spirit sand\Screenshot_2026-11-23-03-49-23-202_com.mobilechess.mi.jpg`: HP rekan naik 3%, item yang dibeli ? memberi ? stack
- `match\spirit sand\Screenshot_2026-11-27-17-37-35-837_com.mobilechess.mi.jpg`: ATK rekan naik 3%, item yang dibeli ? memberi ? stack

## Patch note vs data

| Item | Patch note | Status di data |
|---|---|---|
| Odette | (baru) | ada di data |
| Harley | Midas Touch!: Bisa digunakan setelah Babak 11-2 >> 11-3 dimulai. Me-refresh Toko 1 kali | sudah di data |
| Harley | dan menampilkan 3 Hero 5 Gold. Mendapatkan 1 >> 2 kesempatan pembelian Hero gratis | sudah di data |
| Harley | minimal 2 >> 4 Hero 4 Gold. Efek baru: Mendapatkan 2 kesempatan pembelian Hero | sudah di data |
| Chou | Win or Lose: Mendapatkan 3 >> 2 Gold setelah kalah dalam babak. | sudah di data |
| Dyrroth | Abyssal Favor: Dyrroth mendapatkan 4 >> 2 EXP Commander dengan melahap Hero. | sudah di data |
| Yaelned'aSpaPtOkaWne1r k | i pembelian Hero gratis dan 1 >> 2 Gold setiap kali level Commander | item tidak ditemukan di data |
| Wanwan's Power | Berpeluang 50% >> 60% untuk mendapatkan 1 Gold setiap kali lawan tereliminasi. | sudah di data |
| Sharp Arrow | Hero di baris terakhir mendapatkan 10% >> 15% Physical ATK pada setiap Basic ATK, | sudah di data |
| Sharp Arrow | hingga 6 >> 5 stack. | sudah di data |
| Experienced Shuffle | Langsung dapatkan 25 >> 22 EXP. | sudah di data |
| Vexana | Unrestricted: Vexana mendapatkan 4 >> 2 Gold pada setiap Fase Go Go Box. | belum: angka baru tidak ada di data (diterapkan server) · tercatat di server_patch.json |
| S_ Frostrider | Rasio Pewarisan HP Tunggangan: 100% >> 80% | item tidak ditemukan di data |
| Frostrider | - O Rasio Pewarisan HP Tunggangan: 100% >> 80% | belum: angka baru tidak ada di data (diterapkan server) · tercatat di server_patch.json |
| Frostrider | Rasio Pewarisan Hybrid ATK Tunggangan pada 2/4/6 Frostrider: 35%/50%/65% >> 20%/30%/ | tidak bisa dipastikan |
| Dawnbringer | 10 Dawnbringer: Equipment eksklusif Supreme Crown memberikan 350% >> 500% Max HP. | belum: angka baru tidak ada di data (diterapkan server) · tercatat di server_patch.json |
| Valentina | Pengali DMG Skill pada Bintang 2: 165% >> 190% | belum: angka baru tidak ada di data (diterapkan server) · tercatat di server_patch.json |
| Kimmy | Pengali DMG Skill Fase Pertama pada Bintang 3:1.750% >> 1.925% | belum: angka baru tidak ada di data (diterapkan server) · tercatat di server_patch.json |
| Kimmy | Pengali DMG Skill Fase Kedua pada Bintang 3: 750% >> 825% | belum: angka baru tidak ada di data (diterapkan server) · tercatat di server_patch.json |
| Yu Zhong | HP Dasar: 3.545/6.380/15.770 >> 3.760/6.765/16.715 | belum: angka baru tidak ada di data (diterapkan server) · tercatat di server_patch.json |
| Balmond | Nilai Shield Skill pada Bintang 2: 6% >> 5% | tidak bisa dipastikan |
| Kagura | Shield pada Bintang 2: 125% >> 135% dari Max HP | belum: angka baru tidak ada di data (diterapkan server) · tercatat di server_patch.json |
| Ling | Peningkatan Hybrid ATK Permanen saat Memenangkan Duel: 6% >> 8% | belum: angka baru tidak ada di data (diterapkan server) · tercatat di server_patch.json |
| Guinevere | Peluang Mendapatkan Hero Gratis saat Refresh Toko pada Bintang 2: 24% >> 23% | belum: angka baru tidak ada di data (diterapkan server) · tercatat di server_patch.json |
| Dawnbringer | 4/6 Dawnbringer: Equipment Dawnbringer yang baru didapatkan mendapatkan 7/14 >> 9/15 | belum: angka baru tidak ada di data (diterapkan server) · tercatat di server_patch.json |
| Swiftblade | 2/4/6 Swiftblade: Hero Swiftblade mendapatkan 25/50/100 >> 35/65/130 Hybrid Penetration | belum: angka baru tidak ada di data (diterapkan server) · tercatat di server_patch.json |
| Titan | Batas HP untuk Eksekusi (Atribut Balmond): 18% >> 15% | sudah di data |
| Titan | DMG Area setelah Eksekusi (Atribut Balmond): 200% >> 180% | belum: angka baru tidak ada di data (diterapkan server) · tercatat di server_patch.json |
| Melissa | Pengali DMG Area pada Bintang 3: 205% >> 320% | belum: angka baru tidak ada di data (diterapkan server) · tercatat di server_patch.json |
| Melissa | Bonus ATK speed pada Bintang 3: 100% >> 200% | belum: angka baru tidak ada di data (diterapkan server) · tercatat di server_patch.json |
| Eudora | Pengali DMG pada Bintang 3: 700% >> 800% | belum: angka baru tidak ada di data (diterapkan server) · tercatat di server_patch.json |
| Eudora | Pengali DMG Tertunda pada Bintang 3: 345% >> 400% | belum: angka baru tidak ada di data (diterapkan server) · tercatat di server_patch.json |
| Kimmy | Pengali DMG Fase Pertama pada Bintang 3:1.925% >> 2.150% | belum: angka baru tidak ada di data (diterapkan server) · tercatat di server_patch.json |
| Kimmy | Pengali DMG Fase Kedua pada Bintang 3: 825% >> 925% | belum: angka baru tidak ada di data (diterapkan server) · tercatat di server_patch.json |
| Argus | Pengali DMG Basic ATK yang Diperkuat pada Bintang 3: 600% >> 700% | belum: angka baru tidak ada di data (diterapkan server) · tercatat di server_patch.json |
| Lolita | Pengali Physical DMG pada Bintang 3:1.700% >> 1.950% | belum: angka baru tidak ada di data (diterapkan server) · tercatat di server_patch.json |
| Lolita | Pengali DMG Berbasis HP pada Bintang 3: 12% >> 15% | tidak bisa dipastikan |
| Yu Zhong | Pengali DMG untuk Dua Fase Pertama pada Bintang 3: 900% >> 1.050% | belum: angka baru tidak ada di data (diterapkan server) · tercatat di server_patch.json |
| Yu Zhong | Pengali DMG untuk Fase Ketiga pada Bintang 3:1.120% >> 1.300% | belum: angka baru tidak ada di data (diterapkan server) · tercatat di server_patch.json |
| Sora | Pengali DMG pada Bintang 3:1.000% >> 1.200% | belum: angka baru tidak ada di data (diterapkan server) · tercatat di server_patch.json |
| Erza | Shield pada Bintang 2/3:750/1.800 >> 1.050/2.400 | belum: angka baru tidak ada di data (diterapkan server) · tercatat di server_patch.json |
| Balmond | Perolehan Shield untuk Setiap Target yang Terkena pada Bintang 3: 9% >> 7% | belum: angka baru tidak ada di data (diterapkan server) · tercatat di server_patch.json |
| Balmond | Batas Mana pada Bintang 3: 120 >> 170 | belum: angka baru tidak ada di data (diterapkan server) · tercatat di server_patch.json |
| Popol | Jumlah Lemparan Tombak pada Bintang 1/2: 27 >> 18 | belum: angka baru tidak ada di data (diterapkan server) · tercatat di server_patch.json |
| Popol | Pengali DMG per Serangan pada Bintang 1/2: 30%/35% >> 50% | belum: angka baru tidak ada di data (diterapkan server) · tercatat di server_patch.json |
| Popol | Pengali DMG saat Durasi Freeze Berakhir pada Bintang 1/2: 30%/35% >> 50% | belum: angka baru tidak ada di data (diterapkan server) · tercatat di server_patch.json |

## Belum ada screenshot

- Hero: Tanpa screenshot: Alpha (panggilan), Bane (panggilan), Gatotkaca (panggilan), Moskov (panggilan), Zhuxin
- Sinergi: Tanpa screenshot: Chrono Wanderer, Fan yang Bersorak
- Go Go Card: Tidak terlihat: Journey's Windfall (Oranye), Fury's Edge (Bisa Berubah Sewaktu-waktu) (Ungu), Victory's Blessing (Biru), Odette's Power (Oranye), Odette's Power (Oranye)
- Toko Spirit Sand: Tanpa screenshot: HP Rekan +3%
