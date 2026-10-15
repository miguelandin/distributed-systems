import socket
import json
from concurrent.futures import ThreadPoolExecutor
from rpc_server import RPCServer
from procedures import info_imagen, escala_grises, redimensionar
HOST, PORT = '127.0.0.1', 5003
rpc = RPCServer()
rpc.register("info_imagen", info_imagen)
rpc.register("escala_grises", escala_grises)
rpc.register("redimensionar", redimensionar)


def atender(c, a):
    print("ATENDIENDO PETICION")
    msgin = c.recv(4096).decode()
    try:
        res = rpc.dispatch(json.loads(msgin))
    except Exception as e:
        res = {"status": "error", "error": "BAD_MESSAGE", "message": str(e)}

    resString = json.dumps(res)
    c.sendall(resString.encode())


with socket.socket() as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen()
    with ThreadPoolExecutor(max_workers=3) as pool:
        while True:
            c, a = s.accept()
            pool.submit(atender, c, a)
