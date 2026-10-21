"""Snapshot & diff file patch Magic Chess: Go Go (PC).

Pemakaian:
  python patch_tracker.py snapshot              ambil snapshot kondisi sekarang
  python patch_tracker.py list                  daftar snapshot yang tersimpan
  python patch_tracker.py diff                  bandingkan 2 snapshot terakhir
  python patch_tracker.py diff A.json B.json    bandingkan 2 snapshot tertentu

Opsi --game <folder> untuk lokasi instalasi lain.

Sumber yang dicatat:
  manifest      manifest.json (md5 + size semua file game, dipakai launcher)
  rescheck      StreamingAssets/Document/windows/ResCheckConf.xml (md5 per asset bundle)
  mini_patch    MagicChessGoGo_Data/dragon2017/mini_patch (hotfix kecil antar-versi)
  lua_repair    MagicChessGoGo_Data/dragon2017/assets/LuaRepair (hotfix Lua, terenkripsi)
"""
import argparse
import hashlib
import json
import re
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
SNAP_DIR = HERE / "snapshots"
REPORT_DIR = HERE / "reports"
DEFAULT_GAME = Path(r"F:\Magic Chess\MagicChessGoGo\MagicChessGoGo")
DATA = "MagicChessGoGo_Data"
CONSOLE_LIMIT = 15

SOURCE_TITLES = {
    "manifest": "manifest.json (semua file game)",
    "rescheck": "ResCheckConf.xml (asset bundle)",
    "mini_patch": "mini_patch (hotfix kecil)",
    "lua_repair": "LuaRepair (hotfix Lua)",
}


