"""Exploración del formato ROS (.fmt Forms 6i). Uso: python explore.py <archivo.fmt> <modo> [args]"""
import re, sys, collections, json

path = sys.argv[1]
modo = sys.argv[2] if len(sys.argv) > 2 else "stats"
raw = open(path, "rb").read().decode("cp1252")
lines = raw.split("\r\n")

# --- tokenizar registros DEFINE X BEGIN ... END, con valores <<"...">> multilínea
records = []
i = 0
while i < len(lines):
    m = re.match(r"^(DEFINE|DESCRIBE)\s+(\S+)\s*$", lines[i])
    if not m:
        i += 1
        continue
    kind, rtype = m.groups()
    assert lines[i + 1].strip() == "BEGIN", (i, lines[i + 1])
    i += 2
    fields = collections.OrderedDict()
    start = i
    while lines[i].strip() != "END":
        ln = lines[i]
        mm = re.match(r"^\s*(\w+)\s*=\s*(.*)$", ln)
        if kind == "DESCRIBE":
            fields[ln.split()[1]] = ln.split()[0]
            i += 1
            continue
        if not mm:
            raise SystemExit(f"linea {i+1} no reconocida: {ln!r} (reg {rtype} en {start})")
        key, val = mm.groups()
        if val == "(BLONG)":
            i += 1
            assert lines[i].strip() == '<<"', lines[i]
            hx = []
            i += 1
            while lines[i].strip() != '">>':
                hx.append(lines[i].replace(" ", ""))
                i += 1
            val = ("B", bytes.fromhex("".join(hx)))
        elif val.startswith('<<"'):
            buf = val[3:]
            while not buf.endswith('">>'):
                i += 1
                buf += "\n" + lines[i]
            val = ("S", buf[:-3])
        elif lines[i + 1].strip().startswith('<<"'):
            # VARCHAR: longitud en esta línea, texto en la(s) siguiente(s)
            i += 1
            buf = lines[i].strip()[3:]
            while not buf.endswith('">>'):
                i += 1
                buf += "\n" + lines[i]
            val = ("S", buf[:-3])
        else:
            val = ("N", val)
        fields[key] = val
        i += 1
    records.append((kind, rtype, fields, start))
    i += 1

if modo == "dump":  # imprime registros i..j en forma compacta
    a, b = int(sys.argv[3]), int(sys.argv[4])
    for k, (kind, rtype, f, ln) in enumerate(records[a:b], a):
        print(k, ln, rtype, {x: v[1] for x, v in f.items()})
    sys.exit()

objs = {}
order = []
props = collections.defaultdict(list)  # oid -> [(rtype, pnum, idx, valor)]
for kind, rtype, f, ln in records:
    if kind != "DEFINE":
        continue
    if rtype == "FRM50_IDFO":
        o = {k: v[1] for k, v in f.items()}
        o["line"] = ln
        objs[int(o["IDFOS_OID"])] = o
        order.append(int(o["IDFOS_OID"]))
    elif rtype in ("F50N", "F50T", "F50B", "F50P", "F50O", "F50S"):
        p = rtype[-1]
        owner = int(f[p + "P"][1])
        num = int(f[p + "N"][1])
        idx = int(f[p + "I"][1])
        val = f.get(p + "V", f.get(p + "O", ("?", None)))[1]
        props[owner].append((rtype, num, idx, val))


def nombre(o):
    return o["IDFOS_NAM"]


if modo == "stats":
    t = collections.Counter(int(objs[o]["IDFOS_TYP"]) for o in objs)
    for typ, c in sorted(t.items()):
        ejemplos = [nombre(objs[o]) for o in order if int(objs[o]["IDFOS_TYP"]) == typ][:6]
        print(f"TYP {typ:4} x{c:4}  {ejemplos}")
elif modo == "tree":  # árbol por IDFOS_POI (sólo tipos con nombre o filtrados)
    maxdepth = int(sys.argv[3]) if len(sys.argv) > 3 else 3
    hijos = collections.defaultdict(list)
    for oid in order:
        hijos[int(objs[oid]["IDFOS_POI"])].append(oid)

    def rec(oid, d):
        o = objs[oid]
        print("  " * d + f"[{o['IDFOS_TYP']}] oid={oid} {nombre(o)!r} OPN={o['IDFOS_OPN']} OOI={o['IDFOS_OOI']} CNT={o['IDFOS_CNT']} nprops={len(props[oid])}")
        if d < maxdepth:
            for h in hijos[oid]:
                rec(h, d + 1)

    for r in hijos[0]:
        rec(r, 0)
elif modo == "props":  # props de un oid
    oid = int(sys.argv[3])
    print(objs[oid])
    for p in props[oid]:
        v = p[3]
        if isinstance(v, str) and len(v) > 300:
            v = v[:300] + "..."
        print(p[:3], repr(v))
elif modo == "proptypes":  # para un TYP: qué números de prop aparecen y ejemplos
    typ = sys.argv[3]
    c = collections.defaultdict(list)
    for oid in order:
        if objs[oid]["IDFOS_TYP"] == typ:
            for rt, num, idx, val in props[oid]:
                c[(rt, num)].append((nombre(objs[oid]), val))
    for (rt, num), l in sorted(c.items(), key=lambda x: x[0][1]):
        ej = collections.Counter(str(v)[:60] for _, v in l).most_common(4)
        print(rt, num, len(l), ej)
elif modo == "find":  # buscar texto en valores
    pat = re.compile(sys.argv[3], re.I)
    for oid in order:
        for p in props[oid]:
            if isinstance(p[3], str) and pat.search(p[3]):
                print(oid, objs[oid]["IDFOS_TYP"], nombre(objs[oid]), p[:3], repr(p[3][:120]))
