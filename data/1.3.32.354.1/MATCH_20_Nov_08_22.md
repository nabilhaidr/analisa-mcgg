# Analisa Pertandingan — 20 Nov 08-22

_Data game 1.3.32.354.1, Season 8 "Arena Para Penyihir" · dibuat 2026-11-28 03:35_

- **Peringkat:** -
- **HP akhir:** 3
- **Babak terbaca:** I-1 – III-3 (13 babak), kehilangan HP di 10 babak
- **Pertandingan:** ID - · poin -
- Pemain: CinCoeg

## Catatan otomatis

- Rekaman berhenti di III-3 tanpa layar hasil: peringkat akhir tidak diketahui.
- HP hilang per fase: Fase I −21, Fase II −53, Fase III −23. Terbanyak di Fase II.
- 10 kekalahan beruntun (sampai III-2, babak creep II-3 dilewati).
- Level 7 pertama terlihat di II-4.
- Level 8 pertama terlihat di II-6.
- Level 9 pertama terlihat di III-3.
- Rata-rata Gold di awal babak Fase II: 34.
- Rata-rata Gold di awal babak Fase III: 42.

## Timeline (CinCoeg)

| Babak | HP awal | Perubahan | Gold awal | Level | Kejadian |
|---|---|---|---|---|---|
| I-1 | 100 | +0 tidak kehilangan HP | 2 | 3 |  |
| I-2 | 100 | -5 kalah | 7 | 4 | Pilih Go Go Card |
| I-3 | 95 | -7 kalah | 11 | 4 |  |
| I-4 | 88 | -9 kalah | 18 | 5 | Go Go Box |
| II-1 | 79 | -10 kalah | 24 | 5 |  |
| II-2 | 69 | -11 kalah | 34 | 5 |  |
| II-3 | 58 | +0 tidak kehilangan HP | 27 | 6 | Pilih Go Go Card (pilihan: Divine Execution) |
| II-4 | 58 | -11 kalah | 43 | 7 |  |
| II-5 | 47 | -11 kalah | 29 | 7 |  |
| II-6 | 36 | -10 kalah | 45 | 8 | Go Go Box |
| III-1 | 26 | -8 kalah | 22 | 8 |  |
| III-2 | 18 | -15 kalah | 38 | 8 |  |
| III-3 | 3 | - | 66 | 9 | Pilih Go Go Card |

## HP semua pemain

| Pemain | I-1 | I-2 | I-3 | I-4 | II-1 | II-2 | II-3 | II-4 | II-5 | II-6 | III-1 | III-2 | III-3 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| maulinaw | 100 | 100 | 93 | 86 | 86 | 86 | 86 | 86 | 86 | 86 | 76 | 76 | 63 |
| Deirdre Ji | 100 | 100 | 100 | 96 | 91 | 91 | 81 | 81 | 81 | 81 | 81 | 81 | 63 |
| Ryoshi | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 88 | 88 | 76 | 76 | 76 |
| Vie | 100 | 100 | 95 | 95 | 90 | 81 | 72 | 72 | 72 | 57 | 57 | 44 | 44 |
| PEJUANG | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 |
| Kempleng | 100 | 100 | 93 | 93 | 93 | 84 | 84 | 84 | 73 | 62 | 62 | 47 | 30 |
| CinCoeg | 100 | 100 | 95 | 88 | 79 | 69 | 58 | 58 | 47 | 36 | 26 | 18 | 3 |
| Zura*Dyrr | 100 | 100 | 100 | 94 | 94 | 85 | 76 | 76 | 66 | 53 | 37 | 26 | 26 |

## Kejadian

| Waktu | Babak | Kejadian | Detail |
|---|---|---|---|
| 01:35 | I-2 | Pilih Go Go Card |  |
| 04:35 | I-4 | Go Go Box |  |
| 07:05 | II-3 | Pilih Go Go Card | pilihan: Divine Execution |
| 11:10 | II-6 | Go Go Box |  |
| 13:50 | III-3 | Pilih Go Go Card |  |

## Catatan metode

- Tata letak: ponsel; frame tiap 5 detik; OCR: windows.
- HP dari panjang bar: HP = (panjang − 8.3) / 0.940, dikalibrasi dari 728 angka HP yang terbaca OCR.
- Angka HP hanya diambil dari teks yang ujung kanannya sejajar dengan ujung kanan bar (angka jumlah unit di samping pedang saat bertarung diabaikan); bila bar terpotong di tepi atau ada shield, bar hanya batas bawah. Tanpa angka OCR, HP = angka yang paling sering terbaca untuk pemain itu dengan panjang bar yang sama.
- HP awal babak = nilai terbanyak di 60% awal babak (bila kosong: bacaan pertama di babak itu), lalu dibuat tidak pernah naik (nilai yang melanggar urutan digabung dengan tetangganya, diambil mediannya).
- Gold awal babak = Gold tertinggi dalam 10 detik sejak Gold pertama terbaca di babak itu (pendapatan babak kadang masuk beberapa detik setelah label babak berganti). Gold hanya dibaca saat penghitung Gold tampil (harga jual unit atau dialog yang menutupinya diabaikan); angka yang terlewat OCR HUD dibaca ulang dari kotak Gold saja (rapid, ambang skor rendah agar angka satu digit ikut terbaca).
- Label babak: OCR HUD; bila kosong, OCR potongan label saja (rapid); bila masih kosong, label yang tampilannya paling mirip (skor >= 0,93, unggul >= 0,03). Label dipakai bila termasuk rantai terpanjang yang tidak pernah mundur (maks. 2 babak + 1 per 40 detik ke depan); frame di antara dua label dibagi rata.
- Pilihan Go Go Card = kartu yang tampil di layar pilihan; kartu yang akhirnya diambil terlihat di layar hasil. Pilihan bisa ditunda (layar disembunyikan lalu dibuka lagi): layar yang memuat kartu dari pilihan sebelumnya (sama, atau sebagian setelah Refresh) ditandai "dibuka lagi", bukan pilihan baru.
- Teks Win/Lose Streak di layar tidak dicatat: OCR frame penuh tidak bisa membedakan streak sendiri dari streak lawan yang sedang tampil. Menang/kalah beruntun di Catatan otomatis dihitung dari HP; babak creep (I-1, lalu babak ke-3 tiap fase: II-3, III-3, IV-3, V-3) tidak memutus kekalahan beruntun.
