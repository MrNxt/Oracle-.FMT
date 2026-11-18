"""Calibración del diccionario ROS: número de propiedad del .fmt/.mmt -> propiedad oficial de Forms.

Entrada: pares (archivo ROS .fmt/.mmt, volcado TSV de la Open API del mismo módulo, hecho con
volcar_api.ps1 en modo sólo lectura). Salida:
  * config/diccionario_ros.yaml              diccionario que usa forms2apex (editable a mano)
  * tools/calibracion/reporte_calibracion.md cobertura, ambigüedades y números sin mapear

Método
------
1. Tipos: cada tipo de objeto ROS se asocia al tipo de la API con más rutas de nombres en común
   (ruta = nombres desde el objeto de primer nivel siguiendo los dueños). Los empates (p. ej. un
   LOV y su record group con el mismo nombre) se resuelven por coincidencia de valores.
2. Objetos: se emparejan por (tipo, ruta).
3. Propiedades, por (número ROS, tipo de objeto ROS). Para cada propiedad candidata de la API:
     - acierto: el valor ROS coincide con el de la API (booleano, número, texto, referencia a objeto
                por nombre, o código PL/SQL normalizado); también se prueban booleanos invertidos;
     - no_def:  donde el ROS la tiene, la API dice que NO es el valor por defecto;
     - def_aus: donde el ROS NO la tiene, la API dice que SÍ es el valor por defecto.
   El ROS sólo graba valores distintos del default, así que la propiedad correcta maximiza las tres.
   Empates: se prefiere la variante de texto (…_NAM) si la propiedad ROS es texto.
   Dentro de un tipo de objeto, cada constante se asigna a un solo número ROS (el de mejor puntaje).
4. Si todos los tipos de objeto de un número coinciden en la constante, la entrada es global;
   si no, se guarda ``por_tipo`` (p. ej. 464 = TRG_TXT en triggers, PGU_TXT en program units).
5. Defaults: valor que informa la API en los objetos donde el ROS no grabó la propiedad.

Uso:
    .venv/Scripts/python.exe tools/calibracion/calibrar.py \\
        samples/STKC007.fmt tools/calibracion/volcados/STKC007.api.tsv \\
        samples/fini018.fmt tools/calibracion/volcados/fini018.api.tsv ...
"""

from __future__ import annotations

import argparse
import collections
import datetime as dt
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "src"))

import yaml  # noqa: E402

from forms2apex.parser.plsql_blob import extraer  # noqa: E402
from forms2apex.parser.ros_arbol import ArbolRos, PropRos, leer_arbol  # noqa: E402

UMBRAL_ACIERTO = 0.9
TIPOS_PROP_API = {1: "booleano", 2: "numero", 3: "texto", 4: "objeto"}

