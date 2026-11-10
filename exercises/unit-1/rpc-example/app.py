from time import sleep
from rpc_client import RPCClient
rpc = RPCClient('127.0.0.1', 5003)

while True:
    print(rpc.call('info_imagen', 'foto.jpg'))
    print(rpc.call('escala_grises', 'foto.jpg'))
    print(rpc.call('redimensionar', 'foto.jpg', 800, 600))
    sleep(1)

# TODO: probar procedimiento inexistente y argumentos incorrectos
