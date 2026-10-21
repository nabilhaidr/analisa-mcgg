"""Bagian bersama alat analisa (mc_lineup.py, mc_patch.py, mc_match.py): data season terbaru, pencocokan nama,
dan halaman HTML/MD dengan gaya yang sama. Halaman ditulis ke data/<versi>/ supaya path ikon "img/..." dari S<n>.json
langsung bisa dipakai.
"""
import difflib
import html
import json
import re
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]


def version_key(v):
    return tuple(int(x) if x.isdigit() else 0 for x in re.split(r"[._]", v))


def latest_version():
    versions = [p.name for p in DATA.iterdir() if p.is_dir() and any(p.glob("S*.json"))]
    if not versions:
        raise SystemExit("Belum ada data/<versi>/S<n>.json. Jalankan dulu: .venv\\Scripts\\python mc_data.py")
    return max(versions, key=version_key)


def load_season(season=None, version=None):
    """(season data, data folder). Default: the lowest season of the newest version (= active season; the next
    season's file sits next to it, e.g. S7 aktif + S8 berikutnya)."""
    folder = DATA / (version or latest_version())
    seasons = sorted(int(p.stem[1:]) for p in folder.glob("S*.json") if p.stem[1:].isdigit())
    if not seasons:
        raise SystemExit(f"Tidak ada S<n>.json di {folder}")
    sid = season or seasons[0]
    path = folder / f"S{sid}.json"
    if not path.exists():
        raise SystemExit(f"{path} tidak ada (season tersedia: {', '.join(map(str, seasons))})")
    return json.loads(path.read_text(encoding="utf-8")), folder


def norm(text):
    for k, v in {"Ⅰ": "i", "Ⅱ": "ii", "Ⅲ": "iii", "Ⅳ": "iv", "Ⅴ": "v"}.items():
        text = text.replace(k, v)
    return re.sub(r"[^a-z0-9]", "", text.lower())


class Names:
    """Fuzzy lookup of game names (hero, synergy, commander, ...): exact after normalising, then difflib."""

    def __init__(self, names, aliases=None):
        self.by_key = {norm(n): n for n in names}
        for alias, name in (aliases or {}).items():
            self.by_key.setdefault(norm(alias), name)

    def find(self, text, cutoff=0.72):
        key = norm(text)
        if not key:
            return None
        if key in self.by_key:
            return self.by_key[key]
        m = difflib.get_close_matches(key, list(self.by_key), n=1, cutoff=cutoff)
        return self.by_key[m[0]] if m else None


def split_list(text):
    """'Odette, Gord; Vexana' / newline separated -> items."""
    return [x.strip() for x in re.split(r"[,;\n]+", text or "") if x.strip()]


def slug(text):
    return re.sub(r"[^A-Za-z0-9]+", "_", text).strip("_")[:60] or "analisa"


def round_label(rnd, stages=((1, 4), (5, 10), (11, 16))):
    """Round number -> I-2 / II-1 ... (phase IV and later are 6 rounds each, like the game)."""
    for i, (a, b) in enumerate(stages):
        if a <= rnd <= b:
            return f"{ROMAN[i]}-{rnd - a + 1}"
    start, i = stages[-1][1] + 1, len(stages)
    while rnd > start + 5:
        start, i = start + 6, i + 1
    return f"{ROMAN[i] if i < len(ROMAN) else i + 1}-{rnd - start + 1}"


# ------------------------------------------------------------------ HTML / Markdown

def esc(x):
    return html.escape(str(x))


def img(src, cls="", alt="", title=None):
    t = f' title="{esc(title)}"' if title else ""
    return f'<img src="{esc(src)}" class="{cls}" alt="{esc(alt)}" loading="lazy"{t}>' if src else ""


def chip(text, icon=None, cls="", title=None):
    t = f' title="{esc(title)}"' if title else ""
    return f'<span class="chip {cls}"{t}>{img(icon, "ci")}{esc(text)}</span>'


