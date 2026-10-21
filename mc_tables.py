"""Baca tabel data Magic Chess: Go Go (format "$mulonggame_table_1").

Isi modul:
  - load_schema()   : ambil susunan kolom tiap tabel (CData_<Tabel>_Element) dari GameAssembly.pdb
  - load_tables()   : ekstrak TextAsset dari StreamingAssets/Document/windows/*.unity3d
  - Tables.parse()  : decode tabel (flag '0' polos, '1' bitmask per baris, '2' tanpa kolom key + indeks)
  - Language        : teks terjemahan; kunci = hash Java (h*31+c) dari "<Tabel>_<field>_<key>"

Hasil ekstraksi di-cache per versi game di cache/<versi>/ supaya run berikutnya cepat.
"""
import json
import mmap
import re
import struct
from pathlib import Path

MAGIC = b"$mulonggame_table_1\0"
DATA = "MagicChessGoGo_Data"
DOCUMENT = f"{DATA}/StreamingAssets/Document/windows"


# ---------------------------------------------------------------- PDB schema

def _numeric(buf, pos):
    v = struct.unpack_from("<H", buf, pos)[0]
    if v < 0x8000:
        return v, pos + 2
    size = {0x8000: 1, 0x8001: 2, 0x8002: 2, 0x8003: 4, 0x8004: 4, 0x8009: 8, 0x800A: 8}[v]
    fmt = {1: "<b", 2: "<h", 4: "<i", 8: "<q"}[size]
    return struct.unpack_from(fmt, buf, pos + 2)[0], pos + 2 + size


def _cstr(buf, pos):
    end = buf.index(b"\0", pos)
    return buf[pos:end].decode("utf-8", "replace"), end + 1


def _msf_stream(mm, index):
    block_size, _, _, dir_bytes, _, block_map_addr = struct.unpack_from("<6I", mm, 32)
    n_dir = (dir_bytes + block_size - 1) // block_size
    dir_blocks = struct.unpack_from(f"<{n_dir}I", mm, block_map_addr * block_size)
    directory = b"".join(mm[b * block_size:(b + 1) * block_size] for b in dir_blocks)[:dir_bytes]
    num_streams = struct.unpack_from("<I", directory, 0)[0]
    sizes = struct.unpack_from(f"<{num_streams}I", directory, 4)
    pos = 4 + 4 * num_streams
    for i, size in enumerate(sizes):
        n = 0 if size == 0xFFFFFFFF else (size + block_size - 1) // block_size
        blocks = struct.unpack_from(f"<{n}I", directory, pos)
        pos += 4 * n
        if i == index:
            return b"".join(mm[b * block_size:(b + 1) * block_size] for b in blocks)[:size]
    raise IndexError(index)


_BASIC = {0x30: "bool", 0x20: "uint8", 0x74: "int32", 0x75: "uint32", 0x76: "int64", 0x40: "float", 0x41: "double"}


