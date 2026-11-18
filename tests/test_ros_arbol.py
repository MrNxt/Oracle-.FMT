from __future__ import annotations

from pathlib import Path

from forms2apex.parser.ros_arbol import leer_arbol


def _nodo(oid, poi, typ, ooi, nombre=""):
    return (
        f"DEFINE  FRM50_IDFO\nBEGIN\n   IDFOS_POI = {poi}\n   IDFOS_OID = {oid}\n"
        f'   IDFOS_NAM = <<"{nombre}">>\n   IDFOS_TYP = {typ}\n   IDFOS_OOI = {ooi}\n'
        f"   IDFOS_OPN = 0\n   IDFOS_CNT = 0\nEND\n\n"
    )


def _texto(oid, num, valor, i=1):
    return f'DEFINE  F50T\nBEGIN\n   TP = {oid}\n   TI = {i}\n   TN = {num}\n   TV = <<"{valor}">>\nEND\n\n'


def _num(oid, num, valor, i=1):
    return f"DEFINE  F50N\nBEGIN\n   NP = {oid}\n   NI = {i}\n   NN = {num}\n   NV = {valor}\nEND\n\n"


FMT = (
    _nodo(1, 0, 22, 0, "FORM1")
    + _texto(1, 211, "FORM1")
    + _nodo(2, 1, 8, 0)  # lista de bloques
    + _nodo(3, 2, 7, 1, "BLQ")
    + _texto(3, 211, "BLQ")
    + _num(3, 268, 4, 2)
    + _nodo(4, 3, 31, 0)  # lista de ítems
    + _nodo(5, 4, 30, 3, "ITEM1")
    + _texto(5, 211, "ITEM1")
    + _nodo(6, 5, 69, 0)  # lista de triggers del ítem
    + _nodo(7, 6, 68, 5, "WHEN-VALIDATE-ITEM")
    + _num(99, 1, 1)  # propiedad de un nodo inexistente -> advertencia
)


def test_jerarquia_y_propiedades(tmp_path: Path):
    ruta = tmp_path / "f.fmt"
    ruta.write_bytes(FMT.encode("cp1252"))
    a = leer_arbol(ruta)
    assert a.raiz is not None and a.raiz.nombre == "FORM1"
    blq = a.nodos[3]
    assert blq.prop(268) == 4 and blq.prop(999, "x") == "x" and blq.tiene(211)
    assert [n.nombre for n in a.hijos_objeto(a.raiz)] == ["BLQ"]  # salta la lista intermedia
    assert [n.nombre for n in a.hijos_objeto(blq, 30)] == ["ITEM1"]
    trig = a.nodos[7]
    assert a.dueno(trig).nombre == "ITEM1"
    assert a.ruta_nombres(trig) == ("BLQ", "ITEM1", "WHEN-VALIDATE-ITEM")
    assert a.nodos[2].es_lista and not blq.es_lista
    assert any("inexistente" in adv for adv in a.advertencias)