# Propiedades que la herramienta necesita (para el reporte de cobertura), por tipo de objeto de la API.
IMPRESCINDIBLES: dict[str, list[str]] = {
    "FORM_MODULE": ["NAME", "TITLE", "FRST_NAVIGATION_BLK_NAM", "MNU_MOD", "CONSOLE_WIN"],
    "BLOCK": ["NAME", "DB_BLK", "QRY_DAT_SRC_TYP", "QRY_DAT_SRC_NAM", "WHERE_CLAUSE", "ORDR_BY_CLAUSE",
              "RECS_DISP_COUNT", "INSRT_ALLOWED", "UPDT_ALLOWED", "DEL_ALLOWED", "QRY_ALLOWED",
              "DML_DAT_TYP", "DML_DAT_NAM", "NXT_NAVIGATION_BLK_NAM", "PREV_NAVIGATION_BLK_NAM"],
    "ITEM": ["NAME", "ITM_TYP", "DAT_TYP", "MAX_LEN", "REQUIRED", "DB_ITM", "COL_NAM", "INIT_VAL",
             "LOV_NAM", "CNV_NAM", "VISIBLE", "ENABLED", "PRMPT", "LABEL", "FMT_MSK", "COPY_VAL_FROM_ITM",
             "CALC_MODE", "FORMULA", "HINT", "INSRT_ALLOWED", "UPDT_ALLOWED", "QRY_ALLOWED",
             "CHKED_VAL", "UNCHKED_VAL", "PRMRY_KEY"],
    "RELATION": ["NAME", "DETAIL_BLK", "JOIN_COND", "DEL_REC"],
    "LOV": ["NAME", "TITLE", "REC_GRP_NAM"],
    "LV_COLMAP": ["NAME", "TITLE", "RTRN_ITM"],
    "REC_GROUP": ["NAME", "REC_GRP_QRY", "REC_GRP_TYP"],
    "ALERT": ["NAME", "ALT_MSG", "ALT_STY", "BTN_1_LBL", "BTN_2_LBL", "BTN_3_LBL"],
    "FORM_PARAM": ["NAME", "PARAM_DAT_TYP", "PARAM_INIT_VAL", "MAX_LEN"],
    "TRIGGER": ["NAME", "TRG_TXT", "TRG_STY"],
    "PROG_UNIT": ["NAME", "PGU_TXT", "PGU_TYP"],
    "ATT_LIB": ["NAME", "LIB_LOC", "LIB_SRC"],
    "WINDOW": ["NAME", "TITLE", "PRMRY_CNV"],
    "CANVAS": ["NAME", "CNV_TYP", "WND_NAM"],
    "MENU": ["NAME"],
    "MENU_ITEM": ["NAME", "LABEL", "MNU_ITM_TYP", "SUB_MNU_NAM", "MNU_ITM_CODE", "COM_TYP"],
}


# ----------------------------------------------------------------------------- volcado de la API
@dataclass
class ObjApi:
    id: int
    dueno: int
    tipo: str
    nombre: str
    props: dict[str, tuple[int, int, str, str]] = field(default_factory=dict)  # const -> (pnum, ptipo, esdef, valor)


def _desescapar(s: str) -> str:
    return re.sub(r"\\(.)", lambda m: {"t": "\t", "n": "\n", "r": "\r", "\\": "\\"}.get(m.group(1), m.group(1)), s)


def leer_volcado(ruta: Path) -> dict[int, ObjApi]:
    objs: dict[int, ObjApi] = {}
    for linea in ruta.read_text(encoding="utf-8").split("\n"):
        if not linea:
            continue
        c = linea.split("\t")
        if c[0] == "O":
            objs[int(c[1])] = ObjApi(int(c[1]), int(c[2]), c[4], _desescapar(c[5]))
        elif c[0] == "P":
            objs[int(c[1])].props[c[3]] = (int(c[2]), int(c[4]), c[5], _desescapar(c[6]))
    return objs


def ruta_api(objs: dict[int, ObjApi], o: ObjApi) -> tuple[str, ...]:
    partes: list[str] = []
    actual: ObjApi | None = o
    vistos: set[int] = set()
    while actual is not None and actual.id not in vistos and actual.dueno != 0:
        vistos.add(actual.id)
        partes.append(actual.nombre)
        actual = objs.get(actual.dueno)
    return tuple(reversed(partes))


