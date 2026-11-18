from __future__ import annotations

from forms2apex.parser.plsql_blob import extraer
from conftest import blob_codigo


def test_trigger_quita_el_envoltorio_begin_end():
    b = blob_codigo("P14_25_NOV_201616_42_39", "BEGIN\n", "IF :B.X IS NULL THEN\n  NULL;\nEND IF;", "\nEND;",
                    "KEY-NEXT-ITEM (BSEL.W_CLAVE)")
    r = extraer(b)
    assert r.tipo == "trigger"
    assert r.texto == "IF :B.X IS NULL THEN\n  NULL;\nEND IF;"
    assert r.descripcion == "KEY-NEXT-ITEM (BSEL.W_CLAVE)"
    assert r.nombre_interno == "P14_25_NOV_201616_42_39"


def test_trigger_con_nombre_interno_corto():
    # Caso real (STKC007): "PU_003" no debe quedar tapado por el cuerpo, que es más largo.
    b = blob_codigo("PU_003", "BEGIN\n", ":SYSTEM.MESSAGE_LEVEL := 10;\n" * 20, "\nEND;", "WHEN-NEW-FORM-INSTANCE (Pantalla)")
    r = extraer(b)
    assert r.tipo == "trigger" and r.nombre_interno == "PU_003"
    assert r.texto.startswith(":SYSTEM.MESSAGE_LEVEL")


def test_cuerpo_que_termina_en_end_propio():
    b = blob_codigo("P1", "BEGIN\n", "BEGIN\n  PRINT;\nEND;", "\nEND;", "KEY-PRINT (Pantalla)")
    assert extraer(b).texto == "BEGIN\n  PRINT;\nEND;"


def test_formula_calculation():
    b = blob_codigo("P14_13_ABR_201211_16_16", "BEGIN\n:BDOC.TOTA_EFEC:=(", "nvl(:bdoc.a,0) + 1", ");\nEND;",
                    "FORMULA-CALCULATION (BDOC.TOTA_EFEC)")
    r = extraer(b)
    assert r.tipo == "formula" and r.item_formula == "BDOC.TOTA_EFEC" and r.texto == "nvl(:bdoc.a,0) + 1"


def test_program_unit_con_relleno_de_ceros():
    fuente = "PROCEDURE PP_CARGAR_DATOS IS\nBEGIN\n  NULL;\nEND;"
    r = extraer(blob_codigo("PP_CARGAR_DATOS", fuente, relleno={1: b"\x00\x00\x00\x00"}))
    assert r.tipo == "unidad" and r.texto == fuente and r.nombre_interno == "PP_CARGAR_DATOS"


def test_program_unit_sin_fragmento_de_nombre():
    fuente = "PACKAGE PP_GLOBAL IS\n  x NUMBER;\nEND;"
    r = extraer(blob_codigo(fuente))
    assert r.tipo == "unidad" and r.texto == fuente and r.nombre_interno == ""


def test_acentos_cp1252():
    r = extraer(blob_codigo("PU_1", "BEGIN\n", "-- validación de año", "\nEND;", "X (Pantalla)"))
    assert r.texto == "-- validación de año"


def test_binario_vacio_o_irreconocible():
    assert extraer(None).tipo == "vacio"
    r = extraer(b"\x00" * 40)
    assert r.tipo == "desconocido" and r.advertencias
