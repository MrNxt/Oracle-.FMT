import sys, io, contextlib, runpy, os
f = sys.argv[1]; oid=int(sys.argv[2]); a=int(sys.argv[3]); b=int(sys.argv[4])
sys.argv=[sys.argv[0], f, "none"]
with contextlib.redirect_stdout(io.StringIO()):
    g = runpy.run_path(os.path.join(os.path.dirname(__file__), "explore.py"))
blob=[p[3] for p in g["props"][oid] if p[1]==464][0]
seg=blob[a:b]
for k in range(0,len(seg),32):
    c=seg[k:k+32]
    print(f"{a+k:6} {c.hex(' ',4):72} {''.join(chr(x) if 32<=x<127 else '.' for x in c)}")