def extract_schema(pdb_path):
    """Return {table_class: [[field, type], ...]} for every IL2CPP CData_*_Element struct."""
    with open(pdb_path, "rb") as f:
        mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        tpi = _msf_stream(mm, 2)
    header_size, ti, _, rec_bytes = struct.unpack_from("<4I", tpi, 4)
    records, pos = {}, header_size
    while pos < header_size + rec_bytes:
        length, leaf = struct.unpack_from("<HH", tpi, pos)
        records[ti] = (leaf, pos + 4, pos + 2 + length)
        pos += 2 + length
        ti += 1

    def type_name(t):
        if t < 0x1000:
            return _BASIC.get(t & 0xFF, f"basic_{t:#x}") + ("*" if (t >> 8) & 7 else "")
        leaf, start, _ = records.get(t, (None, 0, 0))
        if leaf in (0x1001, 0x1002):  # modifier / pointer
            inner = type_name(struct.unpack_from("<I", tpi, start)[0])
            return inner + ("*" if leaf == 0x1002 else "")
        if leaf in (0x1504, 0x1505):
            return _cstr(tpi, _numeric(tpi, start + 16)[1])[0]
        return f"leaf{leaf}"

    def members(field_ti):
        _, p, end = records[field_ti]
        out = []
        while p < end:
            if tpi[p] >= 0xF0:  # LF_PADn
                p += max(tpi[p] & 0x0F, 1)
                continue
            kind = struct.unpack_from("<H", tpi, p)[0]
            if kind == 0x150D:  # LF_MEMBER
                ftype = struct.unpack_from("<I", tpi, p + 4)[0]
                name, p = _cstr(tpi, _numeric(tpi, p + 8)[1])
                out.append([name, type_name(ftype)])
            elif kind == 0x1400:  # LF_BCLASS
                p = _numeric(tpi, p + 8)[1]
            elif kind in (0x150E, 0x1510, 0x150F):  # static member / nested type / method
                p = _cstr(tpi, p + 8)[1]
            elif kind == 0x1511:  # LF_ONEMETHOD
                mprop = (struct.unpack_from("<H", tpi, p + 2)[0] >> 2) & 7
                p = _cstr(tpi, p + 8 + (4 if mprop in (4, 6) else 0))[1]
            elif kind == 0x1409:  # LF_VFUNCTAB
                p += 8
            else:
                raise ValueError(f"unknown member leaf {kind:#x}")
        return out

    schema = {}
    for leaf, start, _ in records.values():
        if leaf not in (0x1504, 0x1505):
            continue
        props, field_ti = struct.unpack_from("<HI", tpi, start + 2)
        if props & 0x80 or field_ti == 0:  # forward reference
            continue
        name = _cstr(tpi, _numeric(tpi, start + 16)[1])[0]
        m = re.fullmatch(r"CData_(\w+?)_Element_t[0-9A-F]{40}", name)
        if m:
            schema[m.group(1)] = members(field_ti)
    return schema


# ---------------------------------------------------------------- extraction

def game_version(game):
    return json.loads((game / "manifest.json").read_text(encoding="utf-8"))["version"]


def load_schema(game, cache):
    path = cache / "schema.json"
    if not path.exists():
        print("  membaca skema dari GameAssembly.pdb ...")
        cache.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(extract_schema(game / "GameAssembly.pdb")), encoding="utf-8")
    return json.loads(path.read_text(encoding="utf-8"))


def load_tables(game, cache):
    """Extract every TextAsset under Document/windows once; return {name: Path}."""
    out = cache / "tables"
    if not out.is_dir():
        import UnityPy  # only needed on first extraction

        print("  mengekstrak tabel dari bundle Document (sekali per versi) ...")
        tmp = cache / "tables.partial"
        tmp.mkdir(parents=True, exist_ok=True)
        for bundle in sorted((game / DOCUMENT).glob("*.unity3d")):
            for obj in UnityPy.load(str(bundle)).objects:
                if obj.type.name == "TextAsset":
                    asset = obj.read()
                    data = asset.m_Script.encode("utf-8", "surrogateescape")
                    (tmp / f"{asset.m_Name}.bin").write_bytes(data)
        tmp.rename(out)
    return {p.stem: p for p in out.glob("*.bin")}


# ---------------------------------------------------------------- decoding

class Reader:
    def __init__(self, buf, pos=0):
        self.buf, self.pos = buf, pos

    def unpack(self, fmt):
        v = struct.unpack_from(fmt, self.buf, self.pos)[0]
        self.pos += struct.calcsize(fmt)
        return v

    def string(self):
        n = s = 0
        while True:  # 7-bit encoded length
            c = self.buf[self.pos]
            self.pos += 1
            n |= (c & 0x7F) << s
            s += 7
            if c < 0x80:
                break
        v = self.buf[self.pos:self.pos + n].decode("utf-8", "replace")
        self.pos += n
        return v


_SCALAR = {"int32": "<i", "uint32": "<I", "int64": "<q", "float": "<f", "double": "<d", "uint8": "<B", "bool": "<?"}
_ELEM = {"Int32": "int32", "UInt32": "uint32", "Single": "float", "Double": "double", "String": "String_t*"}


def _read_value(r, t):
    if t in _SCALAR:
        return r.unpack(_SCALAR[t])
    if t == "String_t*":
        return r.string()
    m = re.fullmatch(r"(Int32|UInt32|Single|Double|String)((?:U5BU5D)+)\*", t)
    if m:  # arrays: 1-byte count, then elements
        depth = len(m.group(2)) // 6
        inner = _ELEM[m.group(1)] if depth == 1 else f"{m.group(1)}{'U5BU5D' * (depth - 1)}*"
        return [_read_value(r, inner) for _ in range(r.unpack("<B"))]
    raise TypeError(t)


