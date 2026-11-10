import socket
import json
from datetime import datetime
from typing import Any
HOST = '0.0.0.0'
PORT = 5001

def procesar(f: str):
    datos:dict[str,Any] = json.loads(f)

    respuesta = {'status':'error', 'message':'JSON invalido'}

    tipo = datos.get('type')
    if tipo == 'message':
        respuesta={
            'status':'ok',
            'message':'Hola cliente'
        }
    elif tipo == 'time':
        respuesta={
                'status':'ok',
                'time':datetime.now().strftime('%H:%M:%S')
        }

    return json.dumps(respuesta)


def atender_cliente(c:socket.socket ,addr: tuple[str,int]):
    with c: # con el with cerramos correctamente la conexión
        while True:
            data = c.recv(4096)
            if not data:
                break
            print(f"Recibido de {addr}: {data.decode()}")
            respuesta=procesar(data.decode())
            c.sendall(respuesta.encode())



with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen()

    while True:
        c, addr = s.accept() # c=conexión 
        print(f"Recibida conexión de {addr}")
        atender_cliente(c,addr)
