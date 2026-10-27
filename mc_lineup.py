"""Analisa lineup Magic Chess: Go Go dari daftar hero, target sinergi, atau screenshot -> data/<versi>/LINEUP_<nama>.html/.md.

Pemakaian (Python sistem; screenshot butuh opencv-python):
  python mc_lineup.py --heroes "Odette, Gord, Vexana, Irithel, Atlas, Karina, Hilda, Zhuxin, Minotaur" \\
                      --crystals "Astro Power" --commander Minotaur --level 9
  python mc_lineup.py --synergies "Astro Power 6, Mage 4" --level 9 [--free-crystals 1] [--top 3]
  python mc_lineup.py --screenshot hasil.jpg [--row 2 | --all-rows] [--crystals ...]
  python mc_lineup.py --screenshot rekomendasi.jpg --board --commander Kalea --crystals "Dragon Altar, Defender"
                      (layar Rekomendasi Lineup: semua baris papan = satu lineup, jalur Go Go Card di bawahnya ikut)
  python mc_lineup.py --file lineup.txt        baris "heroes: ...", "crystals: ...", "synergies: ...", "commander: ...", "level: 9"
Opsi umum: --season 8, --capacity (Kapasitas +1 sudah diambil), --star 2 (bintang untuk tabel stat; per hero "Odette:3"),
--name "judul" (nama file).

Isi laporan: sinergi aktif + efeknya, tingkat berikutnya (hero/crystal yang dibutuhkan), jalur ultra, slot level, stok pool
dan peluang toko per harga, peluang crystal sinergi di Go Go Box, kartu/equipment yang terkait sinergi, skill commander, dan
catatan Patch server per hero. Mode --synergies mencari susunan hero yang memenuhi target dalam batas slot, lalu mengisi slot
sisa dengan hero yang paling banyak mengaktifkan sinergi tambahan. Penilaiannya dari angka game, bukan win rate.
Aturan dari pengalaman bermain ikut dipakai: hanya 1 crystal Pilihan yang aktif, Kapasitas +1 sekali per pertandingan.
"""
import argparse
import itertools
import re
import sys
from pathlib import Path

from mc_common import (Names, chip, esc, img, load_season, md_table, page, rel_src, shown_path, slug, split_list, stamp,
                       table, ul, write_report)

STAR = re.compile(r"\s*(?:[:*★]\s*|\s+★?)([123])\s*$")


# ------------------------------------------------------------------ input

def parse_heroes(items, names):
    """'Odette:3' / 'Odette ★2' -> [(hero, star or None)]; unknown names are reported."""
    out, unknown = [], []
    for raw in items:
        m = STAR.search(raw)
        star = int(m.group(1)) if m else None
        name = names.find(STAR.sub("", raw))
        (out.append((name, star)) if name else unknown.append(raw))
    return out, unknown


def parse_targets(text, names):
    """'Astro Power 6, Mage 4' -> {'Astro Power': 6, 'Mage': 4}."""
    out = {}
    for item in split_list(text):
        m = re.match(r"(.+?)\s*[x×:]?\s*(\d+)$", item)
        name = names.find(m.group(1) if m else item)
        if not name:
            raise SystemExit(f"Sinergi tidak dikenal: {item}")
        out[name] = int(m.group(2)) if m else 2
    return out


def read_file(path):
    fields = {}
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if ":" in line and not line.lstrip().startswith("#"):
            k, v = line.split(":", 1)
            fields[k.strip().lower()] = v.strip()
    return fields


# ------------------------------------------------------------------ analysis

