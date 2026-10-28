# Sistema RPC en Python sobre TCP

## Estructura del Proyecto
```text
.
├── assets/
│   ├── client.gif
│   └── server.gif
├── client/
│   ├── client_example.py     # Script principal para arrancar el cliente
│   └── rpc_client.py         # Lógica central del cliente RPC y conexión
├── common/
│   └── protocol.py           # Serialización, deserialización y formato JSON
├── server/
│   ├── procedures.py         # Funciones y cálculos expuestos por el servidor
│   ├── rpc_server.py         # Despachador de funciones y manejo de concurrencia
│   └── server.py             # Script principal para arrancar el servidor TCP
├── tests/
│   └── test_rpc.py           # Batería de pruebas del protocolo y conectividad
├── requirements.txt          # Dependencias (si aplica)
└── README.md                 # Este archivo
```
## Ejecución:
##### Levantar el Servidor
En tu primera terminal, colócate en la raíz del proyecto y ejecuta el servidor. Este registrará los procedimientos disponibles y se quedará a la escucha en el puerto local:
```bash
python -m server.server
```
##### Ejecutar el Cliente
Abre una segunda terminal, asegúrate de estar en la raíz del proyecto y lanza el cliente de pruebas. Este script se conectará al servidor e invocará las funciones remotas:
```bash
python -m client.client_example
```

## Ejemplos de uso
#### Peticiones correctas:
![normal example](assets/normal-example.gif)

#### Peticiones incorrectas:
![error example](assets/error-example.gif)

#### Varias peticiones
![thread example](assets/thread-example.gif)