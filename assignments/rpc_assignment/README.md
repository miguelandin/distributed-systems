# Práctica 1 — Desarrollo de un sistema RPC sobre una instancia EC2

## Objetivo

Construir una pequeña capa RPC en Python sobre TCP.

- El cliente se ejecuta en el ordenador del alumno.
- El servidor se ejecuta en una instancia Amazon EC2.
- El intercambio de mensajes usa JSON.
- No se permite utilizar frameworks RPC (gRPC, RPyC, Pyro, etc.).

## Estructura proporcionada

```text
practica_rpc/
├── client/
│   ├── client_example.py
│   └── rpc_client.py
├── server/
│   ├── server.py
│   ├── procedures.py
│   └── rpc_server.py
├── common/
│   └── protocol.py
├── tests/
│   └── test_rpc.py
└── README.md
```

## Qué está hecho

Se proporciona:

1. Estructura inicial del proyecto.
2. Utilidades básicas para enviar y recibir mensajes JSON sobre TCP.
3. Un servidor TCP mínimo que acepta una conexión y muestra el mensaje recibido.
4. Algunas funciones remotas de ejemplo.
5. Un cliente de ejemplo.
6. Pruebas básicas del protocolo.
7. Indicaciones de despliegue en EC2.

## Qué debe implementar el alumno

El alumno debe completar:

- `RPCClient.call()`.
- El dispatcher del servidor.
- El registro y ejecución de procedimientos.
- La gestión de errores.
- Los timeouts.
- La concurrencia.
- Al menos dos procedimientos remotos adicionales.
- La integración completa entre cliente local y servidor EC2.

## Puesta en marcha rápida

### 1. Servidor local

Desde la raíz del proyecto:

```bash
python -m server.server
```

### 2. Cliente local

En otra terminal:

```bash
python -m client.client_example
```

El código inicial solo demuestra el envío de un mensaje JSON. La capa RPC todavía no está implementada.

## Configuración básica en EC2

1. Crear una instancia Linux en AWS EC2.
2. Permitir tráfico TCP de entrada al puerto elegido, por ejemplo `5000`.
3. Conectarse por SSH.
4. Copiar esta carpeta a la instancia.
5. Ejecutar:

```bash
python -m server.server
```

6. En el cliente, sustituir `127.0.0.1` por la IP pública o DNS público de la instancia EC2.

> No expongas puertos innecesarios y limita el origen de las reglas del Security Group siempre que sea posible.

## Formato de mensajes esperado

Petición:

```json
{
  "function": "sumar",
  "args": [4, 7]
}
```

Respuesta correcta:

```json
{
  "status": "ok",
  "result": 11
}
```

Respuesta de error:

```json
{
  "status": "error",
  "error": "PROCEDURE_NOT_FOUND"
}
```

## Restricciones

- Usar Python 3.10 o superior.
- Usar TCP.
- Usar JSON.
- No usar frameworks RPC.
- Mantener separado el código de aplicación de la lógica de comunicación.
