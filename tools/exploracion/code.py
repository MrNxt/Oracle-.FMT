"""Extrae el fuente de todos los triggers (68) y program units (58). Uso: python code.py <fmt> [resumen|full OID]"""
import sys, struct, runpy, io, contextlib, os, re, collections

fmt, modo = sys.argv[1], sys.argv[2]
arg = sys.argv[3] if len(sys.argv) > 3 else None
sys.argv = [sys.argv[0], fmt, "none"]
with contextlib.redirect_stdout(io.StringIO()):
    g = runpy.run_path(os.path.join(os.path.dirname(__file__), "explore.py"))
props, objs, order = g["props"], g["objs"], g["order"]

OK = set(range(32, 256)) | {9, 10, 13}


def chunk(blob, i):
    if i + 4 > len(blob):
        return None
    n = struct.unpack(">I", blob[i:i + 4])[0]
    if 1 <= n <= len(blob) - i - 4:
        t = blob[i + 4:i + 4 + n]
        if all(b in OK for b in t):
            return n, t
    return None


def primer_chunk(blob, desde, ventana=12, minimo=1):
    mejor = None
    for k in range(desde, min(desde + ventana, len(blob))):
        c = chunk(blob, k)
        if c and c[0] >= minimo and (mejor is None or c[0] > mejor[1]):
            mejor = (k, c[0], c[1])
    return mejor


def extraer(blob):
    # nombre interno: primer chunk después de la cabecera
    n_ents = struct.unpack(">I", blob[12:16])[0]
    pos = 16 + 4 * n_ents
    nombre = primer_chunk(blob, pos, ventana=40, minimo=1)
    seq = [nombre]
    p = nombre[0] + 4 + nombre[1]
    while True:
        c = primer_chunk(blob, p, ventana=8)
        if not c:
            break
        seq.append(c)
        p = c[0] + 4 + c[1]
    return [(k, n, t.decode("cp1252")) for k, n, t in seq], p


for oid in order:
    o = objs[oid]
    if o["IDFOS_TYP"] not in ("58", "68"):
        continue
    if arg and int(arg) != oid:
        continue
    blob = [p[3] for p in props[oid] if p[1] == 464]
    if not blob or not isinstance(blob[0], bytes):
        print(oid, o["IDFOS_NAM"], "SIN BLOB 464", [p[:3] for p in props[oid]])
        continue
    seq, fin = extraer(blob[0])
    if modo == "resumen":
        print(f"{oid:4} {o['IDFOS_TYP']} {o['IDFOS_NAM'][:28]:28} blob={len(blob[0]):6} chunks=" +
              " | ".join(f"@{k}:{n}:{t[:22]!r}" for k, n, t in seq))
    else:
        for k, n, t in seq:
            print(f"--- @{k} len={n}\n{t}")