def table(headers, rows, cls="list"):
    """rows: lists of cell HTML (already escaped)."""
    head = "".join(f"<th>{esc(h)}</th>" for h in headers)
    body = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f'<div class="scroll"><table class="{cls}"><tr>{head}</tr>{body}</table></div>'


def md_table(headers, rows):
    clean = lambda c: str(c).replace("|", "/").replace("\n", " ")
    return ["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)] + \
           ["| " + " | ".join(clean(c) for c in r) + " |" for r in rows]


def ul(items, cls=""):
    return f'<ul class="{cls}">' + "".join(f"<li>{x}</li>" for x in items) + "</ul>" if items else ""


def svg_chart(series, x_labels, y_max=100, height=260, highlight=None):
    """Line chart: series = {name: [y or None per x]}; the highlighted series is drawn thick and first in the legend."""
    n = len(x_labels)
    if not n:
        return ""
    w, h, left, top, bottom = max(640, 26 * n), height, 36, 12, 40
    px = lambda i: left + (w - left - 12) * (i / max(n - 1, 1))
    py = lambda v: top + (h - top - bottom) * (1 - v / y_max)
    palette = ["#e8590c", "#3366e6", "#2b9a61", "#8d55d9", "#d48a12", "#d93d72", "#0c8599", "#7d8798", "#a61e4d", "#5c940d"]
    grid = "".join(f'<line x1="{left}" x2="{w - 12}" y1="{py(v):.1f}" y2="{py(v):.1f}" class="grid"/>'
                   f'<text x="{left - 6}" y="{py(v) + 4:.1f}" text-anchor="end" class="axis">{v}</text>'
                   for v in range(0, y_max + 1, max(y_max // 4, 1)))
    step = max(1, n // 16)
    xl = "".join(f'<text x="{px(i):.1f}" y="{h - bottom + 16}" text-anchor="middle" class="axis">{esc(lab)}</text>'
                 for i, lab in enumerate(x_labels) if i % step == 0)
    lines, legend = [], []
    order = sorted(series, key=lambda s: s != highlight)
    for k, name in enumerate(order):
        color = palette[k % len(palette)]
        pts = [(px(i), py(v)) for i, v in enumerate(series[name]) if v is not None]
        if not pts:
            continue
        width = 3.2 if name == highlight else 1.4
        d = " ".join(f"{'M' if j == 0 else 'L'}{x:.1f},{y:.1f}" for j, (x, y) in enumerate(pts))
        lines.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}" opacity="{1 if name == highlight else .75}"/>')
        legend.append(f'<span class="lg"><i style="background:{color}"></i>{esc(name)}</span>')
    return (f'<div class="scroll"><svg viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" class="chart">{grid}{xl}'
            f'{"".join(reversed(lines))}</svg></div><div class="legend">{"".join(legend)}</div>')


CSS = """
:root { --bg:#f5f6f8; --card:#fff; --text:#1c2230; --muted:#5d6879; --line:#e2e6ed; --accent:#3366e6; --chip:#eef1f6;
  --good:#2b9a61; --bad:#c2410c; --warn:#b4530a; --c1:#7d8798; --c2:#2b9a61; --c3:#2a77cf; --c4:#8d55d9; --c5:#d48a12; --c7:#d93d72; }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { --bg:#0e1117; --card:#161b24; --text:#e6ebf2;
  --muted:#98a3b4; --line:#283040; --accent:#7ea1ff; --chip:#212837; --good:#4cc38a; --bad:#ff8a5c; --warn:#ffb454; } }
* { box-sizing: border-box; }
body { margin:0; background:var(--bg); color:var(--text); font:15px/1.55 system-ui, "Segoe UI", Roboto, sans-serif; }
header, main { max-width:1180px; margin:0 auto; padding:0 16px; }
header { padding-top:22px; }
h1 { font-size:24px; margin:0 0 4px; } h2 { font-size:20px; margin:0 0 10px; } h3 { font-size:16px; margin:16px 0 8px; }
.meta, .muted { color:var(--muted); } .small { font-size:12.5px; }
section { background:var(--card); border:1px solid var(--line); border-radius:14px; padding:18px; margin:16px 0; }
.grid3 { display:grid; gap:12px; grid-template-columns:repeat(auto-fit, minmax(260px, 1fr)); }
.box { border:1px solid var(--line); border-left:4px solid var(--accent); border-radius:10px; padding:10px 12px; }
.box.good { border-left-color:var(--good); } .box.bad { border-left-color:var(--bad); } .box.warn { border-left-color:var(--warn); }
.box h4 { margin:0 0 6px; font-size:15px; }
ul { margin:4px 0; padding-left:18px; } li { margin:3px 0; }
.scroll { overflow-x:auto; }
.list { width:100%; border-collapse:collapse; font-size:14px; }
.list th, .list td { text-align:left; vertical-align:top; padding:6px 8px; border-bottom:1px solid var(--line); }
.list td { font-variant-numeric:tabular-nums; }
.chip { display:inline-flex; align-items:center; gap:4px; background:var(--chip); border:1px solid var(--line); border-radius:999px;
  padding:1px 9px 1px 3px; font-size:13px; margin:2px 3px 2px 0; white-space:nowrap; }
.chip .ci { width:22px; height:22px; border-radius:50%; object-fit:cover; }
.chip.c1 { border-color:var(--c1); } .chip.c2 { border-color:var(--c2); } .chip.c3 { border-color:var(--c3); }
.chip.c4 { border-color:var(--c4); } .chip.c5 { border-color:var(--c5); } .chip.c7 { border-color:var(--c7); }
.chip.on { outline:2px solid var(--good); } .chip.off { opacity:.55; }
.buff { color:var(--good); font-weight:700; } .nerf { color:var(--bad); font-weight:700; } .warn { color:var(--warn); font-weight:700; }
.big { width:56px; height:56px; border-radius:50%; vertical-align:middle; margin-right:8px; }
.shot { max-width:100%; border-radius:8px; border:1px solid var(--line); }
.shots { display:grid; gap:8px; grid-template-columns:repeat(auto-fill, minmax(240px, 1fr)); }
.shots figure { margin:0; } .shots figcaption { font-size:12.5px; color:var(--muted); }
.chart { max-width:none; } .chart .grid { stroke:var(--line); } .chart .axis { fill:var(--muted); font-size:11px; }
.legend { display:flex; flex-wrap:wrap; gap:6px 14px; font-size:13px; margin-top:4px; }
.legend i { display:inline-block; width:14px; height:4px; border-radius:2px; margin-right:5px; vertical-align:middle; }
code { background:var(--chip); padding:0 4px; border-radius:4px; }
pre { background:var(--chip); padding:10px; border-radius:8px; overflow-x:auto; font-size:12.5px; }
"""


def page(title, body, subtitle=""):
    return (f'<!doctype html>\n<html lang="id">\n<head>\n<meta charset="utf-8">\n'
            f'<meta name="viewport" content="width=device-width, initial-scale=1">\n<meta name="color-scheme" content="light dark">\n'
            f"<title>{esc(title)}</title>\n<style>{CSS}</style>\n</head>\n<body>\n"
            f'<header><h1>{esc(title)}</h1><p class="meta">{subtitle}</p></header>\n<main>{body}</main>\n</body>\n</html>\n')


def write_report(folder, stem, html_text, md_lines):
    """Write <stem>.html and <stem>.md into the data folder; returns both paths."""
    out_html, out_md = folder / f"{stem}.html", folder / f"{stem}.md"
    out_html.write_text(html_text, encoding="utf-8")
    out_md.write_text("\n".join(md_lines).rstrip() + "\n", encoding="utf-8")
    return out_html, out_md


def stamp(d):
    return (f"Data game {esc(d['game_version'])}, Season {d['season']} \"{esc(d.get('info', {}).get('name', ''))}\" · "
            f"dibuat {datetime.now():%Y-%m-%d %H:%M}")