class Game:
    def __init__(self, d):
        self.d = d
        self.H = {h["name"]: h for h in d["heroes"]}
        self.S = {s["name"]: s for s in d["synergies"]}
        self.C = {c["name"]: c for c in d["commanders"]}
        self.levels = {lv["level"]: lv for lv in d.get("info", {}).get("levels", [])}
        self.pool = d.get("info", {}).get("pool_per_hero", {})
        self.hero_names = Names(self.H, {"YSS": "Yi Sun-shin", "Xborg": "X.Borg"})
        self.syn_names = Names(self.S)
        self.cmd_names = Names(self.C)
        self.buyable = [h for h in d["heroes"] if not h.get("summoned")]

    def counts(self, heroes, crystals):
        out = {}
        for h in heroes:
            for s in self.H[h]["synergies"]:
                out[s] = out.get(s, 0) + 1
        for s in crystals:  # a crystal of the hero's own synergy still adds +1
            out[s] = out.get(s, 0) + 1
        return out

    def tier(self, syn, n):
        tiers = self.S[syn]["tiers"]
        reached = [t for t in tiers if t["count"] <= n]
        nxt = [t for t in tiers if t["count"] > n]
        return (reached[-1] if reached else None), (nxt[0] if nxt else None)

    def slots(self, level, capacity):
        lv = self.levels.get(level)
        return (lv["hero_slots"] if lv else level) + (1 if capacity else 0)

    def active_tiers(self, heroes, crystals):
        return {s: t for s, n in self.counts(heroes, crystals).items() if (t := self.tier(s, n)[0])}


def solve(game, targets, slots, crystals, free, top):
    """Hero sets that reach every target synergy count within the slots (crystals: fixed + `free` assignable ones).
    Core = minimal set for the targets; remaining slots get heroes that activate the most extra synergy tiers."""
    fixed = game.counts([], crystals)
    cand = [h["name"] for h in game.buyable if set(h["synergies"]) & set(targets)]
    cand.sort(key=lambda n: (-len(set(game.H[n]["synergies"]) & set(targets)), -game.H[n]["cost"]))
    cand = cand[:22]  # keeps the search fast; heroes sharing several targets come first

    def shortfall(heroes):
        c = game.counts(heroes, [])
        return sum(max(0, need - c.get(s, 0) - fixed.get(s, 0)) for s, need in targets.items())

    cores, seen = [], set()
    for k in range(1, slots + 1):
        for combo in itertools.combinations(cand, k):
            if shortfall(combo) <= free:
                key = frozenset(combo)
                if not any(c <= key for c in seen):  # skip supersets of a smaller core
                    seen.add(key)
                    cores.append(list(combo))
        if len(cores) >= 60:
            break
    results = []
    for core in cores:
        heroes = list(core)
        c = game.counts(heroes, [])
        extra = []  # free crystals go to the target that still misses most
        for _ in range(free):
            miss = {s: need - c.get(s, 0) - fixed.get(s, 0) - extra.count(s) for s, need in targets.items()}
            s = max(miss, key=miss.get)
            if miss[s] > 0:
                extra.append(s)
        while len(heroes) < slots:  # fill: most newly active tiers, then synergies brought closer, then cost
            best, best_key = None, None
            base = game.active_tiers(heroes, crystals + extra)
            have = game.counts(heroes, crystals + extra)
            for h in game.buyable:
                if h["name"] in heroes:
                    continue
                after = game.active_tiers(heroes + [h["name"]], crystals + extra)
                gained = sum(1 for s, t in after.items() if base.get(s) != t)
                key = (gained, sum(1 for s in h["synergies"] if s in have), h["cost"])
                if best_key is None or key > best_key:
                    best, best_key = h["name"], key
            if not best:
                break
            heroes.append(best)
        active = game.active_tiers(heroes, crystals + extra)
        score = (len(core), -len(extra), -sum(t["level"] for t in active.values()), -sum(game.H[h]["cost"] for h in core))
        results.append({"core": core, "heroes": heroes, "crystals": crystals + extra, "free_used": extra, "score": score})
    results.sort(key=lambda r: r["score"])
    unique, keys = [], set()
    for r in results:
        k = frozenset(r["heroes"])
        if k not in keys:
            keys.add(k)
            unique.append(r)
    return unique[:top]


