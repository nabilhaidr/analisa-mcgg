"""Bandingkan data season antar versi game: hero/skill/stat/sinergi/commander yang di-buff atau di-nerf, plus kartu,
equipment, Ensiklopedia, Toko Spirit Sand (harga/peluang/batas beli/efek) dan Go Go Box (isi per babak, pool, harga hero).

Pemakaian (Python biasa cukup, tidak butuh .venv):
  python mc_diff.py                        2 versi terakhir di data/, semua season yang ada di keduanya
  python mc_diff.py --season 7             hanya season 7
  python mc_diff.py LAMA.json BARU.json    bandingkan 2 file S<n>.json tertentu

Alur setelah game update: jalankan mc_data.py (membuat data/<versi baru>/), lalu mc_diff.py.
Hasil: ringkasan di terminal + data/diff/<lama>_vs_<baru>_S<n>.md

Label buff/nerf untuk stat dihitung pasti (naik = buff, kecuali "Batas Mana" yang naik = nerf).
Untuk teks skill/sinergi, angka yang naik/turun ditandai "kemungkinan buff/nerf" karena
konteks angkanya (damage, durasi, cooldown) tidak selalu bisa dipastikan dari teks.
"""
import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
NUMBER = re.compile(r"-?\d+(?:\.\d+)?")
LOWER_IS_BETTER = {"Batas Mana", "Mana max"}  # "Mana max" = label in older exports


def version_key(v):
    return tuple(int(x) if x.isdigit() else 0 for x in re.split(r"[._]", v))


def to_float(s):
    try:
        return float(str(s).rstrip("%"))
    except ValueError:
        return None


def text_change(old, new):
    """Describe how a description changed: (label, detail) or None when identical."""
    old, new = old or "", new or ""
    if old == new:
        return None
    if NUMBER.sub("#", old) == NUMBER.sub("#", new):
        pairs = [(a, b) for a, b in zip(NUMBER.findall(old), NUMBER.findall(new)) if a != b]
        ups = sum(float(b) > float(a) for a, b in pairs)
        label = ("angka naik (kemungkinan buff)" if ups == len(pairs)
                 else "angka turun (kemungkinan nerf)" if ups == 0 else "angka berubah")
        return label, ", ".join(f"{a} → {b}" for a, b in pairs)
    return "teks berubah", f"Lama: {old}\n  Baru: {new}"


def by_name(items):
    return {x["name"]: x for x in items}


def diff_skills(old_skills, new_skills, prefix="Skill"):
    out = []
    so, sn = by_name(old_skills), by_name(new_skills)
    out += [f"{prefix} baru **{n}**: {sn[n]['description']}" for n in sorted(sn.keys() - so.keys())]
    out += [f"{prefix} dihapus **{n}**" for n in sorted(so.keys() - sn.keys())]
    for n in sorted(so.keys() & sn.keys()):
        change = text_change(so[n]["description"], sn[n]["description"])
        if change:
            out.append(f"{prefix} **{n}**: {change[0]}: {change[1]}")
        co, cn = so[n].get("cooldown_ms"), sn[n].get("cooldown_ms")
        if co and cn and co != cn:
            out.append(f"{prefix} **{n}** cooldown {co / 1000:g}s → {cn / 1000:g}s ({'buff' if cn < co else 'nerf'})")
    return out


def overall(changes):
    text = " ".join(changes)
    buff = text.count("(buff)") + text.count("kemungkinan buff")
    nerf = text.count("(nerf)") + text.count("kemungkinan nerf")
    if buff and not nerf:
        return "BUFF"
    if nerf and not buff:
        return "NERF"
    return "campuran" if buff and nerf else "berubah"


