from __future__ import annotations

from client.rpc_client import RPCClient

HOST = "127.0.0.1"
PORT = 5000


def main():
    rpc = RPCClient(HOST, PORT)
    print(rpc.call("sumar", 4, 7))
    print(rpc.call("multiplicar", 3, 5))
    print(rpc.call("tarea_lenta", 2))
    print(rpc.call("raiz_cuadrada", 64))
    print(rpc.call("logaritmo_neperiano", 12))


if __name__ == "__main__":
    main()
