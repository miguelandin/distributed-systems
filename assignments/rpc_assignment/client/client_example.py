"""Cliente de ejemplo proporcionado.

Primero demuestra paso de mensajes explícito.
Cuando RPCClient esté implementado, el alumno puede sustituir esta
parte por llamadas `rpc.call(...)`.
"""

from __future__ import annotations

import socket

from common.protocol import send_json, recv_json

HOST = "127.0.0.1"  # Sustituir por IP/DNS de EC2 al desplegar
PORT = 5000


def main():
    request = {
        "function": "sumar",
        "args": [4, 7],
    }

    print("Enviando:", request)

    with socket.create_connection((HOST, PORT), timeout=5) as sock:
        send_json(sock, request)
        response = recv_json(sock)

    print("Respuesta:", response)

    # Cuando RPCClient esté completo:
    #
    # from client.rpc_client import RPCClient
    # rpc = RPCClient(HOST, PORT)
    # print(rpc.call("sumar", 4, 7))
    # print(rpc.call("multiplicar", 3, 5))
    # print(rpc.call("tarea_lenta", 2))


if __name__ == "__main__":
    main()