def analyze(game, heroes, crystals, commander, level, capacity, stars, star_default):
    d, H = game.d, game.H
    slots = game.slots(level, capacity)
    counts = game.counts(heroes, crystals)
    syn_rows = []
    for s, n in sorted(counts.items(), key=lambda x: (-(game.tier(*x)[0] or {}).get("count", 0), -x[1], x[0])):
        cur, nxt = game.tier(s, n)
        missing = [h for h in game.S[s]["heroes"] if h not in heroes and not H.get(h, {}).get("summoned")]
        syn_rows.append({"name": s, "count": n, "crystal": crystals.count(s), "tier": cur, "next": nxt,
                         "first": game.S[s]["tiers"][0]["count"], "max": game.S[s]["tiers"][-1]["count"], "missing": missing})
    active = [r for r in syn_rows if r["tier"]]
    hero_rows = []
    for h in heroes:
        st = stars.get(h) or star_default
        server = (H[h].get("stats_server") or {}).get(str(st), {})
        hero_rows.append({"name": h, "star": st, "hero": H[h], "stats": {**(H[h]["stats"].get(str(st)) or {}), **server},
                          "server_stats": server})
    by_cost = {}
    for h in heroes:
        by_cost.setdefault(H[h]["cost"], []).append(h)
    syn_set = {r["name"] for r in syn_rows}
    text = lambda c: c["name"] + " " + (c.get("description_server") or c["description"])
    cards = [c for c in d["cards"] if c.get("active", True) and not c.get("removed_server") and any(s in text(c) for s in syn_set)]
    cmd = game.C.get(commander) if commander else None
    if cmd and cmd.get("power_card"):
        pc = next((c for c in d["cards"] if c["name"] == cmd["power_card"]["name"]), None)
        if pc and pc not in cards:
            cards.insert(0, pc)
    equip = [e for e in d["equipment"] if e.get("active", True) and e["category"].startswith("Eksklusif")
             and any(s in " ".join(lv["summary"] + " " + " ".join(lv["passives"]) for lv in e["levels"]) for s in syn_set)]
    box = []  # chance that a given synergy's crystal is among the Go Go Box crystals (equal weights, drawn without repeat)
    for r in (d.get("go_go_box") or {}).get("rounds", []):
        pool = [p for p in r["crystals"]["pool"] if not p.get("missing")]
        if pool and r["crystals"]["max"]:
            box.append({"label": r["label"], "min": r["crystals"]["min"], "max": r["crystals"]["max"], "size": len(pool),
                        "names": {p["name"].replace("Magic Crystal ", "") for p in pool}})
    notes = []
    if len(heroes) > slots:
        notes.append(("bad", f"{len(heroes)} hero melebihi slot Level {level} ({slots}{' termasuk Kapasitas +1' if capacity else ''})."))
    elif len(heroes) < slots:
        notes.append(("warn", f"Masih ada {slots - len(heroes)} slot kosong di Level {level}."))
    if len(crystals) > 1:
        notes.append(("", "Crystal Pilihan hanya 1 yang aktif; crystal lainnya harus crystal biasa (kartu Badge/Blessing, Legacy of "
                          "Valor, Prime Selection, creep IV-3, Go Go Box mulai II-6, Peti Magic Crystal)."))
    idle = [f"{r['name']} {r['count']}/{r['first']} ({', '.join(h for h in heroes if r['name'] in H[h]['synergies']) or 'crystal'})"
            for r in syn_rows if not r["tier"]]
    if idle:
        notes.append(("warn", "Belum aktif: " + "; ".join(idle) + "."))
    for r in syn_rows:
        if r["tier"] and r["next"] and r["next"]["count"] - r["count"] == 1:
            notes.append(("good", f"{r['name']} tinggal 1 lagi ke tingkat {r['next']['count']} "
                                  f"(crystal {r['name']} atau hero: {', '.join(r['missing'][:6]) or '-'})."))
    five = by_cost.get(5, [])
    if len(five) >= 2:
        notes.append(("warn", f"{len(five)} hero 5 Gold ({', '.join(five)}): masing-masing hanya {game.pool.get('5', '?')} salinan "
                              "di pool; ★2 butuh 3 salinan."))
    for h in heroes:
        for n in H[h].get("server", []):
            notes.append(("", f"{h}: Patch {n['patch']} (server) {n['text']}"))
    return {"heroes": heroes, "crystals": crystals, "commander": cmd, "level": level, "capacity": capacity, "slots": slots,
            "syn_rows": syn_rows, "active": active, "hero_rows": hero_rows, "by_cost": by_cost,
            "odds": (game.levels.get(level) or {}).get("shop_odds", []), "cards": cards, "equip": equip, "box": box, "notes": notes}


