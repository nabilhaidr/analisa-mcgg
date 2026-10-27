"""Ekspor data patch Magic Chess: Go Go: hero, sinergi, stat, skill, commander (+ detail tooltip skill), Go Go Card, equipment,
Toko Spirit Sand (Mistbender), Ensiklopedia (termasuk tabel DMG Commander per babak).

Pemakaian (pakai Python di .venv karena butuh UnityPy):
  .venv\\Scripts\\python mc_data.py                    season aktif + season berikutnya
  .venv\\Scripts\\python mc_data.py --season 7 8       season tertentu
  .venv\\Scripts\\python mc_data.py --lang EN          bahasa teks (default Indonesian)

Hasil: data/<versi game>/S<n>.html (bisa dicari/difilter), S<n>.md (laporan teks),
       S<n>.json (dipakai mc_diff.py untuk membandingkan antar patch),
       img/<Atlas>/*.png (ikon hero, commander, sinergi, equipment, Go Go Card, skill; lihat mc_images.py).
Setelah game update: jalankan skrip ini lagi, lalu `python mc_diff.py` untuk melihat buff/nerf.

Batasan: angka balance yang dikirim server saat login (mis. patch note 7.2) tidak ada di file
lokal, dan "Jangkauan ATK" tidak tersimpan sebagai kolom tabel.
"""
import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

from mc_images import attach_icons
from mc_tables import Language, Tables, game_version

HERE = Path(__file__).resolve().parent
SERVER_PATCH = HERE / "server_patch.json"  # patch-note changes applied by the server (not in the game files)
GAMEPLAY_NOTES = HERE / "catatan_gameplay.json"  # game rules learned from playing (not in the game files)
DEFAULT_GAME =Path(r"F:\Magic Chess\MagicChessGoGo\MagicChessGoGo")

PLACEHOLDER = re.compile(r"^\[(\d+)\|(-?\d+)\|([^|\]]+)\|([^|\]]*)\|([^|\]]*)(?:\|[^\]]*)?\]$")
NUM_TAG = re.compile(r"<(%?)Num(\d+)>|\[(%?)Num(\d+)\]")
ATTR_SCALING = re.compile(r"^(?:\[C\d)?\s*<(\d+)\s*(\[[^\]]+\])>\]?$")
# [kind|effect|field|unit|scale-or-formula|label]: scale "0.001" multiplies, "N*20" is applied to the value
FORMULA = re.compile(r"^(?:\[C\d)?\[(\d{5,})\|(\d+)\|([^|\]]*)(?:\|([^|\]]*))?(?:\|([^|\]]*))?(?:\|[^\]]*)?\]\]?$")
SPEC_LABEL = re.compile(r"\[\d+\|-?\d+\|[^|\]]*\|[^|\]]*\|[^|\]]*\|(\d+)")
# Runtime formula kinds seen in skill text: kind -> (default effect field, renderer)
FORMULA_KINDS = {
    10100: ("m_FPara1", lambda v: f"{fmt_num(v * 100)}% ATK"),   # Physical DMG ratio
    10101: ("m_FPara1", lambda v: f"{fmt_num(v * 100)}% ATK"),   # Magic DMG ratio
    10502: ("m_FPara1", lambda v: f"{fmt_num(v * 100)}% ATK"),   # adaptive DMG ratio
    10107: ("m_FPara0", lambda v: f"{fmt_num(v * 100)}%"),       # heal, % Max HP
    10500: ("m_Para1", lambda v: fmt_num(v / 1000)),             # duration ms -> s
    101420: ("m_FPara1", lambda v: f"{fmt_num(v * 100)}%"),      # shield, % Max HP
    101421: ("m_FPara0", lambda v: fmt_num(v)),                  # flat shield
    105010: ("m_Value0", lambda v: f"{fmt_num(v / 100)}%"),      # attribute bonus
    105011: ("m_Value0", lambda v: fmt_num(v)),                  # flat attribute bonus (Hybrid DEF/Penetration)
}
STATS = [  # (label as shown in-game, MCHeroStarlevel column, scale)
    ("HP", "m_BaseHp", 1), ("Physical ATK", "m_BasePhyAtt", 1), ("Magic ATK", "m_BaseMagAtt", 1),
    ("ATK Speed", "m_AttSpeed", 0.0001), ("Physical DEF", "m_PhyBaseShield", 1), ("Magic DEF", "m_MagBaseShield", 1),
    ("Batas Mana Awal", "m_BaseMp", 1), ("Batas Mana", "m_MaxMp", 1),
]
RELATION_TYPE = {1: "Faksi", 2: "Role"}
OCCUPATION = {1: "Pertarungan", 2: "Daya Tahan", 3: "Suplai", 4: "Strategi"}  # MCHero.m_occupation
CARD_TIER = {1: "Biru", 2: "Ungu", 3: "Oranye", 4: "Spesial"}                  # MCSuperCrystalKey.m_Level
EQUIP_ORIGIN = {0: "Reguler", 1: "Magic Crystal", 2: "Reguler (Dasar)", 3: "Eksklusif Sinergi",
                4: "Eksklusif Commander", 5: "Khusus"}                         # MCEquipBase.m_EquipOrigin
# Ensiklopedia tabs in in-game order: HookBook_MC column -> tab name. Each column holds [title, body] CommonText ids,
# except m_RelationDes ([title, body] BattleShowMessage ids, rewards from GiftPackage_MC).
HANDBOOK_TABS = [("m_SeasonValue", "Peraturan Game"), ("m_SeasonRound", "Babak"), ("m_SeasonHero", "Hero"),
                 ("m_SeasonCommander", "Commander"), ("m_SeasonGlod", "Gold"), ("m_SeasonUp", "Tutorial Lanjutan"),
                 ("m_RelationDes", "Panduan Sinergi"), ("m_SeasonDes", "Informasi Season")]
# CommonText ids the Ensiklopedia UI uses directly (not listed in HookBook_MC)
TEXT_UPGRADE_COST, TEXT_DMG_TITLE, TEXT_DMG_BODY, TEXT_DMG_NOTE = 152101, 152102, 152084, 152082
START_LEVEL = 3  # commander starts at level 3; the in-game cost and shop-odds tables start there too
ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]
# Toko Spirit Sand (Mistbender). The currency is a buff counter (SpecialStore.m_ChipType = [type, effect id]); its name
# is the [img=27] icon used in the Mistbender text (DescriptionIconShow 27). m_MaximumPurchase 999 = no limit.
STORE_CURRENCY_ICON, STORE_UNLIMITED = 27, 999
STACK_FORMULA = 10021  # m_Calculate: attribute = stacks of effect FPara1 x FPara3 (Echomancer 0.03% per Echo Energy)
STORE_VERIFIED = set()  # seasons whose Toko Spirit Sand was checked against in-game screenshots
# Orbs per Go Go Box (heroes not counted). Not in a table: seen in every box of the 2026-10-21 match, also with 2 players left.
GO_GO_BOX_ORBS = 8


def fmt_num(v):
    if isinstance(v, float):
        v = round(v, 2)
        return str(int(v)) if v == int(v) else f"{v:g}"
    return str(v)


TEXT_TOKENS = {"AdaptiveDamage": "Adaptive DMG"}  # [$Name] words the client fills in (Alpha, Vale)


def clean(text):
    """Strip in-game markup: ####=newline, [C9..] colour, [ff6363]..[-], [img=9], ${Tag}$, [$Token]."""
    if not text:
        return ""
    text = text.replace("####", "\n").rstrip("#")
    text = re.sub(r"\[\$(\w+)\]", lambda m: TEXT_TOKENS.get(m.group(1), re.sub(r"(?<=[a-z])(?=[A-Z])", " ", m.group(1))), text)
    text = re.sub(r"\$\{[^}]*\}\$", "", text)
    text = re.sub(r"\[img=\d+\]", "", text)
    text = re.sub(r"\[[0-9a-fA-F]{6}\]|\[-\]", "", text)
    for _ in range(3):  # colour codes are one digit: [C9<Num1>] -> [C935%] must keep "35%"
        text = re.sub(r"\[C\d([^\[\]]*)\]", r"\1", text)
    return re.sub(r"[ \t]+", " ", text).strip()


def unquote(text):
    """Some language cells keep their CSV quoting: "...""Spanner Spin""..."."""
    text = (text or "").strip()
    if len(text) > 1 and text[0] == text[-1] == '"':
        text = text[1:-1].replace('""', '"')
    return text


def handbook_text(text):
    """Ensiklopedia text: '##' = newline."""
    return clean(unquote(text).replace("##", "\n"))


def merge_hybrid(attrs):
    """The game shows equal Physical + Magic bonuses as one Hybrid line: "+10% Hybrid ATK", "+20 Hybrid DEF"."""
    out = list(attrs)
    for kind in ("ATK", "DEF"):
        phys = next((a for a in out if a.endswith(f" Physical {kind}")), None)
        mag = next((a for a in out if a.endswith(f" Magic {kind}")), None)
        if phys and mag and phys.rsplit(" ", 2)[0] == mag.rsplit(" ", 2)[0]:
            out[out.index(phys)] = f"{phys.rsplit(' ', 2)[0]} Hybrid {kind}"
            out.remove(mag)
    return out