def diff_heroes(a, b):
    ha, hb = by_name(a["heroes"]), by_name(b["heroes"])
    changed = {}
    for name in sorted(ha.keys() & hb.keys()):
        old, new = ha[name], hb[name]
        changes = []
        if old["cost"] != new["cost"]:
            changes.append(f"Cost {old['cost']} → {new['cost']}")
        if old["synergies"] != new["synergies"]:
            changes.append(f"Sinergi {', '.join(old['synergies'])} → {', '.join(new['synergies'])}")
        for star in sorted(old["stats"].keys() & new["stats"].keys(), key=int):
            so, sn = old["stats"][star], new["stats"][star]
            for label in sn:
                vo, vn = to_float(so.get(label)), to_float(sn[label])
                if vo is None or vn is None or vo == vn:
                    continue
                better = (vn > vo) != (label in LOWER_IS_BETTER)
                changes.append(f"★{star} {label}: {so[label]} → {sn[label]} ({'buff' if better else 'nerf'})")
        changes += diff_skills(old["skills"], new["skills"])
        if changes:
            changed[name] = changes
    return sorted(hb.keys() - ha.keys()), sorted(ha.keys() - hb.keys()), changed


def diff_synergies(a, b):
    key = lambda s: f"{s['name']} ({s['type']})"
    sa, sb = {key(s): s for s in a["synergies"]}, {key(s): s for s in b["synergies"]}
    changed = {}
    for name in sorted(sa.keys() & sb.keys()):
        old, new = sa[name], sb[name]
        changes = []
        joined, left = sorted(set(new["heroes"]) - set(old["heroes"])), sorted(set(old["heroes"]) - set(new["heroes"]))
        if joined:
            changes.append(f"Hero masuk: {', '.join(joined)}")
        if left:
            changes.append(f"Hero keluar: {', '.join(left)}")
        change = text_change(old["explain"], new["explain"])
        if change:
            changes.append(f"Penjelasan: {change[0]}: {change[1]}")
        to, tn = {t["count"]: t for t in old["tiers"]}, {t["count"]: t for t in new["tiers"]}
        changes += [f"Tier baru **{c}**: {tn[c]['effect']}" for c in sorted(tn.keys() - to.keys())]
        changes += [f"Tier dihapus **{c}**" for c in sorted(to.keys() - tn.keys())]
        for c in sorted(to.keys() & tn.keys()):
            change = text_change(to[c]["effect"], tn[c]["effect"])
            if change:
                changes.append(f"Tier **{c}**: {change[0]}: {change[1]}")
        if changes:
            changed[name] = changes
    return sorted(sb.keys() - sa.keys()), sorted(sa.keys() - sb.keys()), changed


def diff_commanders(a, b):
    ca, cb = by_name(a["commanders"]), by_name(b["commanders"])
    changed = {}
    for name in sorted(ca.keys() & cb.keys()):
        skills = lambda c: [dict(s["skill"], name=f"Lv {s['from_level']}+ {s['skill']['name']}", type=s.get("type"))
                            for s in c["skills"]]
        changes = diff_skills(skills(ca[name]), skills(cb[name]))
        types_old = {s["name"]: s["type"] for s in skills(ca[name])}
        changes += [f"Skill **{s['name']}**: {types_old[s['name']]} → {s['type']}" for s in skills(cb[name])
                    if types_old.get(s["name"]) and s["type"] and types_old[s["name"]] != s["type"]]
        # tooltip details (Alucard's "Hadiah", Lylia's prices, ...); exports older than the field have none to compare
        details = lambda c: {(s["name"], k["keyword"]): k["text"] for s in skills(c) for k in s.get("details") or []}
        do, dn = details(ca[name]), details(cb[name])
        if do:
            changes += [f"Detail baru **{s} · {k}**: {dn[s, k]}" for s, k in sorted(dn.keys() - do.keys())]
            changes += [f"Detail dihapus **{s} · {k}**" for s, k in sorted(do.keys() - dn.keys())]
            for s, k in sorted(do.keys() & dn.keys()):
                change = text_change(do[s, k], dn[s, k])
                if change:
                    changes.append(f"Detail **{s} · {k}**: {change[0]}: {change[1]}")
        if changes:
            changed[name] = changes
    return sorted(cb.keys() - ca.keys()), sorted(ca.keys() - cb.keys()), changed


