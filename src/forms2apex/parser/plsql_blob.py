"""Extracción del código PL/SQL fuente desde la propiedad binaria 464 (BLONG) de un .fmt / .mmt.

El binario mezcla el texto fuente con el P-code compilado. El texto viaja en fragmentos
``[longitud: 4 bytes big-endian][texto cp1252]``, inmediatamente después de una cabecera
``[00000042][flags][...][N: 4 bytes][N enteros de 4 bytes]``.

Secuencias observadas (STKC007, FINI018, WAPIDEMO):

* Trigger / comando de menú::

      [nombre interno]  [BEGIN\\n]  [cuerpo]  [\\nEND;]  ["NOMBRE-TRIGGER (DUEÑO)" | "MENU.ITEM"]

  Forms envuelve el cuerpo escrito por el usuario con ``BEGIN``/``END;``; se devuelve sólo el cuerpo.

* FORMULA-CALCULATION (ítem calculado por fórmula)::

      [nombre interno]  [BEGIN\\n:BLOQUE.ITEM:=(]  [fórmula]  [);\\nEND;]  [descripción]

* Program unit::

      [nombre]  [fuente completo: PROCEDURE / FUNCTION / PACKAGE [BODY] ...]

  A veces falta el fragmento del nombre, o hay 4 bytes en cero entre el nombre y el fuente.
"""

from __future__ import annotations

import re
import struct
from dataclasses import dataclass, field

CODIFICACION = "cp1252"
_BYTES_TEXTO = frozenset(range(32, 256)) | {9, 10, 13}
_RE_UNIDAD = re.compile(r"^\s*(PACKAGE\s+BODY|PACKAGE|PROCEDURE|FUNCTION)\b", re.IGNORECASE)
_RE_FORMULA = re.compile(r"^BEGIN\n:(?P<item>[\w$#.]+)\s*:=\s*\($", re.IGNORECASE)


@dataclass
class Fragmento:
    offset: int
    texto: str


@dataclass
class CodigoExtraido:
    """Resultado de la extracción. ``tipo``: trigger | formula | unidad | desconocido | vacio."""

    tipo: str
    texto: str = ""
    nombre_interno: str = ""
    descripcion: str = ""  # "WHEN-NEW-FORM-INSTANCE (Pantalla)", "KEY-NEXT-ITEM (BSEL.X)", "MENU.ITEM"
    item_formula: str = ""  # sólo para FORMULA-CALCULATION
    fragmentos: list[Fragmento] = field(default_factory=list)
    advertencias: list[str] = field(default_factory=list)


def _fragmento_en(blob: bytes, i: int) -> tuple[int, bytes] | None:
    if i + 4 > len(blob):
        return None
    n = struct.unpack(">I", blob[i : i + 4])[0]
    if n < 1 or n > len(blob) - i - 4:
        return None
    datos = blob[i + 4 : i + 4 + n]
    if not all(b in _BYTES_TEXTO for b in datos):
        return None
    return n, datos


def _mejor_fragmento(blob: bytes, desde: int, ventana: int) -> tuple[int, int, bytes] | None:
    """El fragmento válido MÁS LARGO que empieza dentro de [desde, desde+ventana).

    Elegir el más largo evita falsos positivos cortos (p. ej. 4 bytes en cero seguidos de un
    fragmento real cuya longitud contiene un byte imprimible)."""
    mejor: tuple[int, int, bytes] | None = None
    for k in range(desde, min(desde + ventana, len(blob))):
        f = _fragmento_en(blob, k)
        if f and (mejor is None or f[0] > mejor[1]):
            mejor = (k, f[0], f[1])
    return mejor


def fragmentos(blob: bytes) -> list[Fragmento]:
    """Secuencia de fragmentos de texto consecutivos tras la cabecera."""
    if len(blob) < 16:
        return []
    n_ent = struct.unpack(">I", blob[12:16])[0]
    pos = 16 + 4 * n_ent
    if pos > len(blob):
        return []
    res: list[Fragmento] = []
    # Primer fragmento: el MÁS TEMPRANO que tenga otro fragmento válido a continuación (los nombres
    # internos cortos como "PU_003" quedarían tapados si se eligiera el más largo de una ventana).
    primero: tuple[int, int, bytes] | None = None
    for k in range(pos, min(pos + 64, len(blob))):
        f = _fragmento_en(blob, k)
        if f and _mejor_fragmento(blob, k + 4 + f[0], 8) is not None:
            primero = (k, f[0], f[1])
            break
    if primero is None:
        primero = _mejor_fragmento(blob, pos, 64)  # un único fragmento (sin continuación)
    if primero is None:
        return []
    k, n, datos = primero
    while True:
        res.append(Fragmento(k, datos.decode(CODIFICACION)))
        siguiente = _mejor_fragmento(blob, k + 4 + n, 8)
        if siguiente is None:
            break
        k, n, datos = siguiente
    return res


def extraer(blob: bytes | None) -> CodigoExtraido:
    """Interpreta los fragmentos de un BLONG de código."""
    if not blob:
        return CodigoExtraido(tipo="vacio")
    frs = fragmentos(blob)
    textos = [f.texto for f in frs]
    res = CodigoExtraido(tipo="desconocido", fragmentos=frs)
    if not textos:
        res.advertencias.append("no se encontraron fragmentos de texto en el binario")
        return res

    # Trigger / comando de menú: [interno][BEGIN\n][cuerpo...][\nEND;][descripción]
    if len(textos) >= 3 and textos[1] == "BEGIN\n":
        try:
            fin = max(j for j in range(2, len(textos)) if textos[j] == "\nEND;")
        except ValueError:
            fin = -1
        if fin >= 2:
            res.tipo = "trigger"
            res.nombre_interno = textos[0]
            res.texto = "".join(textos[2:fin])
            res.descripcion = textos[fin + 1] if fin + 1 < len(textos) else ""
            return res

    # FORMULA-CALCULATION: [interno][BEGIN\n:B.I:=(][fórmula][);\nEND;][descripción]
    if len(textos) >= 4:
        m = _RE_FORMULA.match(textos[1])
        if m and textos[3] == ");\nEND;":
            res.tipo = "formula"
            res.nombre_interno = textos[0]
            res.item_formula = m.group("item")
            res.texto = textos[2]
            res.descripcion = textos[4] if len(textos) > 4 else ""
            return res

    # Program unit: el fuente es el primer fragmento que empieza con PROCEDURE/FUNCTION/PACKAGE.
    for j, t in enumerate(textos[:3]):
        if _RE_UNIDAD.match(t):
            res.tipo = "unidad"
            res.nombre_interno = textos[0] if j > 0 else ""
            res.texto = t
            return res

    res.advertencias.append(
        "estructura de fragmentos no reconocida: " + " | ".join(repr(t[:30]) for t in textos[:5])
    )
    return res