# ------------------------------------------------------------------ output

def hero_chip(game, name, extra=""):
    h = game.H[name]
    return chip(name + extra, h.get("icon"), f"c{h['cost']}", ", ".join(h["synergies"]) + f" · {h['cost']} Gold")


def syn_chip(game, name, n=None, on=True):
    return chip(f"{name} {n}" if n is not None else name, game.S[name].get("icon"), "on" if on else "off")


def stat_text(r, mark="*"):
    st = r["stats"]
    atk = max(float(st.get("Physical ATK", 0) or 0), float(st.get("Magic ATK", 0) or 0))
    srv = mark if {"Physical ATK", "Magic ATK"} & set(r["server_stats"]) else ""
    return f"★{r['star']}: HP {st.get('HP', '-')}, ATK {atk:g}{srv}"


def next_text(r):
    if not r["next"]:
        return "maks"
    return f"+{r['next']['count'] - r['count']} ke {r['next']['count']}: " + (", ".join(r["missing"][:8]) or "hanya crystal")


def render_html(game, a):
    S = game.S
    chips = "".join(syn_chip(game, r["name"], r["count"]) for r in a["active"])
    boxes = [f'<div class="box good"><h4>Sinergi aktif</h4><p>{chips or "-"}</p></div>',
             f'<div class="box"><h4>Slot & biaya</h4><p>{len(a["heroes"])}/{a["slots"]} hero di Level {a["level"]}'
             f'{" (+Kapasitas +1)" if a["capacity"] else ""} · total {sum(game.H[h]["cost"] for h in a["heroes"])} Gold harga dasar'
             f' · crystal: {esc(", ".join(a["crystals"]) or "-")}</p></div>']
    if a["commander"]:
        c = a["commander"]
        boxes.append(f'<div class="box"><h4>Commander</h4><p>{img(c.get("icon"), "big", c["name"])}<b>{esc(c["name"])}</b> '
                     f'<span class="muted">({esc(c.get("category", ""))})</span></p></div>')
    notes = "".join(f'<li class="{cls}">{esc(t)}</li>' if cls else f"<li>{esc(t)}</li>" for cls, t in a["notes"])
    out = [f'<section><h2>Ringkasan</h2><div class="grid3">{"".join(boxes)}</div>'
           f'<h3>Catatan otomatis</h3><ul>{notes or "<li>-</li>"}</ul></section>']
    rows = []
    for r in a["hero_rows"]:
        skill = r["hero"]["skills"][0] if r["hero"]["skills"] else {}
        rows.append([hero_chip(game, r["name"]), f'{r["hero"]["cost"]} Gold', esc(", ".join(r["hero"]["synergies"])),
                     esc(stat_text(r)).replace("*", '<span class="warn" title="nilai Patch server">*</span>'),
                     esc(skill.get("name", "-"))])
    out.append(f'<section><h2>Hero</h2>{table(["Hero", "Harga", "Sinergi", "Stat", "Skill"], rows)}'
               '<p class="muted small">* = angka Patch server (bukan file game).</p></section>')
    rows = [[syn_chip(game, r["name"], on=bool(r["tier"])), f'{r["count"]}' + (f' (+{r["crystal"]} crystal)' if r["crystal"] else ""),
             f'{r["tier"]["count"]}: {esc(r["tier"]["effect"])}' if r["tier"] else '<span class="muted">belum aktif</span>',
             esc(next_text(r))] for r in a["syn_rows"]]
    out.append(f'<section><h2>Sinergi</h2>{table(["Sinergi", "Jumlah", "Tingkat aktif", "Tingkat berikutnya"], rows)}</section>')
    ultra = [r for r in a["active"] if r["max"] >= 10]
    if ultra:
        items = [f'<b>{esc(r["name"])} {r["max"]}</b>: butuh +{r["max"] - r["count"]} lagi '
                 f'({esc(", ".join(r["missing"]) or "tidak ada hero lain")} + crystal). '
                 f'Tingkat {r["max"]}: {esc(S[r["name"]]["tiers"][-1]["effect"])}' for r in ultra]
        out.append(f'<section><h2>Jalur ultra</h2>{ul(items)}<p class="muted small">Ultra faksi 6 hero = 6 hero + 1 crystal Pilihan '
                   "+ 3 crystal biasa (sumber acak).</p></section>")
    rows = [[f"{c} Gold", ", ".join(map(esc, a["by_cost"].get(c, []))) or "-", game.pool.get(str(c), "-"),
             f'{a["odds"][c - 1]}%' if len(a["odds"]) >= c else "-"] for c in range(1, 6)]
    out.append(f'<section><h2>Stok & peluang toko (Level {a["level"]})</h2>'
               f'{table(["Harga", "Hero di lineup", "Salinan per hero", "Peluang toko"], rows)}'
               '<p class="muted small">★2 = 3 salinan, ★3 = 9 salinan; pool dipakai bersama semua pemain.</p></section>')
    if a["box"]:
        main = [r["name"] for r in a["active"] if any(r["name"] in b["names"] for b in a["box"])]
        rows = [[esc(b["label"]), f'{b["min"]}–{b["max"]} dari {b["size"]}',
                 f'{100 * b["min"] / b["size"]:.0f}–{100 * b["max"] / b["size"]:.0f}%'] for b in a["box"]]
        out.append(f'<section><h2>Crystal dari Go Go Box</h2><p>Peluang crystal satu sinergi tertentu (mis. '
                   f'{esc(", ".join(main[:3]) or "-")}) muncul di Go Go Box, bila bobotnya sama:</p>'
                   f'{table(["Go Go Box", "Crystal sinergi", "Peluang sinergi tertentu"], rows)}'
                   '<p class="muted small">Urutan memilih dari HP terendah: pemain HP tinggi bisa kehabisan.</p></section>')
    if a["commander"]:
        c = a["commander"]
        items = [f'<b>Lv {s["from_level"]}+ {esc(s.get("type", ""))}: {esc(s["skill"]["name"])}</b> — '
                 f'{esc(s["skill"].get("description_server") or s["skill"]["description"])}' for s in c["skills"]]
        if c.get("power_card"):
            items.append(f'<b>Kartu Power {esc(c["power_card"]["name"])}</b> — {esc(c["power_card"]["description"])}')
        out.append(f'<section><h2>Commander {esc(c["name"])}</h2>{ul(items)}</section>')
    if a["cards"]:
        rows = [[chip(c["name"], c.get("icon")), esc(c["tier"]), esc(c.get("description_server") or c["description"])] for c in a["cards"]]
        out.append(f'<section><h2>Go Go Card terkait</h2>{table(["Kartu", "Tingkat", "Efek"], rows)}</section>')
    if a["equip"]:
        rows = [[chip(e["levels"][0]["name"], e.get("icon")), esc(e["category"]),
                 esc("; ".join(e["levels"][0]["attributes"] + e["levels"][0]["passives"]))] for e in a["equip"]]
        out.append(f'<section><h2>Equipment terkait sinergi</h2>{table(["Equipment", "Jenis", "Efek"], rows)}</section>')
    return "".join(out)


