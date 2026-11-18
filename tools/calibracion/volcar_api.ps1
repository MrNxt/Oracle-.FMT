# Calibración - volcado de un módulo Forms 6i (.FMB / .MMB) con la Open API, SOLO LECTURA.
#
# Carga el módulo con d2ffmdld_Load / d2fmmdld_Load y recorre todos sus objetos escribiendo, por
# cada propiedad que el objeto tiene, su valor y si es el valor por defecto. NUNCA llama a funciones
# Save/Set/Create sobre el módulo: el archivo binario no se modifica.
#
# Requiere PowerShell de 32 bits (ifd2f60.dll es de 32 bits) y Forms 6i instalado (C:\dev6i\bin).
# Uso:
#   C:\Windows\SysWOW64\WindowsPowerShell\v1.0\powershell.exe -NoProfile -ExecutionPolicy Bypass `
#       -File volcar_api.ps1 -Modulo <ruta .FMB|.MMB> -Salida <ruta .tsv> [-OracleBin C:\dev6i\bin]
#
# Formato de salida (TSV, UTF-8), una línea por propiedad:
#   O <tab> id <tab> id_dueño <tab> tipo_num <tab> tipo_const <tab> nombre          (línea de objeto)
#   P <tab> id <tab> pnum <tab> const <tab> tipo_prop <tab> es_default <tab> valor  (línea de propiedad)
# Los valores de texto escapan \ como \\, tab como \t, salto de línea como \n y CR como \r.
# Las propiedades de tipo objeto se escriben como @TIPO:NOMBRE#id.
param(
    [Parameter(Mandatory = $true)][string]$Modulo,
    [Parameter(Mandatory = $true)][string]$Salida,
    [string]$OracleBin = "C:\dev6i\bin"
)
$ErrorActionPreference = "Stop"
if ([IntPtr]::Size -ne 4) { throw "Este script debe ejecutarse con PowerShell de 32 bits (SysWOW64)." }
$env:PATH = "$OracleBin;" + $env:PATH

$src = @"
using System;
using System.IO;
using System.Text;
using System.Collections.Generic;
using System.Runtime.InteropServices;
using System.Runtime.ExceptionServices;
using System.Security;

public static class VolcadoApi {
    const CallingConvention C = CallingConvention.Cdecl;
    const string D = "ifd2f60.dll";
    [DllImport(D, CallingConvention = C)] static extern int d2fctxcr_Create(out IntPtr ctx, IntPtr attr);
    [DllImport(D, CallingConvention = C)] static extern int d2ffmdld_Load(IntPtr ctx, out IntPtr m, string f, int fromDb);
    [DllImport(D, CallingConvention = C)] static extern int d2fmmdld_Load(IntPtr ctx, out IntPtr m, string f, int fromDb);
    [DllImport(D, CallingConvention = C)] static extern int d2fprgcn_GetConstName(IntPtr ctx, int p, out IntPtr n);
    [DllImport(D, CallingConvention = C)] static extern int d2fprgt_GetType(IntPtr ctx, int p);
    [DllImport(D, CallingConvention = C)] static extern int d2fobqt_QueryType(IntPtr ctx, IntPtr o, out int t);
    [DllImport(D, CallingConvention = C)] static extern int d2fobgcn_GetConstName(IntPtr ctx, int t, out IntPtr n);
    [DllImport(D, CallingConvention = C)] static extern int d2fobhp_HasProp(IntPtr ctx, IntPtr o, int p);
    [DllImport(D, CallingConvention = C)] static extern int d2fobid_IspropDefault(IntPtr ctx, IntPtr o, int p);
    [DllImport(D, CallingConvention = C)] static extern int d2fobgt_GetTextProp(IntPtr ctx, IntPtr o, int p, out IntPtr v);
    [DllImport(D, CallingConvention = C)] static extern int d2fobgn_GetNumProp(IntPtr ctx, IntPtr o, int p, out int v);
    [DllImport(D, CallingConvention = C)] static extern int d2fobgb_GetBoolProp(IntPtr ctx, IntPtr o, int p, out int v);
    [DllImport(D, CallingConvention = C)] static extern int d2fobgo_GetObjProp(IntPtr ctx, IntPtr o, int p, out IntPtr v);

