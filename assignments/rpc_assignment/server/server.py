"""Servidor TCP mínimo proporcionado.

Esta versión acepta una conexión cada vez y devuelve una respuesta
temporal. El alumno deberá integrar RPCServer y convertirlo después
en un servidor concurrente.
"""

from __future__ import annotations

import socket
from rpc_server import RPCServer
import procedures as proc

from common.protocol import send_json, recv_json


HOST = "0.0.0.0"
PORT = 5000

rpc = RPCServer()
rpc.register("sumar", proc.sumar)
rpc.register("multiplicar", proc.multiplicar)
rpc.register("potencia", proc.potencia)
rpc.register("tarea_lenta", proc.tarea_lenta)
rpc.register("raiz_cuadrada", proc.raiz_cuadrada)
rpc.register("logaritmo_neperiano", proc.logaritmo_neperiano)


def main():
    print(f"Servidor escuchando en {HOST}:{PORT}")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOST, PORT))
        server_socket.listen()

        while True:
            client_socket, address = server_socket.accept()

            with client_socket:
                print(f"Conexión recibida desde {address}")

                try:
                    request = recv_json(client_socket)
                    print("Mensaje recibido:", request)

                    # Respuesta temporal para comprobar la comunicación.
                    # TODO (alumno):
                    # Sustituir por:
                    # response = rpc_server.dispatch(request)
                    response = {
                        "status": "error",
                        "error": "RPC_NOT_IMPLEMENTED",
                    }

                    send_json(client_socket, response)

                except Exception as exc:
                    print(f"Error atendiendo la conexión: {exc}")

            # TODO (alumno):
            # Esta implementación es secuencial.
            # Modificarla al final de la práctica para atender
            # múltiples clientes simultáneamente.


if __name__ == "__main__":
    main()
