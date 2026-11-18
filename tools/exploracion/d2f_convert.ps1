# Convierte un módulo binario <-> texto con la Open API de Forms 6i (d2fctxcf_ConvertFile).
# Ejecutar con PowerShell x86. Uso: d2f_convert.ps1 -Archivo <ruta> -TipoMod <n> -Direccion <n>
param([string]$Archivo, [int]$TipoMod, [int]$Direccion)
$src = @"
using System;
using System.Runtime.InteropServices;
public static class D2FC {
  [DllImport("ifd2f60.dll", CallingConvention=CallingConvention.Cdecl)] public static extern int d2fctxcr_Create(out IntPtr ctx, IntPtr attr);
  [DllImport("ifd2f60.dll", CallingConvention=CallingConvention.Cdecl)] public static extern int d2fctxcf_ConvertFile(IntPtr ctx, string fname, int modtyp, int direction);
}
"@
Add-Type -TypeDefinition $src
$env:PATH = "C:\dev6i\bin;" + $env:PATH
$attr = [Runtime.InteropServices.Marshal]::AllocHGlobal(256)
for ($k = 0; $k -lt 256; $k++) { [Runtime.InteropServices.Marshal]::WriteByte($attr, $k, 0) }
$ctx = [IntPtr]::Zero
$null = [D2FC]::d2fctxcr_Create([ref]$ctx, $attr)
$st = [D2FC]::d2fctxcf_ConvertFile($ctx, $Archivo, $TipoMod, $Direccion)
"ConvertFile($TipoMod,$Direccion) status=$st"