    const int P_NAME = 300, P_NEXT = 302, P_OWNER = 326, P_PREVIOUS = 350, MAX_PROP = 550;

    static IntPtr ctx;
    static int[] tipos = new int[MAX_PROP + 1];
    static string[] consts = new string[MAX_PROP + 1];
    static Dictionary<long, int> ids = new Dictionary<long, int>();
    static Queue<IntPtr> cola = new Queue<IntPtr>();
    static Dictionary<long, int> dueno = new Dictionary<long, int>();
    public static List<string> Diagnostico = new List<string>();
    public static int Fallos = 0;

    static string Esc(string s) {
        if (s == null) return "";
        return s.Replace("\\", "\\\\").Replace("\t", "\\t").Replace("\n", "\\n").Replace("\r", "\\r");
    }
    static string Str(IntPtr p) { return p == IntPtr.Zero ? null : Marshal.PtrToStringAnsi(p); }

    [HandleProcessCorruptedStateExceptions, SecurityCritical]
    static int Llamar(Func<int> f, out bool fallo) {
        try { fallo = false; return f(); } catch (Exception) { fallo = true; Fallos++; return -1; }
    }

    [HandleProcessCorruptedStateExceptions, SecurityCritical]
    static string Texto(IntPtr o, int p) {
        try { IntPtr v; int st = d2fobgt_GetTextProp(ctx, o, p, out v); return st == 0 ? Str(v) : null; }
        catch (Exception) { Fallos++; return null; }
    }
    [HandleProcessCorruptedStateExceptions, SecurityCritical]
    static IntPtr Obj(IntPtr o, int p) {
        try { IntPtr v; int st = d2fobgo_GetObjProp(ctx, o, p, out v); return st == 0 ? v : IntPtr.Zero; }
        catch (Exception) { Fallos++; return IntPtr.Zero; }
    }
    [HandleProcessCorruptedStateExceptions, SecurityCritical]
    static int Tipo(IntPtr o) {
        try { int t; return d2fobqt_QueryType(ctx, o, out t) == 0 ? t : -1; } catch (Exception) { Fallos++; return -1; }
    }
    static string TipoConst(int t) {
        try { IntPtr n; return d2fobgcn_GetConstName(ctx, t, out n) == 0 ? Str(n) : "?"; } catch (Exception) { return "?"; }
    }

    static int Id(IntPtr o) {
        long k = o.ToInt64();
        int id;
        if (!ids.TryGetValue(k, out id)) { id = ids.Count + 1; ids[k] = id; cola.Enqueue(o); }
        return id;
    }