def diff_texts(old_items, new_items):
    """Generic diff for {name: text}: added, removed and changed (with number-aware labels)."""
    changed = {}
    for name in sorted(old_items.keys() & new_items.keys()):
        change = text_change(old_items[name], new_items[name])
        if change:
            changed[name] = [f"{change[0]}: {change[1]}"]
    return sorted(new_items.keys() - old_items.keys()), sorted(old_items.keys() - new_items.keys()), changed


def diff_cards(a, b):
    # a card switching between active and inactive shows up as a text change ending in "[nonaktif]"
    texts = lambda d: {f"{c['name']} ({c['tier']})": c["description"] + ("" if c.get("active", True) else " [nonaktif]")
                       for c in d.get("cards", [])}
    return diff_texts(texts(a), texts(b))


def diff_encyclopedia(a, b):
    """Ensiklopedia text and tables (e.g. DMG Commander per babak), one entry per tab/section."""
    def texts(d):
        out = {}
        for tab in d.get("encyclopedia", []):
            for s in tab["sections"]:
                rows = [" | ".join(map(str, r)) for r in s.get("table", {}).get("rows", [])]
                out[f"{tab['name']} / {s.get('title') or '-'}"] = "\n".join([s.get("text", "")] + rows + [s.get("note", "")]).strip()
        return out
    return diff_texts(texts(a), texts(b))


def diff_equipment(a, b):
    texts = lambda d: {lv["name"]: "; ".join(lv["attributes"] + lv["unique"] + lv["passives"])
                       + ("" if e.get("active", True) else " [nonaktif]")
                       for e in d.get("equipment", []) for lv in e["levels"]}
    return diff_texts(texts(a), texts(b))


def range_text(x):
    return str(x["min"]) if x["min"] == x["max"] else f"{x['min']}–{x['max']}"


def diff_pool(title, old, new):
    """Membership, weight and name changes of a pool [{id, name, weight}] (Go Go Box)."""
    po, pn = {p["id"]: p for p in old}, {p["id"]: p for p in new}
    out = []
    if pn.keys() - po.keys():
        out.append(f"{title} masuk: " + ", ".join(pn[i]["name"] for i in sorted(pn.keys() - po.keys())))
    if po.keys() - pn.keys():
        out.append(f"{title} keluar: " + ", ".join(po[i]["name"] for i in sorted(po.keys() - pn.keys())))
    for i in sorted(po.keys() & pn.keys()):
        if po[i]["name"] != pn[i]["name"]:
            out.append(f"{title} #{i}: nama {po[i]['name']} → {pn[i]['name']}")
        if po[i]["weight"] != pn[i]["weight"]:
            out.append(f"{title} {pn[i]['name']}: bobot {po[i]['weight']} → {pn[i]['weight']}")
    return out


