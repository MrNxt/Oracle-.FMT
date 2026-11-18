# Volcado del diccionario de propiedades de la Open API de Forms 6i (ifd2f60.dll). Ejecutar con PowerShell x86.
param([string]$Salida, [string]$Conv = "Cdecl")
$src = @"
using System;
using System.Runtime.InteropServices;
public static class D2F {
  [DllImport("ifd2f60.dll", CallingConvention=CallingConvention.$Conv)] public static extern int d2fctxcr_Create(out IntPtr ctx, IntPtr attr);
  [DllImport("ifd2f60.dll", CallingConvention=CallingConvention.$Conv)] public static extern int d2fprgn_GetName(IntPtr ctx, int pnum, out IntPtr name);
  [DllImport("ifd2f60.dll", CallingConvention=CallingConvention.$Conv)] public static extern int d2fprgcn_GetConstName(IntPtr ctx, int pnum, out IntPtr name);
  [DllImport("ifd2f60.dll", CallingConvention=CallingConvention.$Conv)] public static extern int d2fprgt_GetType(IntPtr ctx, int pnum);
  [DllImport("ifd2f60.dll", CallingConvention=CallingConvention.$Conv)] public static extern int d2fprgvn_GetValueName(IntPtr ctx, int pnum, int val, out IntPtr name);
  [DllImport("ifd2f60.dll", CallingConvention=CallingConvention.$Conv)] public static extern int d2fobgcn_GetConstName(IntPtr ctx, int otyp, out IntPtr name);
  public static string S(IntPtr p) { return p == IntPtr.Zero ? null : Marshal.PtrToStringAnsi(p); }
}
"@
Add-Type -TypeDefinition $src
$env:PATH = "C:\dev6i\bin;" + $env:PATH
$attr = [Runtime.InteropServices.Marshal]::AllocHGlobal(256)
for ($k = 0; $k -lt 256; $k++) { [Runtime.InteropServices.Marshal]::WriteByte($attr, $k, 0) }
$ctx = [IntPtr]::Zero
$st = [D2F]::d2fctxcr_Create([ref]$ctx, $attr)
"create status=$st ctx=$ctx"
$out = New-Object System.Collections.Generic.List[string]
$out.Add("tipo`tnum`tconst`tnombre`tptype`tvalores")
for ($t = 1; $t -le 200; $t++) {
  $p = [IntPtr]::Zero
  $s = [D2F]::d2fobgcn_GetConstName($ctx, $t, [ref]$p)
  if ($s -eq 0 -and $p -ne [IntPtr]::Zero) { $out.Add("OBJ`t$t`t$([D2F]::S($p))`t`t`t") }
}
for ($n = 1; $n -le 1100; $n++) {
  $p1 = [IntPtr]::Zero; $p2 = [IntPtr]::Zero
  $s1 = [D2F]::d2fprgcn_GetConstName($ctx, $n, [ref]$p1)
  $s2 = [D2F]::d2fprgn_GetName($ctx, $n, [ref]$p2)
  if (($s1 -ne 0 -or $p1 -eq [IntPtr]::Zero) -and ($s2 -ne 0 -or $p2 -eq [IntPtr]::Zero)) { continue }
  $ty = [D2F]::d2fprgt_GetType($ctx, $n)
  $vals = @()
  for ($v = 0; $v -le 40; $v++) {
    $pv = [IntPtr]::Zero
    $sv = [D2F]::d2fprgvn_GetValueName($ctx, $n, $v, [ref]$pv)
    if ($sv -eq 0 -and $pv -ne [IntPtr]::Zero) { $vals += "$v=$([D2F]::S($pv))" }
  }
  $out.Add("PROP`t$n`t$([D2F]::S($p1))`t$([D2F]::S($p2))`t$ty`t$($vals -join ';')")
}
[IO.File]::WriteAllLines($Salida, $out)
"lineas: $($out.Count)"
