<#
OCR semua screenshot in-game satu season dengan OCR bawaan Windows (en-US) -> <folder>\ocr.json (dipakai mc_validate.py).
Gambar diperbesar 2x supaya teks kecil (popup Detail Hero) terbaca. Gambar yang tidak berubah (ukuran + waktu ubah sama)
diambil dari ocr.json sebelumnya, jadi menjalankan ulang setelah menambah screenshot hanya memproses gambar baru.

Pemakaian (dari folder patch-tracker):
  powershell -ExecutionPolicy Bypass -File ocr_screens.ps1 -Season 7
  powershell -ExecutionPolicy Bypass -File ocr_screens.ps1 -Folder "screenshot\season 7"

Hasil: {"version": 1, "images": {"<path relatif>": {"stamp", "w", "h", "lines": [{"t", "x", "y", "r", "b"}]}}}
(koordinat dalam piksel gambar asli).
#>
param([int]$Season = 0, [string]$Folder = "")

if (-not $Folder) {
    if ($Season -le 0) { throw "Isi -Season <n> atau -Folder <path>" }
    $Folder = Join-Path $PSScriptRoot "screenshot\season $Season"
}
if (-not (Test-Path -LiteralPath $Folder)) { throw "Folder screenshot tidak ada: $Folder" }
$Folder = (Resolve-Path -LiteralPath $Folder).Path
$Out = Join-Path $Folder "ocr.json"

Add-Type -AssemblyName System.Runtime.WindowsRuntime
$null = [Windows.Media.Ocr.OcrEngine, Windows.Foundation, ContentType = WindowsRuntime]
$null = [Windows.Graphics.Imaging.BitmapDecoder, Windows.Graphics.Imaging, ContentType = WindowsRuntime]
$null = [Windows.Storage.StorageFile, Windows.Storage, ContentType = WindowsRuntime]
$null = [Windows.Globalization.Language, Windows.Globalization, ContentType = WindowsRuntime]
$asTask = ([System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object {
    $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1' })[0]
function Await($op, [Type]$type) {
    $task = $asTask.MakeGenericMethod($type).Invoke($null, @($op))
    $task.Wait(-1) | Out-Null
    $task.Result
}
$engine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromLanguage([Windows.Globalization.Language]::new('en-US'))
if (-not $engine) { throw "OCR Windows bahasa en-US tidak tersedia (Settings > Time & language > Language > English)." }
$scale = 2

$cache = @{}
if (Test-Path -LiteralPath $Out) {
    $old = Get-Content -LiteralPath $Out -Raw -Encoding utf8 | ConvertFrom-Json
    if ($old.images) { foreach ($p in $old.images.PSObject.Properties) { $cache[$p.Name] = $p.Value } }
}

$images = [ordered]@{}
$files = Get-ChildItem -LiteralPath $Folder -Recurse -File | Where-Object { $_.Extension -in '.png', '.jpg', '.jpeg' } |
    Sort-Object FullName
$done = 0
foreach ($f in $files) {
    $rel = $f.FullName.Substring($Folder.Length).TrimStart('\')
    $stamp = "$($f.Length)-$($f.LastWriteTimeUtc.Ticks)"
    if ($cache.ContainsKey($rel) -and $cache[$rel].stamp -eq $stamp) {
        $images[$rel] = $cache[$rel]
        continue
    }
    $file = Await ([Windows.Storage.StorageFile]::GetFileFromPathAsync($f.FullName)) ([Windows.Storage.StorageFile])
    $stream = Await ($file.OpenAsync([Windows.Storage.FileAccessMode]::Read)) ([Windows.Storage.Streams.IRandomAccessStream])
    $decoder = Await ([Windows.Graphics.Imaging.BitmapDecoder]::CreateAsync($stream)) ([Windows.Graphics.Imaging.BitmapDecoder])
    $transform = [Windows.Graphics.Imaging.BitmapTransform]::new()
    $transform.ScaledWidth = [uint32]($decoder.PixelWidth * $scale)
    $transform.ScaledHeight = [uint32]($decoder.PixelHeight * $scale)
    $transform.InterpolationMode = [Windows.Graphics.Imaging.BitmapInterpolationMode]::Fant
    $bitmap = Await ($decoder.GetSoftwareBitmapAsync([Windows.Graphics.Imaging.BitmapPixelFormat]::Bgra8,
        [Windows.Graphics.Imaging.BitmapAlphaMode]::Premultiplied, $transform,
        [Windows.Graphics.Imaging.ExifOrientationMode]::IgnoreExifOrientation,
        [Windows.Graphics.Imaging.ColorManagementMode]::DoNotColorManage)) ([Windows.Graphics.Imaging.SoftwareBitmap])
    $ocr = Await ($engine.RecognizeAsync($bitmap)) ([Windows.Media.Ocr.OcrResult])
    $lines = New-Object System.Collections.ArrayList
    foreach ($l in $ocr.Lines) {
        $rects = $l.Words | ForEach-Object { $_.BoundingRect }
        [void]$lines.Add([ordered]@{
            t = $l.Text
            x = [int](($rects | ForEach-Object { $_.X } | Measure-Object -Minimum).Minimum / $scale)
            y = [int](($rects | ForEach-Object { $_.Y } | Measure-Object -Minimum).Minimum / $scale)
            r = [int](($rects | ForEach-Object { $_.X + $_.Width } | Measure-Object -Maximum).Maximum / $scale)
            b = [int](($rects | ForEach-Object { $_.Y + $_.Height } | Measure-Object -Maximum).Maximum / $scale)
        })
    }
    $images[$rel] = [ordered]@{ stamp = $stamp; w = [int]$decoder.PixelWidth; h = [int]$decoder.PixelHeight; lines = $lines }
    $stream.Dispose()
    $done++
    if ($done % 25 -eq 0) { Write-Output "  $done gambar di-OCR ..." }
}
[ordered]@{ version = 1; images = $images } | ConvertTo-Json -Depth 6 -Compress | Out-File -LiteralPath $Out -Encoding utf8
Write-Output "$($files.Count) gambar ($done baru di-OCR, $($files.Count - $done) dari cache) -> $Out"