def is_localized(field, ftype="String_t*"):
    """String fields named m_m<Upper> live in the language tables, not in the row data."""
    return ftype == "String_t*" and re.match(r"m_m[A-Z]", field) is not None


class Tables:
    def __init__(self, game, cache):
        self.schema = load_schema(game, cache)
        self.files = load_tables(game, cache)
        self._cache = {}

    def columns(self, table):
        name = table
        while name not in self.schema:  # MCHero_S7 -> MCHero
            if "_" not in name:
                raise KeyError(table)
            name = name.rsplit("_", 1)[0]
        cols = []
        for field, ftype in self.schema[name]:
            m = re.fullmatch(r"___(\w+)_(\d+)", field)
            if m and m.group(1) != "m_bError":
                cols.append((int(m.group(2)), m.group(1), re.sub(r"_t[0-9A-F]{40}", "", ftype)))
        return [(n, t) for _, n, t in sorted(cols)]

    def __contains__(self, table):
        return table in self.files

    def parse(self, table):
        if table in self._cache:
            return self._cache[table]
        buf = self.files[table].read_bytes()
        if not buf.startswith(MAGIC):
            raise ValueError(f"{table}: bukan tabel mulonggame")
        flag = chr(buf[len(MAGIC)])
        r = Reader(buf, len(MAGIC) + 1)
        nrows, nfields = r.unpack("<i"), r.unpack("<i")
        cols = self.columns(table)
        if nfields != len(cols):
            raise ValueError(f"{table}: header {nfields} kolom, skema {len(cols)}")
        rows = []
        if flag == "0":
            for _ in range(nrows):
                rows.append({n: _read_value(r, t) for n, t in cols if not is_localized(n, t)})
            end = r.pos
        elif flag == "1":  # per-row presence masks; absent fields keep their default
            nwords = (len(cols) + 31) // 32
            for _ in range(nrows):
                masks = [r.unpack("<I") for _ in range(nwords)]
                rows.append({n: _read_value(r, t) for i, (n, t) in enumerate(cols)
                             if masks[i // 32] >> (i % 32) & 1 and not is_localized(n, t)})
            end = r.pos
        elif flag == "2":  # rows omit the key column; (key, offset) index follows the data
            index_pos = r.unpack("<i")
            ir = Reader(buf, index_pos + 4)
            index = [(ir.unpack("<i"), ir.unpack("<i")) for _ in range(ir.unpack("<i"))]
            key_name = cols[0][0]
            for key, offset in sorted(index, key=lambda e: e[1]):
                r.pos = offset
                row = {key_name: key}
                row.update({n: _read_value(r, t) for n, t in cols[1:] if not is_localized(n, t)})
                rows.append(row)
            end = ir.pos
        else:
            raise NotImplementedError(f"{table}: flag {flag!r}")
        if end != len(buf):
            raise ValueError(f"{table}: parsing berhenti di byte {end} dari {len(buf)}")
        self._cache[table] = rows
        return rows


class Language:
    """AllLanguage*/AddLanguage*: index of (hash, text offset) after a string pool."""

    def __init__(self, tables, lang):
        self.text = {}
        names = [f"AllLanguage{lang}", f"AllLanguage{lang}_moba", f"AddLanguage{lang}", f"AddLanguage{lang}_moba"]
        for name in names:  # Add* loaded last so patch text wins
            if name not in tables.files:
                continue
            buf = tables.files[name].read_bytes()
            r = Reader(buf, len(MAGIC) + 1)
            idx_off = struct.unpack_from("<I", buf, r.pos + 8)[0]
            ir = Reader(buf, idx_off + 4)
            for _ in range(ir.unpack("<I")):
                key, off = ir.unpack("<I"), ir.unpack("<I")
                self.text[key] = Reader(buf, off).string()

    @staticmethod
    def hash(s):
        h = 0
        for c in s.encode("utf-8"):
            h = (h * 31 + c) & 0xFFFFFFFF
        return h

    def get(self, table, field, key):
        return self.text.get(self.hash(f"{table}_{field}_{key}"))