def md5_file(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_manifest(game):
    m = json.loads((game / "manifest.json").read_text(encoding="utf-8"))
    files = {
        path: {"md5": info["md5"], "size": info["size"]}
        for path, info in m["files"].items()
        if info.get("type") == 0
    }
    return m.get("version"), files


def read_rescheck(game):
    # Bukan XML valid: ada baris hash setelah </root>, jadi diparse per <item>.
    text = (game / DATA / "StreamingAssets/Document/windows/ResCheckConf.xml").read_text(encoding="utf-8")
    items = {}
    for tag in re.findall(r"<item\s[^>]*>", text):
        attrs = dict(re.findall(r'(\w+)="([^"]*)"', tag))
        items[attrs["name"]] = {"md5": attrs.get("md5"), "size": int(attrs.get("size", 0)), "type": attrs.get("type")}
    version = re.search(r'<version name="([^"]*)"', text)
    return (version.group(1) if version else None), items


def read_folder(folder):
    if not folder.is_dir():
        return {}
    return {
        p.relative_to(folder).as_posix(): {"md5": md5_file(p), "size": p.stat().st_size}
        for p in sorted(folder.rglob("*"))
        if p.is_file()
    }


def take_snapshot(game):
    version, manifest = read_manifest(game)
    res_version, rescheck = read_rescheck(game)
    sources = {
        "manifest": manifest,
        "rescheck": rescheck,
        "mini_patch": read_folder(game / DATA / "dragon2017/mini_patch"),
        "lua_repair": read_folder(game / DATA / "dragon2017/assets/LuaRepair"),
    }

    snaps = list_snapshots()
    if snaps and load(snaps[-1])["sources"] == sources:
        print(f"Tidak ada perubahan sejak snapshot terakhir ({snaps[-1].name}); tidak disimpan.")
        return

    now = datetime.now()
    snap = {
        "taken_at": now.isoformat(timespec="seconds"),
        "game_dir": str(game),
        "version": version,
        "rescheck_version": res_version,
        "sources": sources,
    }
    SNAP_DIR.mkdir(exist_ok=True)
    out = SNAP_DIR / f"{version}_{now:%Y%m%d-%H%M%S}.json"
    out.write_text(json.dumps(snap, indent=1, sort_keys=True), encoding="utf-8")
    print(f"Snapshot tersimpan: {out}")
    print(f"  versi {version} | " + " | ".join(f"{k}: {len(v)} file" for k, v in sources.items()))


def list_snapshots():
    return sorted(SNAP_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime) if SNAP_DIR.is_dir() else []


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def diff_maps(old, new):
    return {
        "added": sorted(new.keys() - old.keys()),
        "removed": sorted(old.keys() - new.keys()),
        "changed": sorted(k for k in old.keys() & new.keys() if old[k] != new[k]),
    }


def manifest_group(path):
    parts = path.split("/")
    if parts[:2] == [DATA, "StreamingAssets"] and len(parts) > 3:
        return "StreamingAssets/" + parts[2]
    if parts[0] == DATA and len(parts) > 2:
        return f"{DATA}/{parts[1]}"
    return "(root)"


def human(n):
    for unit in ("B", "KB", "MB", "GB"):
        if abs(n) < 1024 or unit == "GB":
            return f"{n:.1f} {unit}" if unit != "B" else f"{n} B"
        n /= 1024


def do_diff(path_a, path_b):
    a, b = load(path_a), load(path_b)
    lines = [
        f"# Diff patch {a['version']} -> {b['version']}",
        "",
        f"- Lama: `{Path(path_a).name}` (diambil {a['taken_at']})",
        f"- Baru: `{Path(path_b).name}` (diambil {b['taken_at']})",
        "",
        "| Sumber | Ditambah | Dihapus | Berubah |",
        "|---|---|---|---|",
    ]
    results = {name: diff_maps(a["sources"].get(name, {}), b["sources"].get(name, {})) for name in SOURCE_TITLES}
    for name, r in results.items():
        lines.append(f"| {SOURCE_TITLES[name]} | {len(r['added'])} | {len(r['removed'])} | {len(r['changed'])} |")

    new_manifest = b["sources"]["manifest"]
    m = results["manifest"]
    download = sum(new_manifest[k]["size"] for k in m["added"] + m["changed"])
    lines += ["", f"Perkiraan ukuran file baru/berubah (manifest): **{human(download)}**", ""]

    groups = {}
    for kind in ("added", "removed", "changed"):
        for path in m[kind]:
            groups.setdefault(manifest_group(path), {"added": 0, "removed": 0, "changed": 0})[kind] += 1
    if groups:
        lines += ["## manifest per folder", "", "| Folder | Ditambah | Dihapus | Berubah |", "|---|---|---|---|"]
        for g in sorted(groups, key=lambda g: -sum(groups[g].values())):
            c = groups[g]
            lines.append(f"| {g} | {c['added']} | {c['removed']} | {c['changed']} |")
        lines.append("")

    labels = {"added": "Ditambah", "removed": "Dihapus", "changed": "Berubah"}
    for name, r in results.items():
        if not any(r.values()):
            continue
        lines += [f"## {SOURCE_TITLES[name]}", ""]
        old_src, new_src = a["sources"].get(name, {}), b["sources"].get(name, {})
        for kind in ("added", "removed", "changed"):
            if not r[kind]:
                continue
            lines += [f"### {labels[kind]} ({len(r[kind])})", ""]
            for key in r[kind]:
                if kind == "changed":
                    size = f"{human(old_src[key]['size'])} -> {human(new_src[key]['size'])}"
                else:
                    size = human((new_src if kind == "added" else old_src)[key]["size"])
                lines.append(f"- `{key}` ({size})")
            lines.append("")

    REPORT_DIR.mkdir(exist_ok=True)
    out = REPORT_DIR / f"diff_{Path(path_a).stem}_vs_{Path(path_b).stem}.md"
    out.write_text("\n".join(lines), encoding="utf-8")

    print(f"Diff {a['version']} -> {b['version']}")
    for name, r in results.items():
        print(f"  {SOURCE_TITLES[name]:<35} +{len(r['added']):<6} -{len(r['removed']):<6} ~{len(r['changed'])}")
    print(f"  Perkiraan ukuran file baru/berubah: {human(download)}")
    for name in ("rescheck", "mini_patch", "lua_repair"):
        r = results[name]
        shown = [("+", k) for k in r["added"]] + [("~", k) for k in r["changed"]] + [("-", k) for k in r["removed"]]
        if shown:
            print(f"\n  {SOURCE_TITLES[name]}:")
            for sign, key in shown[:CONSOLE_LIMIT]:
                print(f"    {sign} {key}")
            if len(shown) > CONSOLE_LIMIT:
                print(f"    ... {len(shown) - CONSOLE_LIMIT} lagi, lihat laporan")
    print(f"\nLaporan lengkap: {out}")


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Snapshot & diff patch Magic Chess: Go Go")
    parser.add_argument("--game", type=Path, default=DEFAULT_GAME, help="folder instalasi game")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("snapshot")
    sub.add_parser("list")
    d = sub.add_parser("diff")
    d.add_argument("old", nargs="?")
    d.add_argument("new", nargs="?")
    args = parser.parse_args()

    if args.cmd == "snapshot":
        take_snapshot(args.game)
    elif args.cmd == "list":
        for p in list_snapshots():
            s = load(p)
            print(f"{p.name:<40} versi {s['version']:<16} diambil {s['taken_at']}")
    elif args.cmd == "diff":
        if args.old and args.new:
            pair = [Path(args.old), Path(args.new)]
            pair = [p if p.exists() else SNAP_DIR / p for p in pair]
        else:
            snaps = list_snapshots()
            if len(snaps) < 2:
                sys.exit("Butuh minimal 2 snapshot. Jalankan 'snapshot' lagi setelah game update.")
            pair = snaps[-2:]
        do_diff(*pair)


if __name__ == "__main__":
    main()