def diff_special_store(a, b):
    """Toko Spirit Sand per item (price, weight, purchase limit, effect) and the store itself.
    None when an export predates the field (nothing to compare)."""
    if "special_store" not in a or "special_store" not in b:
        return None
    sa, sb = a["special_store"] or {}, b["special_store"] or {}
    ia, ib = {i["name"]: i for i in sa.get("items", [])}, {i["name"]: i for i in sb.get("items", [])}
    limit = lambda x: x or "tanpa batas"
    changed = {}
    store = [f"{title}: {sa.get(k)} → {sb.get(k)}" for k, title in
             (("synergy", "Sinergi"), ("currency", "Mata uang"), ("max_storage", "Batas simpan"), ("total_weight", "Total bobot"))
             if sa and sb and sa.get(k) != sb.get(k)]
    if store:
        changed["(toko)"] = store
    for name in sorted(ia.keys() & ib.keys()):
        o, n = ia[name], ib[name]
        changes = []
        if o["price"] != n["price"]:  # cheaper = buff for the player
            changes.append(f"Harga {o['price']} → {n['price']} {sb.get('currency', '')} ({'buff' if n['price'] < o['price'] else 'nerf'})")
        if o["limit"] != n["limit"]:  # None = no limit
            more = (n["limit"] or float("inf")) > (o["limit"] or float("inf"))
            changes.append(f"Batas beli {limit(o['limit'])} → {limit(n['limit'])} ({'buff' if more else 'nerf'})")
        if o["weight"] != n["weight"]:
            changes.append(f"Peluang {o['chance']:g}% (bobot {o['weight']}) → {n['chance']:g}% (bobot {n['weight']})")
        for key, title in (("effect", "Efek"), ("description", "Teks")):
            change = text_change(o.get(key), n.get(key))
            if change:
                changes.append(f"{title}: {change[0]}: {change[1]}")
        joined, left = sorted(set(n.get("pool") or []) - set(o.get("pool") or [])), sorted(set(o.get("pool") or []) - set(n.get("pool") or []))
        if joined:
            changes.append(f"Pilihan masuk: {', '.join(joined)}")
        if left:
            changes.append(f"Pilihan keluar: {', '.join(left)}")
        if changes:
            changed[name] = changes
    return sorted(ib.keys() - ia.keys()), sorted(ia.keys() - ib.keys()), changed


def diff_go_go_box(a, b):
    """Go Go Box per round: orb counts, hero cost chances, pools. Rounds with identical changes (an item added to the
    pool of II-6 ... VIII-6) are listed once. None when an export predates the field."""
    if "go_go_box" not in a or "go_go_box" not in b:
        return None
    ba, bb = a["go_go_box"] or {}, b["go_go_box"] or {}
    ra, rb = {r["round"]: r for r in ba.get("rounds", [])}, {r["round"]: r for r in bb.get("rounds", [])}
    label = lambda r: f"{r['label']} (babak {r['round']})"
    costs = lambda r: " · ".join(f"{c['cost']} Gold {c['chance']:g}%" for c in r["heroes"]["costs"]) or "-"
    grouped = {}
    for n in sorted(ra.keys() & rb.keys()):
        o, w = ra[n], rb[n]
        changes = [f"{title}: {range_text(o[k])} → {range_text(w[k])}" for k, title in
                   (("equipment", "Equipment biasa"), ("crystals", "Crystal sinergi")) if range_text(o[k]) != range_text(w[k])]
        if o["special"]["count"] != w["special"]["count"]:
            changes.append(f"Kapasitas +1: {o['special']['count']} → {w['special']['count']}")
        if o["heroes"]["count"] != w["heroes"]["count"]:
            changes.append(f"Jumlah hero: {o['heroes']['count']} → {w['heroes']['count']}")
        if costs(o) != costs(w):
            changes.append(f"Harga hero: {costs(o)} → {costs(w)}")
        for k, title in (("equipment", "Pool equipment"), ("crystals", "Pool crystal"), ("special", "Item pengisi")):
            changes += diff_pool(title, o[k]["pool"], w[k]["pool"])
        if o.get("extra") != w.get("extra"):
            changes.append(f"Kolom lain: {o.get('extra') or '-'} → {w.get('extra') or '-'}")
        if changes:
            grouped.setdefault(tuple(changes), []).append(label(w))
    changed = {", ".join(rounds): list(changes) for changes, rounds in grouped.items()}
    no, nn = set(ba.get("notes", [])), set(bb.get("notes", []))
    if no != nn:
        changed["Catatan data"] = [f"Baru: {x}" for x in sorted(nn - no)] + [f"Hilang: {x}" for x in sorted(no - nn)]
    return [label(rb[n]) for n in sorted(rb.keys() - ra.keys())], [label(ra[n]) for n in sorted(ra.keys() - rb.keys())], changed


