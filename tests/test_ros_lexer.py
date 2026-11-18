from __future__ import annotations

import pytest

from forms2apex.parser.ros_lexer import ErrorRos, tokenizar, tokenizar_archivo
from conftest import blong_hex


def _define(tipo: str, *lineas: str) -> str:
    return f"DEFINE  {tipo}\nBEGIN\n" + "\n".join(lineas) + "\nEND\n"


def test_describe_y_valores_basicos():
    texto = (
        "/*\n#ROS Script Version 6.0.8.21.0 - Production\n*/\n\n"
        "DESCRIBE  F50N\nBEGIN\n  UB4       NP\n  UB2       NN\nEND\n\n"
        + _define("F50N", "   NP = 4", "   NI = 1", "   NN = 739", "   NV = 31")
        + _define("F50T", "   TP = 5", "   TI = 2", "   TN = 745", '   TV = <<"C\xf3digo">>')
    )
    res = tokenizar(texto)
    assert [r.clase for r in res.registros] == ["DESCRIBE", "DEFINE", "DEFINE"]
    assert res.registros[0].campos == {"NP": "UB4", "NN": "UB2"}
    assert res.registros[1].campos["NV"] == 31
    assert res.registros[2].campos["TV"] == "Código"


def test_texto_con_comillas_internas_sin_escape():
    res = tokenizar(_define("F50T", "   TP = 1", "   TN = 522", '   TV = <<""ADRE"."STK_DOCUMENTO"">>'))
    assert res.registros[0].campos["TV"] == '"ADRE"."STK_DOCUMENTO"'


def test_texto_multilinea_respeta_saltos():
    res = tokenizar(_define("F50T", "   TP = 1", '   TV = <<"línea uno', "  línea dos", 'fin">>', "   TN = 57"))
    assert res.registros[0].campos["TV"] == "línea uno\n  línea dos\nfin"
    assert res.registros[0].campos["TN"] == 57


def test_linea_intermedia_terminada_en_cierre_no_corta_el_texto():
    # La línea 'b">>' no es el cierre porque lo que sigue no es un campo ni END.
    res = tokenizar(_define("F50T", '   TV = <<"a', 'b">>', 'c">>', "   TN = 1"))
    assert res.registros[0].campos["TV"] == 'a\nb">>\nc'


def test_varchar_longitud_y_texto_en_linea_siguiente():
    res = tokenizar(_define("TOOL_MODULE", "   PRODUCT = 9", '     <<"SQL*Forms">>', "   MODID = 0"))
    assert res.registros[0].campos == {"PRODUCT": "SQL*Forms", "MODID": 0}


def test_blong_hex_y_nullp():
    datos = bytes(range(40))
    res = tokenizar(
        _define("F50P", "   PP = 10", "   PV = (BLONG)", '<<"', blong_hex(datos).rstrip("\n"), '">>')
        + _define("F50P", "   PP = 11", "   PV = (BLONG) NULLP")
    )
    assert res.registros[0].campos["PV"] == datos
    assert res.registros[1].campos["PV"] is None


def test_archivo_crlf_cp1252(tmp_path):
    ruta = tmp_path / "x.fmt"
    contenido = _define("F50T", "   TP = 1", '   TV = <<"a\xf1o', 'dos">>', "   TN = 2")
    ruta.write_bytes(contenido.replace("\n", "\r\n").encode("cp1252"))
    res = tokenizar_archivo(ruta)
    assert res.registros[0].campos["TV"] == "año\ndos"
    assert res.registros[0].campos["TN"] == 2


def test_registro_sin_end_es_error():
    with pytest.raises(ErrorRos):
        tokenizar("DEFINE  F50N\nBEGIN\n   NP = 1\n")


def test_define_sin_begin_se_ignora_con_advertencia():
    res = tokenizar("DEFINE  F50N\n   NP = 1\n")
    assert res.registros == []
    assert res.advertencias
