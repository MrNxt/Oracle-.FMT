"""Integración contra los samples reales (se saltan si no están en samples/)."""

from __future__ import annotations

import collections

import pytest

from forms2apex.parser.plsql_blob import extraer
from forms2apex.parser.ros_arbol import leer_arbol
from conftest import requiere_sample

ESPERADO = {
    # archivo: (nodos, {(tipo ROS, tipo de código): cantidad})
    "STKC007.fmt": (1002, {(68, "trigger"): 45, (58, "unidad"): 25}),
    "fini018.fmt": (1296, {(68, "trigger"): 110, (68, "formula"): 3, (58, "unidad"): 53}),
    "WAPIDEMO.mmt": (37, {(42, "trigger"): 8}),
}


@pytest.mark.parametrize("nombre", list(ESPERADO))
def test_todo_el_codigo_se_extrae(nombre):
    arbol = leer_arbol(requiere_sample(nombre))
    nodos, codigo = ESPERADO[nombre]
    assert len(arbol.nodos) == nodos
    assert not arbol.advertencias
    cuenta = collections.Counter()
    for n in arbol.objetos():
        b = n.prop(464)
        if isinstance(b, bytes):
            r = extraer(b)
            cuenta[(n.tipo, r.tipo)] += 1
            if n.tipo == 68 and r.tipo == "trigger":
                assert r.descripcion.startswith(n.nombre + " ("), (n.nombre, r.descripcion)
            if r.tipo == "unidad":
                assert n.nombre.upper() in r.texto.upper()[:300]
    assert dict(cuenta) == codigo