# ----------------------------------------------------------------------------- comparación
def _norm_codigo(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip().upper()


def valor_comparable(arbol: ArbolRos, prop: PropRos) -> tuple[str, str] | None:
    """(clase de comparación, valor normalizado) o None si no es comparable."""
    v = prop.valor
    if v is None:
        return None
    if prop.clase in ("N", "B", "T"):
        return (prop.clase, str(v))
    if prop.clase == "O":
        nodo = arbol.nodos.get(v) if isinstance(v, int) else None
        if nodo is not None and nodo.es_lista:
            nodo = nodo.hijos[0] if nodo.hijos else None
        return ("O", nodo.nombre) if nodo is not None else None
    if prop.clase in ("P", "S") and isinstance(v, bytes):
        r = extraer(v)
        if r.tipo in ("trigger", "unidad", "formula"):
            return ("C", _norm_codigo(r.texto))
    return None


def coincide(cmp: tuple[str, str], api: tuple[int, int, str, str]) -> tuple[bool, bool]:
    """(coincide, coincide_invertido)."""
    clase, v = cmp
    _, ptipo, _, a = api
    if clase == "B" and ptipo == 1:
        return v == a, (v in ("0", "1") and a in ("0", "1") and v != a)
    if clase == "N" and ptipo == 2:
        return v == a, False
    if clase in ("T", "O") and ptipo == 3:
        return v == a, False
    if clase in ("T", "O") and ptipo == 4:
        m = re.match(r"@[^:]*:(.*)#\d+$", a)
        return (m is not None and m.group(1) == v), False
    if clase == "C" and ptipo == 3:
        return _norm_codigo(a) == v, False
    return False, False


# ----------------------------------------------------------------------------- emparejamiento
def emparejar_tipos(arbol: ArbolRos, objs: dict[int, ObjApi]) -> dict[int, str]:
    por_ruta_api: dict[tuple[str, tuple], ObjApi] = {}
    rutas_api: dict[str, set] = collections.defaultdict(set)
    for o in objs.values():
        if o.nombre and o.dueno != 0:
            r = ruta_api(objs, o)
            rutas_api[o.tipo].add(r)
            por_ruta_api[(o.tipo, r)] = o
    nodos_por_tipo: dict[int, list] = collections.defaultdict(list)
    for n in arbol.objetos():
        if n.nombre and n is not arbol.raiz:
            nodos_por_tipo[n.tipo].append(n)

    res: dict[int, str] = {}
    for t, nodos in nodos_por_tipo.items():
        rs = {arbol.ruta_nombres(n) for n in nodos}
        puntajes = []
        for a, ras in rutas_api.items():
            solap = len(rs & ras)
            if solap < max(1, len(rs) // 2):
                continue
            # desempate: cuántos valores escalares ROS aparecen entre los valores del objeto API
            hits = 0
            for n in nodos[:40]:
                o = por_ruta_api.get((a, arbol.ruta_nombres(n)))
                if o is None:
                    continue
                vals_api = {v[3] for v in o.props.values()}
                hits += sum(1 for p in n.props if p.clase in ("N", "T", "B") and p.numero != 211
                            and p.valor not in (None, "") and str(p.valor) in vals_api)
            puntajes.append((solap, hits, a))
        if puntajes:
            res[t] = max(puntajes)[2]
    if arbol.raiz is not None:
        raiz_api = next((o for o in objs.values() if o.dueno == 0), None)
        if raiz_api:
            res[arbol.raiz.tipo] = raiz_api.tipo
    return res


# ----------------------------------------------------------------------------- estadística
@dataclass
class Est:
    total: int = 0
    aciertos: collections.Counter = field(default_factory=collections.Counter)
    invertidos: collections.Counter = field(default_factory=collections.Counter)
    no_def: collections.Counter = field(default_factory=collections.Counter)
    aus_total: collections.Counter = field(default_factory=collections.Counter)
    aus_def: collections.Counter = field(default_factory=collections.Counter)
    clase: collections.Counter = field(default_factory=collections.Counter)
    ejemplos: list = field(default_factory=list)


@dataclass
class Candidato:
    const: str
    invertido: bool
    puntaje: tuple[float, float, float, int]  # (acierto, no_def, def_aus, preferencia de tipo)


def candidatos(est: Est, info_api: dict[str, tuple[int, int]]) -> list[Candidato]:
    if est.total == 0:
        return []
    clase = est.clase.most_common(1)[0][0]
    res = []
    for k in set(est.aciertos) | set(est.invertidos):
        for inv, cnt in ((False, est.aciertos[k]), (True, est.invertidos[k])):
            if cnt == 0 or cnt / est.total < UMBRAL_ACIERTO:
                continue
            no_def = 0.0 if inv else est.no_def[k] / cnt
            aus = est.aus_def[k] / est.aus_total[k] if est.aus_total[k] else 0.5
            ptipo = info_api.get(k, (0, 0))[1]
            pref = 1 if (clase == "T" and ptipo == 3) or (clase in ("N", "B") and ptipo in (1, 2)) else 0
            res.append(Candidato(k, inv, (round(cnt / est.total, 3), round(no_def, 3), round(aus, 3), pref - int(inv))))
    res.sort(key=lambda c: c.puntaje, reverse=True)
    return res


def calibrar(pares: list[tuple[Path, Path]]):
    est: dict[tuple[int, int], Est] = collections.defaultdict(Est)  # (num, tipo ROS)
    tipos: dict[int, collections.Counter] = collections.defaultdict(collections.Counter)
    nombres_tipo: dict[int, set] = collections.defaultdict(set)
    alineados_tipo: collections.Counter = collections.Counter()
    defaults: dict[tuple[int, str], collections.Counter] = collections.defaultdict(collections.Counter)
    info_api: dict[str, tuple[int, int]] = {}
    sin_par: collections.Counter = collections.Counter()
    alineados: list[tuple[int, set[int], dict]] = []
    modulos: list[str] = []

    for ruta_ros, ruta_tsv in pares:
        arbol = leer_arbol(ruta_ros)
        objs = leer_volcado(ruta_tsv)
        modulos.append(ruta_ros.name)
        mapa = emparejar_tipos(arbol, objs)
        for t, a in mapa.items():
            tipos[t][a] += 1
        indice: dict[tuple, list[ObjApi]] = collections.defaultdict(list)
        for o in objs.values():
            indice[(o.tipo, ruta_api(objs, o) if o.dueno != 0 else ())].append(o)
            for k, (pn, pt, _, _) in o.props.items():
                info_api[k] = (pn, pt)

        for n in arbol.objetos():
            if n.es_lista and n is not arbol.raiz:
                continue
            nombres_tipo[n.tipo].add(n.nombre)
            a = mapa.get(n.tipo)
            cand = indice.get((a, () if n is arbol.raiz else arbol.ruta_nombres(n)), []) if a else []
            par = cand[0] if len(cand) == 1 else None
            if par is None:
                for p in n.props:
                    sin_par[(p.numero, n.tipo)] += 1
                continue
            alineados_tipo[n.tipo] += 1
            presentes: set[int] = set()
            for p in n.props:
                e = est[(p.numero, n.tipo)]
                e.clase[p.clase] += 1
                if len(e.ejemplos) < 3 and p.valor is not None:
                    v = f"<binario {len(p.valor)} b>" if isinstance(p.valor, bytes) else str(p.valor)
                    e.ejemplos.append(f"{n.nombre}: {v[:50]}")
                cmp = valor_comparable(arbol, p)
                if cmp is None:
                    continue
                e.total += 1
                presentes.add(p.numero)
                for k, api in par.props.items():
                    ok, inv = coincide(cmp, api)
                    if ok:
                        e.aciertos[k] += 1
                        if api[2] == "0":
                            e.no_def[k] += 1
                    if inv:
                        e.invertidos[k] += 1
            alineados.append((n.tipo, presentes, par.props))
            for k, (_, _, esdef, val) in par.props.items():
                if esdef == "1":
                    defaults[(n.tipo, k)][val] += 1

    # Segunda pasada: ausencias (objetos del mismo tipo donde el ROS no grabó la propiedad).
    por_tipo: dict[int, list] = collections.defaultdict(list)
    for t, pres, props in alineados:
        por_tipo[t].append((pres, props))
    for (num, t), e in est.items():
        cands = set(e.aciertos) | set(e.invertidos)
        for pres, props in por_tipo[t]:
            if num in pres:
                continue
            for k in cands:
                if k in props:
                    e.aus_total[k] += 1
                    if props[k][2] == "1":
                        e.aus_def[k] += 1
    return est, tipos, nombres_tipo, alineados_tipo, defaults, info_api, sin_par, modulos


def asignar(est: dict[tuple[int, int], Est], info_api) -> dict[tuple[int, int], tuple[Candidato, list[Candidato], str]]:
    """Elige una constante por (num, tipo) evitando que una constante quede en dos números del mismo tipo.

    Empates: se prefiere la constante que ese mismo número ROS tiene en otros tipos de objeto
    (la numeración ROS es global salvo excepciones como la 464)."""
    todos = {clave: candidatos(e, info_api) for clave, e in est.items()}
    votos: dict[int, collections.Counter] = collections.defaultdict(collections.Counter)
    for (num, _), cs in todos.items():
        if cs:
            votos[num][cs[0].const] += 1
    for (num, _), cs in todos.items():
        cs.sort(key=lambda c: (c.puntaje, votos[num][c.const]), reverse=True)
    res = {}
    ocupadas: set[tuple[int, str]] = set()  # (tipo, const)
    orden = sorted((c for c in todos if todos[c]), key=lambda c: (todos[c][0].puntaje, est[c].total), reverse=True)
    for clave in orden:
        num, t = clave
        libres = [c for c in todos[clave] if (t, c.const) not in ocupadas]
        if not libres:
            continue
        el = libres[0]
        empatados = [c for c in libres if c.puntaje[:3] == el.puntaje[:3]
                     and votos[num][c.const] == votos[num][el.const]]
        acierto, no_def, _, _ = el.puntaje
        if no_def < 0.5 and not el.invertido:
            conf = "baja"  # la API dice que el valor grabado es el default: no cuadra con el ROS
        elif len(empatados) == 1 and acierto == 1.0 and no_def >= 0.9 and est[clave].total >= 3:
            conf = "alta"
        elif len(empatados) == 1:
            conf = "media"
        else:
            conf = "baja"
        ocupadas.add((t, el.const))
        res[clave] = (el, [c for c in libres[1:4]], conf)
    return res


# ----------------------------------------------------------------------------- salida
def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("archivos", nargs="+", help="pares: <ros> <volcado.tsv> ...")
    ap.add_argument("--diccionario-api", default=str(RAIZ / "tools/exploracion/d2f_dict.tsv"))
    ap.add_argument("--salida", default=str(RAIZ / "config/diccionario_ros.yaml"))
    ap.add_argument("--reporte", default=str(RAIZ / "tools/calibracion/reporte_calibracion.md"))
    a = ap.parse_args()
    if len(a.archivos) % 2:
        ap.error("los archivos van de a pares: <ros> <volcado.tsv>")
    pares = [(Path(a.archivos[i]), Path(a.archivos[i + 1])) for i in range(0, len(a.archivos), 2)]

    nombres_es: dict[str, str] = {}
    if Path(a.diccionario_api).exists():
        for ln in Path(a.diccionario_api).read_text(encoding="utf-8-sig").splitlines():
            c = ln.split("\t")
            if len(c) >= 3 and c[2] != "<null>":
                nombres_es[c[1]] = c[2]

    est, tipos, nombres_tipo, alineados_tipo, defaults, info_api, sin_par, modulos = calibrar(pares)
    asig = asignar(est, info_api)

    tipos_yaml = {}
    for t in sorted(nombres_tipo):
        if tipos.get(t):
            tipos_yaml[t] = {"const": tipos[t].most_common(1)[0][0], "alineados": alineados_tipo.get(t, 0),
                             "ejemplos": sorted(x for x in nombres_tipo[t] if x)[:3]}
    tipo_api = {t: v["const"] for t, v in tipos_yaml.items()}

    def entrada(num: int, t: int) -> dict:
        el, alts, conf = asig[(num, t)]
        e = est[(num, t)]
        d = {"const": el.const, "nombre": nombres_es.get(el.const, ""),
             "tipo_api": TIPOS_PROP_API.get(info_api.get(el.const, (0, 0))[1], "?"),
             "confianza": conf, "muestras": e.total, "acierto": el.puntaje[0]}
        if el.invertido:
            d["invertido"] = True
        if defaults.get((t, el.const)):
            dv = defaults[(t, el.const)].most_common(1)[0][0]
            # Sólo tiene sentido un default escalar (no código ni textos largos heredados).
            if d["tipo_api"] in ("booleano", "numero") or (d["tipo_api"] == "texto" and len(dv) <= 60 and "\n" not in dv):
                d["default"] = dv
        if alts:
            d["alternativas"] = [c.const + (" (invertido)" if c.invertido else "") for c in alts]
        return d

    numeros = sorted({num for num, _ in est})
    props_yaml: dict[int, dict] = {}
    sin_mapear = []
    for num in numeros:
        tipos_num = sorted(t for (n, t) in est if n == num)
        mapeados = [t for t in tipos_num if (num, t) in asig]
        clase = collections.Counter()
        for t in tipos_num:
            clase.update(est[(num, t)].clase)
        if not mapeados:
            ej = [x for t in tipos_num for x in est[(num, t)].ejemplos][:3]
            sin_mapear.append((num, clase.most_common(1)[0][0] if clase else "?", tipos_num, ej))
            continue
        entradas = {t: entrada(num, t) for t in mapeados}
        consts = {v["const"] for v in entradas.values()}
        bloque: dict = {"clase_ros": clase.most_common(1)[0][0]}
        if len(consts) == 1:
            base = next(iter(entradas.values()))
            bloque.update({k: v for k, v in base.items() if k not in ("default", "muestras", "acierto", "confianza")})
            bloque["confianza"] = min((v["confianza"] for v in entradas.values()), key=["alta", "media", "baja"].index)
            bloque["muestras"] = sum(v["muestras"] for v in entradas.values())
            dfl = {t: v["default"] for t, v in entradas.items() if "default" in v}
            if dfl:
                bloque["defaults"] = dfl
            bloque["tipos_objeto"] = mapeados
        else:
            bloque["por_tipo"] = entradas
        sin_tipo = [t for t in tipos_num if t not in mapeados]
        if sin_tipo:
            bloque["tipos_sin_mapear"] = sin_tipo
        props_yaml[num] = bloque

    # Ajustes manuales (sobreviven a cada recalibración).
    ajustes_path = Path(__file__).with_name("ajustes_manuales.yaml")
    ajustes = yaml.safe_load(ajustes_path.read_text(encoding="utf-8")) if ajustes_path.exists() else {}
    clase_de: dict[int, collections.Counter] = collections.defaultdict(collections.Counter)
    for (n, _), e in est.items():
        clase_de[n].update(e.clase)
    for num, aj in (ajustes or {}).items():
        cl = clase_de[int(num)].most_common(1)[0][0] if clase_de[int(num)] else "?"
        props_yaml[int(num)] = {"clase_ros": cl, **aj}
        sin_mapear = [s for s in sin_mapear if s[0] != int(num)]
        for t in aj.get("tipos_objeto", []):
            asig.setdefault((int(num), t), (Candidato(aj["const"], False, (1.0, 1.0, 1.0, 0)), [], "manual"))
    props_yaml = dict(sorted(props_yaml.items()))

    salida = {
        "generado": {
            "por": "tools/calibracion/calibrar.py",
            "fecha": dt.date.today().isoformat(),
            "modulos": modulos,
            "nota": ("Número de propiedad ROS -> propiedad oficial de Forms 6i. Editable a mano. "
                     "'defaults' = valor que asume Forms cuando la propiedad no está grabada en el .fmt, "
                     "por número de tipo de objeto ROS. 'por_tipo' = el mismo número significa cosas "
                     "distintas según el tipo de objeto."),
        },
        "tipos_objeto": tipos_yaml,
        "propiedades": props_yaml,
    }
    Path(a.salida).parent.mkdir(parents=True, exist_ok=True)
    Path(a.salida).write_text(
        "# Generado por la calibración (etapa 0). Ver tools/calibracion/reporte_calibracion.md\n"
        + yaml.safe_dump(salida, allow_unicode=True, sort_keys=False, width=120), encoding="utf-8")

    # ------------------------------------------------------------------ reporte
    conf = collections.Counter(v[2] for v in asig.values())
    L = [f"# Reporte de calibración del diccionario ROS ({dt.date.today().isoformat()})", "",
         f"Módulos: {', '.join(modulos)}", "", "## Resumen", "",
         f"- Números de propiedad ROS encontrados: **{len(numeros)}**",
         f"- Mapeados: **{len(props_yaml)}**; pares (número, tipo de objeto) mapeados: {len(asig)} "
         f"(alta {conf['alta']}, media {conf['media']}, baja {conf['baja']})",
         f"- Con significado distinto según el tipo de objeto: **{sum(1 for v in props_yaml.values() if 'por_tipo' in v)}**",
         f"- Sin mapear: **{len(sin_mapear)}**", "",
         "## Tipos de objeto", "", "| Tipo ROS | Tipo API | Objetos alineados | Ejemplos |", "|---|---|---|---|"]
    for t, v in tipos_yaml.items():
        L.append(f"| {t} | {v['const']} | {v['alineados']} | {', '.join(v['ejemplos'])} |")

    por_tipo_const: dict[tuple[str, str], list] = collections.defaultdict(list)
    for (num, t), (el, _, cf) in asig.items():
        por_tipo_const[(tipo_api.get(t, "?"), el.const)].append((num, cf, el.invertido))
    L += ["", "## Cobertura de propiedades imprescindibles", "",
          "| Objeto | Propiedad | Nº ROS | Confianza |", "|---|---|---|---|"]
    faltan = []
    for ta, consts in IMPRESCINDIBLES.items():
        for k in consts:
            hit = por_tipo_const.get((ta, k))
            if hit:
                L.append(f"| {ta} | {k} | {', '.join(str(h[0]) + (' (inv.)' if h[2] else '') for h in hit)} "
                         f"| {', '.join(h[1] for h in hit)} |")
            else:
                faltan.append((ta, k))
                L.append(f"| {ta} | {k} | — | **sin evidencia** |")
    L += ["", f"Imprescindibles sin evidencia: **{len(faltan)}**. Significa que en ningún objeto de las "
          "muestras esa propiedad tiene un valor distinto del default, así que no aparece grabada en el "
          ".fmt. El parser asumirá el default de Forms y lo registrará; conviene calibrar con un módulo "
          "que la use.", ""]

    L += ["## Mapeos con confianza media o baja", "",
          "| Nº | Tipo ROS | Const | Muestras | Acierto / no-def / def-aus | Alternativas |", "|---|---|---|---|---|---|"]
    for (num, t), (el, alts, cf) in sorted(asig.items()):
        if cf != "alta":
            p = el.puntaje
            L.append(f"| {num} | {t} ({tipo_api.get(t, '?')}) | {el.const}{' (inv.)' if el.invertido else ''} "
                     f"| {est[(num, t)].total} | {p[0]} / {p[1]} / {p[2]} | {', '.join(c.const for c in alts)} |")
    L += ["", "## Números ROS sin mapear", "", "| Nº | Clase | Tipos ROS | Ejemplos |", "|---|---|---|---|"]
    for num, clase, ts, ej in sin_mapear:
        L.append(f"| {num} | {clase} | {', '.join(map(str, ts))} | {'; '.join(ej)[:110]} |")
    Path(a.reporte).write_text("\n".join(L) + "\n", encoding="utf-8")

    print(f"diccionario: {a.salida}\nreporte:     {a.reporte}")
    print(f"números ROS: {len(numeros)}  mapeados: {len(props_yaml)}  pares (num,tipo): {len(asig)} {dict(conf)}  "
          f"sin mapear: {len(sin_mapear)}  imprescindibles sin evidencia: {len(faltan)}")
    if faltan:
        print("  sin evidencia:", ", ".join(f"{t}.{k}" for t, k in faltan))


if __name__ == "__main__":
    main()
