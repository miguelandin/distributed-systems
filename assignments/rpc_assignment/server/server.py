from __future__ import annotations

import socket
from server.rpc_server import RPCServer
import server.procedures as proc
from common.protocol import send_json, recv_json
from concurrent.futures import ThreadPoolExecutor

HOST = "0.0.0.0"
PORT = 5000

rpc = RPCServer()
rpc.register("sumar", proc.sumar)
rpc.register("multiplicar", proc.multiplicar)
rpc.register("potencia", proc.potencia)
rpc.register("tarea_lenta", proc.tarea_lenta)
rpc.register("raiz_cuadrada", proc.raiz_cuadrada)
rpc.register("logaritmo_neperiano", proc.logaritmo_neperiano)


def attend(client_socket: socket.socket, address:socket._Address):
    with client_socket:
        print(f"Conexión recibida desde {address}")
        try:
            request = recv_json(client_socket)
            print("Mensaje recibido: ", request)

            response = rpc.dispatch(request)
            send_json(client_socket, response)

        except Exception as exc:
            print(f"Error atendiendo la conexión: {exc}")


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
