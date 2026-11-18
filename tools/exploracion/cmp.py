import sys, io, contextlib, runpy, os
f=sys.argv[1]; oids=[int(x) for x in sys.argv[2].split(",")]
sys.argv=[sys.argv[0], f, "none"]
with contextlib.redirect_stdout(io.StringIO()):
    g = runpy.run_path(os.path.join(os.path.dirname(__file__), "explore.py"))
P,O=g["props"],g["objs"]
nums=sorted({p[1] for o in oids for p in P[o]})
print("prop  "+" ".join(f"{O[o]['IDFOS_NAM'][:13]:>13}" for o in oids))
for n in nums:
    row=[]
    for o in oids:
        v=[p[3] for p in P[o] if p[1]==n]
        s="" if not v else (("<blob>" if isinstance(v[0],bytes) else str(v[0])))
        row.append(f"{s[:13]:>13}")
    print(f"{n:4}  "+" ".join(row))
