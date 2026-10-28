from __future__ import annotations

import sys
import time
from concurrent.futures import ThreadPoolExecutor

from client.rpc_client import RPCClient

HOST = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
PORT = 5000
N_CLIENTES = 15
SEGUNDOS = 2


def llamada(i: int) -> str:
    rpc = RPCClient(HOST, PORT, timeout=30)
    inicio = time.perf_counter()
    rpc.call("tarea_lenta", SEGUNDOS)
    return f"cliente {i:2d} terminó en {time.perf_counter() - inicio:.2f} s"


def main():
    inicio = time.perf_counter()
    with ThreadPoolExecutor(max_workers=N_CLIENTES) as pool:
        for linea in pool.map(llamada, range(N_CLIENTES)):
            print(linea)
    total = time.perf_counter() - inicio
    print(f"\n{N_CLIENTES} llamadas de {SEGUNDOS} s en {total:.2f} s "
          f"(en secuencia serían {N_CLIENTES * SEGUNDOS} s)")


if __name__ == "__main__":
    main()