NOT_COMPARED = "tidak dibandingkan (salah satu ekspor belum punya data ini; jalankan ulang mc_data.py untuk versi itu)"


def report(a, b):
    sections = [("Hero", diff_heroes(a, b)), ("Sinergi", diff_synergies(a, b)), ("Commander", diff_commanders(a, b)),
                ("Go Go Card", diff_cards(a, b)), ("Equipment", diff_equipment(a, b)),
                ("Ensiklopedia", diff_encyclopedia(a, b)), ("Toko Spirit Sand", diff_special_store(a, b)),
                ("Go Go Box", diff_go_go_box(a, b))]
    lines = [f"# Diff Season {b['season']}: {a['game_version']} → {b['game_version']}", ""]
    summary = []
    for title, result in sections:
        if result is None:
            summary.append(f"{title}: {NOT_COMPARED}")
            continue
        added, removed, changed = result
        verdicts = [overall(c) for c in changed.values()]
        counts = ", ".join(f"{verdicts.count(v)} {v}" for v in ("BUFF", "NERF", "campuran", "berubah") if v in verdicts)
        summary.append(f"{title}: {len(added)} baru, {len(removed)} dihapus, {len(changed)} berubah"
                       + (f" ({counts})" if counts else ""))
    lines += [f"- {s}" for s in summary] + [""]
    for title, result in sections:
        lines += [f"## {title}", ""]
        if result is None:
            lines += [NOT_COMPARED[0].upper() + NOT_COMPARED[1:] + ".", ""]
            continue
        added, removed, changed = result
        if added:
            lines += [f"**Baru:** {', '.join(added)}", ""]
        if removed:
            lines += [f"**Dihapus:** {', '.join(removed)}", ""]
        for name, changes in changed.items():
            lines += [f"### {name}: {overall(changes)}", ""] + [f"- {c}" for c in changes] + [""]
        if not (added or removed or changed):
            lines += ["Tidak ada perubahan.", ""]
    return "\n".join(lines), summary


def pairs_from_data(seasons):
    versions = sorted((p.name for p in DATA.iterdir() if p.is_dir() and p.name != "diff"), key=version_key)
    if len(versions) < 2:
        sys.exit("Butuh data dari minimal 2 versi game. Jalankan mc_data.py lagi setelah game update.")
    old, new = versions[-2], versions[-1]
    common = sorted({int(p.stem[1:]) for p in (DATA / old).glob("S*.json")}
                    & {int(p.stem[1:]) for p in (DATA / new).glob("S*.json")})
    wanted = [s for s in common if not seasons or s in seasons]
    if not wanted:
        sys.exit(f"Tidak ada season yang sama di {old} dan {new}.")
    return [(DATA / old / f"S{s}.json", DATA / new / f"S{s}.json") for s in wanted]


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Diff data season Magic Chess: Go Go antar versi")
    ap.add_argument("files", nargs="*", type=Path, help="LAMA.json BARU.json (opsional)")
    ap.add_argument("--season", type=int, nargs="*")
    args = ap.parse_args()
    if args.files and len(args.files) != 2:
        sys.exit("Berikan tepat 2 file: LAMA.json BARU.json")
    pairs = [tuple(args.files)] if args.files else pairs_from_data(args.season)

    out_dir = DATA / "diff"
    out_dir.mkdir(parents=True, exist_ok=True)
    for old_path, new_path in pairs:
        a, b = (json.loads(p.read_text(encoding="utf-8")) for p in (old_path, new_path))
        text, summary = report(a, b)
        out = out_dir / f"{a['game_version']}_vs_{b['game_version']}_S{b['season']}.md"
        out.write_text(text, encoding="utf-8")
        print(f"Season {b['season']}: {a['game_version']} → {b['game_version']}")
        for s in summary:
            print(f"  {s}")
        print(f"  Laporan: {out}")


if __name__ == "__main__":
    main()
