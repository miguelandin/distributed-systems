"""Esqueleto de la capa cliente RPC.

Esta clase debe ocultar a la aplicación:
- creación del mensaje
- serialización
- conexión TCP
- envío y recepción
- tratamiento de errores
"""

from __future__ import annotations

import socket
from typing import Any

from common.protocol import send_json, recv_json


class RPCClient:
    def __init__(self, host: str, port: int, timeout: float = 5.0):
        self.host = host
        self.port = port
        self.timeout = timeout

    def call(self, function: str, *args: Any) -> Any:
        """Ejecuta un procedimiento remoto y devuelve su resultado.

        TODO (alumno):
        1. Crear la petición RPC.
        2. Abrir una conexión TCP.
        3. Configurar timeout.
        4. Enviar la petición.
        5. Recibir la respuesta.
        6. Devolver el resultado si status == "ok".
        7. Gestionar respuestas de error.
        8. Gestionar fallos de comunicación sin bloquear indefinidamente.
        """
        raise NotImplementedError("Completar RPCClient.call()")
