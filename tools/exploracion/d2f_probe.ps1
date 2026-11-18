param([string]$Fn, [int]$N = 211)
$src = @"
using System;
using System.Runtime.InteropServices;
public static class D2F {
  [DllImport("ifd2f60.dll", CallingConvention=CallingConvention.Cdecl)] public static extern int d2fctxcr_Create(out IntPtr ctx, IntPtr attr);
  [DllImport("ifd2f60.dll", CallingConvention=CallingConvention.Cdecl)] public static extern int d2fprgn_GetName(IntPtr ctx, int pnum, out IntPtr name);
  [DllImport("ifd2f60.dll", CallingConvention=CallingConvention.Cdecl)] public static extern int d2fprgcn_GetConstName(IntPtr ctx, int pnum, out IntPtr name);
  [DllImport("ifd2f60.dll", CallingConvention=CallingConvention.Cdecl)] public static extern int d2fprgt_GetType(IntPtr ctx, int pnum);
  [DllImport("ifd2f60.dll", CallingConvention=CallingConvention.Cdecl)] public static extern int d2fobgcn_GetConstName(IntPtr ctx, int otyp, out IntPtr name);
  public static string S(IntPtr p) { return p == IntPtr.Zero ? "<null>" : Marshal.PtrToStringAnsi(p); }
}
"@
Add-Type -TypeDefinition $src
$env:PATH = "C:\dev6i\bin;" + $env:PATH
$attr = [Runtime.InteropServices.Marshal]::AllocHGlobal(256)
for ($k = 0; $k -lt 256; $k++) { [Runtime.InteropServices.Marshal]::WriteByte($attr, $k, 0) }
$ctx = [IntPtr]::Zero
$null = [D2F]::d2fctxcr_Create([ref]$ctx, $attr)
$p = [IntPtr]::Zero
switch ($Fn) {
  "name"  { $s = [D2F]::d2fprgn_GetName($ctx, $N, [ref]$p); "$Fn($N) st=$s -> $([D2F]::S($p))" }
  "const" { $s = [D2F]::d2fprgcn_GetConstName($ctx, $N, [ref]$p); "$Fn($N) st=$s -> $([D2F]::S($p))" }
  "type"  { $s = [D2F]::d2fprgt_GetType($ctx, $N); "$Fn($N) -> $s" }
  "obj"   { $s = [D2F]::d2fobgcn_GetConstName($ctx, $N, [ref]$p); "$Fn($N) st=$s -> $([D2F]::S($p))" }
}
