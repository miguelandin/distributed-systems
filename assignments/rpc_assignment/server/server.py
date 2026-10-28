from __future__ import annotations

import socket
from server.rpc_server import RPCServer
import server.procedures as proc
from common.protocol import send_json, recv_json
from concurrent.futures import ThreadPoolExecutor
from typing import Any

HOST = "0.0.0.0"
PORT = 5000
READ_TIMEOUT = 10.0

rpc = RPCServer()
rpc.register("sumar", proc.sumar)
rpc.register("multiplicar", proc.multiplicar)
rpc.register("potencia", proc.potencia)
rpc.register("tarea_lenta", proc.tarea_lenta)
rpc.register("raiz_cuadrada", proc.raiz_cuadrada)
rpc.register("logaritmo_neperiano", proc.logaritmo_neperiano)
rpc.register("hora", proc.hora)


def attend(client_socket: socket.socket, address: socket._Address):
    with client_socket:
        print(f"Conexión recibida desde {address}")
        client_socket.settimeout(READ_TIMEOUT)

        try:
            request = recv_json(client_socket)
        except TimeoutError:
            print(f"{address} timeout")
            return
        except ConnectionError:
            print(f"{address} conection closed")
            return

        print(f"{address} petition: {request}")
        response = rpc.dispatch(request)

        try:
            send_json(client_socket, response)
        except OSError as e:
            print(f"{address} response couldn't be sent: {e}")


def main():
    print(f"Servidor escuchando en {HOST}:{PORT}")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOST, PORT))
        server_socket.listen()

        with ThreadPoolExecutor(max_workers=10) as pool:
            while True:
                pool.submit(attend, *server_socket.accept())


if __name__ == "__main__":
    main()
