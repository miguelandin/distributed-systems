import socket
from time import sleep
import json
HOST='127.0.0.1'
PORT=5001
timeout:int = 3

def enviar(texto:str, s:socket.socket) -> str:
    s.sendall(texto.encode())
    return s.recv(4096).decode()


with socket.create_connection((HOST,PORT), timeout=timeout) as c:
    c.settimeout(timeout)

    while True:
        sleep(2)
        mensaje={
            "type":"message",
            "text":"Hola servidor"
        }
        mensaje1 = {
            "type":"time",
            "text":"Hola"
        }

        print(enviar(json.dumps(mensaje), c))
        print(enviar(json.dumps(mensaje1), c))
