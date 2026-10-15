import socket
import json

HOST, PORT = '0.0.0.0', 5002

temp: dict[str, int] = {"Madrid": 21, "Paris": 17, "Roma": 25}
hum: dict[str, str] = {"Madrid": "4%", "Paris": "20%", "Roma": "40%"}
pro: dict[str, str] = {"Madrid": "Lluvias",
                       "Paris": "Nublado", "Roma": "Soleado"}
fut: dict[str, str] = {"Madrid": "Soleado",
                       "Paris": "Nublado", "Roma": "Lluvias"}


# Funciones que deben implementar los alumnos
def temperatura(ciudad):
    return temp.get(ciudad)


def humedad(ciudad):
    return hum.get(ciudad)


def pronostico(ciudad):
    return pro.get(ciudad)


def futuro(ciudad):
    return fut.get(ciudad)


def procesar(r):
    ciudad = r.get('ciudad')
    operacion = r.get('operacion')

    if operacion == 'temperatura':
        resultado = temperatura(ciudad)

    elif operacion == 'humedad':
        resultado = humedad(ciudad)

    elif operacion == 'pronostico':
        resultado = pronostico(ciudad)

    elif operacion == 'futuro':
        resultado = futuro(ciudad)

    else:
        return {
            'status': 'error',
            'message': 'Operacion desconocida'
        }

    if resultado is None:
        return {
            'status': 'error',
            'message': 'Ciudad no disponible'
        }

    return {
        'status': 'ok',
        'result': resultado
    }


with socket.socket() as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen()

    while True:
        c, _ = s.accept()

        with c:
            r = json.loads(c.recv(4096).decode())
            respuesta = procesar(r)
            c.sendall(json.dumps(respuesta).encode())
