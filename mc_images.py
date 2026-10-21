"""Ikon laporan (hero, commander, sinergi, equipment, Go Go Card, skill) dari atlas UI game.

Atlas UI Magic Chess: Go Go memakai format NGUI: tiap bundle StreamingAssets/UI/windows/<Atlas>.unity3d berisi satu
Texture2D dan satu MonoBehaviour (UIAtlas) yang daftar mSprites-nya menyimpan nama + kotak tiap ikon (x, y, width,
height; titik asal kiri atas). Tabel data merujuk ikon sebagai "<Atlas>/<nama sprite>": MCHero.m_Head,
MCEquipBase.m_Icon, RelationSkillTip_MC.m_RelationIcon, MCSuperCrystalKey.m_MiniIcon, MCSkill.m_IconFile.

attach_icons() mengganti setiap field "icon" berisi rujukan itu dengan path relatif ke PNG di data/<versi>/img/<Atlas>/,
sehingga S<n>.html bisa memuatnya langsung. Gambar yang sudah ada tidak diekstrak ulang.
"""
from pathlib import Path

from mc_tables import DATA

UI_DIR = f"{DATA}/StreamingAssets/UI/windows"
IMG_DIR = "img"


def _icon_fields(node):
    """Yield every dict that has a string "icon" field, anywhere in the season data."""
    if isinstance(node, dict):
        if isinstance(node.get("icon"), str):
            yield node
        for v in node.values():
            yield from _icon_fields(v)
    elif isinstance(node, list):
        for v in node:
            yield from _icon_fields(v)


def _atlas_sprites(bundle):
    """(PIL image of the atlas texture, {sprite name: rect}) from one NGUI atlas bundle."""
    import UnityPy  # only needed when an icon is not extracted yet

    texture, rects = None, {}
    for obj in UnityPy.load(str(bundle)).objects:
        if obj.type.name == "Texture2D":
            texture = obj.read().image
        elif obj.type.name == "MonoBehaviour":
            rects.update({s["name"]: s for s in obj.read_typetree().get("mSprites", [])})
    return texture, rects


def export_icons(game, refs, out_dir):
    """Write out_dir/img/<Atlas>/<sprite>.png for every "<Atlas>/<sprite>" ref; return {ref: relative path}.
    Refs whose atlas bundle or sprite does not exist are left out."""
    by_atlas = {}
    for ref in refs:
        atlas, _, sprite = ref.partition("/")
        if atlas and sprite and "/" not in sprite:
            by_atlas.setdefault(atlas, set()).add(sprite)
    found = {}
    for atlas, sprites in sorted(by_atlas.items()):
        folder = out_dir / IMG_DIR / atlas
        todo = {s for s in sprites if not (folder / f"{s}.png").exists()}
        if todo:
            bundle = game / UI_DIR / f"{atlas}.unity3d"
            if not bundle.exists():
                continue
            texture, rects = _atlas_sprites(bundle)
            if texture is None:
                continue
            folder.mkdir(parents=True, exist_ok=True)
            for s in todo & rects.keys():
                r = rects[s]
                texture.crop((r["x"], r["y"], r["x"] + r["width"], r["y"] + r["height"])).save(folder / f"{s}.png", optimize=True)
        for s in sprites:
            if (folder / f"{s}.png").exists():
                found[f"{atlas}/{s}"] = f"{IMG_DIR}/{atlas}/{s}.png"
    return found


def attach_icons(season_data, game, out_dir):
    """Replace "icon" refs in the season data with image paths (None when the game has no such sprite).
    Returns (number of icons found, refs not found)."""
    nodes = list(_icon_fields(season_data))
    paths = export_icons(Path(game), {n["icon"] for n in nodes}, Path(out_dir))
    missing = sorted({n["icon"] for n in nodes} - paths.keys())
    for n in nodes:
        n["icon"] = paths.get(n["icon"])
    return len(paths), missing
