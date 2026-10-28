from __future__ import annotations

from client.rpc_client import RPCClient

HOST = "127.0.0.1"
PORT = 5000


def main():
    rpc = RPCClient(HOST, PORT)
    print(rpc.call("sumar", 4, 7, 8))
    print(rpc.call("raiz_cuadrada", -64))
    print(rpc.call("tarea_lenta", 10))


if __name__ == "__main__":
    main()
