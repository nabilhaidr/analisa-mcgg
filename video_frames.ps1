<#
Ambil frame dari rekaman pertandingan (MP4) dengan API Windows.Media.Editing (tanpa ffmpeg), untuk analisis pertandingan.
Frame yang sudah ada tidak diambil ulang. Setelah itu bisa di-OCR: ocr_screens.ps1 -Folder <Out>.

Pemakaian (dari folder patch-tracker):
  powershell -ExecutionPolicy Bypass -File video_frames.ps1 -Video "screenshot\season 7\match\<rekaman>.mp4" -Out <folder> -Step 5
  Opsi: -Start <detik> -End <detik> -Width <piksel, default 1280>
Hasil: <Out>\f_<detik, 5 digit>.jpg (rekaman 20 menit, -Step 5 = 248 frame, ±1 detik per frame).
Rekaman layar ponsel biasanya HEVC (H.265), yang tidak bisa di-decode API ini (0xC00D5212): pakai video_frames.py (PyAV).
#>
param([string]$Video, [string]$Out, [double]$Step = 10, [double]$Start = 0, [double]$End = 0, [int]$Width = 1280)

Add-Type -AssemblyName System.Runtime.WindowsRuntime
$null = [Windows.Storage.StorageFile, Windows.Storage, ContentType = WindowsRuntime]
$null = [Windows.Media.Editing.MediaClip, Windows.Media.Editing, ContentType = WindowsRuntime]
$null = [Windows.Media.Editing.MediaComposition, Windows.Media.Editing, ContentType = WindowsRuntime]
$asTask = ([System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object {
    $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1' })[0]
function Await($op, [Type]$type) {
    $task = $asTask.MakeGenericMethod($type).Invoke($null, @($op))
    try { $task.Wait(-1) | Out-Null } catch { throw $task.Exception.InnerException }
    $task.Result
}

New-Item -ItemType Directory -Force -Path $Out | Out-Null
$file = Await ([Windows.Storage.StorageFile]::GetFileFromPathAsync((Resolve-Path -LiteralPath $Video).Path)) ([Windows.Storage.StorageFile])
$clip = Await ([Windows.Media.Editing.MediaClip]::CreateFromFileAsync($file)) ([Windows.Media.Editing.MediaClip])
$comp = [Windows.Media.Editing.MediaComposition]::new()
# Clips is a WinRT IList; PowerShell 5.1 does not expose .Add() on it, so call it through the .NET interface
try { $comp.Clips.Append($clip) } catch {
    [System.Collections.Generic.ICollection[Windows.Media.Editing.MediaClip]].GetMethod('Add').Invoke($comp.Clips, @($clip)) | Out-Null
}
$dur = $clip.OriginalDuration.TotalSeconds
$props = $clip.GetVideoEncodingProperties()
$height = [int]($Width * $props.Height / $props.Width)
"Durasi {0:N1} detik, {1}x{2}, {3}/{4} fps" -f $dur, $props.Width, $props.Height, $props.FrameRate.Numerator, $props.FrameRate.Denominator
if ($End -le 0 -or $End -gt $dur) { $End = $dur - 0.5 }
$n = 0
for ($t = $Start; $t -le $End; $t += $Step) {
    $path = Join-Path $Out ("f_{0:00000}.jpg" -f [int]$t)
    if (Test-Path -LiteralPath $path) { continue }
    try {
        $img = Await ($comp.GetThumbnailAsync([TimeSpan]::FromSeconds($t), $Width, $height,
                      [Windows.Media.Editing.VideoFramePrecision]::NearestFrame)) ([Windows.Graphics.Imaging.ImageStream])
    } catch {
        # e.g. 0xC00D5212 for HEVC phone recordings without a usable Windows decoder: stop instead of writing empty files
        throw ("Frame detik {0} gagal di-decode (codec {1}): {2} Untuk rekaman HEVC pakai: python video_frames.py" -f
               $t, $props.Subtype, $_.Exception.Message)
    }
    $src = [System.IO.WindowsRuntimeStreamExtensions]::AsStreamForRead($img)
    $dst = [System.IO.File]::Create($path)
    $src.CopyTo($dst)
    $dst.Close(); $src.Close()
    $n++
}
"$n frame baru di $Out"
