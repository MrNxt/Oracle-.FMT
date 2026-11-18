"""Utilidades compartidas por los tests."""

from __future__ import annotations

import struct
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
SAMPLES = RAIZ / "samples"


def fragmento(texto: str) -> bytes:
    """Fragmento del binario de código: [longitud 4 bytes big-endian][texto cp1252]."""
    datos = texto.encode("cp1252")
    return struct.pack(">I", len(datos)) + datos


def blob_codigo(*textos: str, relleno: dict[int, bytes] | None = None) -> bytes:
    """Arma un BLONG de código sintético: cabecera mínima + fragmentos (+ relleno antes del i-ésimo)."""
    cabecera = struct.pack(">IIII", 0x42, 0x00800000, 0x00440000, 1) + struct.pack(">I", 0x278)
    cuerpo = b""
    for i, t in enumerate(textos):
        if relleno and i in relleno:
            cuerpo += relleno[i]
        cuerpo += fragmento(t)
    # Cola que imita P-code: no debe confundirse con texto.
    return cabecera + cuerpo + b"\x00\x00\x02\x65\xab\xcd\xab\xcd\x00\x00"


def blong_hex(datos: bytes) -> str:
    """Representación hexadecimal tal como la escribe el .fmt (grupos de 8 dígitos, 8 por línea)."""
    h = datos.hex()
    grupos = [h[i : i + 8] for i in range(0, len(h), 8)]
    return "\n".join(" ".join(grupos[i : i + 8]) + " " for i in range(0, len(grupos), 8))


def requiere_sample(nombre: str) -> Path:
    ruta = SAMPLES / nombre
    if not ruta.exists():
        pytest.skip(f"falta el sample {nombre}")
    return ruta
