"""Analiza el BLONG de código (prop 464). Uso: python blob.py <fmt> <oid> [oid...]"""
import sys, struct, runpy, io, contextlib

fmt = sys.argv[1]
sys.argv = [sys.argv[0], fmt, "none"]
with contextlib.redirect_stdout(io.StringIO()):
    g = runpy.run_path(__file__.replace("blob.py", "explore.py"))
props, objs = g["props"], g["objs"]

def imprimible(bs):
    return all(b in (9, 10, 13) or 32 <= b < 127 or b >= 160 for b in bs)

for oid in map(int, sys.argv[3:] if False else []):
    pass

import os
oids = [int(x) for x in os.environ["OIDS"].split(",")]
for oid in oids:
    blob = [p[3] for p in props[oid] if p[1] == 464][0]
    print(f"===== oid {oid} {objs[oid]['IDFOS_NAM']} typ={objs[oid]['IDFOS_TYP']} len={len(blob)}")
    print("cabecera:", blob[:48].hex(" ", 4))
    # buscar fragmentos [len][texto] de forma secuencial a partir de cada offset
    i = 0
    while i < len(blob) - 4:
        n = struct.unpack(">I", blob[i:i + 4])[0]
        if 3 <= n <= len(blob) - i - 4 and imprimible(blob[i + 4:i + 4 + n]):
            txt = blob[i + 4:i + 4 + n].decode("cp1252")
            corto = txt if len(txt) < 160 else txt[:120] + f" ...[{len(txt)}c]... " + txt[-40:]
            print(f"  @{i:6} len={n:6} {corto!r}")
            i += 4 + n
        else:
            i += 1
