"""Utilidades de protocolo proporcionadas por el profesor.

Este módulo implementa un framing sencillo:
- 4 bytes iniciales con la longitud del mensaje (big endian).
- A continuación, el JSON codificado en UTF-8.

El alumno puede reutilizar estas funciones, pero no debe modificar
su comportamiento sin justificarlo.
"""

from __future__ import annotations

import json
import socket
import struct
from typing import Any

HEADER_SIZE = 4
ENCODING = "utf-8"


def _recv_exact(sock: socket.socket, size: int) -> bytes:
    """Recibe exactamente `size` bytes o lanza ConnectionError."""
    chunks = []
    remaining = size

    while remaining:
        chunk = sock.recv(remaining)
        if not chunk:
            raise ConnectionError("La conexión se cerró antes de recibir todos los datos.")
        chunks.append(chunk)
        remaining -= len(chunk)

    return b"".join(chunks)


def send_json(sock: socket.socket, message: dict[str, Any]) -> None:
    """Serializa un diccionario a JSON y lo envía por TCP."""
    payload = json.dumps(message, ensure_ascii=False).encode(ENCODING)
    header = struct.pack("!I", len(payload))
    sock.sendall(header + payload)


def recv_json(sock: socket.socket) -> dict[str, Any]:
    """Recibe un mensaje JSON completo enviado con `send_json`."""
    header = _recv_exact(sock, HEADER_SIZE)
    (payload_size,) = struct.unpack("!I", header)
    payload = _recv_exact(sock, payload_size)
    data = json.loads(payload.decode(ENCODING))

    if not isinstance(data, dict):
        raise ValueError("El mensaje recibido debe ser un objeto JSON.")

    return data
