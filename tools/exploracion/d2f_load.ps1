# Viabilidad: diccionario de la API (nombre/const/tipo) + carga del FMB y lectura de bloques/ítems.
param([string]$Fmb, [string]$Dic)
$src = @"
using System;
using System.Text;
using System.Runtime.InteropServices;
public static class D2F {
  const CallingConvention C = CallingConvention.Cdecl;
  [DllImport("ifd2f60.dll", CallingConvention=C)] public static extern int d2fctxcr_Create(out IntPtr ctx, IntPtr attr);
  [DllImport("ifd2f60.dll", CallingConvention=C)] public static extern int d2fprgn_GetName(IntPtr ctx, int pnum, out IntPtr name);
  [DllImport("ifd2f60.dll", CallingConvention=C)] public static extern int d2fprgcn_GetConstName(IntPtr ctx, int pnum, out IntPtr name);
  [DllImport("ifd2f60.dll", CallingConvention=C)] public static extern int d2fprgt_GetType(IntPtr ctx, int pnum);
  [DllImport("ifd2f60.dll", CallingConvention=C)] public static extern int d2fprgcv_GetConstValue(IntPtr ctx, string cname, out int pnum);
  [DllImport("ifd2f60.dll", CallingConvention=C)] public static extern int d2ffmdld_Load(IntPtr ctx, out IntPtr fmd, string fname, int fromdb);
  [DllImport("ifd2f60.dll", CallingConvention=C)] public static extern int d2fobgo_GetObjProp(IntPtr ctx, IntPtr obj, int pnum, out IntPtr val);
  [DllImport("ifd2f60.dll", CallingConvention=C)] public static extern int d2fobgt_GetTextProp(IntPtr ctx, IntPtr obj, int pnum, out IntPtr val);
  [DllImport("ifd2f60.dll", CallingConvention=C)] public static extern int d2fobgn_GetNumProp(IntPtr ctx, IntPtr obj, int pnum, out int val);
  [DllImport("ifd2f60.dll", CallingConvention=C)] public static extern int d2fobgb_GetBoolProp(IntPtr ctx, IntPtr obj, int pnum, out int val);
  [DllImport("ifd2f60.dll", CallingConvention=C)] public static extern int d2fobqt_QueryType(IntPtr ctx, IntPtr obj, out int typ);
  public static string S(IntPtr p) { return p == IntPtr.Zero ? "<null>" : Marshal.PtrToStringAnsi(p); }
}
"@
Add-Type -TypeDefinition $src
$env:PATH = "C:\dev6i\bin;" + $env:PATH
$attr = [Runtime.InteropServices.Marshal]::AllocHGlobal(256)
for ($k = 0; $k -lt 256; $k++) { [Runtime.InteropServices.Marshal]::WriteByte($attr, $k, 0) }
$ctx = [IntPtr]::Zero
$null = [D2F]::d2fctxcr_Create([ref]$ctx, $attr)

# 1) diccionario: se escribe línea a línea para saber dónde corta si algo falla
$w = New-Object IO.StreamWriter($Dic, $false, [Text.Encoding]::UTF8)
for ($n = 1; $n -le 550; $n++) {
  $p1 = [IntPtr]::Zero; $p2 = [IntPtr]::Zero
  $s2 = [D2F]::d2fprgn_GetName($ctx, $n, [ref]$p2)
  $s1 = [D2F]::d2fprgcn_GetConstName($ctx, $n, [ref]$p1)
  $ty = [D2F]::d2fprgt_GetType($ctx, $n)
  $w.WriteLine("$n`t$([D2F]::S($p1))`t$([D2F]::S($p2))`t$ty"); $w.Flush()
}
$w.Close()
"diccionario ok"

$P_NAME = 300; $P_BLOCK = 29; $P_NEXT = 302; $P_ITEM = 229
$P_QDS = 383; $P_RECS = 393; $P_INS = 219; $P_ITTY = 231
"NAME=$P_NAME BLOCK=$P_BLOCK NEXT=$P_NEXT ITEM=$P_ITEM QRY_DAT_SRC_NAM=$P_QDS RECS_DISP_COUNT=$P_RECS INSERT_ALLOWED=$P_INS ITM_TYP=$P_ITTY"

# 2) carga del FMB
$fmd = [IntPtr]::Zero
$st = [D2F]::d2ffmdld_Load($ctx, [ref]$fmd, $Fmb, 0)
"load st=$st"
if ($st -ne 0) { exit 1 }
$blk = [IntPtr]::Zero
$null = [D2F]::d2fobgo_GetObjProp($ctx, $fmd, $P_BLOCK, [ref]$blk)
while ($blk -ne [IntPtr]::Zero) {
  $pn = [IntPtr]::Zero; $null = [D2F]::d2fobgt_GetTextProp($ctx, $blk, $P_NAME, [ref]$pn)
  $pq = [IntPtr]::Zero; $null = [D2F]::d2fobgt_GetTextProp($ctx, $blk, $P_QDS, [ref]$pq)
  $r = 0; $null = [D2F]::d2fobgn_GetNumProp($ctx, $blk, $P_RECS, [ref]$r)
  $ia = 0; $null = [D2F]::d2fobgb_GetBoolProp($ctx, $blk, $P_INS, [ref]$ia)
  "BLOQUE $([D2F]::S($pn)) origen=$([D2F]::S($pq)) regs=$r insert=$ia"
  $it = [IntPtr]::Zero; $null = [D2F]::d2fobgo_GetObjProp($ctx, $blk, $P_ITEM, [ref]$it); $k = 0
  while ($it -ne [IntPtr]::Zero -and $k -lt 3) {
    $pi = [IntPtr]::Zero; $null = [D2F]::d2fobgt_GetTextProp($ctx, $it, $P_NAME, [ref]$pi)
    $ty = 0; $null = [D2F]::d2fobgn_GetNumProp($ctx, $it, $P_ITTY, [ref]$ty)
    "   item $([D2F]::S($pi)) tipo=$ty"
    $nx = [IntPtr]::Zero; $null = [D2F]::d2fobgo_GetObjProp($ctx, $it, $P_NEXT, [ref]$nx); $it = $nx; $k++
  }
  $nb = [IntPtr]::Zero; $null = [D2F]::d2fobgo_GetObjProp($ctx, $blk, $P_NEXT, [ref]$nb); $blk = $nb
}
