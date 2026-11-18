"""Lexer del formato de texto ROS de Forms 6i (.fmt, .mmt).

El archivo es una secuencia de registros:

    DESCRIBE  <TIPO>          esquema: una línea "<TIPO_CAMPO> <NOMBRE>" por campo
    BEGIN
      UB4       NP
    END

    DEFINE  <TIPO>            datos: una línea "<CAMPO> = <valor>" por campo
    BEGIN
       NP = 4
       TV = <<"texto">>
    END

Formas de valor encontradas:
  * número:                 ``NV = 31``
  * texto en una línea:     ``TV = <<"E">>``
  * texto multilínea:       ``TV = <<"línea 1`` ... ``línea n">>`` (saltos de línea reales, sin escapes)
  * texto con longitud:     ``MODNAME = 55`` y en la línea siguiente ``<<"...">>`` (campos VARCHAR)
  * binario:                ``PV = (BLONG)`` y luego ``<<"`` + líneas de hexadecimal + ``">>``
  * binario vacío:          ``PV = (BLONG) NULLP``

Los textos no escapan comillas: el delimitador es ``<<"`` al inicio y ``">>`` al final.
Codificación: cp1252 (Windows-1252).
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path

log = logging.getLogger(__name__)

CODIFICACION = "cp1252"

_RE_CABECERA = re.compile(r"^(DEFINE|DESCRIBE)\s+(\S+)\s*$")
_RE_CAMPO = re.compile(r"^\s*(\w+)\s*=\s*(.*)$")
_INICIO_TEXTO = '<<"'
_FIN_TEXTO = '">>'

Valor = int | str | bytes | None


class ErrorRos(Exception):
    """Error de formato irrecuperable en un archivo ROS."""


@dataclass
class Registro:
    """Un registro DEFINE o DESCRIBE del archivo."""

    clase: str  # "DEFINE" | "DESCRIBE"
    tipo: str  # FRM50_IDFO, F50N, F50T, ...
    campos: dict[str, Valor]
    linea: int  # línea (1-based) de la cabecera


@dataclass
class ResultadoLexer:
    registros: list[Registro] = field(default_factory=list)
    advertencias: list[str] = field(default_factory=list)


def leer_texto(ruta: str | Path) -> str:
    """Lee el archivo en cp1252 y normaliza los saltos de línea a ``\\n``."""
    datos = Path(ruta).read_bytes()
    return datos.decode(CODIFICACION, errors="replace").replace("\r\n", "\n").replace("\r", "\n")


def _parece_campo_o_fin(linea: str) -> bool:
    s = linea.strip()
    return s == "END" or _RE_CAMPO.match(linea) is not None


def tokenizar(texto: str) -> ResultadoLexer:
    """Convierte el contenido de un archivo ROS en registros."""
    res = ResultadoLexer()
    lineas = texto.split("\n")
    n = len(lineas)
    i = 0

    def leer_texto_delimitado(primera: str, i: int) -> tuple[str, int]:
        """``primera`` empieza después de ``<<"``. Devuelve (texto, índice de la última línea usada)."""
        partes = [primera]
        while True:
            actual = partes[-1]
            if actual.endswith(_FIN_TEXTO):
                # Un texto multilínea podría tener una línea intermedia terminada en '">>':
                # sólo cerramos si lo que sigue es otro campo o el END del registro.
                if i + 1 >= n or _parece_campo_o_fin(lineas[i + 1]):
                    partes[-1] = actual[: -len(_FIN_TEXTO)]
                    return "\n".join(partes), i
            i += 1
            if i >= n:
                raise ErrorRos(f"texto sin cerrar al final del archivo (empezó en la línea {i})")
            partes.append(lineas[i])

    while i < n:
        m = _RE_CABECERA.match(lineas[i])
        if not m:
            i += 1
            continue
        clase, tipo = m.groups()
        linea_cab = i + 1
        if i + 1 >= n or lineas[i + 1].strip() != "BEGIN":
            res.advertencias.append(f"línea {linea_cab}: {clase} {tipo} sin BEGIN; se ignora")
            i += 1
            continue
        i += 2
        campos: dict[str, Valor] = {}
        while i < n and lineas[i].strip() != "END":
            ln = lineas[i]
            if not ln.strip():
                i += 1
                continue
            if clase == "DESCRIBE":
                partes = ln.split()
                if len(partes) == 2:
                    campos[partes[1]] = partes[0]
                i += 1
                continue
            mc = _RE_CAMPO.match(ln)
            if not mc:
                raise ErrorRos(f"línea {i + 1}: no se reconoce {ln!r} dentro de {tipo}")
            clave, crudo = mc.groups()
            crudo = crudo.rstrip()
            valor: Valor
            if crudo.startswith("(BLONG)"):
                resto = crudo[len("(BLONG)") :].strip()
                if resto == "NULLP":
                    valor = None
                else:
                    i += 1
                    if i >= n or lineas[i].strip() != _INICIO_TEXTO:
                        raise ErrorRos(f"línea {i + 1}: se esperaba '<<\"' tras (BLONG)")
                    hexa: list[str] = []
                    i += 1
                    while i < n and lineas[i].strip() != _FIN_TEXTO:
                        hexa.append(lineas[i].replace(" ", ""))
                        i += 1
                    try:
                        valor = bytes.fromhex("".join(hexa))
                    except ValueError as e:
                        raise ErrorRos(f"línea {i + 1}: hexadecimal inválido en BLONG: {e}") from e
            elif crudo.startswith(_INICIO_TEXTO):
                valor, i = leer_texto_delimitado(crudo[len(_INICIO_TEXTO) :], i)
            elif i + 1 < n and lineas[i + 1].strip().startswith(_INICIO_TEXTO):
                # VARCHAR: la longitud en esta línea, el texto en la(s) siguiente(s).
                i += 1
                valor, i = leer_texto_delimitado(lineas[i].strip()[len(_INICIO_TEXTO) :], i)
            else:
                try:
                    valor = int(crudo)
                except ValueError:
                    valor = crudo  # valor no numérico sin delimitar: se conserva tal cual
            campos[clave] = valor
            i += 1
        if i >= n:
            raise ErrorRos(f"registro {tipo} de la línea {linea_cab} sin END")
        res.registros.append(Registro(clase, tipo, campos, linea_cab))
        i += 1
    return res


def tokenizar_archivo(ruta: str | Path) -> ResultadoLexer:
    return tokenizar(leer_texto(ruta))
