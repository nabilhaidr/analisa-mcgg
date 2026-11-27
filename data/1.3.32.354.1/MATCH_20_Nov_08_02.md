# Analisa Pertandingan — 20 Nov 08-02

_Data game 1.3.32.354.1, Season 8 "Arena Para Penyihir" · dibuat 2026-11-28 03:31_

- **Peringkat:** -
- **HP akhir:** 1
- **Babak terbaca:** I-1 – III-6 (16 babak), kehilangan HP di 8 babak
- **Pertandingan:** ID - · poin -
- Pemain: CinCoeg

## Catatan otomatis

- Rekaman berhenti di III-6 tanpa layar hasil: peringkat akhir tidak diketahui.
- HP hilang per fase: Fase I −2, Fase II −45, Fase III −52. Terbanyak di Fase III.
- 3 babak beruntun tanpa kehilangan HP (sampai I-3).
- 7 kekalahan beruntun (sampai III-5, babak creep III-3 dilewati).
- Level 7 pertama terlihat di II-3.
- Level 8 pertama terlihat di II-6.
- Level 9 pertama terlihat di III-3.
- Rata-rata Gold di awal babak Fase II: 38.
- Rata-rata Gold di awal babak Fase III: 27.

## Timeline (CinCoeg)

| Babak | HP awal | Perubahan | Gold awal | Level | Kejadian |
|---|---|---|---|---|---|
| I-1 | 100 | +0 tidak kehilangan HP | 2 | 3 |  |
| I-2 | 100 | +0 tidak kehilangan HP | 21 | 4 | Pilih Go Go Card |
| I-3 | 100 | +0 tidak kehilangan HP | 23 | 5 |  |
| I-4 | 100 | -2 kalah | 21 | 6 | Go Go Box |
| II-1 | 98 | +0 tidak kehilangan HP | 35 | 6 |  |
| II-2 | 98 | +0 tidak kehilangan HP | 44 | 6 |  |
| II-3 | 98 | +0 tidak kehilangan HP | 32 | 7 | Pilih Go Go Card |
| II-4 | 98 | -12 kalah | 42 | 7 |  |
| II-5 | 86 | -15 kalah | 52 | 7 |  |
| II-6 | 71 | -18 kalah | 24 | 8 | Go Go Box |
| III-1 | 53 | -14 kalah | 33 | 8 |  |
| III-2 | 39 | -12 kalah | 48 | 8 |  |
| III-3 | 27 | +0 tidak kehilangan HP | 23 | 9 | Pilih Go Go Card |
| III-4 | 27 | -18 kalah | 23 | 9 |  |
| III-5 | 9 | -8 kalah | 23 | 9 |  |
| III-6 | 1 | - | 10 | 9 |  |

## HP semua pemain

| Pemain | I-1 | I-2 | I-3 | I-4 | II-1 | II-2 | II-3 | II-4 | II-5 | II-6 | III-1 | III-2 | III-3 | III-4 | III-5 | III-6 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Luxurya | 100 | 100 | 100 | 100 | 93 | 93 | 93 | 93 | 83 | 71 | 71 | 71 | 60 | 60 | 60 | 60 |
| wenstark | 100 | 100 | 100 | 100 | 100 | 93 | 93 | 93 | 93 | 93 | 84 | 84 | 84 | 84 | 67 | 67 |
| Bill' | 100 | 100 | 100 | 92 | 92 | 84 | 84 | 84 | 84 | 83 | 71 | 56 | 56 | 56 | 56 | 43 |
| CinCoeg | 100 | 100 | 100 | 100 | 98 | 98 | 98 | 98 | 86 | 71 | 53 | 39 | 27 | 27 | 9 | 1 |
| Byy | 100 | 100 | 95 | 95 | 90 | 90 | 82 | 82 | 82 | 82 | 82 | 82 | 82 | 82 | 82 | 82 |
| XxXxfastx | 100 | 100 | 93 | 88 | 88 | 88 | 79 | 79 | 79 | 79 | 68 | 68 | 68 | 68 | 68 |  |
| eaj9 0 |  |  |  | 89 |  |  |  |  |  |  |  | 39 | 29 |  |  |  |

## Kejadian

| Waktu | Babak | Kejadian | Detail |
|---|---|---|---|
| 01:40 | I-2 | Pilih Go Go Card |  |
| 04:55 | I-4 | Go Go Box |  |
| 07:15 | II-3 | Pilih Go Go Card |  |
| 11:30 | II-6 | Go Go Box |  |
| 14:10 | III-3 | Pilih Go Go Card |  |

## Catatan metode

- Tata letak: ponsel; frame tiap 5 detik; OCR: windows.
- HP dari panjang bar: HP = (panjang − 8.4) / 0.940, dikalibrasi dari 711 angka HP yang terbaca OCR.
- Angka HP hanya diambil dari teks yang ujung kanannya sejajar dengan ujung kanan bar (angka jumlah unit di samping pedang saat bertarung diabaikan); bila bar terpotong di tepi atau ada shield, bar hanya batas bawah. Tanpa angka OCR, HP = angka yang paling sering terbaca untuk pemain itu dengan panjang bar yang sama.
- HP awal babak = nilai terbanyak di 60% awal babak (bila kosong: bacaan pertama di babak itu), lalu dibuat tidak pernah naik (nilai yang melanggar urutan digabung dengan tetangganya, diambil mediannya).
- Gold awal babak = Gold tertinggi dalam 10 detik sejak Gold pertama terbaca di babak itu (pendapatan babak kadang masuk beberapa detik setelah label babak berganti). Gold hanya dibaca saat penghitung Gold tampil (harga jual unit atau dialog yang menutupinya diabaikan); angka yang terlewat OCR HUD dibaca ulang dari kotak Gold saja (rapid, ambang skor rendah agar angka satu digit ikut terbaca).
- Label babak: OCR HUD; bila kosong, OCR potongan label saja (rapid); bila masih kosong, label yang tampilannya paling mirip (skor >= 0,93, unggul >= 0,03). Label dipakai bila termasuk rantai terpanjang yang tidak pernah mundur (maks. 2 babak + 1 per 40 detik ke depan); frame di antara dua label dibagi rata.
- Pilihan Go Go Card = kartu yang tampil di layar pilihan; kartu yang akhirnya diambil terlihat di layar hasil. Pilihan bisa ditunda (layar disembunyikan lalu dibuka lagi): layar yang memuat kartu dari pilihan sebelumnya (sama, atau sebagian setelah Refresh) ditandai "dibuka lagi", bukan pilihan baru.
- Teks Win/Lose Streak di layar tidak dicatat: OCR frame penuh tidak bisa membedakan streak sendiri dari streak lawan yang sedang tampil. Menang/kalah beruntun di Catatan otomatis dihitung dari HP; babak creep (I-1, lalu babak ke-3 tiap fase: II-3, III-3, IV-3, V-3) tidak memutus kekalahan beruntun.
