"""Árbol de objetos de un archivo ROS (.fmt / .mmt), todavía sin semántica de Forms.

Registros que forman el árbol:
  * ``FRM50_IDFO``: un nodo (objeto). IDFOS_OID = id, IDFOS_POI = nodo padre, IDFOS_TYP = tipo de
    objeto (número), IDFOS_OOI = objeto dueño (bloque, ítem, form...), IDFOS_NAM = nombre.
    Entre un objeto y sus hijos siempre hay un nodo "lista" sin nombre (tipo par, p. ej. 31 = lista
    de ítems de un bloque).
  * ``F50N`` / ``F50T`` / ``F50B`` / ``F50O`` / ``F50P`` / ``F50S``: propiedades del nodo indicado
    en el campo ``?P``; ``?N`` es el NÚMERO de propiedad (sin nombre en el archivo), ``?I`` el orden
    y ``?V`` (u ``OO``) el valor. Sólo se graban las propiedades distintas del valor por defecto.
  * ``TOOL_MODULE``: metadatos del módulo (producto, tipo, versión). ``VG_COLOR``: paleta (se ignora).

La traducción número de propiedad -> significado la hace ``diccionario.py`` con
``config/diccionario_ros.yaml`` (generado por la calibración).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path

from .ros_lexer import Registro, Valor, tokenizar_archivo

log = logging.getLogger(__name__)

# Clase de propiedad según el registro: (campo dueño, campo número, campo índice, campo valor)
_CLASES_PROP = {
    "F50N": ("NP", "NN", "NI", "NV"),
    "F50T": ("TP", "TN", "TI", "TV"),
    "F50B": ("BP", "BN", "BI", "BV"),
    "F50O": ("OP", "ON", "OI", "OO"),
    "F50P": ("PP", "PN", "PI", "PV"),
    "F50S": ("SP", "SN", "SI", "SV"),
}


@dataclass
class PropRos:
    numero: int
    clase: str  # N (número), T (texto), B (booleano), O (referencia a nodo), P / S (binario)
    indice: int
    valor: Valor


@dataclass
class NodoRos:
    oid: int
    padre: int  # IDFOS_POI
    tipo: int  # IDFOS_TYP
    dueno: int  # IDFOS_OOI
    nombre: str
    linea: int
    props: list[PropRos] = field(default_factory=list)
    hijos: list["NodoRos"] = field(default_factory=list)

    def prop(self, numero: int, defecto: Valor = None) -> Valor:
        """Valor de la primera propiedad con ese número, o ``defecto`` si no está grabada."""
        for p in self.props:
            if p.numero == numero:
                return p.valor
        return defecto

    def tiene(self, numero: int) -> bool:
        return any(p.numero == numero for p in self.props)

    @property
    def es_lista(self) -> bool:
        """Nodo contenedor sin nombre (lista de hijos)."""
        return not self.nombre and not any(p.numero == 211 for p in self.props)


@dataclass
class ArbolRos:
    ruta: Path
    nodos: dict[int, NodoRos] = field(default_factory=dict)
    raiz: NodoRos | None = None
    modulo_info: dict[str, Valor] = field(default_factory=dict)
    advertencias: list[str] = field(default_factory=list)

    def objetos(self, tipo: int | None = None) -> list[NodoRos]:
        """Nodos en orden de archivo (opcionalmente filtrados por tipo)."""
        return [n for n in self.nodos.values() if tipo is None or n.tipo == tipo]

    def hijos_objeto(self, nodo: NodoRos, tipo: int | None = None) -> list[NodoRos]:
        """Hijos "reales" de un objeto, saltando los nodos lista intermedios."""
        res: list[NodoRos] = []
        for h in nodo.hijos:
            if h.es_lista:
                res.extend(x for x in h.hijos if tipo is None or x.tipo == tipo)
            elif tipo is None or h.tipo == tipo:
                res.append(h)
        return res

    def dueno(self, nodo: NodoRos) -> NodoRos | None:
        return self.nodos.get(nodo.dueno) if nodo.dueno else None

    def ruta_nombres(self, nodo: NodoRos) -> tuple[str, ...]:
        """Nombres desde el objeto de primer nivel hasta ``nodo`` siguiendo los dueños (sin el módulo)."""
        partes: list[str] = []
        actual: NodoRos | None = nodo
        vistos: set[int] = set()
        while actual is not None and actual.oid not in vistos and actual is not self.raiz:
            vistos.add(actual.oid)
            partes.append(actual.nombre)
            actual = self.dueno(actual)
        return tuple(reversed(partes))


def _construir(ruta: Path, registros: list[Registro], advertencias: list[str]) -> ArbolRos:
    arbol = ArbolRos(ruta=ruta, advertencias=list(advertencias))
    pendientes: list[tuple[int, PropRos, int]] = []
    for r in registros:
        if r.clase != "DEFINE":
            continue
        c = r.campos
        if r.tipo == "FRM50_IDFO":
            try:
                nodo = NodoRos(
                    oid=int(c["IDFOS_OID"]),
                    padre=int(c.get("IDFOS_POI") or 0),
                    tipo=int(c["IDFOS_TYP"]),
                    dueno=int(c.get("IDFOS_OOI") or 0),
                    nombre=str(c.get("IDFOS_NAM") or ""),
                    linea=r.linea,
                )
            except (KeyError, TypeError, ValueError) as e:
                arbol.advertencias.append(f"línea {r.linea}: nodo FRM50_IDFO incompleto ({e}); se ignora")
                continue
            if nodo.oid in arbol.nodos:
                arbol.advertencias.append(f"línea {r.linea}: OID {nodo.oid} repetido; se conserva el primero")
                continue
            arbol.nodos[nodo.oid] = nodo
        elif r.tipo in _CLASES_PROP:
            fp, fn, fi, fv = _CLASES_PROP[r.tipo]
            try:
                dueno, numero, indice = int(c[fp]), int(c[fn]), int(c.get(fi) or 0)
            except (KeyError, TypeError, ValueError) as e:
                arbol.advertencias.append(f"línea {r.linea}: propiedad {r.tipo} incompleta ({e}); se ignora")
                continue
            pendientes.append((dueno, PropRos(numero, r.tipo[-1], indice, c.get(fv)), r.linea))
        elif r.tipo == "TOOL_MODULE":
            arbol.modulo_info = dict(c)
        # VG_COLOR y otros: no aportan al análisis.

    for dueno, prop, linea in pendientes:
        nodo = arbol.nodos.get(dueno)
        if nodo is None:
            arbol.advertencias.append(f"línea {linea}: propiedad {prop.numero} de un nodo inexistente ({dueno})")
            continue
        nodo.props.append(prop)

    for nodo in arbol.nodos.values():
        nodo.props.sort(key=lambda p: p.indice)
        if nodo.padre == 0:
            if arbol.raiz is None:
                arbol.raiz = nodo
            else:
                arbol.advertencias.append(f"más de una raíz: {nodo.oid} {nodo.nombre!r}")
            continue
        padre = arbol.nodos.get(nodo.padre)
        if padre is None:
            arbol.advertencias.append(f"nodo {nodo.oid} {nodo.nombre!r} con padre inexistente {nodo.padre}")
            continue
        padre.hijos.append(nodo)
    if arbol.raiz is None:
        arbol.advertencias.append("el archivo no tiene nodo raíz (módulo)")
    return arbol


def leer_arbol(ruta: str | Path) -> ArbolRos:
    """Lee un .fmt / .mmt y devuelve su árbol de objetos."""
    ruta = Path(ruta)
    lex = tokenizar_archivo(ruta)
    arbol = _construir(ruta, lex.registros, lex.advertencias)
    for a in arbol.advertencias:
        log.warning("%s: %s", ruta.name, a)
    return arbol
