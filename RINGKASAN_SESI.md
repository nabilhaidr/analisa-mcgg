# Ringkasan proyek patch-tracker — Magic Chess: Go Go (per 2026-10-30)

## Cara melanjutkan di chat baru
Tulis: **"Baca `F:\Magic Chess\patch-tracker\RINGKASAN_SESI.md` lalu lanjutkan."**
Bahasa kerja: Indonesia. Folder kerja: `F:\Magic Chess\patch-tracker\`. Client game: `F:\Magic Chess\MagicChessGoGo\MagicChessGoGo\`.
Repo GitHub: `nabilhaidr/analisa-mcgg`, kerja langsung di branch **`main`** (branch lain digabung ke `main`). Di sesi cloud
(Linux) ada repo ini tanpa client game, tanpa rekaman MP4 (di-`.gitignore`), dan tanpa OCR Windows: pasang
`pip install -r requirements.txt`; OCR memakai RapidOCR atau `ocr.json` yang ikut di repo (lihat `mc_ocr.py`).

## Tujuan
Membaca isi patch Magic Chess: Go Go langsung dari file game PC (hero, sinergi faksi/role, stat, skill, commander, Go Go Card,
equipment, Ensiklopedia), menyajikannya sebagai laporan per season (HTML/MD/JSON), membandingkan antar versi game, dan
memastikan isinya sama dengan layar in-game (430 screenshot Season 7).

## Status sekarang
- Versi game **1.3.24.344.1** = klien Patch 7.2 (file game sudah memuat revamp Lukas dan Equipment Reforger; listing toko
  dari hasil pencarian: ±9–14 Okt 2026; cek terakhir: belum ada update). Season aktif **S7 "Chrono Echoes"** (Rank Season 9,
  2026-08-11 s/d 2026-11-15 17:59:59 waktu server global); **S8 "Arena Para Penyihir"** sudah ada di file (mulai 2026-11-15,
  28 hero baru, faksi baru FAIRY TAIL, Dawnbringer, Dragonslayer, Frostrider, Titan; role Deadeye, Weapons Master).
- Laporan terbaru: `data/1.3.24.344.1/S7.html|md|json` dan `S8.*`.
- **S7.html sudah divalidasi ke 430 screenshot: semua cocok** (0 selisih). Satu-satunya beda = angka balance Patch 7.2 dan
  Penyesuaian Keseimbangan 20/10 yang diterapkan server; keduanya sudah dicatat di `server_patch.json` dan tampil di S7.html
  sebagai catatan oranye "Patch 7.2 (server)" / "Patch 20/10 (server)".

## Tool dan file (`F:\Magic Chess\patch-tracker\`)
| File | Fungsi | Jalankan |
|---|---|---|
| `patch_tracker.py` | Snapshot & diff hash file game (manifest, ResCheckConf, mini_patch, LuaRepair) → `snapshots/`, `reports/` | `python patch_tracker.py snapshot` / `diff` / `list` |
| `mc_tables.py` | Library: skema tabel dari PDB, ekstrak TextAsset (cache `cache/<versi>/`), parser tabel, teks bahasa | di-import `mc_data.py` |
| `mc_data.py` | Ekspor data season → `data/<versi>/S<n>.json/.md/.html` (bahasa Indonesia, opsi `--season 7 8`, `--lang EN`); juga menerapkan `server_patch.json`. `summons` = unit panggilan di luar daftar hero (Johnny, Turret, Makhluk Suci) untuk deteksi layar hasil | `.venv\Scripts\python mc_data.py` |
| `mc_images.py` | Ekstrak ikon dari atlas UI NGUI (`StreamingAssets/UI/windows/<Atlas>.unity3d`: Texture2D + MonoBehaviour `mSprites` = nama, x, y, lebar, tinggi; asal kiri atas) → `data/<versi>/img/<Atlas>/<sprite>.png`; field `icon` di JSON jadi path relatif. File yang sudah ada tidak diekstrak ulang | dipanggil `mc_data.py` |
| `report_template.html` | Template S<n>.html: tab Hero, Sinergi (+ tabel Toko Spirit Sand di bawahnya, tautan dari kartu Mistbender), Commander, Go Go Card, Equipment, Info Season, Ensiklopedia, Patch Server; cari/filter, tombol "Tampilkan nonaktif", mode gelap | dipakai `mc_data.py` |
| `mc_diff.py` | Bandingkan `S<n>.json` dua versi terakhir: buff/nerf stat, skill, sinergi, commander (+tipe Aktif/Pasif, +detail tooltip), kartu (+aktif), equipment (+aktif), Ensiklopedia/DMG, Toko Spirit Sand (harga/batas beli = buff/nerf, peluang, efek, pilihan), Go Go Box (jumlah orb per jenis, harga hero, isi pool; babak dengan perubahan sama digabung) → `data/diff/`. Field yang belum ada di ekspor lama ditandai "tidak dibandingkan" | `python mc_diff.py` |
| `ocr_screens.ps1` | OCR bawaan Windows (en-US, gambar ×2) semua screenshot satu season → `screenshot/season <n>/ocr.json`, cache per gambar | `powershell -ExecutionPolicy Bypass -File ocr_screens.ps1 -Season 7` |
| `mc_validate.py` | Cocokkan `S<n>.json` dengan OCR screenshot (jenis layar dikenali otomatis; subfolder bebas) → `data/<versi>/VALIDASI_S<n>_auto.md`: **Selisih** (kemungkinan data salah) vs **Cek manual** (kemungkinan salah baca OCR) + status tiap baris patch note | `python mc_validate.py --season 7` (`--dump "(1510)"` = teks OCR 1 screenshot) |
| `catatan_gameplay.json` | Catatan MANUAL aturan permainan dari pengalaman bermain (tidak ada di tabel data): per equipment `id`, `text`, `source`, opsional `seasons`. `mc_data.py` (`apply_gameplay_notes`) menempelkannya sebagai `gameplay_notes` → kotak hijau "Aturan dari pengalaman bermain" di tab Equipment S<n>.html dan baris di S<n>.md. Isi sekarang: Go Go Magic Crystal (1101) dan Choice Magic Crystal (10001) | edit manual → jalankan `mc_data.py` |
| `server_patch.json` | Catatan MANUAL perubahan Patch Note yang diterapkan server (tidak ada di file game): hero `stat/stars/old/new`, commander/`hero_skills`/kartu `replace` [teks lama, teks baru] (+ `attributes` [[label, bintang, nilai]] untuk tabel Atribut Skill hero), kartu `removed`, `synergies`; cukup `text` tanpa `replace` = catatan saja bila angkanya tidak ada di teks file game (stat Johnny, Turret, ambang Echo Energy) | edit manual → jalankan `mc_data.py` |
| `analisis_lineup.py` | Halaman analisis 5 lineup pengguna (peringkat tanpa ultra, papan, sinergi, kartu, build Odette/Lancelot, aturan crystal, pelajaran pertandingan 20 Okt) → `data/1.3.24.344.1/ANALISIS_LINEUP_S7.html` + `.md` dengan ikon dari `img/`. Angka dibaca dari S7.json; teks analisis ditulis tangan di skrip | `python analisis_lineup.py` (setelah `mc_data.py`) |
| `video_frames.ps1` | Ambil frame dari rekaman pertandingan MP4 (API `Windows.Media.Editing`, tanpa ffmpeg) → `f_<detik>.jpg`; lalu bisa `ocr_screens.ps1 -Folder <folder frame>`. **Tidak bisa HEVC** (rekaman layar ponsel; error `0xC00D5212`): sekarang berhenti dengan pesan, tidak lagi meninggalkan JPG 0 byte | `powershell -ExecutionPolicy Bypass -File video_frames.ps1 -Video <mp4> -Out <folder> -Step 5` |
| `video_frames.py` | Sama, dengan PyAV (Python sistem punya `av`): bisa HEVC & H.264, hanya decode keyframe (rekaman ponsel 28 menit ±8 menit), file 0 byte ditimpa | `python video_frames.py <mp4> <folder> --step 5 --width 1600` |
| `mc_lineup.py` | **Analisa lineup** → `data/<versi>/LINEUP_<nama>.html/.md`: sinergi aktif + efek, tingkat berikutnya (hero/crystal), jalur ultra, slot level, stok & peluang toko, peluang crystal di Go Go Box, kartu/equipment terkait, skill commander, catatan Patch server. Input: daftar hero, target sinergi (dicarikan susunan hero), atau screenshot (ikon hero; layar hasil `--all-rows`; layar Rekomendasi Lineup `--board` = seluruh papan satu lineup + jalur Go Go Card, crystal dari lencana di potret diisi lewat `--crystals`) | `python mc_lineup.py --heroes "Odette, Gord, ..." --crystals "Astro Power" --commander Minotaur --level 9` · `--synergies "Astro Power 6, Mage 4"` · `--screenshot hasil.jpg --all-rows` · `--screenshot rekomendasi.jpg --board --commander Kalea --crystals "Dragon Altar, Defender"` |
| `mc_patch.py` | **Analisa Patch Note** dari screenshot Update Patch (OCR, cache per folder) → `PATCH_<nama>.html/.md`: perubahan per bagian dengan panah ↑/↓/~, lama → baru (+%), status (sudah di file game / diterapkan server / tercatat di `server_patch.json`), dampak ke sinergi, **draf entri `server_patch.json`** (teks pengganti dicari di deskripsi file game, di kartu/skill yang paling cocok; kartu "dihapus" → `removed`). Screenshot tumpang tindih digabung | `python mc_patch.py "screenshot\season 7\update patch" --files 1881-1885 --name "Penyesuaian 20-10"` (`--ocr rapid`, `--no-ocr`) |
| `mc_match.py` | **Analisa pertandingan** dari rekaman (MP4, HEVC ponsel/PC) dan/atau layar hasil → `MATCH_<nama>.html/.md` + frame kunci di `match_<nama>/`: timeline HP/Gold/Level per babak (HP dari panjang bar hijau, dikalibrasi angka OCR; label babak dari OCR HUD, potongan label + RapidOCR, lalu kemiripan tampilan, juga di frame yang HUD-nya tertutup overlay seperti layar pilih Go Go Card; Gold hanya saat penghitung Gold tampil, bukan harga jual unit atau dialog; angka yang terlewat OCR Windows dibaca ulang dari kotak Gold dengan RapidOCR, ambang skor 0,1 agar angka satu digit terbaca; Gold awal = tertinggi dalam 10 detik sejak bacaan pertama babak), grafik HP semua pemain, kejadian (Go Go Card — pemilihan yang ditunda lalu dibuka lagi ditandai "dibuka lagi" —, Go Go Box di babak jadwal I-4/II-6/III-6/…, crystal Pilihan, VICTORY/DEFEAT, panel DMG), papan akhir semua pemain (ikon; nama/level dengan RapidOCR bila terpasang; nama yang tidak dikenal OCR, mis. huruf Korea, tampil sebagai potongan gambar `nama_<peringkat>.png`), catatan otomatis (menang/kalah beruntun dari HP; babak creep tidak memutus kekalahan beruntun; teks Win/Lose Streak tidak dipakai). Bisa juga hanya layar hasil. Cache kerja `cache/match/<nama>/`. Tes: `test_mc_match.py` (+ `test_data/gold/`) | `python mc_match.py --video rekaman.mp4 --result hasil.jpg --player CinCoeg --name "..."` · `--frames cache\match\<nama>\frames` · `--result hasil.jpg` saja · `python -m pytest test_mc_match.py` |
| `check_match.py` | **Pemeriksaan konsistensi laporan MATCH** (pengganti `check.py` yang tidak pernah masuk git): md = html, timeline sendiri (perubahan, tereliminasi, kotak ringkasan), tabel HP vs layar hasil, catatan otomatis = `mc_match.insights()` dari tabel laporan, kejadian, papan akhir (nama ikon, sinergi dihitung ulang), gambar ada. Peringatan: babak terlewat, HP sendiri kosong (selain setelah tereliminasi), tanpa papan akhir, level kosong, urutan bertahan vs peringkat, gambar tidak dirujuk. Tiap laporan satu baris ringkasan: peringkat, HP akhir, babak pertama–terakhir, jumlah babak, babak kalah, nama terbaca/baris papan. Kode keluar 1 bila ada kesalahan. Jalankan setelah laporan dibuat ulang/diubah. Tes: `test_check_match.py` | `python check_match.py` · `python check_match.py 15_38 Kalea` · `python -m pytest test_check_match.py` |
| `mc_common.py`, `mc_vision.py` | Modul bersama: data season terbaru, pencocokan nama, halaman HTML/MD, path relatif · deteksi ikon hero/sinergi/kartu/equipment di screenshot (OpenCV, ukuran ikon dicari otomatis; korelasi + selisih warna; ikon dicocokkan paralel di semua inti CPU; `icon_labels()` = nama yang bisa dihasilkan deteksi, kartu bergambar sama = satu nama). Debug: `python mc_vision.py shot.jpg --kind hero --out anotasi.png` | — |
| `mc_ocr.py` | OCR bersama untuk `mc_patch.py`/`mc_match.py`, format sama dengan `ocr_screens.ps1`: mesin `windows` (`ocr_screens.ps1` → `ocr.json`) atau `rapid` (RapidOCR, Windows/Linux, `pip install rapidocr_onnxruntime` → `ocr_rapid.json`). `auto`: Windows bila ada PowerShell; di luar Windows `ocr.json` yang ada bila mencakup semua gambar (ukuran file sama), lalu RapidOCR. `run_rapid`/`ocr_folder` menerima `text_score` (ambang skor RapidOCR, bawaan 0,5, ikut di stamp cache). Tes: `test_mc_ocr.py` | opsi `--ocr auto\|windows\|rapid` di `mc_patch.py`/`mc_match.py` · `python -m pytest test_mc_ocr.py` |
| `requirements.txt` | Paket Python sistem untuk alat analisa (numpy, pillow, opencv-python, av, rapidocr_onnxruntime) | `pip install -r requirements.txt` |
| `data/1.3.24.344.1/VALIDASI_S7.md` | Laporan validasi manual (perbaikan yang dibuat + daftar beda karena server) | — |
| `screenshot/season 7/` | 430 screenshot (hero & sinergi 138, commander 60, equipment 134, go go card 58, ensiklopedia 18, update patch 22) + `ocr.json` (432 gambar, 2 di antaranya dari `match/`); subfolder `match/` = 20 rekaman pertandingan 21–26 Okt (MP4, di-`.gitignore`) + 41 screenshot: layar hasil, 7 Rekomendasi Lineup 20/10, 2 daftar Riwayat, 1 Toko Spirit Sand (8 ada di git, 33 belum) | — |

`.venv` berisi UnityPy, capstone, pycryptodome, pillow. Skrip lain cukup Python sistem (3.13) + `requirements.txt`.

## Alur setelah game update berikutnya
1. `python patch_tracker.py snapshot` lalu `python patch_tracker.py diff` → file apa yang berubah.
2. `.venv\Scripts\python mc_data.py` → data versi baru (ekstraksi ulang otomatis, ±3 menit pertama kali).
   Peringatan `[server_patch.json …] sudah masuk file game` = nilai server kini ada di file → catatan itu boleh dihapus.
3. `python mc_diff.py` → daftar buff/nerf antar versi.
4. Jika ada screenshot baru di `screenshot/season <n>/`: `ocr_screens.ps1 -Season <n>` lalu `python mc_validate.py --season <n>`.
   Periksa bagian "Selisih"; "Cek manual" biasanya salah baca OCR.
5. Baris patch note berstatus "belum … · belum dicatat di server_patch.json" → tambahkan ke `server_patch.json`, jalankan `mc_data.py` lagi.

## Temuan teknis tentang game
- `MagicChessGoGo.exe` hanya stub Unity; logika di `GameAssembly.dll` (IL2CPP, metadata v24). **`GameAssembly.pdb` ikut
  dikirim**, jadi skema semua tabel (`CData_<Tabel>_Element`) dan nama fungsi bisa dibaca.
- Mekanisme patch di disk: `manifest.json` (md5 semua file), `StreamingAssets/Document/windows/ResCheckConf.xml` (md5 per
  bundle), `MagicChessGoGo_Data/dragon2017/mini_patch/` (hotfix aset), `dragon2017/assets/LuaRepair/4031` (hotfix Lua UI,
  AES-256-CBC, key `e1QXm+D7H8uN1IysfAjH9HmipSavvrqWwLzQtynmWK8=`, IV `0dGLZ7oDyjUJg0jT+rHgZQ==` dari metadata
  `ClientLuaCodeRepair`; isinya hanya fix UI Auction).
- Tabel data = TextAsset di `Document/windows/*.unity3d`, format `$mulonggame_table_1`: flag `0` baris biasa, `1` bitmask
  per baris, `2` tanpa kolom key + indeks. Tabel dasar + tabel season (`_S7`, `_extra_all_S7`) digabung.
- Teks: `AllLanguage*`/`AddLanguage*`, kunci = hash Java (`h*31+c`) dari `"<Tabel>_<field>_<key>"`. Teks skill/kartu di
  `BattleShowMessage`, teks hero lama di `ShowMessage`; sebagian sel memakai kutip CSV (dibersihkan `unquote()`).
- Season aktif/berikutnya: `MCSystemConfig` (iSeasonID / iAdvanceSeasonID); tanggal dari `RankSeason_MC`.
- Patch note dan angka balance patch (mis. 7.2) dikirim server; client & menu in-game tetap menampilkan angka file.
- Toko Spirit Sand (S7 dan S8 sama, 11 item, total bobot 980): HP Rekan +1/2/3% (8/16/24), ATK Rekan +1/2/3% (8/16/24),
  Nana (60, maks 1), Magic Crystal Acak (80, maks 1), Hero 4 Gold ★1 Acak (30, maks 5), Mirror Device (80, maks 1),
  1 Equipment Acak yang Diperkuat (80, maks 5). Spirit Sand = buff `4590200` (maks 99 stack). **Temuan:** item ATK +2%/+3%
  menambah 3/5 stack (1% Physical + 1% Magic ATK per stack = +3%/+5%), sedangkan HP +2%/+3% menambah 2/3 stack sesuai nama;
  rumus 10021 dicek lewat Echomancer (FPara3 3 = 0.03% per Echo Energy, cocok teks in-game). Jumlah slot toko dan aturan
  refresh tidak ada di tabel maupun simbol PDB (hanya kelas tabel `CData_SpecialStore`), jadi kemungkinan diatur server.
- **Magic Crystal Pilihan** (dapat 1 di awal Fase Ⅱ, Ⅲ, Ⅳ): hanya **1 yang bisa aktif**; memakai yang baru menggantikan yang
  lama (dari pengalaman bermain pengguna; tidak ada di tabel data, tidak ada tabel VersatileCrystal). 2 dari 3 pilihannya =
  Faction & Role hero itu sendiri, dan crystal sinergi milik hero sendiri tetap +1 (terlihat: Astro 6/10 dengan 5 hero Astro).
  Crystal biasa (satu per hero, bisa banyak) hanya dari sumber acak: kartu Badge/Blessing, Legacy of Valor, Prime Selection,
  creep IV-3, peti crystal, Blessing Lunox, dan **Go Go Box mulai II-6** (lihat poin Go Go Box di bawah). Jadi ultra 10 faksi 6 hero = 6 hero + 1 Pilihan + 3 crystal acak.
- **Go Go Magic Crystal (Kapasitas +1, equipment 1101)**: diambil dari Go Go Box, kapasitas langsung +1 begitu diambil (ikon
  tetap terlihat di tas, tidak perlu dipasang). **Hanya bisa diambil sekali per pertandingan**; pilihan Kapasitas +1 di Go Go
  Box berikutnya tidak bisa diambil (dari pengalaman bermain pengguna; data hanya menunjukkan `m_MaxStack` 1). Jadi kapasitas
  maksimum = slot level + 1 (level 9 → 10). Kedua aturan ini tercatat di `catatan_gameplay.json`.
- **Go Go Box** (`MCRoundRandomEquip_S7` + `AChooseHero` di `MCClassicsBattleConfig_S7`; dicocokkan ke screenshot tutorial
  `ensiklopedia` 1886–1888 dan rekaman 21 Okt 15:38): di akhir tiap fase = babak ke-4, 10, 16, 22, 28, 34, 40, 46 (I-4, II-6,
  III-6, IV-6, …). Isi selalu **8 orb + 3 hero** = `m_EquipTotal` item (equipment biasa `m_NormalEquipMin–Max` + sisanya crystal
  sinergi acak 1001–1008/1050–1056), sisa orb diisi Go Go Magic Crystal (Kapasitas +1). I-4: 8 equipment, hero 3/4 Gold (bobot
  10/20/20); II-6: 5–6 equipment + 1–2 crystal + 1 Kapasitas, hero 4/5 Gold (75/75); III-6: 4 + 2 crystal + 2 Kapasitas, hero
  5 Gold; IV-6 dst.: 3–4 + 3–4 crystal + 1 Kapasitas, hero 5 Gold. Urutan memilih = sisa HP terendah dulu (terverifikasi di II-6).
  Isi tetap 8+3 walau tinggal 2 pemain. `AChooseHero.iSpecialHeroId 451700` = fase pilih tambahan Vexana (6 detik).
  **S8 beda:** mulai IV-6 equipment biasa 4–6 + crystal 1–3 (S7: 3–4 + 3–4), jadi crystal Go Go Box akhir lebih sedikit; daftar
  crystal S8 masih memuat ID 1054 (= Dragoncaller di S7) yang tidak ada di `MCEquipBase_S8`; faksi baru Frostrider (maks 6) tidak
  punya Magic Crystal sama sekali. Diekspor ke S<n>.json/.md/.html sejak 2026-10-21.
- **Babak creep (tanpa lawan pemain)**: I-1 dan babak ke-3 tiap fase berikutnya (II-3, III-3, IV-3, V-3). Go Go Card dipilih
  di awal II-3 dan III-3 (Valir: "Fase Go Go Card pada Babak II-3"), Kartu Power di I-1/I-2; di III-3 ada panel DMG (creep).
  Ensiklopedia: "Dalam setiap Stage, Player akan menghadapi Creep Round". Di 20 laporan MATCH tidak ada pemain yang kehilangan
  HP di 72 dari 74 babak itu (2 sisanya masing-masing 1 pemain), sedangkan setiap babak lain Fase I–III ada yang kalah (±separuh
  pemain). Jadi di babak creep praktis tidak ada yang kehilangan HP (belum terlihat apakah kalah dari creep mengurangi HP), dan
  babak itu bukan menang/kalah PvP (dipakai `mc_match.py`).

## Sumber data per bagian laporan (aturan yang sudah terverifikasi ke screenshot)
| Bagian | Sumber / aturan |
|---|---|
| Hero | `MCHero_S<n>` + `MCHeroStarlevel_S<n>` (stat ★). `m_GuideType == 3` = hero panggilan (Chrono Wanderer, Alpha) → label "Hero panggilan" / `*`. "Jangkauan ATK" tidak ada sebagai kolom |
| Skill & angka | Placeholder `[kind\|efek\|kolom\|unit\|skala/rumus\|label]`: kolom ke-5 dipakai (`0.001` = kali, `N*20` = rumus); efek `m_Calculate 100` menyimpan rasio di `FPara1`. Basic attack tanpa deskripsi disaring. Level yang tidak ada di tabel efek memakai baris level 1, seperti client (Dragoncaller 10 tampil 70%/50% in-game). Teks skill bisa berbeda per bintang (Alpha ★1–★2 vs ★3–★4): deskripsi hanya diisi level yang memakai teks itu (nilai lain tetap di tabel Atribut Skill), dan skill yang teksnya sudah tampil tidak diulang. Token `[$AdaptiveDamage]` = "Adaptive DMG" (`TEXT_TOKENS`) |
| Sinergi | `RelationSkillTip_MC_S<n>` + `RelationSkill_MC_S<n>` |
| Commander | `IndividualCommanderLevel` (skill per level; `m_PassiveSkill == 1` → "Aktif"); teks panjang layar Commander dari `SkillExtraDesc_MC(_S<n>)`; kategori dari `MCHero.m_occupation` |
| Ikon (gambar) | Rujukan `"<Atlas>/<sprite>"` di tabel: hero `MCHero_S<n>.m_Head` (`Atlas_HeroHeadIcon_S<n>`), commander `MCHero.m_Head` (`Atlas_HeroHeadIcon_New*_MC`), sinergi `RelationSkillTip_MC_S<n>.m_RelationIcon` (`Atlas_RelationIcon_S<n>`), equipment `MCEquipBase.m_Icon[0]` (per level), Go Go Card `MCSuperCrystalKey.m_MiniIcon` (`Atlas_GoGoCard_0X_MC`; `m_IconFile` = gambar besar tanpa atlas), skill `MCSkill.m_IconFile`. S7/S8: semua hero, sinergi, commander, kartu aktif, equipment aktif, dan skill punya ikon; hanya 2 kartu nonaktif yang tidak ada spritenya. 751 PNG, ±14 MB untuk S7+S8 |
| Detail tooltip skill commander | Kata bergaris bawah `${TagN}$` di teks skill → `SkillKeyWords_MC.mSkillKeyWordsDesc` + `m_NumDescribe` (field `details` per skill). Layar Commander memakai baris **tabel dasar dulu**, `SkillKeyWords_MC_S<n>` hanya untuk id yang tidak ada di dasar (Lylia = dasar "Harga di Little Witch's Shop", Freya "Efek Sinergi" = `_S7`). `[SkillName/SkillDes<id>]` = teks skill lain (Luo Yi 481601–481625); `${JohnsonBondList}$` = `JohnsonSeasonBondList.m_BondList` (baris season, kalau tidak ada baris default -1; S7 = 15 sinergi). S7: Alucard, Diggie (2), Franco, Freya (2), Johnson, Kalea, Luo Yi, Lylia, semuanya cocok dengan screenshot |
| Go Go Card | `MCSuperCrystalKey` + `_S<n>`. Aktif bila `m_Value1/2/3` ≠ 0 (bobot putaran Go Go Card 1/2/3; dibaca dari kode galeri `MCUIHandBookSuperCrystal.RefreshCardList`). Deskripsi memakai level skill kartu (`m_SkillID/m_SkillID2` = [id, level]). Kartu Power: punya `m_CommanderId`, atau versi umum di level yang sama hanya di putaran 1 |
| Equipment | `MCEquipBase` + `_S<n>`. Aktif = `m_DropState == 1` (empiris, cocok 67/67). Pasif memakai level dari `m_SkillList` = [id, level]. Physical+Magic bernilai sama ditampilkan "Hybrid ATK/DEF" |
| Ensiklopedia | `BattleSeason.m_SeasonHandbookID` → `HookBook_MC` (S7 = 11, S8 = 12), teks `CommonText_MC`; Panduan Sinergi = `m_RelationDes` + `GiftPackage_MC` (`m_GiftType` = `m_RelationDesNum`) |
| DMG Commander | XML `MCClassicsBattleConfig_S<n>` → `SRoundExtraDamage` + `AMCRoundStage` (fase terakhir dipecah per 6 babak → IV, V) |
| Info season | `PlayerLevel_MC_S<n>` (biaya EXP = Gold, peluang toko), `HeroQuality_MC` (pool per hero) |
| Go Go Box (tab Info Season, field `go_go_box`) | `MCRoundRandomEquip_S<n>` (baris `m_RoundConfigId` 0): babak `m_Round` (label dari `AMCRoundStage`), equipment biasa `m_NormalEquipMin–Max` dari `m_NormalEquip`, crystal = `m_EquipTotal` − equipment biasa dari `m_CrystallEquip`, Kapasitas +1 = 8 − `m_EquipTotal` (8 orb = pengamatan, `GO_GO_BOX_ORBS`), hero `m_HeroListNumber` dengan harga diundi bobot `m_HeroList`/`m_HeroListRate` (harga sama dijumlahkan). Teks orb in-game = `summary` item. ID yang tidak ada di tabel equipment → `notes`. S7 cocok dengan rekaman 21 Okt (I-4, II-6, III-6, IV-6) |
| Toko Spirit Sand (Mistbender) | `SpecialStore` (tanpa varian `_S<n>`; harga `m_ChipNum`, bobot acak `m_Probability`, batas beli `m_MaximumPurchase`, 999 = tanpa batas) + `MCSpecialCardPool` (nama `mName`, teks `mSpecialDes`, `m_SkillID`). Efek dari `MCSkill`/`MCEffect` skill item: `OperEnum 20` ke efek `4590200` = bayar Spirit Sand, `OperEnum 1` + `OperEnum 20` = stack buff permanen, bonus per stack dari efek `m_Calculate 10021` (stack × `FPara3`), `OperEnum 50/20009` = equipment tetap/acak. Ditautkan ke sinergi lewat keluarga ID (skill 45900/45901 ↔ buff 4590200). Nama mata uang = `DescriptionIconShow` 27. **Belum terverifikasi** (belum ada screenshot toko) |

## Hasil validasi S7 (430 screenshot)
- `VALIDASI_S7_auto.md`: **0 selisih**, 17 cek manual (semua salah baca OCR yang sudah dicek). Cakupan: 52/52 hero toko,
  20/22 sinergi, 40/40 commander, 110/110 level equipment aktif, 199/199 kartu aktif, 8 tab Ensiklopedia.
- Belum ada screenshot: hero panggilan (Alpha, Gatotkaca, Layla, Moskov, Novaria, X.Borg), sinergi Chrono Wanderer dan
  Fan yang Bersorak, **Toko Spirit Sand** (hanya panel sinergi Mistbender, screenshot 1630). X.Borg ★3 "total 2000% ATK"
  (rumus `N*10`) belum terverifikasi. Setelah toko dicocokkan ke screenshot, tambahkan season ke `STORE_VERIFIED` di `mc_data.py`.
- Kesalahan ekstraksi yang ditemukan & sudah diperbaiki: Baxia Shield (10000%→10%), Vexana (×20), Fanny/Lancelot (0%),
  Rising Fury "hingga" (×10), Solid Alliance Ⅱ (2%→3%), deskripsi panjang 12 commander, kutip CSV, Hybrid ATK/DEF,
  equipment nonaktif (27, termasuk Lightstick/Choice Magic Crystal ganda), skill hero lama kosong, pasif Supreme Blades.

## Perubahan dari server: Patch 7.2 + Penyesuaian 20/10 (`server_patch.json`, tampil di S7.html)
- Hero: Alpha HP ★1/★2 5000/9500 → 5400/10260; X.Borg Hybrid ATK ★1/★2 240/365 → 260/395; Gatotkaca 230/345 → 250/375;
  Karina ★2/★3 215/285 → 200/260; Mathilda ★2/★3 155/210 → 145/195.
- Commander: Dyrroth Abyssal Devourer mulai Babak I-4 → I-3, Abyssal Favor EXP → 3 (file game 2, patch note tulis 1);
  Aurora Frost Treasures minimal 7 → 8 Gold.
- Go Go Card: Dimensional Shot Ⅰ 4% → 5%, Ⅱ 6% → 8%; Death Oracle 30 → 35 Shield; Lunox's Power 10 → 8 Gold & 20 → 18 Gold;
  Angela's Power → 100/190/300/500 (file game 100/190/320/540); Divine Execution 16% → 14%; Healing Fountain 6 → 4 Gold;
  Transmutation 4 → 5 babak; Solid Alliance Ⅰ & Ⅱ dihapus sementara.
- Umum: equipment gelombang kedua dari creep Babak IV-3 selalu berisi Magic Crystal Faction acak.
- **Penyesuaian Keseimbangan (20/10)** (screenshot `update patch` 1881–1885, di-OCR 21 Okt): hero Layla Hybrid ATK ★1/★2
  → 300/450 (patch note tulis lama 260/390, file game 220/330), Novaria 175/265 → 195/295, Thamuz Batas Mana ★1/★2 70 → 50,
  Irithel Batas Mana ★3 100 → 90, Lunox ★2 200 → 185; Badang (Fist Crack) peluang tinju balik 50% → 25%, Serangan Balik ★3
  420% → 800%; commander Layla Destruction Rush 340 → 400 Physical DMG, Johnny ★3 Hybrid ATK 285 → 255, Lukas Makhluk Suci
  kini di baris depan, Vexana 13 Gold di Go Go Box pertama → 10 Gold di tiap 3 Go Go Box pertama (patch note menyebut
  "I Want All of Them!", padahal 13 Gold di file ada di skill Lv 2 "Unrestricted"); Echomancer: Echo Energy untuk Chrono
  Wanderer ★2 400 → 350; kartu Turret of Guardians ★3 Hybrid ATK 590 → 530, HP 7.020 → 5.616.
- Sudah ada di file game (bukan server): 8 kartu sinergi Role baru, Equipment Reforger, Chrono Wanderer + Layla/Novaria,
  revamp Lukas, Vexana's Power, Novel Equipment 3, Magic Surge 100%.
- Di S7.html: angka hero oranye (tooltip = nilai file game), deskripsi kartu/skill commander memakai nilai baru + catatan,
  label "dihapus (server)", dan tab **Patch Server** berisi tabel semua perubahan. JSON tetap menyimpan nilai file game
  (`stats_server`, `description_server`, `removed_server`, `server_patches` adalah field tambahan).

## Analisis gameplay (kesimpulan dari chat 20–21 Okt; teoretis dari data game, bukan win rate)
Halaman lengkap 5 lineup: `data/1.3.24.344.1/ANALISIS_LINEUP_S7.html` (+ `.md`, dibuat `analisis_lineup.py`).
- **Aturan penting** (lihat Temuan teknis): hanya 1 crystal Pilihan aktif; Kapasitas +1 sekali per pertandingan, langsung
  aktif (ikonnya di tas BUKAN item belum terpakai); hero ★3 butuh 9 salinan (stok: 1 Gold 25, 2 Gold 21, 3 Gold 18,
  4 Gold 14, 5 Gold 9); level 9 = 9 slot (+1 bila ambil Kapasitas +1); peluang toko L9: 13/22/25/26/14%; DMG Commander =
  DMG dasar babak (I 3, II 5–6, III 7/11, IV 13/14, V 15) + total bintang unit lawan yang hidup → di Fase IV satu kekalahan
  ±18–24 HP.
- **Tingkat 10 (ultra) terkuat di atas kertas**: Astro Power 10 (2 Sovereign, +300% DMG, +600% HP, True DMG 600% ATK per
  Basic ATK) dan Dragoncaller 10 (naga 70%/50% Max HP + stun beruntun). Ultra butuh 3 crystal acak → bergantung hoki.
- **Tanpa ultra, level 9 (sinergi 4/6)**: 9 slot hanya muat satu sinergi 6 + satu sinergi 4 (atau sinergi 6 + sinergi kecil
  penuh dalam 8 hero). Terkuat menurut data: Mage 6 + Enchanted Tales 4 (Vale, Zhuxin, Kadita, Gord, Vexana, Odette,
  Mathilda, Atlas, Belerick); Marksman 6 + Dauntless 2; Astro 6 + Marksman 4; Dragoncaller 6 + Swiftblade 4.
  Commander: Freya bagus untuk Role 6 (Mage +10/20/30% Magic ATK, Marksman +5/10/25% AS, + hero gratis di 2/4/6),
  Minotaur untuk carry item, Angela untuk carry skill, Lunox (+1 sinergi).
- **Tier list komunitas** (semua sebelum Patch 7.2, belum ada yang sesudahnya): loadoutgg 27 Sep (patch 7.1) commander
  Minotaur #1, Nana, Brody; comp S = Mage+Stargazer, Marksman/Dauntless; A = Astro, Dragoncaller Burst, Echomancer,
  Enchanted Tales/Mage. kitakuji 22 Agt & xcashshop 26 Sep: S = SPECTRE+Starbelle (Lunox, carry Alpha), Hyper Aldous
  (Mistbender+Bruiser, Zilong); A = Starbelle Fanny, Echomancer Dauntless; B = Dragon Altar. Artikel xcashshop 16 Okt memakai
  sinergi season lama (abaikan). **Dicari ulang 2026-10-28: belum ada tier list tertulis setelah Patch 7.2**; yang terindeks
  tetap loadoutgg 27 Sep. Setelah 7.2 hanya konten kreator (judul/deskripsi, belum diverifikasi): TikTok 12 Okt Lunox SPECTRE 6
  + Starbelle 6 + Scavenger 3 "combo terkuat"; YouTube ±15 Okt "Lukas revamp … lagi META"; YouTube ±17 Okt "Alpha Astro Power x
  Alice". Diabaikan: Gamezi (memuat sinergi non-S7 "Vonetis Sea"), daftar commander Lapak/Joytify (nama bukan commander MCGG),
  Topuplist Juli 2026 (S6). loadoutgg.com dan kitakuji.id tidak bisa dibuka dari sesi cloud (jaringan dibatasi). Dicek lagi
  2026-10-28 (sesi yang sama, kueri lain): tetap belum ada; playgroup.gg ("Data-Backed · Win Rates") ternyata untuk Commander
  Magic: The Gathering, bukan MCGG.
- **Data sendiri setelah 7.2** (layar hasil 20 laporan MATCH 21–26 Okt; 140 papan pemain lain, papan sendiri tidak dihitung;
  sinergi dengan >= 4 hero terlihat, crystal tidak terlihat): Starbelle di 22% papan peringkat 1–4 vs 14% papan 5–8 (juara 4
  dari 15), Dauntless 17% vs 14% (juara 5), Stargazer 12% vs 10%; Kishin paling populer tapi tidak unggul (23% vs 27%), SPECTRE
  9% vs 13%, Astro Power 6% vs 10%, Dragoncaller 7% vs 8% (0 juara). Sampel kecil (Starbelle p≈0,24, belum signifikan), satu
  rentang rank (Mythic). Papan sendiri: juara 5 dari 20 (Starbelle + Echomancer 2×, Astro + Mage 2×, Mage + Stargazer).
- **5 lineup favorit pengguna** (screenshot Rekomendasi Lineup), peringkat tanpa ultra:
  1. Aamon: Dauntless 6 + Stargazer 4 + Mistbender 3 (Nana ★3 lewat Mirror Device/Spirit Sand; butuh level 10).
  2. Luo Yi: Starbelle 6 + Astro 4. Build pengguna: **Odette ★2 Fan** dengan Winter Crown + Lightstick + Essence Core dari
     Lancelot ★2 → ATK Odette ±1.200, tiap hero Starbelle ±+400 ATK.
  3. Kagura "Pance kekebalan tubuh": Kishin 6 + Phasewarper 3 + Shadeweaver 3. Build pengguna: **Lancelot ★2 + 3 item Kishin
     Arcane** (Guren +55% DMG, Justice Sword, Nether Claw +50% HP) → HP efektif ±34.000.
  4. Minotaur: Astro 6 + Mage 4. 5. Kalea: Dragon Altar 6 + Dragoncaller 4 (terlemah tanpa ultra, terkuat jika ultra).
  **Penyesuaian 20/10** tidak mengubah peringkat: Badang ★2 (carry Kalea) peluang tinju balik 50% → 25% (DMG balasan ±144 → ±72
  per serangan diterima; saran: item damage ke Zilong, Badang jadi tank), Lunox ★2 −7,5% ATK (pengisi Aamon/Kagura), Irithel
  hanya ★3, Vexana yang di-buff commander-nya (+17 Gold awal), bukan hero di lineup Minotaur.
- **Pertandingan 20 Okt** (ID 374683366623511459): Minotaur, Astro 6 + Mage 4, **peringkat 2**, menyerah di IV-4. Juara
  (MANIAC) sudah Dragoncaller 10 lalu menjual hero (layar hasil hanya mencatat papan akhir). Pelajaran: begitu lawan
  menuju ultra, kejar ultra sendiri; crystal untuk faksi utama, bukan sinergi kecil.
- **Pertandingan 21 Okt** (ID 400762236246143209, `screenshot/season 7/match/`): Kalea, Dragon Altar 6 + Dragoncaller 6,
  **peringkat 4** (+16 poin, Mythical Glory 201). Kalah 8× beruntun di Fase I–II (HP 100 → 24, lose streak + Scavenger 3),
  all-in level 9 di III-1, menang 7× beruntun, lalu kalah IV-4 vs Abahhh (WM 6 + Kishin 6, Freya; −18 HP) dan IV-5 vs
  theprince_cryyyc (SPECTRE 6 + Starbelle 4, **Alpha ★3**). adikagacor (peringkat 3) memakai hero yang sama (stok Suyou
  tinggal 4/14 di IV-2). Peluang terlewat: HP terlalu tipis (berhenti lose streak di ±40 HP); dadu Kalea hangus 2× di 7 poin
  (aktifkan Brankas di 7); cek pemain lain yang memakai faksi sama di akhir Fase II; Zilong/Gusion tanpa item, Golden Staff
  dan Equipment Reforger menganggur. (Kartu: Kalea's Power, Cyclical Support, Payday.)

- **Pertandingan 21 Okt sore (rekaman ponsel HEVC di `screenshot/season 7/match/`, Riwayat 16:10)**: 14:42 Minotaur Marksman 6 +
  Dauntless 4 → **peringkat 8** (pemenang SPECTRE 6 + Starbelle 4, Lunox); 15:00 Angela Echomancer 6 + Stargazer 4 → **peringkat 7**
  (pemenang Defender 6 + Marksman 4); **15:38 (ID 392354550001462153) Minotaur Astro 6 + Mage 4 → JUARA 1** (poin Minotaur
  1405 → 1623, +218). Jalannya: papan awal pengisi (Angela, Martis, Phoveus, Vale, Franco), pindah ke Astro/Mage di II-5;
  Go Go Card Minotaur's Power → Purest Power Ⅰ (II-3) → Divine Execution (III-3, setelah refresh; in-game 14% = nilai server 7.2);
  Go Go Box: Glowing Wand (I-4), **Odette** (II-6), **Odette lagi** (III-6) → Odette ★2, Kapasitas +1 (IV-6) → Melissa ke-10;
  crystal Pilihan Astro di Hilda (III-1), crystal Starbelle dari creep IV-3 (Starbelle 2 + Fan). Level 8 di III-2, Level 9 di
  III-6. HP 100 → 95 (I-2) → 60 (kalah 4× di Fase II: II-1, II-2, II-5, II-6) → 47 (III-5) → 32 (IV-1), lalu **6 babak
  beruntun tanpa kalah IV-2 s/d V-1** (termasuk creep IV-3; HP tetap 32). Total 7 kekalahan PvP.
  Odette ★2: Glowing Wand + Spellblade Talisman + Winter Crown (semua diperkuat Minotaur; Spellblade 80% Mana → skill langsung
  di awal pertarungan, burn 5% Max HP/detik) = 81.489 DMG di IV-6 (Gord 10.478). Juara 2 musuhkoruptor (Lunox, Kishin 6 + WM 4 +
  Phasewarper 3), juara 3 TT:jawirGG (Kagura, Dragoncaller 6 + Kishin 6; dulu tertulis SPECTRE, dikoreksi dari ikon sinergi
  layar hasil 2026-10-21); top 3 semuanya punya Divine Execution. Sisa: Divine
  Glaive menganggur di tas IV-4, Gord cuma 1 item.

## Riwayat pekerjaan (2026-10-20 s/d 2026-10-30)
1. Analisis client dengan REA/Ghidra + PDB; pecahkan format tabel, teks, LuaRepair; tentukan season aktif.
2. Buat `patch_tracker.py`, `mc_tables.py`, `mc_data.py`, `report_template.html`, `mc_diff.py`; validasi awal ke screenshot.
3. Tambah Ensiklopedia + tabel DMG Commander, label Aktif/Pasif commander, status kartu aktif per season.
4. Perbaiki skill hero kosong (Eudora, Angela, Hilda, Karrie, Zilong), skill biasa Minotaur, teks Supreme Blades.
5. Validasi penuh S7.html ke 422 screenshot dengan OCR → 10 perbaikan ekstraksi (lihat di atas), `VALIDASI_S7.md`.
6. Jadikan validasi tool tetap: `ocr_screens.ps1` + `mc_validate.py` (+ analisis patch note).
7. Haas' Claws (screenshot 1665/1666) terverifikasi; perubahan server Patch 7.2 dicatat di `server_patch.json` dan
   ditampilkan di S7.html.
8. Isi Toko Spirit Sand (Mistbender) diekspor: `Season.special_store()`/`store_effect()` di `mc_data.py` → field
   `special_store` di S<n>.json, bagian di S<n>.md, tabel di tab Sinergi S<n>.html (S7 & S8). Dicek di Edge headless
   (desktop & lebar ponsel). Belum terverifikasi ke screenshot.
9. Detail tooltip skill commander (Alucard, Diggie, Franco, Freya, Johnson, Kalea, Luo Yi, Lylia): `Season.keyword_details()`
   dan `johnson_pool()` di `mc_data.py` → field `details` di skill commander S<n>.json, kotak "Detail" di S<n>.html, kutipan
   di S<n>.md; `mc_diff.py` ikut membandingkannya. Cocok dengan 10 screenshot layar Commander yang dikirim di chat
   (tidak disimpan di `screenshot/`). Dicek di Edge headless.
10. Ikon dari file game (`mc_images.py`): kepala hero & commander, ikon sinergi (juga di chip sinergi/hero), ikon skill,
    gambar Go Go Card, ikon equipment (per level) tampil di S<n>.html; PNG di `data/<versi>/img/`. S<n>.md tetap teks.
    Dicek di Edge headless; `mc_validate.py` tetap 0 selisih.
11. (2026-10-21) Halaman analisis 5 lineup (`analisis_lineup.py` → `ANALISIS_LINEUP_S7.html/.md`), diperbarui dengan aturan
    1 crystal Pilihan aktif dan nama 6 kartu Badge/Blessing dari screenshot Rekomendasi Go Go Card (lineup Luo Yi & Minotaur).
12. (2026-10-21) Deskripsi skill Alpha dirapikan: `[$AdaptiveDamage]` → "Adaptive DMG", tidak ada lagi "/-/-", dan 3 blok skill
    yang sama jadi 1. Ikut rapi: Layla (tanpa "/-"), skill duplikat persis di Karina, Atlas, Novaria (S7) dan Helcurt, Karina,
    Valentina (S8). `mc_validate.py` tetap 0 selisih.
13. (2026-10-21) Analisis pertandingan 21 Okt (`screenshot/season 7/match/`: rekaman 20 menit + 2 screenshot hasil; frame
    diambil dengan `Windows.Media.Editing` karena ffmpeg tidak ada): peringkat 4, Kalea, Dragon Altar 6 + Dragoncaller 6.
    Hasil analisis hanya di chat. Layar hasil menampilkan maksimal 9 hero (papan sebenarnya 10/10).
14. (2026-10-21) `catatan_gameplay.json` + `apply_gameplay_notes()`: aturan Kapasitas +1 (sekali per pertandingan, langsung
    aktif) dan crystal Pilihan (1 aktif) tampil di kartu equipment S7/S8.
15. (2026-10-21) `video_frames.ps1` (alat ekstrak frame rekaman) dipindah ke patch-tracker; bagian "Analisis gameplay"
    ditambahkan ke ringkasan ini.
16. (2026-10-21) Patch Note "Penyesuaian Keseimbangan (20/10)" (5 screenshot baru) dicatat di `server_patch.json` sebagai
    patch "20/10". `apply_server_patches()` kini juga mendukung `hero_skills` (deskripsi + `attributes_server`), `synergies`,
    dan catatan `text` tanpa `replace`; S<n>.html menampilkan catatan server di skill hero & kartu sinergi, sel atribut oranye;
    S<n>.md ikut. `mc_validate.py`: 0 selisih, 0 perubahan server belum dicatat. 3 screenshot baru di `ensiklopedia`
    (1886–1888) = popup tutorial Go Go Box (urutan memilih dari sisa HP Commander terendah), tidak ada angka baru.
17. (2026-10-21) `analisis_lineup.py` memperhitungkan Penyesuaian 20/10: `stat()` memakai `stats_server`, bagian baru "Dampak
    Penyesuaian Keseimbangan 20/10" (`PATCH_IMPACT`, angka dari S7.json) + catatan di lineup Aamon, Kagura (Lunox) dan Kalea
    (Badang + saran item damage ke Zilong). Peringkat tidak berubah. Dicek di browser (desktop & 375px), 92 gambar ada di disk.
18. (2026-10-21) Analisis 3 screenshot tutorial Go Go Box (1886–1888) ke data (`MCRoundRandomEquip_S7`, `AChooseHero`) dan
    pertandingan juara 1 (rekaman ponsel 28 menit). Rekaman HEVC tidak terbaca `video_frames.ps1` → dibuat `video_frames.py`
    (PyAV); `video_frames.ps1` diperbaiki agar berhenti dengan pesan dan tidak membuat JPG kosong. Go Go Box ditambahkan sebagai
    sumber crystal biasa di ringkasan, memori, dan `analisis_lineup.py` (MECHANICS). Analisa pertandingan hanya di chat.
19. (2026-10-21) Ekspor Go Go Box: `Season.go_go_box()` di `mc_data.py` → field `go_go_box` di S<n>.json, bagian "Go Go Box" di
    S<n>.md, tabel + pool (chip ikon + teks orb) di tab Info Season S<n>.html, S7 & S8. Helper `battle_config()`/`round_stages()`
    dipakai juga oleh `commander_damage()` (tabel DMG Commander tetap sama). `mc_validate.py` tetap 0 selisih. Dicek di browser.
20. (2026-10-21) `mc_diff.py` membandingkan `special_store` (`diff_special_store`) dan `go_go_box` (`diff_go_go_box`, `diff_pool`).
    Diuji dengan salinan S7.json yang diubah (harga/batas/peluang/item toko, isi babak, pool, babak hilang, catatan), file identik
    (0 perubahan), dan ekspor lama tanpa `go_go_box` ("tidak dibandingkan"). Diff sungguhan baru bisa setelah game update.

21. (2026-10-21, sesi cloud, repo `nabilhaidr/analisa-mcgg`) Melanjutkan 3 alat analisa di Linux (tanpa client game, rekaman,
    dan OCR Windows):
    - `mc_ocr.py` baru (OCR Windows atau RapidOCR, format sama) dipakai `mc_patch.py` dan `mc_match.py`; `requirements.txt`.
    - `mc_lineup.py`: hasil mode daftar hero/target sinergi/screenshot sama dengan laporan lama (OpenCV 5 di Linux); gambar
      screenshot di HTML kini path relatif (dulu `file:///F:/...`). `LINEUP_Astro_Power_6_Mage_4` dan `LINEUP_Hasil_21_Okt_15_38`
      dibuat ulang dengan kode terbaru (catatan "belum aktif" satu baris, ATK di tabel hero).
    - `mc_patch.py` dicek silang dengan 2 mesin OCR; kesalahan di `PATCH_Patch_Note_7_2` diperbaiki: Dyrroth "Babak I-4 >> I-3"
      (dulu terbaca 4 → 1, "sudah di file game"), Angela's Power "390 1640" → 120/230/390/640, baris Transmutation ganda, judul
      sampah "Dimen•innn' Qhnt", panah "(—)" = "~" (Solid Alliance), Abyssal Favor & Death Oracle kini "diterapkan server"
      (angka dicek di posisi kata yang sama, bukan di mana saja). Baris di atas judul pertama screenshot hasil scroll diberikan ke
      item yang benar. Draf `server_patch.json` (diuji dengan anggapan belum ada yang tercatat) kini sama dengan entri manual:
      Dyrroth 2 → 3 EXP, Lunox's Power id 3017 (bukan 3045 yang bernama sama), Angela's Power id 3061 "100 / 190 / 320/540".
      `mc_validate.py --season 7` tetap 0 selisih.
    - `mc_match.py`: perubahan `hud2` sesi lokal (shield, nama kuning, pengisian label babak) belum pernah dijalankan; di sini
      hanya bisa smoke test dengan 6 frame kunci 640 px (tanpa error). Diperbaiki: label babak = rantai terpanjang yang tidak
      mundur (satu label salah baca tidak lagi menggeser batas babak), HP awal babak dibuat tidak pernah naik dengan median
      (satu bacaan terlalu rendah tidak lagi menurunkan semua babak sesudahnya; kenaikan palsu 77 → 78 hilang), teks streak tidak
      masuk timeline, pencocokan kejadian tidak peka spasi. Layar hasil: RapidOCR membaca 16/16 nama (PC 1873 dulu 3/8),
      peringkat dari urutan baris "Level N". Laporan baru (hanya layar hasil): `MATCH_21_Okt_14_42_Minotaur` (peringkat 8) dan
      `MATCH_21_Okt_15_00_Angela` (peringkat 7).
    - `mc_vision.py`: ikon dicocokkan paralel (hasil identik, ±3,8× lebih cepat di 4 inti).
    - Koreksi ringkasan: juara 2/3 pertandingan 15:38 memakai **Kishin 6** (ikon merah bertanduk), bukan SPECTRE 6.

22. (2026-10-26) Repo lokal di-pull (`4062cb0`). `mc_lineup.py` (3 mode) dan `mc_patch.py` (20/10, 7.2) diuji di Windows: laporan
    identik dengan repo. `mc_match.py` diverifikasi di Windows dengan rekaman 15:38 (ponsel) dan Kalea 02:25 (PC); frame diekstrak
    ulang ke `cache/match/<nama>/frames`. Penyebab timeline meleset (dicek per frame, bacaan HP per frame ternyata benar):
    - Saat bertarung dua baris teratas bergeser ke kiri; di kanannya braket pedang + jumlah unit ("11", "25"). Angka itu dibaca
      sebagai HP, dan garis braket membuat baris dianggap ber-shield (angka OCR lalu dipercaya tanpa cek bar). Kini shield hanya
      dicek di kiri bar (segmen putih), angka HP hanya teks yang ujung kanannya sejajar ujung kanan bar, bar yang menyentuh tepi
      kiri crop = `cut` (batas bawah, seperti shield; PC: bar 64 px untuk HP 88).
    - Bar < 15% lebar panel (HP ≲ 35 ponsel) tidak terdeteksi → baris sendiri hilang di late game. Kini bar pendek dikenali dari
      bentuk (tinggi ≤ 1,17% tinggi frame, ujung rata); ikon hati lebih tinggi dan meruncing, chevron braket di kolom kanan.
    - OCR Windows melewatkan label pendek (IV-4, IV-6, V-1 redup di belakang toko) bahkan pada potongan tersendiri. Kini frame
      tanpa label di-OCR ulang dari potongan label 3× (`rounds/`, RapidOCR bila terpasang: "N-4" = IV-4), lalu sisanya dicocokkan
      dari tampilan (peta tepi Sobel pil label, korelasi ≥ 0,93 dan unggul ≥ 0,03; uji leave-one-out 427/427 benar).
    - Tanpa OCR, HP dari bar dikunci ke angka yang paling sering terbaca untuk pemain itu dengan panjang bar sama (selisih ±1 hilang);
      baris nama putih sendiri (Mirror) diabaikan bila ada baris kuning; HP awal babak = bacaan pertama bila 60% awal kosong;
      peringkat > 1 = HP 0 setelah babak terakhir dengan HP sendiri ("0" redup tidak terbaca OCR Windows).
    Hasil: 15:38 cocok 23/23 babak (I-1 – V-1, kalah I-2/II-1/II-2/II-5/II-6/III-5/IV-1, HP akhir 32); Kalea 17/17 + I-4 (88 → 79),
    IV-4 −18, IV-5 tereliminasi (peringkat 4). Hanya OCR Windows: 15:38 22/23 (V-1 tidak terbaca), Kalea 17/17. RapidOCR 1.2.3
    dipasang di Python lokal (OpenCV ikut naik ke 5.0.0): layar hasil 8/8 nama + level di kedua pertandingan. Laporan
    `MATCH_21_Okt_15_38_Minotaur` dan `MATCH_21_Okt_02_25_Kalea_PC` dibuat ulang; 4 frame kunci lama yang tidak dirujuk dihapus.
    Sisa: Gold awal babak kadang salah baca (0/6), babak non-tempur (II-3 pilih Go Go Card) memutus hitungan "kekalahan beruntun"
    (yang kedua diperbaiki di 32).

23. (2026-10-27) `mc_match.py` dijalankan untuk semua rekaman di `screenshot/season 7/match` (20 rekaman 21–26 Okt; 18 baru,
    2 worker paralel, ±8–17 menit per rekaman, frame di `cache/match/<nama>/frames`). Layar hasil dipasangkan dari waktu
    screenshot (mulai rekaman + durasi). Perbaikan selama batch:
    - Tanpa `--result`: layar hasil diambil dari frame akhir rekaman (`result_frames`: frame dengan ID pertandingan + judul kolom;
      panel "Hero yang Ditempatkan" di tengah permainan tidak punya ID). Di 15:38 hasilnya sama dengan screenshot.
    - Peringkat di layar hasil dari grid baris hero (`grid_ranks`), bukan urutan baris "Level N": di 22:43 "Levelg" + baris
      SABRINA (1 hero) membuat Arch. digabung ke TUKANG TOCO. Baris 1 hero kini ikut bila tepat di grid. Teks "Level" tanpa
      angka bukan nama.
    Hasil (peringkat, commander): 21 Okt 14-42 Minotaur 8, 15-00 Angela 7, 22-15 Fanny 5, 22-43 Fanny 1; 22 Okt 03-18 Fanny 4,
    04-55 Fanny 4, 06-16 Fanny 1; 23 Okt 21-47 Fanny 7, 22-08 Fanny 1; 24 Okt 02-51 Fanny 4, 14-43 Fanny 5, 15-06 Fanny 4,
    22-17 Fanny 7, 22-40 Fanny 8, 23-02 Minotaur 1; 25 Okt 23-24 Fanny 5, 23-49 Fanny 7; 26 Okt 00-09 Minotaur 4 (semula
    tercatat 3, lihat 26). Semua 20
    laporan konsisten (peringkat > 1: total kehilangan HP tepat 100; juara: HP akhir = 100 − total). 4 rekaman tanpa screenshot
    hasil (23 Okt 21-47, 24 Okt 14-43, 22-40, 25 Okt 23-24) memakai layar hasil dari rekaman. Nama non-Latin (Korea, dst.)
    tidak terbaca RapidOCR → "baris N" (1 nama di 22-43, 24 Okt 02-51/14-43/15-06, 25 Okt 23-24).
    Bukan input `mc_match`: 7 screenshot "Lineup Akhir" 20/10 (Kalea, Minotaur, Aamon, Luo Yi, Kagura), 2 daftar Riwayat, dan
    `Screenshot_2026-10-22-06-38-48` (Toko Spirit Sand di tengah permainan: "ATK Rekan +1%").

24. (2026-10-27) 7 screenshot Rekomendasi Lineup 20/10 di `match/` = 5 lineup (Kalea dan Luo Yi masing-masing 2 screenshot).
    `mc_lineup.py --board`: semua baris papan jadi satu lineup (baris 1 hero ikut, mis. Odette di lineup Luo Yi) dan jalur
    Go Go Card di bawah papan ikut terbaca; sebelumnya tiap baris papan dianggap lineup sendiri dan baris 1 hero dibuang.
    Laporan `LINEUP_Rekomendasi_<Kalea|Minotaur|Aamon|Luo_Yi|Kagura>_20_Okt.html/.md` (commander dan crystal dari lencana di
    potret diisi manual; Aamon level 10 karena 10 hero). Dicek ke papan tulisan tangan di `analisis_lineup.py`: hero 46/46,
    Go Go Card 30/30, sinergi aktif + jumlahnya sama dengan lencana di atas papan. Screenshot yang tidak dipakai: `23-51-21`
    (tooltip Eudora menutupi Suyou) dan `23-51-57` (kartu pertama tampil Alucard's Power, di `23-52-43` sudah Luo Yi's Power).

25. (2026-10-27) Nama "baris N" di layar hasil (5 laporan) ternyata 3 penyebab: OCR membaca "1254" tapi filter nama
    mensyaratkan 2 huruf Latin; "FET KAT" terbaca 2 potongan (diambil "FET"); nama Hangul (마샤 주니어, 카일라 잘라), "—X—", dan
    huruf hias "ᴍᴀʀsᴍᴇℓℓ" tidak menghasilkan teks sama sekali (model RapidOCR terpasang hanya Cina + Inggris, OCR Windows hanya
    en-US/en-GB; potongan nama 3× juga kosong, "—X—" jadi "1X1"). `mc_match.py`: nama = teks di kolom nama (sejajar "Level N",
    di atas tengah baris; huruf apa saja atau angka) + kata di sampingnya; bila tetap kosong, laporan menampilkan potongan
    gambar nama dari layar hasil (`match_<nama>/nama_<peringkat>.png`). Uji 20 pertandingan di `cache/match/_result`: hanya
    6 baris berubah, 158 sama. Dibuat ulang dari frame cache: `MATCH_21_Okt_22_43`, `24_Okt_02_51`, `24_Okt_14_43` ("1254"),
    `24_Okt_15_06`, `25_Okt_23_24` (+ "FET KAT"); timeline, HP, kejadian, dan peringkat tidak berubah.
    Ditemukan: peringkat 26 Okt 00-09 bergeser (diperbaiki di 26) dan 7 laporan punya level kosong karena "Level9" terbaca
    "Levelg" (diperbaiki di 27). Pemain Korea di 22-43 muncul sebagai "FL-loi" di tabel HP (OCR HUD; diperbaiki di 29).

26. (2026-10-27) Peringkat layar hasil 26 Okt 00-09: di screenshot `00-32-12` notifikasi "Saved screen recording" menutupi
    hero baris 1 (XXMAATT), sehingga `grid_ranks` memakai baris CUMA BISA HAMUI sebagai peringkat 1 dan semua peringkat
    bergeser satu; digabung dengan `00-32-16` (bersih) nama, hero, dan kartu dua baris bercampur, XXMAATT hilang, dan
    peringkat sendiri tercatat 3. Angka peringkat di kolom kiri tidak terbaca OCR (hanya angka level di avatar), tapi baris
    "Level N" terbaca 8/8 di semua layar hasil. `mc_match.py`: baris teratas = baris pertama dengan >= 2 hero, atau lebih
    tinggi bila ada baris "Level N" tepat satu langkah grid (atau lebih) di atasnya; jarak antarbaris tetap dari baris hero.
    `MATCH_26_Okt_00_09` dibuat ulang dari frame cache: **peringkat 4**, XXMAATT 1, CUMA BISA HAMUI 2, RR10 3, arkana 5,
    Via Riana 6, KING BALDWIN 7, Xuu 8 (cocok dengan layar); timeline dan HP tidak berubah. Uji 20 pertandingan di
    `cache/match/_result`: hanya 8 baris pertandingan ini yang berubah, 156 baris lain sama (nama, level, hero, kartu).
    Xuu: 8 dari 9 hero terdeteksi (sama seperti sebelumnya; diperbaiki di 28).

27. (2026-10-27) Level kosong di papan akhir: 24 baris di 7 laporan. 23 baris terbaca "Levelg" (53 dari 330 baris "Level" di
    `cache/match/_result`; layar menunjukkan "Level9"), 1 baris (saaaaa, 24 Okt 22-40) hanya "Level" tanpa angka di kedua
    frame hasil. `mc_match.py`, khusus layar hasil: "Levelg" = Level 9; bila angka tetap tidak ada, potongan baris "Level"
    itu (dengan margin) di-OCR ulang dan terbaca "Level9". Level HUD tidak diubah (hanya 1 "Level g" di ribuan bacaan HUD).
    Dibuat ulang dari frame cache: `MATCH_21_Okt_22_15`, `21_Okt_22_43`, `23_Okt_21_47`, `24_Okt_14_43`, `24_Okt_22_40`,
    `24_Okt_23_02`, `25_Okt_23_24`; kini 0 baris papan akhir tanpa level di 20 laporan. Uji 20 pertandingan: hanya 24 baris
    itu berubah (level kosong → 9), 140 sama; diff laporan hanya kolom level, waktu dibuat, dan catatan metode. `check.py`
    lolos, peringkat tidak berubah. Ditemukan: Giommy (24 Okt 14-43) 8 dari 9 hero terdeteksi, seperti Xuu di 26 (diperbaiki
    di 28).

28. (2026-10-28) Hero terlewat di layar hasil, dua penyebab. (a) Unit panggilan yang bukan hero season tidak punya ikon untuk
    dicocokkan: Giommy (24 Okt 14-43) punya **Turret** dari kartu "Turret of Guardians"; **Johnny** (commander Johnson) ada di
    8 baris, **Makhluk Suci** (commander Lukas) di 2. Ketiganya baris `MCHero` umum (bukan `MCHero_S7`) dengan `m_GuideType`
    3 yang diberikan sebuah efek (`OperEnum` 20002/20005, ID unit di `m_Para2`); bot latihan di tabel itu tidak diberikan efek
    apa pun. `mc_data.py` kini menulis `summons` di `S<n>.json` (+ ikon `HeroHead2900`, `MonsterHead47131`),
    `mc_vision.load_icons(..., "summon")` memuatnya, dan `mc_match.py` mencocokkannya bersama ikon hero. Di papan akhir unit
    ini tampil dengan ikon, tapi tidak ikut hitungan sinergi (sinerginya acak). Deteksi di kiri kolom Go Go Card diabaikan:
    avatar pemain commander Johnson = ikon Johnny (24 Okt 02-51, SINGKUANG kehilangan nama dan level). (b) Hero yang sama dua
    kali di papan dibuang karena baris dua screenshot digabung per nama: Xuu punya dua Lancelot; 10 baris di 7 pertandingan
    punya hero kembar (semua dicek di gambar). Kini baris digabung lewat tumpang-tindih urutan (baris tertutup notifikasi,
    daftar hero digeser), dan sinergi dihitung dari hero unik, sama seperti layar hasil (15:38 Cybertron: Marksman 4 dengan
    Miya ×2, bukan 5). Uji 20 pertandingan di `cache/match/_result`: 24 baris berubah (hanya kolom hero), 140 sama; 4 di
    antaranya urutan hero yang dulu salah (daftar digeser ke kiri). Dibuat ulang dari frame cache: `MATCH_21_Okt_14_42_Minotaur`,
    `21_Okt_15_00_Angela`, `21_Okt_15_38_Minotaur`, `21_Okt_22_43`, `22_Okt_03_18`, `22_Okt_04_55`, `23_Okt_22_08`,
    `24_Okt_02_51`, `24_Okt_14_43`, `24_Okt_22_17`, `24_Okt_22_40`, `25_Okt_23_24`, `25_Okt_23_49`, `26_Okt_00_09`. Diff
    laporan hanya baris papan akhir, waktu dibuat, dan catatan metode; nilai sinergi sama (5 baris hanya berubah urutan); 6
    laporan lain identik; `check.py` lolos. `S7`/`S8` dibuat ulang: hanya `summons` dan waktu ekstrak yang berubah.

29. (2026-10-28) Nama di tabel HP untuk nama yang tidak terbaca di layar hasil: OCR HUD membaca "마샤 주니어" (21 Okt 22-43,
    peringkat 8) sebagai "FL-loi", dan "ᴍᴀʀsᴍᴇℓℓ" (25 Okt 23-24, peringkat 2) sebagai "MagsMeee". `mc_match.py`
    (`unread_player`): bila layar hasil punya tepat 1 nama gambar dan tepat 1 pemain HUD yang tidak mirip nama mana pun di
    layar hasil (rasio 0,6) serta tampil bersama setiap pemain lain di >= 3 frame, baris HP itu memakai gambar nama yang sama
    dengan papan akhir (legenda grafik: "nama baris N (tidak terbaca OCR)"). Syarat frame bersama memisahkan potongan nama:
    "MCG" (24 Okt 02-51) = KeyyMCGG, "BAYW" (24 Okt 15-06) = BAYYY, "BAL" (26 Okt 00-09) = KINGBALDWIN; masing-masing 0 frame
    bersama dengan nama aslinya, sedangkan pemain berbeda minimal 7. Dibuat ulang: `MATCH_21_Okt_22_43`, `25_Okt_23_24`;
    diff hanya nama baris HP, legenda grafik, dan waktu dibuat; 18 laporan lain dan gambar `nama_*.png` identik; `check.py`
    lolos. Ditemukan, belum diperbaiki: di 24 Okt 02-51 (pemain Korea peringkat 6) dan 24 Okt 15-06 (peringkat 1 "—X—") pemain
    bernama gambar tidak masuk tabel HP karena slotnya terisi potongan nama (MCG, BAYW); nama HUD terpotong lain tidak diganti
    nama layar hasil ("AJII" = AJ11, "ENQ" = ENG, "GÖAT", "RRIO", dll., 10 laporan); SABRINA (21 Okt 22-43, peringkat 3, L10)
    hanya 1 hero di papan akhir (belum dicek di gambar).

30. (2026-10-28) Nama Hangul dibaca sebagai teks dengan model Korea RapidOCR (`cache/models/korean/`, lihat Lingkungan).
    `mc_ocr.read_korean` (TextRecognizer RapidOCR 1.2.3, model PP-OCRv5; tanpa model: langkah dilewati). `mc_match.py`:
    nama yang tidak terbaca OCR halaman dibaca dari potongan nama di setiap screenshot layar yang sama (skor tertinggi);
    dipakai bila >= 2 suku kata Hangul dan skor >= 0,6, selain itu tetap gambar. Variasi potongan (2x, padding, abu-abu,
    invert) tidak lebih baik. Hasil: "마샤 주니어" (21 Okt 22-43, tepat, 0,84), "카일라 장라" (24 Okt 02-51; di layar
    "카일라 잘라", 0,73); "ᴍᴀʀsᴍᴇℓℓ" dan "—X—" tidak berisi Hangul (≤ 0,38) dan tetap gambar. Catatan metode laporan
    menyebut nama dan skornya. Diperbaiki sekalian: `cluster_players` memakai nama layar hasil yang kuncinya kosong (Hangul)
    untuk setiap kluster ("" awalan semua kunci); di 02-51 SINGKUANG, KeyyMCGG, MCG sempat jadi "카일라 장라". Uji 20
    pertandingan: hanya 2 nama itu berubah, 160 baris sama. Dibuat ulang: `MATCH_21_Okt_22_43` (papan akhir + baris HP
    "마샤 주니어"), `24_Okt_02_51` (papan akhir; tabel HP tetap tanpa pemain ini karena slotnya terisi "MCG", lihat 29); diff
    hanya nama, legenda grafik, catatan metode, waktu dibuat; 18 laporan lain identik; `check.py` lolos. `nama_8.png`
    (22-43) dan `nama_6.png` (02-51) tidak dirujuk lagi.

31. (2026-10-28) Tabel "HP semua pemain": `cluster_players` baru. (a) Nama mirip tidak digabung bila tampil bersama di >= 3
    frame: "arkana" dan "Via Riana" (26 Okt 00-09, kemiripan 0,71) dulu satu baris berisi HP keduanya, Via Riana hilang.
    (b) Kluster yang terpisah (< 3 frame bersama) dari tepat satu kluster yang lebih besar dan tampil bersama semua yang
    lain = bacaan lain baris pemain itu, digabung (nama anggota dipakai `player_of`): "MCG" + "ANG" (02-51), "BAYW" (15-06),
    "BAL" + "BIS" (00-09), "Kanew...x" (14-43), "Q&100nLight" (23-02), varian "heprince"/"GÖAT"/"S 00 BR". (c) Nama layar
    hasil dipasang satu per kluster, pasangan terbaik dulu (`name_score` >= 0,6: awalan, bagian bersama >= 4 huruf, atau
    kemiripan; I/l/1 dan O/0 dianggap sama): AJII → AJ11, RRIO → RR10, OOLORENG → 0LORENGX00, GÖAT → D%GOATe,
    S 00 BR → Skyzoo BR, ENQ → ENG, MAC LAN → A4ACLAN YUKA. Pemain bernama gambar/Korea TIDAK bisa masuk tabel lewat ini:
    namanya tidak terbaca sama sekali di HUD (`read_frames` butuh >= 3 huruf Latin; di atas bar tanpa nama hanya kosong
    atau angka level). Tabelnya kini 7 baris dengan catatan siapa yang tidak ada (02-51 카일라 장라, 14-43 1254, 15-06
    peringkat 1 gambar, 23-02 EM). Dibuat ulang 20 laporan dari frame cache; 11 berubah, hanya tabel HP (+ catatan metode
    terbaru di Kalea PC dan 06-16): nama, baris potongan hilang, urutan Kalea PC, BAYYY 2 babak (= baris BAYW lama),
    arkana (nilai Via Riana keluar) dan baris baru Via Riana; timeline sendiri, kejadian, papan akhir tidak berubah;
    9 laporan lain identik (hasil buat ulang hanya beda waktu, file lama dipertahankan); `check.py` lolos. Kini setiap
    nama di tabel HP sama dengan nama layar hasil (atau gambarnya).

32. (2026-10-28, sesi cloud, langsung di `main`) `mc_match.py`, catatan otomatis dan daftar kejadian:
    - **Kekalahan beruntun** dulu terputus oleh setiap babak tanpa kehilangan HP, juga babak creep (lihat Temuan teknis). Kini
      `creep_round()` + `insights()`: babak creep tidak memutus dan tidak menambah kekalahan beruntun, dan catatan menyebut babak
      yang dilewati; babak creep dengan >= 2 pemain kehilangan HP tetap dihitung pertarungan (jaga-jaga jadwal season lain).
      8 dari 20 laporan berubah: Kalea PC 3 → 6 (I-4 s/d II-6), 22 Okt 06-16 4 → 8 (I-3 s/d III-1, lalu juara 1), 14-42 3 → 5,
      15-00 4 → 6, 03-18 2 → 3, 24 Okt 14-43 5 → 6, 22-17 4 → 6, 25 Okt 23-49 3 → 5. "Babak beruntun tanpa kehilangan HP" tetap
      menghitung babak creep (memang tanpa kehilangan HP).
    - **Event Win/Lose Streak dihapus**: diambil dari OCR frame penuh, jadi sering milik lawan yang tampil (64 dari 170 teks "Win
      Streak" muncul saat pemain sendiri sedang kalah beruntun, hanya 56 yang angkanya sama dengan streak menang sendiri; 37 dari
      38 "Lose Streak" memang milik sendiri tapi 36 tanpa angka), dan angka "Win streak" bisa terambil dari teks "Lose Streak".
    - Frame cache tidak ada di sesi cloud, jadi 20 laporan diperbarui dari tabelnya sendiri: `insights()` lama menghasilkan
      catatan yang persis sama dengan laporan lama di 20/20 laporan, lalu `insights()` baru dipakai; 208 baris streak keluar dari
      tabel Kejadian, catatan metode streak diganti, waktu dibuat diperbarui, bagian lain identik. Smoke test `mc_match.py
      --frames` dengan 8 frame kunci 640 px jalan tanpa error. Dibuat ulang dari frame cache di PC lokal pada 29 Okt: memang
      hanya waktu dibuat yang berbeda (lihat 36).
33. (2026-10-28) Riset tier list setelah Patch 7.2 dan ringkasan 140 papan pemain lain dari 20 laporan MATCH (lihat Analisis
    gameplay). Ringkasan ini dirapikan (tanggal, judul riwayat, Ide lanjutan).
34. (2026-10-28) `check_match.py`, pengganti `check.py` (yang asli tidak pernah di-commit; isinya tidak diketahui, jadi
    pemeriksaannya disusun ulang dari aturan yang dicatat di 23–31 plus aturan pembuatan laporan di `mc_match.py`). Hasil di
    20 laporan: 0 kesalahan, 2 peringatan (`match_21_Okt_22_43/nama_8.png` dan `match_24_Okt_02_51/nama_6.png` tidak dirujuk
    lagi sejak 30). Diuji dengan 14 salinan laporan yang sengaja dirusak (catatan md saja, catatan usang di md+html, HP awal,
    frame dihapus, hero tak dikenal, jumlah sinergi, dua "(kamu)", waktu dibuat html, baris Win streak, nama tabel HP, kotak
    HP akhir, catatan "Tidak ada di tabel" dihapus, tanda tereliminasi dihapus, urutan bertahan): 14/14 tertangkap. Laporan
    versi sebelum 32 ikut dicoba: 8 catatan usang dan baris streak di 20 laporan tertangkap. Nama kartu bergambar sama
    ("Rising Fury Ⅰ / Ⅱ / Ⅲ", "Reinforcement / Reinforcement+") memakai `mc_vision.icon_labels()`, dipisah dari `load_icons()`
    (hasil `load_icons` identik untuk hero, sinergi, unit panggilan, kartu, equipment). Satu kasus urutan bertahan vs
    peringkat (23 Okt 21-47: GAMEANEH peringkat 4 tak terbaca di IV-2, babak terakhir tabel) ternyata bacaan bolong saat
    rekaman berakhir, jadi babak terakhir tabel tidak dihitung dan pemeriksaan itu hanya peringatan.
35. (2026-10-28) `match_21_Okt_22_43/nama_8.png` ("마샤 주니어") dan `match_24_Okt_02_51/nama_6.png` ("카일라 잘라") dihapus: tidak
    dirujuk sejak 30 (nama kini teks dari model Korea). `check_match.py`: 0 kesalahan, 0 peringatan. Bila perlu, pulihkan dari
    commit `d58b21a`; `mc_match.py` membuatnya lagi hanya bila model Korea tidak ada (nama kembali berupa gambar).
36. (2026-10-29) PC lokal tertinggal 4 commit sesi cloud (32–35); ditarik fast-forward. 20 laporan MATCH dibuat ulang dari
    frame cache lokal dengan input yang sama seperti di 31 (`mc_match.py --frames cache\match\<nama>\frames --player CinCoeg
    --name ... --result <layar hasil>`): 20/20 hanya beda waktu dibuat (md per bagian, html, gambar `match_*/` identik), jadi
    pembaruan dari tabel di 32 sama dengan hasil `mc_match.py`. `check_match.py` pada hasil buat ulang: 0 kesalahan, 0
    peringatan; file lama dipertahankan. Tiga `mc_match.py` paralel kehabisan memori (18 dari 20 gagal saat mulai, lihat
    Lingkungan); yang gagal diulang satu per satu, 9 terakhir dengan `OPENBLAS_NUM_THREADS=1`, hasilnya juga hanya beda waktu
    dibuat. `check.py` asli ditemukan dan dibandingkan dengan `check_match.py` (lihat 37).
37. (2026-10-29) `check_match.py` dilengkapi dengan pemeriksaan `check.py` asli yang belum ada (TDD, tes baru
    `test_check_match.py`, 7 tes, jalan dengan pytest atau unittest): peringatan HP sendiri kosong di timeline (babak setelah
    tereliminasi dikecualikan: 23 Okt 21-47 IV-2 dan 25 Okt 23-24 IV-6 memang kosong), peringatan laporan tanpa papan akhir,
    dan satu baris ringkasan per laporan (pkt, HP akhir, babak pertama–terakhir, n, babak kalah, nama terbaca/baris papan).
    `check()` kini mengembalikan (kesalahan, peringatan, ringkasan). 20 laporan: 0 kesalahan, 0 peringatan; ringkasan sama
    dengan keluaran `check.py` asli kecuali "nama": kini hanya nama berupa teks yang dihitung terbaca (15-06 dan 23-24: 7/8;
    `check.py` menghitung gambar nama sebagai terbaca). `check.py` asli tidak diperlukan lagi.
38. (2026-10-29) `mc_match.py`: label kejadian di batas babak dan Gold awal (TDD, tes baru `test_mc_match.py`, 9 tes + 10
    potongan kotak Gold asli di `test_data/gold/`; diagnosis per frame dari frame cache 20 rekaman):
    - **Pilih Go Go Card** (awal II-3/III-3) tercatat satu babak terlalu awal: layar pemilihan menutup HUD tapi label babak
      tetap tampil redup, dan `rounds_by_look` melewatkan frame tanpa HUD, jadi frame itu ikut pembagian rata dan separuh
      awalnya jatuh ke babak sebelumnya (Kalea 575 s: label III-3, tercatat III-2). Kini frame tanpa HUD juga dicocokkan dari
      tampilan label (ambang sama, 0,93 dan selisih 0,03): di 20 rekaman 119 dari 817 frame tanpa HUD cocok (di Kalea frame
      tanpa label pill <= 0,36). 19 kejadian pindah (II-2→II-3 ×8, III-2→III-3 ×11), juga Pilih Kartu Power 22-43 I-1→I-2
      (label I-2, 0,991) dan Panel DMG yang terlihat di frame pemilihan yang sama (×3).
    - **Go Go Box** (layar "Pilih Hadiah" tanpa label) tetap ditebak dari pembagian rata: 12 dari 24 jatuh di babak pertama fase
      berikutnya, juga sebelum perbaikan ini. Data season menaruh Go Go Box di akhir fase (`go_go_box.rounds`: I-4, II-6,
      III-6, …), jadi `event_round()` memindahkan Go Go Box yang jatuh tepat satu babak sesudah babak jadwal: kini 24/24.
    - **Gold awal 0/6** (Kalea III-2/III-4) bukan salah baca angka Gold: kotak Gold sedang menampilkan harga jual unit yang
      diseret (label merah "1", tempat sampah "5") atau dialog. `gold_shown()`: angka kotak Gold dipakai hanya bila piksel
      kuning-jingga (HSV) >= 0,37 (penghitung Gold 0,48–0,95 di 3292 bacaan, termasuk 2 yang diredupkan overlay dengan angka
      benar; harga jual dan dialog <= 0,26 di 32 bacaan). 11 Gold awal berubah (mis. 22-43 III-1 9→37, 03-18 III-6 7→60,
      Kalea III-2 0→"-"), 6 rata-rata Gold per fase di catatan otomatis ikut berubah.
    20 laporan dibuat ulang dari frame cache (satu per satu): 19 berubah hanya di kejadian, kolom Kejadian timeline, Gold awal,
    dan rata-rata Gold; HP, perubahan, level, dan jumlah babak sama; 25 Okt 23-24 hanya beda waktu dibuat (file lama
    dipertahankan). `check_match.py`: 0 kesalahan, 0 peringatan.
39. (2026-10-30) `mc_match.py`: fallback RapidOCR untuk kotak Gold dan aturan Gold awal babak (TDD: `parse_gold`,
    `gold_labels`, Gold awal di `rounds_table`; 2 fixture baru `test_data/gold/*_lewat.png`). Di 20 rekaman OCR Windows tidak
    membaca angka di 1539 penghitung Gold yang tampil; RapidOCR pada kotak Gold saja (3x + tepi hitam, cache `golds/`, kode
    potong bersama `round_labels`: `box_crops`) membaca 694 di antaranya, dan angkanya sama dengan OCR Windows di 330/330
    penghitung yang terbaca keduanya. Angka satu digit (0–9) tetap tidak terbaca: detektor teks tidak menemukan satu karakter.
    Fallback hanya untuk frame yang HUD-nya tampil, karena layar transisi (pilih Go Go Card) meredupkan HUD dan menampilkan
    Gold sebelum pendapatan babak (Kalea 575 s: 15, lalu 22, 24). Bacaan yang lebih rapat menunjukkan pendapatan babak biasanya
    masuk di akhir babak sebelumnya, tapi kadang beberapa detik setelah label berganti (Kalea IV-5: 19 lalu 38), dan Gold awal
    lama kadang bacaan akhir babak yang sudah memuat pendapatan babak berikutnya (24 Okt 02-51 III-1: 47 di detik ke-75; Gold
    awal sebenarnya 37). Gold awal kini = Gold tertinggi dalam 10 detik sejak bacaan pertama babak (dengan bacaan pertama saja,
    6 babak memakai Gold sebelum pendapatan). 20 laporan dibuat ulang: hanya Gold awal yang berubah (59 naik, 4 turun = Gold
    akhir babak lama, 4 terisi; kosong 49 → 45 dari 407 babak), rata-rata Gold di catatan otomatis (16 laporan), dan satu
    catatan metode baru; kolom lain identik. `check_match.py`: 0 kesalahan, 0 peringatan.
40. (2026-10-30) `mc_match.py`/`mc_ocr.py`: Gold satu digit (TDD: 2 fixture `test_data/gold/*_satu.png`, tes baru
    `test_mc_ocr.py`). RapidOCR sebenarnya menemukan angka satu digit di kotak Gold, tapi skornya 0,24–0,5, di bawah
    `text_score` bawaannya 0,5, jadi dibuang. `gold_labels` kini membaca kotak Gold dengan `text_score` 0,1 (`GOLD_SCORE`):
    dari 823 kotak tanpa angka, 710 terbaca (dicek mata, benar; yang tertutup kursor mouse tetap kosong), dan 130/130 kotak
    yang sudah terbaca tetap sama. Pengenal saja (tanpa deteksi) pada daerah angka dicoba dulu tapi ditolak: tepi koin
    terbaca "0" atau "9" di depan angka (3 → 93), dan di PC ruang kosong di kiri angka satu digit yang ada di tengah terbaca
    "1" (0 → 10). `mc_ocr.run_rapid`/`ocr_folder` menerima `text_score` (bagian dari stamp cache; bawaan tetap 0,5) dan selalu
    mengirim ketiga ambang, karena RapidOCR menyimpan ambang terakhir yang diberikan. 20 laporan dibuat ulang: Gold awal
    kosong 45 → 2 dari 407 babak (43 terisi; 16 turun karena bacaan akhir babak diganti bacaan awal satu digit, mis. 24 Okt
    02-51 I-2 10 → 5, lalu I-3 memang mulai 10), rata-rata Gold di 3 laporan, dan catatan metode; kolom lain identik.
    `check_match.py`: 0 kesalahan, 0 peringatan.
41. (2026-10-30) `mc_match.py`: kejadian "Pilih Go Go Card" (TDD: `event_kinds`, `reopened_picks`). (a) 23 Okt 21-47
    mencatat pemilihan di II-6 (09:05) dan III-2 (11:55): layarnya asli ("Silakan pilih 1 Go Go Card", panel HP tampil), tapi
    itu pemilihan II-3 yang ditunda. Layar pemilihan bisa disembunyikan (tersisa tombol "Silakan pilih" di kiri) lalu dibuka
    lagi: II-3 Fast Promotion / Premium Client I, sama lagi di II-6, lalu Starbelle's Badge / Premium Client I di III-2
    setelah Refresh habis; layar hasil memang hanya menunjukkan 2 Go Go Card (Starbelle's Badge, Echomancer's Badge). Layar
    pemilihan yang memuat kartu dari pilihan sebelumnya kini ditandai "dibuka lagi, pilihan II-3: …". (b) 24 Okt 15-06 tanpa
    pemilihan III-3: OCR memotong teksnya jadi "Silakan | sh | ilih 1 Go Go Card." (satu-satunya varian yang terlewat di 20
    rekaman), jadi polanya kini "ilih 1 Go Go Card"; III-3 (13:45, Bright Sunshine) dan frame kuncinya kini ada. 20 laporan
    dibuat ulang: hanya kejadian 21-47 dan 15-06 dan catatan metode Go Go Card yang berubah; `check_match.py`: 0 kesalahan,
    0 peringatan.

## Lingkungan & catatan teknis
- Ghidra 12.1.4 di `C:\tools\ghidra_12.1.4_PUBLIC` (dipakai REA MCP). Untuk membongkar satu fungsi tanpa Ghidra dipakai
  skrip capstone + daftar simbol PDB (`text_all_syms.json`) di scratchpad sesi lama (folder sementara, bisa hilang).
- OCR Windows butuh bahasa English terpasang. `ocr.json` berukuran ±1 MB, dibuat ulang hanya untuk gambar yang berubah.
- RapidOCR (PP-OCRv3, `rapidocr_onnxruntime` 1.2.3) dibandingkan dengan OCR Windows pada 2026-10-21: layar hasil PC 1873 = 8/8 nama
  pemain (Windows 3/8), layar hasil ponsel 8/8 nama + level; patch note 20/10 dan 7.2 menghasilkan laporan `mc_patch.py` yang sama
  (RapidOCR juga membaca panah "Lukas (~)" yang terlewat OCR Windows). Kelemahan: kadang spasi hilang ("MCKOPAKEHAMA", "GoGo
  Card"); semua pencocokan nama/kejadian sudah tidak peka spasi. Waktu: ±4 detik per screenshot di container 4 inti.
- Model RapidOCR Korea (diunduh 2026-10-28 atas permintaan pengguna): `cache/models/korean/korean_PP-OCRv5_rec_mobile.onnx`
  (13.488.748 byte, SHA256 `cd6e2ea5…773c9b`) dari ModelScope `RapidAI/RapidOCR` v3.10.0, sesuai `default_models.yaml`
  RapidOCR. Daftar karakter (11.945, 11.172 Hangul) ada di metadata ONNX; dipakai lewat
  `rapidocr_onnxruntime.ch_ppocr_v3_rec.TextRecognizer({"model_path": ..., "rec_img_shape": [3, 48, 320]})`. `cache/` di-gitignore:
  setelah clone, unduh ulang.
- Sesi cloud (2026-10-28): `pip install -r requirements.txt` jalan (OpenCV 5.0.0, PyAV 19, RapidOCR); `mc_validate.py --season 7`
  bisa dijalankan (0 selisih, 17 cek manual). Frame cache `cache/match/` dan rekaman MP4 tidak ada, jadi laporan MATCH tidak bisa
  dibuat ulang di cloud (lihat 32). Jaringan dibatasi: halaman di luar daftar domain yang diizinkan (mis. loadoutgg.com,
  kitakuji.id) tidak bisa dibuka; tambahkan di pengaturan environment (Network access → Allowed domains) bila perlu.
- Unity persistentDataPath `C:\Users\nabil\AppData\LocalLow\mulonggame\MagicChessGoGo` hanya berisi log/cache WebView.
  Pertandingan tidak tersimpan lokal: `Player.log` hanya mencatat ID battle (ditimpa tiap game dibuka; sesi sebelumnya di
  `Player-prev.log`), `.data/db/Database.db` hanya antrean analitik.
- Drive F: adalah HDD eksternal USB. Pada 2026-10-21 koneksinya sempat putus (NTFS Event 140 "failed to flush", lalu Event 98
  "needs Full Chkdsk"; baca file → Input/output error, Edge headless macet). Diperbaiki dengan pindah kabel/port + `chkdsk F: /f`
  (tidak ada masalah, 0 bad sector). Kalau terjadi lagi: cek `Get-Volume -DriveLetter F` dan event NTFS sebelum menulis ke F:.
- RAM PC lokal 7,2 GB (page file 22 GB, batas commit ±29 GB). Pada 2026-10-29 sisa commit memori sering < 1 GB saat Chrome,
  WSL (vmmem ±3 GB), ChatGPT, Codex dan Claude terbuka, dan tiga `mc_match.py` paralel gagal (OpenBLAS "Memory allocation
  still failed", `MemoryError`, WinError 1450 "Insufficient system resources"). Satu `mc_match.py` memakai ±0,6 GB dan
  ±1,5–3 menit per laporan dari frame cache: buat ulang laporan satu per satu dan cek `FreeVirtualMemory`
  (`Get-CimInstance Win32_OperatingSystem`) dulu; `OPENBLAS_NUM_THREADS=1` menghemat memori tanpa mengubah hasil. Proses
  latar belakang yang dimulai Claude Code tetap berjalan walau sesinya berakhir: cek dulu sebelum menjalankan ulang.

## Ide lanjutan (belum dikerjakan)
- **Tenggat S7: 2026-11-15 17:59:59 (waktu server global).** Screenshot dan cek in-game S7 di bawah (Toko Spirit Sand, hero
  panggilan, Vexana) harus sebelum itu.
- Screenshot yang belum ada: hero panggilan Alpha, Gatotkaca, Layla, Moskov, Novaria, X.Borg (termasuk X.Borg ★3 "total 2000%
  ATK", rumus `N*10`), sinergi Chrono Wanderer dan Fan yang Bersorak.
- Jalankan diff sungguhan (`patch_tracker.py` + `mc_diff.py`) setelah update game berikutnya.
- S8: Kartu Power ada di level 3 (beda dengan S7); pengelompokan tab galeri S8 baru bisa dicek setelah ada screenshot S8.
- Isi `server_patch.json` untuk S8 begitu Patch Note S8 keluar (gunakan status dari `mc_validate.py`).
- Ambil screenshot Toko Spirit Sand (beberapa refresh) untuk memverifikasi harga/nama dan bonus ATK +2%/+3% yang
  sebenarnya (3% atau 2%?), lalu set `STORE_VERIFIED`. `mc_validate.py` belum mencocokkan `special_store` dan `go_go_box` ke screenshot (`mc_diff.py` sudah membandingkannya antar versi).
  Satu screenshot toko sudah ada: `match/Screenshot_2026-10-22-06-38-48` ("ATK Rekan +1%").
- Cek lagi tier list setelah Patch 7.2 / Penyesuaian 20/10 beberapa hari lagi (2026-10-28, dua kali: belum ada tier list
  tertulis, lihat Analisis gameplay).
- Cek in-game apakah bonus 30 Gold commander Vexana (Penyesuaian 20/10) aktif dari Lv 1 atau baru di Lv 2 ("Unrestricted").
- `mc_match.py` tabel HP: pemain yang namanya tidak terbaca di daftar HUD (카일라 잘라, "—X—", "1254", "EM") tidak masuk
  tabel; bar HP tanpa nama ada 1-4 per frame dari berbagai sebab, jadi perlu pelacakan bar (posisi/HP) untuk menautkannya
  (lihat 31). Cek SABRINA 21 Okt 22-43 (1 hero di papan akhir).
- `mc_match.py`: nama huruf hias/simbol ("ᴍᴀʀsᴍᴇℓℓ", "—X—") masih tampil sebagai gambar; model Korea membaca "카일라 잘라"
  sebagai "카일라 장라" (lihat 30).