    public static int Volcar(string modulo, string salida, bool esMenu, out string error) {
        error = null;
        IntPtr attr = Marshal.AllocHGlobal(256);
        for (int i = 0; i < 256; i++) Marshal.WriteByte(attr, i, 0);
        if (d2fctxcr_Create(out ctx, attr) != 0) { error = "no se pudo crear el contexto"; return 1; }
        for (int p = 1; p <= MAX_PROP; p++) {
            tipos[p] = d2fprgt_GetType(ctx, p);
            IntPtr n; consts[p] = d2fprgcn_GetConstName(ctx, p, out n) == 0 ? Str(n) : null;
        }
        IntPtr mod;
        int st = esMenu ? d2fmmdld_Load(ctx, out mod, modulo, 0) : d2ffmdld_Load(ctx, out mod, modulo, 0);
        if (st != 0) { error = "Load devolvió " + st; return 2; }

        // Diagnóstico de códigos de retorno de HasProp / IspropDefault.
        Diagnostico.Add("HasProp(modulo,NAME)=" + d2fobhp_HasProp(ctx, mod, P_NAME));
        Diagnostico.Add("IspropDefault(modulo,NAME)=" + d2fobid_IspropDefault(ctx, mod, P_NAME));
        int YES = d2fobhp_HasProp(ctx, mod, P_NAME);

        using (var w = new StreamWriter(salida, false, new UTF8Encoding(false))) {
            Id(mod);
            dueno[mod.ToInt64()] = 0;
            while (cola.Count > 0) {
                IntPtr o = cola.Dequeue();
                int id = ids[o.ToInt64()];
                int t = Tipo(o);
                int idDueno; dueno.TryGetValue(o.ToInt64(), out idDueno);
                w.WriteLine("O\t" + id + "\t" + idDueno + "\t" + t + "\t" + TipoConst(t) + "\t" + Esc(Texto(o, P_NAME)));
                for (int p = 1; p <= MAX_PROP; p++) {
                    int tp = tipos[p];
                    if (tp < 1 || tp > 4) continue;
                    bool f;
                    IntPtr oo = o; int pp = p;
                    int hp = Llamar(() => d2fobhp_HasProp(ctx, oo, pp), out f);
                    if (f || hp != YES) continue;
                    int idf = Llamar(() => d2fobid_IspropDefault(ctx, oo, pp), out f);
                    string esDef = f ? "?" : (idf == YES ? "1" : "0");
                    string val = null;
                    if (tp == 1) {
                        int v = 0; int r = Llamar(() => { int x; int s = d2fobgb_GetBoolProp(ctx, oo, pp, out x); v = x; return s; }, out f);
                        if (!f && r == 0) val = v != 0 ? "1" : "0";
                    } else if (tp == 2) {
                        int v = 0; int r = Llamar(() => { int x; int s = d2fobgn_GetNumProp(ctx, oo, pp, out x); v = x; return s; }, out f);
                        if (!f && r == 0) val = v.ToString();
                    } else if (tp == 3) {
                        val = Texto(o, p);
                    } else {
                        IntPtr r = Obj(o, p);
                        if (r != IntPtr.Zero) {
                            // Cabeza de lista de hijos: el referido es de este objeto y no tiene anterior.
                            bool esHijo = p != P_NEXT && p != P_PREVIOUS && p != P_OWNER
                                && Obj(r, P_OWNER) == o && Obj(r, P_PREVIOUS) == IntPtr.Zero;
                            if (esHijo) {
                                IntPtr h = r; int guarda = 0;
                                while (h != IntPtr.Zero && guarda++ < 100000) {
                                    if (!ids.ContainsKey(h.ToInt64())) dueno[h.ToInt64()] = id;
                                    Id(h);
                                    h = Obj(h, P_NEXT);
                                }
                            }
                            int tr = Tipo(r);
                            val = "@" + TipoConst(tr) + ":" + (Texto(r, P_NAME) ?? "") + "#" + Id(r);
                            if (!dueno.ContainsKey(r.ToInt64())) {
                                IntPtr ow = Obj(r, P_OWNER);
                                int idOw; dueno[r.ToInt64()] = ow != IntPtr.Zero && ids.TryGetValue(ow.ToInt64(), out idOw) ? idOw : 0;
                            }
                        }
                    }
                    if (val == null) continue;
                    w.WriteLine("P\t" + id + "\t" + p + "\t" + consts[p] + "\t" + tp + "\t" + esDef + "\t" + Esc(val));
                }
            }
        }
        return 0;
    }
}
"@
Add-Type -TypeDefinition $src -Language CSharp

$ext = [IO.Path]::GetExtension($Modulo).ToLower()
$esMenu = $ext -eq ".mmb"
$err = $null
$rc = [VolcadoApi]::Volcar((Resolve-Path $Modulo).Path, $Salida, $esMenu, [ref]$err)
[VolcadoApi]::Diagnostico | ForEach-Object { "diag: $_" }
"llamadas fallidas atrapadas: $([VolcadoApi]::Fallos)"
if ($rc -ne 0) { "ERROR: $err"; exit $rc }
"volcado OK -> $Salida"