def render_md(game, a, heading="##"):
    lines = [f"{heading} Ringkasan", "",
             f"- Sinergi aktif: {', '.join(f'{r['name']} {r['count']}' for r in a['active']) or '-'}",
             f"- {len(a['heroes'])}/{a['slots']} hero di Level {a['level']}{' (+Kapasitas +1)' if a['capacity'] else ''}; "
             f"crystal: {', '.join(a['crystals']) or '-'}"]
    if a["commander"]:
        lines.append(f"- Commander: {a['commander']['name']}")
    lines += [""] + [f"- {t}" for _, t in a["notes"]] + ["", f"{heading} Hero", ""]
    lines += md_table(["Hero", "Harga", "Sinergi", "Stat", "Skill"],
                      [[r["name"], f"{r['hero']['cost']} Gold", ", ".join(r["hero"]["synergies"]), stat_text(r),
                        (r["hero"]["skills"][0]["name"] if r["hero"]["skills"] else "-")] for r in a["hero_rows"]])
    lines += ["", "_* = angka Patch server (bukan file game)._"]
    lines += ["", f"{heading} Sinergi", ""]
    lines += md_table(["Sinergi", "Jumlah", "Tingkat aktif", "Tingkat berikutnya"],
                      [[r["name"], f"{r['count']}" + (f" (+{r['crystal']} crystal)" if r["crystal"] else ""),
                        f"{r['tier']['count']}: {r['tier']['effect']}" if r["tier"] else "belum aktif", next_text(r)]
                       for r in a["syn_rows"]])
    ultra = [r for r in a["active"] if r["max"] >= 10]
    if ultra:
        lines += ["", f"{heading} Jalur ultra", ""] + [
            f"- **{r['name']} {r['max']}**: butuh +{r['max'] - r['count']} lagi ({', '.join(r['missing']) or 'tidak ada hero lain'} "
            f"+ crystal). Tingkat {r['max']}: {game.S[r['name']]['tiers'][-1]['effect']}" for r in ultra]
    lines += ["", f"{heading} Stok & peluang toko (Level {a['level']})", ""]
    lines += md_table(["Harga", "Hero di lineup", "Salinan per hero", "Peluang toko"],
                      [[f"{c} Gold", ", ".join(a["by_cost"].get(c, [])) or "-", game.pool.get(str(c), "-"),
                        f"{a['odds'][c - 1]}%" if len(a["odds"]) >= c else "-"] for c in range(1, 6)])
    if a["box"]:
        lines += ["", f"{heading} Crystal dari Go Go Box", ""]
        lines += md_table(["Go Go Box", "Crystal sinergi", "Peluang sinergi tertentu"],
                          [[b["label"], f"{b['min']}–{b['max']} dari {b['size']}",
                            f"{100 * b['min'] / b['size']:.0f}–{100 * b['max'] / b['size']:.0f}%"] for b in a["box"]])
    if a["commander"]:
        c = a["commander"]
        lines += ["", f"{heading} Commander {c['name']}", ""]
        lines += [f"- **Lv {s['from_level']}+ {s.get('type', '')}: {s['skill']['name']}** — "
                  f"{(s['skill'].get('description_server') or s['skill']['description']).replace(chr(10), ' ')}" for s in c["skills"]]
    if a["cards"]:
        lines += ["", f"{heading} Go Go Card terkait", ""]
        lines += [f"- **{c['name']}** ({c['tier']}): {(c.get('description_server') or c['description']).replace(chr(10), ' ')}"
                  for c in a["cards"]]
    if a["equip"]:
        lines += ["", f"{heading} Equipment terkait sinergi", ""]
        lines += [f"- **{e['levels'][0]['name']}** ({e['category']}): {'; '.join(e['levels'][0]['attributes'] + e['levels'][0]['passives'])}"
                  for e in a["equip"]]
    return lines + [""]