def layered(tables, names, key):
    """Merge base + season tables; later tables override rows with the same key."""
    merged = {}
    for name in names:
        if name in tables:
            for row in tables.parse(name):
                merged[tuple(row.get(k, 0) for k in key)] = row
    return merged


class Season:
    def __init__(self, tables, lang, sid):
        self.t, self.L, self.sid, self.s = tables, lang, sid, f"_S{sid}"
        s = self.s
        self.skills = layered(tables, ["MCSkill", f"MCSkill_extra_all{s}", f"MCSkill{s}"], ("m_SkillID", "m_SkillLevel"))
        self.effects = layered(tables, ["MCEffect", f"MCEffect_extra_all{s}", f"MCEffect{s}"], ("m_EffectID", "m_EffectLevel"))
        self.triggers = layered(tables, ["MCTrigger", f"MCTrigger{s}"], ("m_TriggerID", "m_Level"))
        self.card_rows = layered(tables, ["MCSuperCrystalKey", f"MCSuperCrystalKey{s}"], ("m_ID",))
        self.season_cards = {r["m_ID"] for r in tables.parse(f"MCSuperCrystalKey{s}")} if f"MCSuperCrystalKey{s}" in tables else set()

    # -- placeholders --------------------------------------------------------
    @staticmethod
    def _row(table, rid, level):
        # A missing level falls back to level 1, like the client: Dragoncaller 10 (skill level past the last effect row)
        # reads 70% / 50% in-game, which is the level-1 row. Alpha's ★4 Force Wave (120%) comes from the same rule.
        for key in ((rid, level), (rid, 1), (rid, 0)):
            if key in table:
                return table[key]
        return next((r for k, r in table.items() if k[0] == rid), None)

    def num(self, spec, level):
        spec = spec.strip()
        m = ATTR_SCALING.match(spec)
        if m:  # <1025 [2|..|FPara1|@|N]> = ratio x attribute (1025 = Total Physical ATK)
            inner = self.num(m.group(2), level).rstrip("%")
            ratio = float(inner) if re.fullmatch(r"-?[\d.]+", inner) else 0.0
            attr = self.L.get("AttrbuteDescribe_MC", "mName", m.group(1)) or f"atribut {m.group(1)}"
            return f"{fmt_num(ratio * 100)}% {attr}"
        m = FORMULA.match(spec)
        if m:  # [kind|effect|field|...]: value the client computes at runtime from an effect row
            kind, row = FORMULA_KINDS.get(int(m.group(1))), self._row(self.effects, int(m.group(2)), level)
            if not kind or row is None:
                return "(dinamis)"
            field = m.group(3) if m.group(3) not in ("", "0") else kind[0][2:]
            # plain-ratio effects (m_Calculate 100) keep the ratio in the kind's default field even when the
            # placeholder names another one (Fanny/Lancelot: FPara7 empty, FPara1 = 2.7 -> 270% like in-game)
            v = float(row.get("m_" + field) or row.get(kind[0]) or 0)
            scale = m.group(5) or ""
            if scale not in ("", "0"):
                expr = scale.replace("N", repr(v)) if "N" in scale else f"{v!r}*{scale}"
                if re.fullmatch(r"[\d.eE+\-*/() ]+", expr):
                    v = eval(expr, {"__builtins__": {}})  # noqa: S307 - digits and operators only
            return kind[1](v)
        m = PLACEHOLDER.match(spec)
        if not m:
            return clean(spec)
        typ, rid, field, unit, formula = m.groups()
        table = {1: self.skills, 2: self.effects, 3: self.triggers}.get(int(typ))
        row = self._row(table, int(rid), level) if table is not None else None
        if row is None:
            return spec
        field, _, idx = field.partition("-")
        v = row.get("m_" + field, 0)
        if idx:
            v = v[int(idx) - 1] if isinstance(v, list) and len(v) >= int(idx) else 0
        expr = (formula or "N").replace("N", repr(float(v)))
        if re.fullmatch(r"[\d.eE+\-*/() ]+", expr):
            v = eval(expr, {"__builtins__": {}})  # noqa: S307 - digits and operators only
        return fmt_num(v) + ("%" if unit == "%" else "")

    def describe(self, text, specs_by_level):
        """Fill <NumK>/[NumK] with values per level, joined as a/b/c when they differ."""
        def repl(m):
            k = int(m.group(2) or m.group(4)) - 1
            vals = [self.num(specs[k], level) for level, specs in specs_by_level if k < len(specs)]
            if not vals:
                return "?"
            uniq = list(dict.fromkeys(vals))
            return uniq[0] if len(uniq) == 1 else "/".join(vals)
        text = re.sub(r"\$\{Tag(\d+)\}\$", lambda m: self.keyword(int(m.group(1))), unquote(text))
        return clean(NUM_TAG.sub(repl, text))

    def keyword(self, tag_id):
        for table in (f"SkillKeyWords_MC{self.s}", "SkillKeyWords_MC"):
            text = self.L.get(table, "mSkillKeyWordsContent", tag_id)
            if text:
                return clean(text)
        return ""

    def keyword_details(self, texts, johnson_pool):
        """Tooltip behind each underlined keyword (${TagN}$) of a skill text: SkillKeyWords_MC.mSkillKeyWordsDesc filled
        with its m_NumDescribe. The commander screen reads the base row first (Lylia's "Harga di Little Witch's Shop"
        matches the base row, not SkillKeyWords_MC_S7); season rows only add ids the base lacks (Freya's Efek Sinergi).
        [SkillName<id>]/[SkillDes<id>] embed another skill (Luo Yi), ${JohnsonBondList}$ is JohnsonSeasonBondList."""
        rows = {}
        for table in (f"SkillKeyWords_MC{self.s}", "SkillKeyWords_MC"):  # base table last so it wins
            if table in self.t:
                rows.update({r["m_SkillKeyWordsID"]: (table, r) for r in self.t.parse(table)})
        tags = dict.fromkeys(int(x) for text in texts if text for x in re.findall(r"\$\{Tag(\d+)\}\$", text))
        out = []
        for tag in tags:
            table, row = rows.get(tag, (None, {}))
            text = table and self.L.get(table, "mSkillKeyWordsDesc", tag)
            if not text:
                continue

            def embed(m):
                sk = self.skill(int(m.group(2)))
                return (sk["name"] if m.group(1) == "Name" else sk["description"]) if sk else ""
            text = re.sub(r"\[Skill(Name|Des)(\d+)\]", embed, text)
            text = text.replace("${JohnsonBondList}$", ", ".join(johnson_pool))
            out.append({"keyword": self.keyword(tag), "text": self.describe(text, [(1, row.get("m_NumDescribe") or [])])})
        return out

    def johnson_pool(self, syn):
        """Synergies Johnny can roll (JohnsonSeasonBondList: row for this battle season, else the default row -1)."""
        if "JohnsonSeasonBondList" not in self.t:
            return []
        rows = {r.get("m_BattleSeasonID"): r for r in self.t.parse("JohnsonSeasonBondList")}
        names = {s["id"]: s["name"] for s in syn}
        return [names[i] for i in (rows.get(self.sid) or rows.get(-1) or {}).get("m_BondList", []) if i in names]

    def message(self, text_id):
        """Skill/card text. Newer ids live in BattleShowMessage; older heroes (Eudora, Zilong, ...) use ShowMessage."""
        if not text_id:
            return None
        text = self.L.get("BattleShowMessage", "mMessage", text_id) or self.L.get("ShowMessage", "mMessage", text_id)
        return unquote(text) if text else None

    # -- domain ---------------------------------------------------------------
    def skill(self, skill_id, levels=None):
        rows = sorted((k[1], r) for k, r in self.skills.items() if k[0] == skill_id)
        if levels:
            rows = [(lv, r) for lv, r in rows if lv in levels] or rows
        named = [(lv, r) for lv, r in rows if self.message(r.get("m_SkillName"))]
        if not named:  # basic attacks and helper skills have no player-facing text
            return None
        first = named[0][1]
        # "Atribut Skill" table: entry k of NumDescribe is labelled by SkillAddition[k], or (newer
        # skills) by the 6th field of the placeholder itself, e.g. [2|1131002|FPara1|%|N*100|170|0].
        attributes = []
        additions = first.get("m_SkillAddition") or []
        for k, spec in enumerate(first.get("m_NumDescribe") or []):
            label_id = additions[k] if k < len(additions) and additions[k] not in ("", "0") else None
            if label_id is None:
                m = SPEC_LABEL.search(spec)
                label_id = m.group(1) if m and m.group(1) != "0" else None
            label = label_id and self.L.get("SkillAddition", "mSkillAdditionDescription", label_id)
            if not label:
                continue
            values = [re.sub(r"%\s.*$", "%", self.num(r["m_NumDescribe"][k], lv))  # "150% Total Physical ATK" -> "150%"
                      for lv, r in named if k < len(r.get("m_NumDescribe", []))]
            attributes.append({"label": clean(label), "values": values})
        # Some skills switch text by star (Alpha: ★3-★4 use the transformed skill's text). Fill each text only with the
        # levels that use it, otherwise the later levels show up as "-" in the first text ("50% ATK/70% ATK/-/-").
        same_text = [(lv, r) for lv, r in named if r.get("m_SkillDescription") == first.get("m_SkillDescription")]
        return {
            "id": skill_id,
            "name": clean(self.message(first["m_SkillName"])),
            "description": self.describe(self.message(first.get("m_SkillDescription")),
                                         [(lv, r.get("m_NumDescribe", [])) for lv, r in same_text]),
            "attributes": attributes,
            "cooldown_ms": first.get("m_SkillColdDown"),
            "icon": first.get("m_IconFile"),  # "<Atlas>/<sprite>", turned into an image path by mc_images
        }

    def synergies(self):
        tip_t, rel_t = f"RelationSkillTip_MC{self.s}", f"RelationSkill_MC{self.s}"
        tiers = {}
        for r in self.t.parse(rel_t):
            rid, cnt, lv = r.get("m_relationId", 0), r.get("m_NeedCnt", 0), r.get("m_skillLv", 0)
            text = self.L.get(rel_t, "mSkillDescription", f"{rid}_{cnt}")
            if text:
                tiers.setdefault(rid, []).append({
                    "count": cnt, "level": lv,
                    "effect": self.describe(text, [(lv, r.get("m_NumDescribe", []))]),
                })
        out = []
        for r in self.t.parse(tip_t):
            rid = r["m_RelationId"]
            out.append({
                "id": rid,
                "type": RELATION_TYPE.get(r.get("m_RelationType"), str(r.get("m_RelationType"))),
                "name": self.L.get(tip_t, "mRelationAttach", rid) or f"#{rid}",
                "explain": self.describe(self.L.get(tip_t, "mRelationExplain", rid), [(1, r.get("m_NumDescribe", []))]),
                "tiers": sorted(tiers.get(rid, []), key=lambda x: x["count"]),
                "heroes": [],
                "icon": r.get("m_RelationIcon"),
            })
        return out

    def card_name(self, card_id):
        row = self.card_rows.get((card_id,))
        return clean(self.message(row.get("m_SkillName"))) if row else f"Go Go Card #{card_id}"

    def heroes(self, synergy_names):
        hero_t = f"MCHero{self.s}"
        stars = {}
        for r in self.t.parse(f"MCHeroStarlevel{self.s}"):
            stars.setdefault(r["m_ID"], {})[r.get("m_StarId", 0)] = r
        out = []
        for h in self.t.parse(hero_t):
            hid = h["m_ID"]
            name = self.L.get(hero_t, "mName", hid)
            if not name or hid not in stars:
                continue
            star_rows = dict(sorted(stars[hid].items()))
            skills, shown = [], set()
            for entry in h.get("m_SkillList", []):
                if not entry:
                    continue
                texts = {r.get("m_SkillDescription") for (sid, _), r in self.skills.items() if sid == entry[0]}
                if texts and texts <= shown:  # same text already shown (Alpha's ★3 form, listed twice more)
                    continue
                sk = self.skill(entry[0], set(star_rows))
                if sk and sk["description"]:
                    skills.append(sk)
                    shown |= texts
            hero = {
                "id": hid,
                "name": name,
                "cost": star_rows[min(star_rows)].get("m_BuyingPrice"),
                "synergies": [synergy_names.get(x, f"#{x}") for x in h.get("m_Sort", [])],
                "stats": {star: {label: fmt_num(r.get(col, 0) * scale) for label, col, scale in STATS}
                          for star, r in star_rows.items()},
                "skills": [s for s in skills if s and s["description"]],  # basic attacks: name "Basic ATK", no text
                # GuideType 3 = summoned only (Echomancer's Chrono Wanderers, SPECTRE's Alpha); never sold in the shop
                "summoned": h.get("m_GuideType") == 3,
                "icon": h.get("m_Head"),
            }
            strengthen = h.get("m_strengthen") or []  # [Go Go Card id, replacement skill id, icon]
            if len(strengthen) >= 2 and strengthen[1].isdigit():
                skill = self.skill(int(strengthen[1]), set(star_rows))
                if skill:
                    hero["enhanced"] = {"card": self.card_name(int(strengthen[0])), "skill": skill}
            out.append(hero)
        return sorted(out, key=lambda x: (x["cost"] or 0, x["name"]))

    def summons(self):
        """Units on the board that are not season heroes: summon-only rows of the shared MCHero table (m_GuideType 3)
        that an effect gives the player (OperEnum 20002/20005, unit id in m_Para2): Johnny (Johnson), Turret (Turret of
        Guardians), Makhluk Suci (Lukas). The result screen lists them among the heroes. The bots of that table
        (Bot, Physical ATK, Magic ATK) are given by no effect."""
        given = {int(r.get("m_Para2", 0)) for r in self.effects.values() if r.get("m_OperEnum") in (20002, 20005)}
        season = {r["m_ID"] for r in self.t.parse(f"MCHero{self.s}")}
        out = []
        for h in self.t.parse("MCHero"):
            name = self.L.get("MCHero", "mName", h["m_ID"])
            if h.get("m_GuideType") == 3 and h["m_ID"] in given and h["m_ID"] not in season and name:
                out.append({"id": h["m_ID"], "name": name, "icon": h.get("m_Head")})
        return out

    def cards(self):
        # m_Value1..3 = weight in Go Go Card round 1/2/3. The in-game card book (MCUIHandBookSuperCrystal.RefreshCardList)
        # lists only cards with a non-zero weight, so all-zero cards are inactive this season.
        # Power cards: the commander-exclusive ones carry m_CommanderId; the generic "<Commander>'s Power" versions sit at
        # the same level in the season table and, like them, only appear in round 1 (the Power card round).
        power_levels = {r.get("m_Level") for (cid,), r in self.card_rows.items()
                        if cid in self.season_cards and r.get("m_CommanderId")}
        out = []
        for (cid,), r in sorted(self.card_rows.items()):
            name = clean(self.message(r.get("m_SkillName")))
            if not name:
                continue
            commander = r.get("m_CommanderId") or 0
            weights = [r.get(f"m_Value{i}", 0) for i in (1, 2, 3)]
            generic_power = (cid in self.season_cards and r.get("m_Level") in power_levels
                             and weights[0] and not any(weights[1:]))
            # m_SkillID / m_SkillID2 = [skill id, level]: tiered cards share effects and differ by level
            # (Solid Alliance II = level 2 of 82140 -> 3%, not the 2% of level 1)
            level = next((s[1] for s in (r.get("m_SkillID"), r.get("m_SkillID2")) if s and len(s) > 1 and s[1]), 1)
            out.append({
                "id": cid,
                "name": name,
                "tier": "Power" if commander or generic_power else CARD_TIER.get(r.get("m_Level"), f"Level {r.get('m_Level')}"),
                "commander_id": commander or None,
                "commander": self.L.get("MCHero", "mName", commander) if commander else None,
                "season_only": cid in self.season_cards,
                "active": any(weights),
                "rounds": [i + 1 for i, w in enumerate(weights) if w],
                "weights": weights,
                "description": self.describe(self.message(r.get("m_SkillDescription")), [(level, r.get("m_NumDescribe", []))]),
                "icon": r.get("m_MiniIcon"),  # card art as shown in the Go Go Card book (m_IconFile = big art, no atlas)
            })
        return out

    def commanders(self, cards, syn):
        heroes = {r["m_ID"]: r for r in self.t.parse("MCHero")}
        pool = self.johnson_pool(syn)
        power = {c["commander_id"]: c for c in cards if c["commander_id"]}
        # Commanders playable this season are the ones with a Power card in MCSuperCrystalKey_S<n>.
        ids = sorted(power) or sorted(cid for cid, r in heroes.items() if r.get("m_CommanderType") == 1)
        levels = {}
        for r in self.t.parse("IndividualCommanderLevel"):
            levels.setdefault(r["m_ID"], []).append(r)
        # the commander screen shows the longer SkillExtraDesc_MC text when a skill has one (Ling, Alice, Johnson, ...)
        extra = layered(self.t, ["SkillExtraDesc_MC", f"SkillExtraDesc_MC{self.s}"], ("m_SkillID",))
        out = []
        for cid in ids:
            skills = []
            for r in sorted(levels.get(cid, []), key=lambda r: r.get("m_HeroLevel", 0)):
                sk = self.skill(r.get("m_HeroSkill"))
                long = extra.get((r.get("m_HeroSkill"),))
                long_text = long and self.message(int(long.get("m_ExtraDescription") or 0))
                if sk and long_text:
                    sk["description"] = self.describe(long_text, [(1, long.get("m_ExtraNumDescribe") or [])])
                if sk:
                    base = self.message((self._row(self.skills, r.get("m_HeroSkill"), 1) or {}).get("m_SkillDescription"))
                    details = self.keyword_details([long_text, base], pool)
                    if details:
                        sk["details"] = details
                if sk and (not skills or skills[-1]["skill"]["id"] != sk["id"]):
                    # m_PassiveSkill = 1 marks the skill the player triggers ("Aktif" in-game), despite its name
                    skills.append({"from_level": r.get("m_HeroLevel", 0), "type": "Aktif" if r.get("m_PassiveSkill") else "Pasif",
                                   "skill": sk})
            out.append({
                "id": cid,
                "name": self.L.get("MCHero", "mName", cid) or f"Commander #{cid}",
                "category": OCCUPATION.get(heroes.get(cid, {}).get("m_occupation"), "-"),
                "skills": skills,
                "power_card": {k: power[cid][k] for k in ("name", "description")} if cid in power else None,
                "icon": heroes.get(cid, {}).get("m_Head"),
            })
        return sorted(out, key=lambda c: c["name"])

    def attribute(self, attr_id, value, meta):
        info = meta.get(attr_id, {})
        name = self.L.get("AttrbuteDescribe_MC", "mName", attr_id) or f"atribut {attr_id}"
        v = value * info.get("m_ChangePara", 1.0)
        return f"+{fmt_num(v * 100)}% {name}" if "%" in info.get("m_ShowType", "") else f"+{fmt_num(float(v))} {name}"

    def equipment(self):
        meta = {r["m_ID"]: r for r in self.t.parse("AttrbuteDescribe_MC")}
        rows = {}
        for table in ("MCEquipBase", f"MCEquipBase{self.s}"):
            if table in self.t:
                for r in self.t.parse(table):
                    rows[(r["m_EuqipID"], r.get("m_EquipUpgradeState", 0))] = (table, r)
        items = {}
        for (eid, up), (table, r) in sorted(rows.items()):
            key = f"{eid}_{up}"
            name = self.L.get(table, "mItemName", key)
            if not name:
                continue
            attrs = merge_hybrid([self.attribute(r[f"m_Attr{i}"], r.get(f"m_AttrValue{i}", 0), meta)
                                  for i in (1, 2, 3) if r.get(f"m_Attr{i}")])
            unique = [self.attribute(r["m_ExclusiveAttr1"], r.get("m_ExclusiveAttrValue1", 0), meta)] if r.get("m_ExclusiveAttr1") else []
            # m_SkillList entries are [skill id, skill level]; without the level every level gets joined
            # (Supreme Blades: "Peningkatan Saat Ini: 0%/1%/.../50%")
            passives = [f"{s['name']}: {s['description']}"
                        for s in (self.skill(e[0], {e[1]} if len(e) > 1 and e[1] else None) for e in r.get("m_SkillList", []) if e) if s]
            # m_DropState 1 = in this season's item pool. Checked against the in-game equipment list: all 67 items
            # seen there have it, the 25 never shown (Lightstick 5011, Boxing Glove tier 1-2, ...) do not.
            icon = (r.get("m_Icon") or [None])[0]
            item = items.setdefault(eid, {"id": eid, "category": EQUIP_ORIGIN.get(r.get("m_EquipOrigin") or 0, "-"),
                                          "season_only": table != "MCEquipBase", "active": bool(r.get("m_DropState")),
                                          "icon": icon, "levels": []})
            item["levels"].append({"upgraded": bool(up), "name": name, "summary": clean(self.L.get(table, "mItemDes", key)),
                                   "attributes": attrs, "unique": unique, "passives": passives, "icon": icon})
        return sorted(items.values(), key=lambda x: (x["category"], x["levels"][0]["name"]))

    def store_effect(self, skill_id, currency, meta, equipment):
        """What a shop item does, read from the effect rows of its skill (MCSpecialCardPool.m_SkillID)."""
        skill = self._row(self.skills, skill_id, 1) or {}
        effects = [e for e in (self._row(self.effects, skill.get(f"m_Effect{i}"), 1) for i in range(6)
                               if skill.get(f"m_Effect{i}")) if e]
        out = {"text": "", "pool": [], "cost": 0}
        counter, stacks = None, 0
        for e in effects:
            op, target = e.get("m_OperEnum"), int(e.get("m_Para0") or 0)
            if op == 20 and target == currency:  # pays: removes stacks of the Spirit Sand buff
                out["cost"] -= int(e.get("m_Para2") or 0)
            elif op == 1 and (e.get("m_Para4") or 0) > 1:  # adds 1 stack to a counter buff (max m_Para4)
                counter, stacks = e["m_EffectID"], stacks + 1
            elif op == 20 and target == counter:  # extra stacks on that counter
                stacks += int(e.get("m_Para2") or 0)
            elif op in (50, 20009):  # equipment: fixed id (m_Para2) or random from m_LogicParam (20009 = upgraded)
                fixed = int(e.get("m_Para2") or 0) if op == 50 else 0
                if fixed in equipment:
                    name, summary = equipment[fixed]
                    out["text"] = f"Mendapatkan {name}" + (f" ({summary})" if summary else "")
                else:
                    out["pool"] = [equipment[int(i)][0] for i in e.get("m_LogicParam") or [] if int(i) in equipment]
                    out["text"] = (("1 equipment versi diperkuat, " if op == 20009 else "1 item ")
                                   + f"acak dari {len(out['pool'])} pilihan yang ada di season ini")
        if counter:
            per_stack = {(b["m_Attr0"], b.get("m_FPara3", 0)) for b in self.effects.values()
                         if b.get("m_Calculate") == STACK_FORMULA and int(b.get("m_FPara1") or 0) == counter}
            attrs = merge_hybrid([self.attribute(a, v * stacks, meta) for a, v in sorted(per_stack)])
            out["stacks"] = stacks
            out["text"] = (f"{', '.join(attrs)} untuk Hero rekan, permanen sampai akhir pertandingan "
                           f"(+{stacks} stack; bisa dibeli lagi dan menumpuk)")
            out["percent"] = [float(re.sub(r"[^\d.]", "", a.split("%")[0])) for a in attrs if "%" in a]
        return out

    def special_store(self, synergies, equipment):
        """Toko Spirit Sand: SpecialStore (price m_ChipNum, weight m_Probability, limit m_MaximumPurchase) +
        MCSpecialCardPool (name, text, skill). Linked to the synergy whose skills share the currency effect's id
        family (Mistbender: skills 45900/45901, Spirit Sand buff 4590200). None if that synergy is not in the season."""
        if "SpecialStore" not in self.t or "MCSpecialCardPool" not in self.t:
            return None
        rows = self.t.parse("SpecialStore")
        currency = int((rows[0].get("m_ChipType") or ["0"])[-1]) if rows else 0
        owners = {r.get("m_relationId") for r in self.t.parse(f"RelationSkill_MC{self.s}")
                  if r.get("m_SkillId", 0) // 100 == currency // 10000}
        synergy = next((s for s in synergies if s["id"] in owners), None)
        if not synergy:
            return None
        pool = {r["m_ID"]: r for r in self.t.parse("MCSpecialCardPool")}
        meta = {r["m_ID"]: r for r in self.t.parse("AttrbuteDescribe_MC")}
        equip = {e["id"]: (e["levels"][0]["name"], e["levels"][0]["summary"]) for e in equipment if e.get("active", True)}
        total = sum(r.get("m_Probability", 0) for r in rows) or 1
        items = []
        for r in rows:
            card = pool.get(r.get("m_SpecialCardPoolID"), {})
            name = clean(self.L.get("MCSpecialCardPool", "mName", card.get("m_ID"))) or f"#{r['m_ItemID']}"
            effect = self.store_effect(card.get("m_SkillID"), currency, meta, equip)
            notes = []
            named = re.search(r"\+(\d+(?:\.\d+)?)%", name)
            if named and effect.get("percent") and float(named.group(1)) not in effect["percent"]:
                notes.append(f"Nama item menyebut +{named.group(1)}%, tapi data efek memberi {effect['stacks']} stack "
                             f"(+{fmt_num(effect['percent'][0])}%).")
            if effect["cost"] and effect["cost"] != r.get("m_ChipNum"):
                notes.append(f"Efek pembayaran memotong {effect['cost']} Spirit Sand, bukan {r.get('m_ChipNum')}.")
            limit = r.get("m_MaximumPurchase", 0)
            items.append({
                "id": r["m_ItemID"], "name": name,
                "description": clean(self.L.get("MCSpecialCardPool", "mSpecialDes", card.get("m_ID"))),
                "price": r.get("m_ChipNum", 0), "weight": r.get("m_Probability", 0),
                "chance": round(100 * r.get("m_Probability", 0) / total, 1),
                "limit": None if limit >= STORE_UNLIMITED else limit,
                "refresh_round": r.get("m_RefreshRound"),
                "effect": effect["text"], "pool": effect["pool"], "notes": notes,
            })
        cur_row = self._row(self.effects, currency, 1) or {}
        currency_name = clean(self.L.get("DescriptionIconShow", "mShowDes", STORE_CURRENCY_ICON)) or "Spirit Sand"
        return {
            "synergy": synergy["name"],
            "title": f"Toko {currency_name}",
            "currency": currency_name,
            "currency_text": clean(self.L.get("DescriptionIconShow", "mDesContent", STORE_CURRENCY_ICON)),
            "max_storage": int(cur_row.get("m_Para4") or 0) or None,
            "total_weight": total,
            "verified": self.sid in STORE_VERIFIED,
            "items": items,
        }

    def go_go_box(self, equipment):
        """Go Go Box rounds (MCRoundRandomEquip_S<n>). Per round: m_NormalEquipMin-Max regular items from m_NormalEquip,
        synergy Magic Crystals (m_CrystallEquip) up to m_EquipTotal, the remaining GO_GO_BOX_ORBS filled with m_SpecialEquip
        (Go Go Magic Crystal = Kapasitas +1), and m_HeroListNumber heroes whose Gold cost is drawn from m_HeroList with the
        weights m_HeroListRate (equal costs add up). Matches the 2026-10-21 match: regular + crystal + Kapasitas orbs were
        I-4 8+0+0, II-6 6+1+1, III-6 4+2+2, IV-6 4+3+1, and only 5 Gold heroes from III-6 on."""
        table = f"MCRoundRandomEquip{self.s}"
        if table not in self.t:
            return None
        levels = {e["id"]: e["levels"][0] for e in equipment}
        missing = set()

        def pool(ids, rates):
            out = []
            for i, w in zip(ids or [], list(rates or []) + [0] * len(ids or [])):
                if i in levels:
                    out.append({"id": i, "name": levels[i]["name"], "summary": levels[i]["summary"], "weight": w})
                elif i:  # e.g. S8 still lists 1054 (S7 Magic Crystal Dragoncaller), which MCEquipBase_S8 lacks
                    missing.add(i)
                    out.append({"id": i, "name": f"#{i}", "summary": "", "weight": w, "missing": True})
            return out

        rows = sorted(self.t.parse(table), key=lambda r: r["m_Round"])
        rows = [r for r in rows if not r.get("m_RoundConfigId")] or rows  # 0 = the classic (Rank) mode
        labels = round_labels(round_stages(battle_config(self.t, self.sid)), rows[-1]["m_Round"] if rows else 0)
        rounds = []
        for r in rows:
            total, lo, hi = r.get("m_EquipTotal", 0), r.get("m_NormalEquipMin", 0), r.get("m_NormalEquipMax", 0)
            crystals = pool(r.get("m_CrystallEquip"), r.get("m_CrystalEquipRate"))
            special = pool(r.get("m_SpecialEquip"), r.get("m_SpecialEquipRate"))
            costs = {}
            for cost, w in zip(r.get("m_HeroList") or [], r.get("m_HeroListRate") or []):
                if cost:
                    costs[cost] = costs.get(cost, 0) + w
            weight = sum(costs.values()) or 1
            extra = {k: v for k in ("m_MustEquip", "m_RoundSwitch", "m_Roulette")
                     if (v := r.get(k)) and (any(v) if isinstance(v, list) else True)}
            rounds.append({
                "round": r["m_Round"], "label": labels.get(r["m_Round"], str(r["m_Round"])),
                "equipment": {"min": lo, "max": hi, "pool": pool(r.get("m_NormalEquip"), r.get("m_NormalEquipRate"))},
                "crystals": {"min": max(total - hi, 0) if crystals else 0, "max": max(total - lo, 0) if crystals else 0,
                             "pool": crystals},
                "special": {"count": max(GO_GO_BOX_ORBS - total, 0) if special else 0, "pool": special},
                "heroes": {"count": r.get("m_HeroListNumber", 0),
                           "costs": [{"cost": c, "weight": w, "chance": round(100 * w / weight, 1)} for c, w in sorted(costs.items())]},
                **({"extra": extra} if extra else {}),
            })
        notes = [f"ID {i} ada di daftar Go Go Box tapi tidak ada di tabel equipment season ini (MCEquipBase / MCEquipBase{self.s}), "
                 "jadi kemungkinan tidak pernah muncul." for i in sorted(missing)]
        return {"orbs": GO_GO_BOX_ORBS, "rounds": rounds, "notes": notes}

    def season_info(self):
        info = {"name": self.L.get("BattleSeason", "mSeasonName", self.sid)}
        level_t = f"PlayerLevel_MC{self.s}"
        if level_t in self.t:
            info["levels"] = [{"level": r.get("m_Level", 0), "exp_cost": r.get("m_Exp", 0), "hero_slots": r.get("m_MaxPopulation", 0),
                               "shop_odds": [r.get(f"m_Quality{i}", 0) for i in range(1, 6)]} for r in self.t.parse(level_t)]
        if "HeroQuality_MC" in self.t:
            first = self.t.columns("HeroQuality_MC")[0][0]
            info["pool_per_hero"] = {str(r.get(first)): r.get("m_Base") for r in self.t.parse("HeroQuality_MC") if r.get("m_Base")}
        return info

    def gift_text(self, row):
        text = self.message(int(row.get("m_DescID") or 0)) or ""
        nums = row.get("m_NumDescribe") or []
        text = re.sub(r"<Num(\d+)>", lambda m: nums[int(m.group(1)) - 1] if int(m.group(1)) <= len(nums) else "?", text)
        return clean(re.sub(r"<Gold_\d+>", "", text))

    def synergy_guide(self, book):
        """Panduan Sinergi tab: [title, body] BattleShowMessage ids; m_RelationDesNum = GiftPackage_MC.m_GiftType."""
        sections = []
        for (title, body), gift_type in zip(book.get("m_RelationDes") or [], book.get("m_RelationDesNum") or []):
            sections.append({"title": clean(self.message(title)), "text": clean(self.message(body) or "")})
            groups = {}  # m_LevelID = reward tier title, e.g. "Hadiah 300 Poin"
            for r in sorted(self.t.parse("GiftPackage_MC"), key=lambda r: (r["m_PackageGroupID"], r.get("m_PackageID", 0))):
                if r.get("m_GiftType") == gift_type:
                    groups.setdefault(r.get("m_LevelID"), []).append(self.gift_text(r))
            sections += [{"title": clean(self.message(int(level))), "text": "\n".join(options)}
                         for level, options in groups.items() if level]
        return sections

    def encyclopedia(self, info):
        """In-game Ensiklopedia: the HookBook_MC row of this season (BattleSeason.m_SeasonHandbookID)."""
        season = next((r for r in self.t.parse("BattleSeason") if r["m_SeasonID"] == self.sid), {})
        book = next((r for r in self.t.parse("HookBook_MC") if r["m_ID"] == season.get("m_SeasonHandbookID")), None)
        if not book:
            return []
        text = lambda i: self.L.get("CommonText_MC", "mText", i)
        levels = [lv for lv in info.get("levels", []) if lv["level"] >= START_LEVEL]
        tabs = []
        for col, name in HANDBOOK_TABS:
            if col == "m_RelationDes":
                sections = self.synergy_guide(book)
            else:
                sections = [{"title": clean(text(t)), "text": handbook_text(text(b))} for t, b in book.get(col) or []]
            if col == "m_SeasonHero" and sections and any(book.get("m_SeasonHeroShop") or []):
                pool = info.get("pool_per_hero", {})
                sections[-1]["table"] = {  # attached to "Peluang Refresh Toko"
                    "header": ["Level"] + [f"Hero {c} Gold" for c in range(1, 6)],
                    "rows": [["Jumlah (setiap hero)"] + [pool.get(str(c), "-") for c in range(1, 6)]]
                            + [[f"Level {lv['level']}"] + [f"{x}%" if x else "/" for x in lv["shop_odds"]] for lv in levels]}
            if col == "m_SeasonCommander":
                show_cost, show_dmg = ((book.get("m_SeasonCommanderDes") or []) + [0, 0])[:2]
                if show_cost and levels:
                    sections.append({"title": clean(text(TEXT_UPGRADE_COST)), "text": "", "table": {
                        "header": ["Level", "Gold yang dibutuhkan"],
                        "rows": [[f"{a['level']} → {b['level']}", b["exp_cost"]] for a, b in zip(levels, levels[1:])]}})
                damage = commander_damage(self.t, self.sid)
                if show_dmg and damage:
                    sections.append({"title": clean(text(TEXT_DMG_TITLE)), "text": handbook_text(text(TEXT_DMG_BODY)),
                                     "table": {"header": ["Babak", "DMG Dasar"], "rows": [[d["rounds"], d["damage"]] for d in damage]},
                                     "note": handbook_text(text(TEXT_DMG_NOTE))})
            if sections:
                tabs.append({"name": name, "sections": sections})
        return tabs

    def build(self, version):
        syn = self.synergies()
        heroes = self.heroes({s["id"]: s["name"] for s in syn})
        by_name = {s["name"]: s for s in syn}
        for h in heroes:
            for sname in h["synergies"]:
                if sname in by_name:
                    by_name[sname]["heroes"].append(h["name"])
        cards = self.cards()
        info = self.season_info()
        equipment = self.equipment()
        return {
            "game_version": version,
            "season": self.sid,
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "info": info,
            "synergies": syn,
            "heroes": heroes,
            "summons": self.summons(),
            "commanders": self.commanders(cards, syn),
            "cards": cards,
            "equipment": equipment,
            "special_store": self.special_store(syn, equipment),
            "go_go_box": self.go_go_box(equipment),
            "encyclopedia": self.encyclopedia(info),
        }


def current_seasons(tables):
    """iSeasonID (aktif) and iAdvanceSeasonID (berikutnya) from the client's MCSystemConfig."""
    raw = tables.files["MCSystemConfig"].read_bytes().decode("utf-8", "replace")
    m = re.search(r'<MCSeasonConfig iSeasonID="(\d+)"[^>]*iAdvanceSeasonID="(\d+)"', raw)
    return [int(m.group(1)), int(m.group(2))] if m else []


def round_labels(stages, last):
    """Round number -> in-game label (I-2, II-1, ...). AMCRoundStage ends with an open phase (end 99), which the
    game labels as further stages of the previous stage's length (rounds 17-22 = IV, 23-28 = V)."""
    spans, size = [], 6
    for start, end in stages:
        if end < 99:
            spans.append((start, end))
            size = end - start + 1
            continue
        while start <= last:
            spans.append((start, start + size - 1))
            start += size
    labels = {}
    for i, (start, end) in enumerate(spans):
        for rnd in range(start, end + 1):
            labels[rnd] = f"{ROMAN[i] if i < len(ROMAN) else i + 1}-{rnd - start + 1}"
    return labels


def battle_config(tables, sid):
    """Season battle config MCClassicsBattleConfig_S<n> (XML) without comments; "" when the season has none."""
    name = f"MCClassicsBattleConfig_S{sid}"
    if name not in tables:
        return ""
    return re.sub(r"<!--.*?-->", "", tables.files[name].read_bytes().decode("utf-8", "replace"), flags=re.S)


def round_stages(xml):
    """AMCRoundStage of a battle config: [(first round, last round)] per phase."""
    return [(int(a), int(b)) for a, b in re.findall(r'<SMCRoundRange\s+iStage="\d+"\s+iStartRound="(\d+)"\s+iEndRound="(\d+)"', xml)]


def commander_damage(tables, sid):
    """Base Commander DMG per round from the season battle config (MCClassicsBattleConfig_S<n>, XML):
    APhaseDamage/SRoundExtraDamage, grouped into round ranges like the Ensiklopedia table."""
    xml = battle_config(tables, sid)
    if not xml:
        return []
    damage = {int(r): int(v) for r, v in re.findall(r'<SRoundExtraDamage\s+iRound="(\d+)"\s+iValue="(\d+)"', xml)}
    labels = round_labels(round_stages(xml), max(damage, default=0))
    rows = []
    for rnd in sorted(damage):
        if rows and rows[-1]["damage"] == damage[rnd] and rows[-1]["to"] == rnd - 1:
            rows[-1]["to"] = rnd
        else:
            rows.append({"from": rnd, "to": rnd, "damage": damage[rnd]})
    for row in rows:
        first, last = labels.get(row["from"], str(row["from"])), labels.get(row["to"], str(row["to"]))
        row["rounds"] = first if first == last else f"{first} → {last}"
    return rows


def name_key(name):
    for k, v in {"Ⅰ": "I", "Ⅱ": "II", "Ⅲ": "III", "Ⅳ": "IV", "Ⅴ": "V"}.items():
        name = name.replace(k, v)
    return re.sub(r"[^a-z0-9]", "", name.lower())


def replace_text(text, pairs):
    """Apply [old, new] pairs; None when an old text is missing (patch note no longer matches the file)."""
    for old, new in pairs:
        if old not in text:
            return None
        text = text.replace(old, new, 1)
    return text


def server_attributes(attrs, changes):
    """[[label, star, new value]] -> copy of a skill's attribute table with the server values; None if a cell is missing."""
    out = [dict(a, values=list(a["values"])) for a in attrs]
    for label, star, value in changes:
        row = next((a for a in out if a["label"] == label), None)
        if row is None or not 1 <= star <= len(row["values"]):
            return None
        row["values"][star - 1] = value
    return out


def apply_server_patches(d, sid, path=SERVER_PATCH):
    """Patch-note changes the server applies on top of the game files (server_patch.json). The file values stay as
    they are (mc_diff compares game files); the server values go into extra fields shown as 'Patch x (server)':
    heroes: stats_server + server, commander / hero skills / cards: description_server + server (hero skills also
    attributes_server), cards: removed_server. A change with only "text" (no "replace") is a note: the changed number
    is not in the file text (e.g. Johnny's stats, a synergy's hidden threshold).
    Returns the changes that could not be applied, for a warning."""
    if not path.exists():
        return []
    patches = json.loads(path.read_text(encoding="utf-8")).get(str(sid), [])
    heroes = {name_key(h["name"]): h for h in d["heroes"]}
    skills = {(name_key(c["name"]), name_key(s["skill"]["name"])): s for c in d["commanders"] for s in c["skills"]}
    hero_skills = {(name_key(h["name"]), name_key(s["name"])): s for h in d["heroes"] for s in h["skills"]}
    synergies = {name_key(s["name"]): s for s in d["synergies"]}
    cards = {c["id"]: c for c in d["cards"]}
    for p in patches:
        changes = []
        note = lambda ch, text: {"patch": p["patch"], "text": text + (f" ({ch['note']})" if ch.get("note") else "")}
        for ch in p.get("heroes", []):
            stats = ["Physical ATK", "Magic ATK"] if ch["stat"] == "Hybrid ATK" else [ch["stat"]]
            old, new = [list(map(fmt_num, ch[k])) for k in ("old", "new")]
            text = f"{ch['stat']} ★{'/★'.join(map(str, ch['stars']))}: {'/'.join(old)} → {'/'.join(new)}"
            h = heroes.get(name_key(ch["name"]))
            cur = [(h["stats"].get(s) or h["stats"].get(str(s)) or {}).get(stats[0]) for s in ch["stars"]] if h else None
            if not h:
                status = "hero tidak ada di data"
            elif cur == new:
                status = "sudah masuk file game"
            else:
                status = "diterapkan server" if cur == old else f"diterapkan server (file game: {'/'.join(map(str, cur))})"
                for star, value in zip(ch["stars"], new):
                    for stat in stats:
                        h.setdefault("stats_server", {}).setdefault(str(star), {})[stat] = value
                h.setdefault("server", []).append(note(ch, text))
            changes.append({"kind": "Hero", "target": ch["name"], "text": text, "status": status})
        for kind, items in (("Commander", p.get("commanders", [])), ("Skill hero", p.get("hero_skills", [])),
                            ("Sinergi", p.get("synergies", [])), ("Go Go Card", p.get("cards", []))):
            for ch in items:
                if kind == "Commander":
                    item = skills.get((name_key(ch["name"]), name_key(ch["skill"])))
                    target, base = f"{ch['name']} / {ch['skill']}", item["skill"] if item else None
                elif kind == "Skill hero":
                    item = hero_skills.get((name_key(ch["name"]), name_key(ch["skill"])))
                    target, base = f"{ch['name']} / {ch['skill']}", item
                elif kind == "Sinergi":
                    item = synergies.get(name_key(ch["name"]))
                    target, base = ch["name"], item
                else:
                    item = cards.get(ch.get("id")) or next((c for c in d["cards"] if name_key(c["name"]) == name_key(ch["name"])), None)
                    target, base = ch["name"], item
                if ch.get("removed"):
                    text = "Dihapus sementara pada season ini"
                    status = "kartu tidak ada di data" if not item else "diterapkan server"
                    if item:
                        item["removed_server"] = p["patch"]
                        item.setdefault("server", []).append(note(ch, text))
                    changes.append({"kind": kind, "target": target, "text": text, "status": status})
                    continue
                pairs = ch.get("replace", [])
                text = ch.get("text") or "; ".join(f"{a} → {b}" for a, b in pairs)
                updated = replace_text(base.get("description", ""), pairs) if base else None
                attrs = server_attributes(base.get("attributes") or [], ch["attributes"]) if base and ch.get("attributes") else None
                if not base:
                    status = f"{kind.lower()} tidak ada di data"
                elif not pairs:
                    status = "diterapkan server (catatan; angkanya tidak ada di teks file game)"
                    item.setdefault("server", []).append(note(ch, text))
                elif ch.get("attributes") and attrs is None:
                    status = "atribut skill tidak ditemukan di file game (perbarui server_patch.json)"
                elif updated is not None:
                    status = "diterapkan server"
                    base["description_server"] = updated
                    if attrs:
                        base["attributes_server"] = attrs
                    item.setdefault("server", []).append(note(ch, text))
                elif all(b in base["description"] and a not in base["description"] for a, b in pairs):
                    status = "sudah masuk file game"
                else:
                    status = "teks lama tidak ditemukan di file game (perbarui server_patch.json)"
                changes.append({"kind": kind, "target": target, "text": text, "status": status})
        d.setdefault("server_patches", []).append({"patch": p["patch"], "source": p.get("source", ""),
                                                   "changes": changes, "notes": p.get("notes", [])})
    return [c for p in d.get("server_patches", []) for c in p["changes"] if not c["status"].startswith("diterapkan")]


def apply_gameplay_notes(d, sid, path=GAMEPLAY_NOTES):
    """Rules learned from playing (catatan_gameplay.json) -> equipment["gameplay_notes"]. Returns notes whose id is not
    in this season's equipment, for a warning."""
    if not path.exists():
        return []
    equipment = {e["id"]: e for e in d["equipment"]}
    missing = []
    for n in json.loads(path.read_text(encoding="utf-8")).get("equipment", []):
        if n.get("seasons") and sid not in n["seasons"]:
            continue
        item = equipment.get(n["id"])
        if not item:
            missing.append(n)
            continue
        item.setdefault("gameplay_notes", []).append({"text": n["text"], "source": n.get("source", "")})
    return missing


def rank_season_for(tables, battle_season):
    """RankSeason_MC uses btn_S<n> icons; map battle season -> rank season dates."""
    for r in tables.parse("RankSeason_MC"):
        if r.get("m_SeasonIcon", "").endswith(f"_S{battle_season}"):
            return r
    return None


def md(text):
    return (text or "").replace("\n", "  \n")


def to_markdown(d, rank):
    info = d.get("info", {})
    title = f"Season {d['season']}" + (f": {info['name']}" if info.get("name") else "")
    lines = [f"# Magic Chess: Go Go: {title}", ""]
    lines.append(f"- Versi game: `{d['game_version']}` · diekstrak {d['generated_at']}")
    if rank:
        start = rank["m_SeasonStartTime"].replace("_", " ")
        end = rank["m_SeasonEndTime"].replace("_", " ")
        lines.append(f"- Dipakai di Rank Season {rank['m_SeasonID']}: {start} s/d {end} (waktu server global)")
    n_f = sum(s["type"] == "Faksi" for s in d["synergies"])
    n_r = sum(s["type"] == "Role" for s in d["synergies"])
    active_cards = [c for c in d["cards"] if c.get("active", True)]
    active_equip = [e for e in d["equipment"] if e.get("active", True)]
    summoned = {h["name"] for h in d["heroes"] if h.get("summoned")}
    tag = lambda name: f"{name}*" if name in summoned else name
    lines += [f"- {len(d['heroes']) - len(summoned)} hero toko + {len(summoned)} hero panggilan · {n_f} faksi · {n_r} role · "
              f"{len(d['commanders'])} commander · "
              f"{len(active_cards)} Go Go Card aktif ({len(d['cards']) - len(active_cards)} nonaktif) · "
              f"{len(active_equip)} equipment aktif ({len(d['equipment']) - len(active_equip)} nonaktif)",
              "- Angka `a/b/c` = nilai di ★1/★2/★3. `X% ATK` = rasio damage dari parameter efek;"
              " `(dinamis)` = nilai yang hanya dihitung saat battle.",
              "- `*` = hero panggilan: tidak dijual di Toko, hanya dipanggil oleh sinergi (Chrono Wanderer dari Echomancer,"
              " Alpha dari SPECTRE).",
              ("- Angka **tebal** dan catatan _Patch x (server)_ = perubahan Patch Note yang diterapkan server, bukan dari file game"
               " (dicatat manual di `server_patch.json`); nilai file game ada di catatannya." if d.get("server_patches") else
               "- Angka hasil hotfix server (mis. patch note yang diumumkan in-game) tidak tersimpan di file lokal."), ""]

    server = lambda item: [f"_Patch {n['patch']} (server): {n['text']}_" for n in item.get("server", [])]
    stat = lambda h, star, label: (f"**{v}**" if (v := (h.get("stats_server") or {}).get(str(star), {}).get(label))
                                   else h["stats"][star][label])

    if info.get("levels"):
        lines += ["## Info season", "", "| Level | Biaya EXP | Slot hero | 1 Gold | 2 Gold | 3 Gold | 4 Gold | 5 Gold |",
                  "|---|---|---|---|---|---|---|---|"]
        for lv in info["levels"]:
            lines.append(f"| {lv['level']} | {lv['exp_cost']} | {lv['hero_slots']} | " + " | ".join(f"{x}%" for x in lv["shop_odds"]) + " |")
        if info.get("pool_per_hero"):
            lines += ["", "Jumlah salinan tiap hero di pool: " + ", ".join(f"{k} Gold = {v}" for k, v in info["pool_per_hero"].items())]
        lines.append("")

    box = d.get("go_go_box")
    if box and box["rounds"]:
        rng = lambda x: str(x["min"]) if x["min"] == x["max"] else f"{x['min']}–{x['max']}"
        lines += ["## Go Go Box", "",
                  f"_Sumber: `MCRoundRandomEquip_S{d['season']}`. Babak Go Go Box ada di akhir tiap fase; player memilih 1 hadiah "
                  f"berurutan dari sisa HP Commander terendah. Tiap Go Go Box berisi {box['orbs']} orb (equipment biasa, crystal "
                  "sinergi acak sampai total equipment babak itu, sisanya Kapasitas +1; jumlah orb dari pengamatan in-game) + hero. "
                  "Harga tiap hero diundi dengan bobot di tabel (bobot harga yang sama dijumlahkan). Teks orb in-game = ringkasan "
                  "item dalam kurung._", "",
                  "| Babak | Equipment biasa | Crystal sinergi | Kapasitas +1 | Hero | Harga hero: peluang (bobot) |",
                  "|---|---|---|---|---|---|"]
        for r in box["rounds"]:
            costs = ", ".join(f"{c['cost']} Gold {fmt_num(c['chance'])}% ({c['weight']})" for c in r["heroes"]["costs"])
            lines.append(f"| {r['label']} (babak {r['round']}) | {rng(r['equipment'])} | {rng(r['crystals'])} | "
                         f"{r['special']['count']} | {r['heroes']['count']} | {costs or '-'} |")
        lines.append("")
        for key, title in (("equipment", "Pool equipment biasa"), ("crystals", "Pool crystal sinergi"), ("special", "Item pengisi")):
            groups = {}  # rounds sharing the same pool are listed once
            for r in box["rounds"]:
                if r[key]["pool"]:
                    groups.setdefault(tuple((p["id"], p["weight"]) for p in r[key]["pool"]), (r[key]["pool"], []))[1].append(r["label"])
            for pool, rounds in groups.values():
                same = len({p["weight"] for p in pool}) == 1
                names = ", ".join(p["name"] + (f" ({p['summary']})" if p["summary"] else "") + (" (tidak ada di tabel equipment)" if p.get("missing") else "")
                                  + ("" if same else f" [bobot {p['weight']}]") for p in pool)
                lines.append(f"- **{title}** ({', '.join(rounds)}; {len(pool)} item{', peluang sama' if same else ''}): {names}")
        lines += [f"- Kolom lain babak {r['label']}: " + ", ".join(f"`{k}` = {v}" for k, v in r["extra"].items())
                  for r in box["rounds"] if r.get("extra")]
        lines += [f"- _Catatan data: {n}_" for n in box.get("notes", [])]
        lines.append("")

    for p in d.get("server_patches", []):
        lines += [f"## Perubahan dari server: Patch {p['patch']}", "",
                  f"_Diumumkan di Patch Note in-game ({p['source']}) tapi diterapkan server, tidak ada di file game._", "",
                  "| Bagian | Item | Perubahan | Status |", "|---|---|---|---|"]
        lines += [f"| {c['kind']} | {c['target']} | {c['text']} | {c['status']} |" for c in p["changes"]]
        lines += [""] + [f"- {n}" for n in p.get("notes", [])] + [""]

    lines += ["## Daftar hero", "", "| Hero | Cost | Sinergi | HP ★1/★2/★3 | Physical ATK | Magic ATK | ATK Speed |", "|---|---|---|---|---|---|---|"]
    for h in d["heroes"]:
        col = lambda label: "/".join(stat(h, star, label) for star in h["stats"])
        lines.append(f"| {tag(h['name'])} | {h['cost']} | {', '.join(h['synergies'])} | {col('HP')} | {col('Physical ATK')} | "
                     f"{col('Magic ATK')} | {col('ATK Speed')} |")
    lines.append("")

    for kind in ("Faksi", "Role"):
        lines += [f"## Sinergi: {kind}", ""]
        for s in (x for x in d["synergies"] if x["type"] == kind):
            lines += [f"### {s['name']}", "", f"Hero: {', '.join(map(tag, s['heroes'])) or '-'}", ""]
            if s["explain"]:
                lines += [md(s["explain"]), ""]
            for t in s["tiers"]:
                lines.append(f"- **{t['count']}**: {t['effect'].replace(chr(10), ' ')}")
            lines += [""] + ([f"{n}  " for n in server(s)] + [""] if s.get("server") else [])

    store = d.get("special_store")
    if store:
        lines += [f"## {store['title']} (sinergi {store['synergy']})", "",
                  f"_Sumber: `SpecialStore` + `MCSpecialCardPool` (nama/teks), efek dari `MCSkill`/`MCEffect`. Harga dalam"
                  f" {store['currency']} (batas simpan {store['max_storage']}). Peluang = bobot item / total bobot"
                  f" ({store['total_weight']}); jumlah slot dan aturan refresh toko tidak ada di tabel."
                  + ("" if store["verified"] else " **Belum terverifikasi**: belum ada screenshot toko ini.") + "_", "",
                  "| Item | Harga | Peluang (bobot) | Batas beli | Efek |", "|---|---|---|---|---|"]
        for it in store["items"]:
            effect = "; ".join(x for x in (it["effect"] or it["description"] or "sesuai nama item",
                                           f"pilihan: {', '.join(it['pool'])}" if it["pool"] else "",
                                           *[f"_Catatan data: {n}_" for n in it["notes"]]) if x)
            lines.append(f"| {it['name']} | {it['price']} {store['currency']} | {it['chance']}% ({it['weight']}) | "
                         f"{it['limit'] or 'tanpa batas'} | {effect} |")
        lines.append("")

    def skill_md(sk, prefix=""):
        out = [f"**{prefix}{sk['name']}**  ", md(sk.get("description_server") or sk["description"])] + \
              [f"  \n{n}" for n in server(sk)] + [""]
        attrs = sk.get("attributes_server") or sk.get("attributes")
        if attrs:
            out += ["| Atribut Skill | " + " | ".join(f"★{i + 1}" for i in range(len(attrs[0]["values"]))) + " |",
                    "|---" * (len(attrs[0]["values"]) + 1) + "|"]
            out += [f"| {a['label']} | " + " | ".join(v if v == f else f"**{v}**" for v, f in zip(a["values"], file["values"]))
                    + " |" for a, file in zip(attrs, sk["attributes"])]
            out.append("")
        return out

    lines += ["## Detail hero", ""]
    for h in d["heroes"]:
        lines += [f"### {h['name']}", "", f"Cost {h['cost']} · {', '.join(h['synergies'])}"
                  + (" · hero panggilan (tidak dijual di Toko)" if h.get("summoned") else ""), ""]
        labels = [label for label, _, _ in STATS]
        lines += ["| ★ | " + " | ".join(labels) + " |", "|---" * (len(labels) + 1) + "|"]
        for star in h["stats"]:
            lines.append(f"| {star} | " + " | ".join(stat(h, star, label) for label in labels) + " |")
        lines.append("")
        lines += [f"{s}  " for s in server(h)] + ([""] if h.get("server") else [])
        for sk in h["skills"]:
            lines += skill_md(sk)
        if h.get("enhanced"):
            lines += skill_md(h["enhanced"]["skill"], f"Versi diperkuat ({h['enhanced']['card']}): ")

    lines += ["## Commander", ""]
    for cat in sorted({c["category"] for c in d["commanders"]}):
        lines += [f"### {cat}", ""]
        for c in (x for x in d["commanders"] if x["category"] == cat):
            lines += [f"#### {c['name']}", ""]
            for s in c["skills"]:
                kind = f" ({s['type']})" if s.get("type") else ""
                desc = s["skill"].get("description_server") or s["skill"]["description"]
                lines += [f"**Lv {s['from_level']}+{kind}: {s['skill']['name']}**  ", md(desc)] + \
                         [f"  \n{n}" for n in server(s)] + [""]
                for k in s["skill"].get("details") or []:  # tooltip of an underlined keyword
                    lines += [f"> *Detail \"{k['keyword']}\":*  ", "> " + md(k["text"]).replace("\n", "\n> "), ""]
            if c.get("power_card"):
                lines += [f"*Kartu Power — {c['power_card']['name']}:* {md(c['power_card']['description'])}", ""]

    lines += ["## Go Go Card", "",
              "_Hanya kartu aktif (yang tampil di menu Go Go Card in-game). `Putaran` = putaran Go Go Card tempat kartu bisa muncul;"
              " Kartu Power hanya muncul di putaran 1 (babak I-2)._", ""]

    def card_md(c):
        rounds = f" · putaran {', '.join(map(str, c['rounds']))}" if c.get("rounds") and c["tier"] != "Power" else ""
        removed = f" **[dihapus sementara, Patch {c['removed_server']} (server)]**" if c.get("removed_server") else ""
        desc = (c.get("description_server") or c["description"]).replace(chr(10), " ")
        notes = "".join(f" {n}" for n in server(c) if not c.get("removed_server"))
        return f"- **{c['name']}**{' (season ini)' if c['season_only'] else ''}{rounds}{removed}: {desc}{notes}"

    for tier in ("Power", "Spesial", "Oranye", "Ungu", "Biru"):
        group = [c for c in active_cards if c["tier"] == tier]
        if group:
            lines += [f"### {tier} ({len(group)})", ""] + [card_md(c) for c in group] + [""]
    inactive = [c for c in d["cards"] if not c.get("active", True)]
    if inactive:
        lines += [f"### Tidak aktif di season ini ({len(inactive)})", "",
                  "_Ada di tabel dasar game, tapi bobot kemunculannya 0 sehingga tidak tampil in-game._", "",
                  ", ".join(f"{c['name']} ({c['tier']})" for c in inactive), ""]

    lines += ["## Equipment", "", "_Hanya equipment yang ada di pool season ini (tampil di menu Equipment in-game)._", ""]
    for cat in sorted({e["category"] for e in active_equip}):
        lines += [f"### {cat}", ""]
        for e in (x for x in active_equip if x["category"] == cat):
            for lv in e["levels"]:
                bits = lv["attributes"] + [f"Atribut Unik: {u}" for u in lv["unique"]] + [f"Pasif Unik - {p}" for p in lv["passives"]]
                lines.append(f"- **{lv['name']}** ({lv['summary']}): " + "; ".join(bits))
            lines += [f"  - _Aturan dari pengalaman bermain:_ {n['text']} _({n['source']})_" for n in e.get("gameplay_notes", [])]
        lines.append("")
    inactive_equip = [e for e in d["equipment"] if not e.get("active", True)]
    if inactive_equip:
        lines += [f"### Tidak aktif di season ini ({len(inactive_equip)})", "",
                  "_Ada di tabel equipment, tapi tidak masuk pool season ini sehingga tidak tampil in-game._", "",
                  ", ".join(f"{e['levels'][0]['name']} ({e['category']})" for e in inactive_equip), ""]

    if d.get("encyclopedia"):
        lines += ["## Ensiklopedia", ""]
        for tab in d["encyclopedia"]:
            lines += [f"### {tab['name']}", ""]
            for s in tab["sections"]:
                lines += [f"#### {s['title']}", ""] if s.get("title") else []
                lines += [md(s["text"]), ""] if s.get("text") else []
                if s.get("table"):
                    t = s["table"]
                    lines += ["| " + " | ".join(t["header"]) + " |", "|---" * len(t["header"]) + "|"]
                    lines += ["| " + " | ".join(str(x) for x in row) + " |" for row in t["rows"]] + [""]
                lines += [md(s["note"]), ""] if s.get("note") else []
    return "\n".join(lines)


def to_html(d, rank):
    """Self-contained searchable page: report_template.html with the season JSON embedded."""
    data = dict(d)
    if rank:
        data["rank"] = {"id": rank["m_SeasonID"], "start": rank["m_SeasonStartTime"].replace("_", " "),
                        "end": rank["m_SeasonEndTime"].replace("_", " ")}
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")  # keep </script> out of the JSON
    template = (HERE / "report_template.html").read_text(encoding="utf-8")
    title = f"MCGG Season {d['season']} ({d['game_version']})"
    return template.replace("__TITLE__", title).replace("__DATA__", payload)


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Ekspor data patch Magic Chess: Go Go")
    ap.add_argument("--game", type=Path, default=DEFAULT_GAME)
    ap.add_argument("--season", type=int, nargs="*", help="default: season aktif + berikutnya dari MCSystemConfig")
    ap.add_argument("--lang", default="Indonesian", help="akhiran file AllLanguage<lang>, mis. EN, Indonesian")
    args = ap.parse_args()

    version = game_version(args.game)
    print(f"Versi game {version}")
    tables = Tables(args.game, HERE / "cache" / version)
    lang = Language(tables, "EN")
    if args.lang != "EN":
        lang.text.update(Language(tables, args.lang).text)  # fallback ke EN bila teks tidak ada

    seasons = args.season or current_seasons(tables)
    print(f"Season: {seasons}" + ("" if args.season else f" (aktif S{seasons[0]}, berikutnya S{seasons[-1]})"))
    out_dir = HERE / "data" / version
    out_dir.mkdir(parents=True, exist_ok=True)
    for sid in seasons:
        d = Season(tables, lang, sid).build(version)
        for c in apply_server_patches(d, sid):
            print(f"  [server_patch.json S{sid}] {c['kind']} {c['target']}: {c['status']}")
        for n in apply_gameplay_notes(d, sid):
            print(f"  [catatan_gameplay.json S{sid}] equipment {n['id']} ({n.get('name', '')}) tidak ada di data season ini")
        found, missing = attach_icons(d, args.game, out_dir)
        print(f"  S{sid}: {found} ikon di {out_dir / 'img'}"
              + (f"; {len(missing)} rujukan ikon tidak ada di atlas game: {', '.join(missing[:5])}" if missing else ""))
        (out_dir / f"S{sid}.json").write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
        rank = rank_season_for(tables, sid)
        (out_dir / f"S{sid}.md").write_text(to_markdown(d, rank), encoding="utf-8")
        (out_dir / f"S{sid}.html").write_text(to_html(d, rank), encoding="utf-8")
        print(f"  S{sid} {d['info'].get('name') or ''}: {len(d['heroes'])} hero, {len(d['synergies'])} sinergi, "
              f"{len(d['commanders'])} commander, {sum(c['active'] for c in d['cards'])} kartu aktif, "
              f"{sum(e['active'] for e in d['equipment'])} equipment aktif, "
              f"{len((d['special_store'] or {}).get('items', []))} item Toko Spirit Sand, "
              f"{len((d['go_go_box'] or {}).get('rounds', []))} babak Go Go Box, {len(d['encyclopedia'])} tab Ensiklopedia"
              f" -> {out_dir / f'S{sid}.html'} (+ .md, .json)")


if __name__ == "__main__":
    main()