# ------------------------------------------------------------------ main

def from_screenshot(d, folder, path, row, all_rows, board=False):
    import mc_vision
    rows = [r for r in mc_vision.rows(mc_vision.detect(path, mc_vision.load_icons(d, folder, "hero"), "hero"))
            if board or len(r) >= 2]
    if not rows:
        raise SystemExit("Tidak ada ikon hero yang dikenali di screenshot ini (papan 3D/toko tidak bisa; pakai layar hasil, "
                         "Rekomendasi Lineup, atau panel Hero yang Ditempatkan).")
    cards = mc_vision.rows(mc_vision.detect(path, mc_vision.load_icons(d, folder, "card"), "card"))
    if board:  # Rekomendasi Lineup: every grid row (also a lone hero) is one lineup; the Go Go Card path is a row below
        return [{"heroes": list(dict.fromkeys(f["name"] for r in rows for f in r)), "row": "papan",
                 "cards": [f["name"] for r in cards for f in r]}], len(rows)
    picked = rows if all_rows else [rows[min(max(row, 1), len(rows)) - 1]]
    out = []
    for r in picked:
        y = sum(f["y"] for f in r) / len(r)
        near = next((c for c in cards if abs(sum(f["y"] for f in c) / len(c) - y) < r[0]["size"] * 0.6), [])
        out.append({"heroes": list(dict.fromkeys(f["name"] for f in r)), "row": rows.index(r) + 1,
                    "cards": [f["name"] for f in near]})
    return out, len(rows)


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Analisa lineup dari daftar hero, target sinergi, atau screenshot")
    ap.add_argument("--heroes")
    ap.add_argument("--synergies", help="target, mis. 'Astro Power 6, Mage 4'")
    ap.add_argument("--screenshot", type=Path)
    ap.add_argument("--file", type=Path)
    ap.add_argument("--crystals", default="")
    ap.add_argument("--commander")
    ap.add_argument("--level", type=int, default=9)
    ap.add_argument("--capacity", action="store_true", help="Kapasitas +1 sudah diambil (slot +1)")
    ap.add_argument("--free-crystals", type=int, default=1, help="crystal bebas untuk mode --synergies (default 1 = Pilihan)")
    ap.add_argument("--top", type=int, default=3)
    ap.add_argument("--star", type=int, default=2)
    ap.add_argument("--row", type=int, default=1)
    ap.add_argument("--all-rows", action="store_true")
    ap.add_argument("--board", action="store_true", help="semua baris = satu lineup (layar Rekomendasi Lineup)")
    ap.add_argument("--season", type=int)
    ap.add_argument("--version")
    ap.add_argument("--name")
    args = ap.parse_args()
    if args.file:
        f = read_file(args.file)
        args.heroes = args.heroes or f.get("heroes")
        args.synergies = args.synergies or f.get("synergies")
        args.crystals = args.crystals or f.get("crystals", "")
        args.commander = args.commander or f.get("commander")
        args.level = int(f.get("level", args.level))
    if not (args.heroes or args.synergies or args.screenshot):
        ap.error("isi --heroes, --synergies, --screenshot, atau --file")

    d, folder = load_season(args.season, args.version)
    game = Game(d)
    crystals = []
    for c in split_list(args.crystals):
        name = game.syn_names.find(c)
        if not name:
            raise SystemExit(f"Crystal sinergi tidak dikenal: {c}")
        crystals.append(name)
    commander = game.cmd_names.find(args.commander) if args.commander else None
    if args.commander and not commander:
        raise SystemExit(f"Commander tidak dikenal: {args.commander}")

    lineups, intro, intro_md = [], "", []
    if args.screenshot:
        found, total = from_screenshot(d, folder, args.screenshot, args.row, args.all_rows, args.board)
        lineups = [{"title": "Papan" if args.board else f"Baris {f['row']}", "heroes": f["heroes"], "stars": {},
                    "crystals": crystals, "cards": f["cards"]} for f in found]
        picked = "semua baris sebagai satu papan" if args.board else "baris " + ", ".join(str(f["row"]) for f in found)
        intro = (f'<section><h2>Screenshot</h2><p><img class="shot" src="{esc(rel_src(args.screenshot, folder))}" alt=""></p>'
                 f'<p class="muted">{total} baris hero dikenali dari ikon; dianalisa: {picked}. '
                 "Crystal tidak terlihat dari ikon: isi --crystals bila ada.</p></section>")
        intro_md = [f"Screenshot: `{shown_path(args.screenshot)}` · {total} baris hero dikenali; dianalisa: {picked}", ""]
    elif args.heroes:
        heroes, unknown = parse_heroes(split_list(args.heroes), game.hero_names)
        if unknown:
            raise SystemExit(f"Hero tidak dikenal: {', '.join(unknown)}")
        lineups.append({"title": "Lineup", "heroes": [h for h, _ in heroes], "stars": {h: s for h, s in heroes if s},
                        "crystals": crystals})
    else:
        targets = parse_targets(args.synergies, game.syn_names)
        slots = game.slots(args.level, args.capacity)
        found = solve(game, targets, slots, crystals, args.free_crystals, args.top)
        if not found:
            raise SystemExit(f"Target {targets} tidak bisa dicapai dengan {slots} slot dan {args.free_crystals} crystal bebas.")
        lineups = [{"title": f"Kandidat {i}", "heroes": r["heroes"], "stars": {}, "crystals": r["crystals"], "core": r["core"],
                    "free": r["free_used"]} for i, r in enumerate(found, 1)]
        rows = [[f'<a href="#lu{i}">Kandidat {i}</a>', " ".join(hero_chip(game, h) for h in lu["heroes"]),
                 esc(", ".join(lu["crystals"]) or "-"),
                 " ".join(syn_chip(game, s, game.counts(lu["heroes"], lu["crystals"])[s])
                          for s in game.active_tiers(lu["heroes"], lu["crystals"]))] for i, lu in enumerate(lineups, 1)]
        target_text = ", ".join(f"{s} {n}" for s, n in targets.items())
        intro = (f'<section><h2>Target: {esc(target_text)}</h2><p class="muted">{slots} slot (Level {args.level}'
                 f'{" + Kapasitas +1" if args.capacity else ""}), crystal tetap: {esc(", ".join(crystals) or "-")}, '
                 f'crystal bebas: {args.free_crystals}. Inti = hero minimal untuk target; slot sisa diisi hero yang paling banyak '
                 'mengaktifkan sinergi tambahan.</p>' + table(["Kandidat", "Hero", "Crystal", "Sinergi aktif"], rows) + "</section>")
        intro_md = [f"Target: **{target_text}** · {slots} slot · crystal tetap {', '.join(crystals) or '-'} · "
                    f"crystal bebas {args.free_crystals}", ""] + \
                   [f"- Kandidat {i}: {', '.join(lu['heroes'])} (crystal: {', '.join(lu['crystals']) or '-'})"
                    for i, lu in enumerate(lineups, 1)] + [""]

    body, md = [intro], list(intro_md)
    for i, lu in enumerate(lineups, 1):
        a = analyze(game, lu["heroes"], lu["crystals"], commander, args.level, args.capacity, lu["stars"], args.star)
        head = f"{lu['title']}: " + ", ".join(f"{r['name']} {r['count']}" for r in a["active"][:3])
        extra = f'<p>Go Go Card terdeteksi: {" ".join(chip(c) for c in lu["cards"])}</p>' if lu.get("cards") else ""
        if lu.get("core"):
            extra += f'<p class="muted">Inti target: {esc(", ".join(lu["core"]))}; crystal bebas dipakai: {esc(", ".join(lu["free"]) or "-")}</p>'
        body.append(f'<section id="lu{i}"><h2>{esc(head)}</h2><p>{" ".join(hero_chip(game, h) for h in lu["heroes"])}</p>{extra}</section>')
        body.append(render_html(game, a))
        md += [f"# {head}", "", ", ".join(lu["heroes"]), ""]
        if lu.get("cards"):
            md += [f"Go Go Card terdeteksi: {', '.join(lu['cards'])}", ""]
        md += render_md(game, a)
        print(f"{head}  ({len(lu['heroes'])} hero)")
    name = args.name or args.synergies or f"{lineups[0]['title']} {' '.join(lineups[0]['heroes'][:3])}"
    title = f"Analisa Lineup — {name}"
    out_html, out_md = write_report(folder, f"LINEUP_{slug(name)}", page(title, "".join(body), stamp(d)),
                                    [f"# {title}", "", f"_{stamp(d)}_", ""] + md)
    print(f"Laporan: {out_html}\n         {out_md}")


if __name__ == "__main__":
    main()
