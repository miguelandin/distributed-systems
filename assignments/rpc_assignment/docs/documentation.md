# Práctica 1 — Sistema RPC sobre una instancia EC2

**Sistemas Distribuidos · Programación distribuida en Python**

- **Autor:** Miguel Cabrera Landín 
- **Repositorio:** <https://github.com/miguelandin/distributed-systems/tree/main/assignments/rpc_assignment>
- **Vídeo de demostración:** [Screencast (mp4)](https://github.com/miguelandin/distributed-systems/releases/download/video/Screencast.From.2026-10-28.23-23-15.mp4)

## 1. Objetivo y alcance

Se ha desarrollado un sistema cliente-servidor en Python, usando exclusivamente la biblioteca estándar, que permite invocar procedimientos de forma remota a través de una capa RPC propia. El cliente se ejecuta en el ordenador local y el servidor en una instancia Amazon EC2. El trabajo cubre las seis fases de la práctica: despliegue en EC2, protocolo de mensajes sobre TCP, capa RPC (`RPCClient`), servidor con dispatcher de procedimientos, gestión de errores y timeouts, y servidor concurrente.

## 2. Arquitectura

```
 Tu ordenador                                            Instancia EC2
 ────────────                                            ─────────────
 client_example.py                                       server.py  (socket TCP + ThreadPoolExecutor)
      │  rpc.call("sumar", 4, 7)                              │  accept() → attend() en un hilo del pool
      ▼                                                       ▼
 RPCClient  (client/rpc_client.py)                       RPCServer.dispatch  (server/rpc_server.py)
      │                                                       │  localiza "sumar" y ejecuta sumar(4, 7)
      ▼                                                       ▼
 send_json / recv_json  (common/protocol.py) ◀──TCP:5000──▶ recv_json / send_json  (common/protocol.py)

            {"function": "sumar", "args": [4, 7]}  ──────────▶
            ◀──────────  {"status": "ok", "result": 11}
```

El sistema está dividido en tres capas con responsabilidades separadas:

| Capa                | Fichero                | Responsabilidad                                                                                                                                                                                               |
| ------------------- | ---------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Protocolo           | `common/protocol.py`   | Enmarcado de mensajes, serialización JSON y lectura/escritura sobre el socket. Es el único módulo compartido por cliente y servidor, lo que garantiza que ambos extremos hablan exactamente el mismo formato. |
| RPC cliente         | `client/rpc_client.py` | Clase `RPCClient`: convierte una llamada local en una petición de red y la respuesta en un valor de retorno.                                                                                                  |
| RPC servidor        | `server/rpc_server.py` | Clase `RPCServer`: registro de procedimientos y *dispatcher* que valida y ejecuta cada petición.                                                                                                              |
| Transporte servidor | `server/server.py`     | Socket de escucha, pool de hilos y ciclo de vida de cada conexión (`attend`).                                                                                                                                 |
| Lógica de negocio   | `server/procedures.py` | Los procedimientos expuestos. No saben nada de sockets ni de JSON.                                                                                                                                            |

Esta separación permite cambiar una capa sin tocar las otras: por ejemplo, sustituir JSON por otro formato solo afectaría a `protocol.py`, y añadir un procedimiento solo requiere definirlo en `procedures.py` y registrarlo en `server.py`.

## 3. Protocolo de comunicación

**Transporte.** Se usa TCP porque garantiza entrega fiable y ordenada, imprescindible para una llamada que espera exactamente una respuesta. A cambio, TCP es un flujo de bytes sin fronteras de mensaje: un `recv()` puede devolver medio mensaje o uno y medio. Resolver esto es el primer problema de diseño del protocolo.

**Enmarcado (framing).** Cada mensaje viaja como una cabecera de 4 bytes en orden de red (`struct.pack("!I", len(payload))`) seguida del cuerpo JSON codificado en UTF-8. El receptor lee primero los 4 bytes, conoce la longitud exacta del cuerpo y llama a `_recv_exact`, que repite `recv()` hasta acumular todos los bytes o detecta un cierre prematuro (`ConnectionError`). Se descartaron dos alternativas: un delimitador como `\n`, que obliga a escanear el flujo y prohíbe ese carácter en el contenido, y cerrar la conexión para marcar el fin, que impediría enviar la respuesta por el mismo socket.

**Formato de los mensajes.**

| Mensaje            | Campos                                                 | Ejemplo                                                                                     |
| ------------------ | ------------------------------------------------------ | ------------------------------------------------------------------------------------------- |
| Petición           | `function` (str), `args` (lista)                       | `{"function": "sumar", "args": [4, 7]}`                                                     |
| Respuesta correcta | `status: "ok"`, `result`                               | `{"status": "ok", "result": 11}`                                                            |
| Respuesta de error | `status: "error"`, `error` (código), `message` (texto) | `{"status": "error", "error": "PROCEDURE_NOT_FOUND", "message": "procedure 'x' not found"}` |

**Serialización.** JSON se eligió por ser legible, estar en la biblioteca estándar y ser independiente del lenguaje, de modo que un cliente escrito en otro lenguaje podría usar el servidor sin cambios. Sus limitaciones condicionan los procedimientos: solo viajan `str`, números, booleanos, `null`, listas y objetos. Las tuplas de `*args` llegan al servidor como listas, y un valor como `datetime` no es serializable, por lo que el procedimiento `hora` devuelve la fecha en formato ISO 8601 como cadena.

**Una conexión por llamada.** Cada `call()` abre una conexión TCP, envía la petición, espera la respuesta y cierra. El servidor no guarda ningún estado entre llamadas y cada hilo atiende exactamente una petición, lo que simplifica mucho la concurrencia. El coste es un *handshake* TCP por llamada (un RTT adicional), asumible para esta práctica; una conexión persistente sería la mejora natural para un uso intensivo.

## 4. Capa RPC

**Cliente.** `RPCClient(host, port, timeout=5.0)` ofrece un único método `call(function, *args)`. Quien lo usa escribe `rpc.call("sumar", 4, 7)` y recibe `11`, como si la función fuera local: la construcción del mensaje, la conexión, el envío, la espera y la interpretación de la respuesta quedan ocultos. Esa es la transparencia que persigue RPC. Lo que no puede ocultarse es la latencia ni la posibilidad de fallo parcial, y por eso el cliente expone un `timeout` configurable.

**Dispatcher.** `RPCServer` mantiene un diccionario nombre → función. El registro es explícito (`rpc.register("sumar", proc.sumar)`): se descartó exponer automáticamente todo el módulo con `getattr`, porque haría accesible desde la red cualquier función importada. `dispatch(request)` valida la petición, localiza el procedimiento, lo ejecuta con `procedure(*args)` y devuelve siempre un diccionario de respuesta; por diseño nunca lanza excepciones, de modo que `attend` solo tiene que enviar lo que recibe.

**Procedimientos.** Además de los cuatro proporcionados (`sumar`, `multiplicar`, `potencia`, `tarea_lenta`) se han añadido `raiz_cuadrada` y `logaritmo_neperiano` (ambos con dominio restringido, útiles para provocar errores de ejecución), `hora` (devuelve la hora del servidor, que permite comprobar que la ejecución ocurre de verdad en la máquina remota) y `mensaje` (eco: devuelve su argumento, útil para probar la serialización de cadenas y la identificación de hilos).

## 5. Gestión de errores y timeouts

Se distinguen los errores que detecta el servidor, que viajan en la respuesta con un código fijo, de los que ocurren en el propio cliente y nunca llegan a tener respuesta.

| Código                       | Situación                                                                                     | Dónde se detecta                             |
| ---------------------------- | --------------------------------------------------------------------------------------------- | -------------------------------------------- |
| `INVALID_REQUEST`            | `function` no es una cadena o `args` no es una lista                                          | `dispatch`, antes de buscar el procedimiento |
| `PROCEDURE_NOT_FOUND`        | El nombre no está registrado                                                                  | `dispatch`, al consultar el diccionario      |
| `INVALID_ARGUMENTS`          | Número de argumentos incorrecto (`TypeError` al invocar)                                      | `dispatch`, `except TypeError`               |
| `FAILED_PROCEDURE_EXECUTION` | Cualquier otra excepción dentro del procedimiento, p. ej. `raiz_cuadrada(-64)` → `ValueError` | `dispatch`, `except Exception`               |

En el cliente, `get_data` devuelve el `result` si el estado es `ok` y, si es `error`, devuelve una cadena `CÓDIGO : mensaje`; una respuesta sin ninguno de los dos estados lanza `ServerError`. Las excepciones locales (timeout, cierre de conexión por el servidor, respuesta mal formada) se capturan en `call` y se devuelven también como texto descriptivo. Si el servidor no está disponible, `socket.create_connection` lanza `ConnectionRefusedError` o `TimeoutError` al llamador.

**Timeouts.** Hay dos, independientes y con preguntas distintas:

- *Cliente* (`timeout=5.0`): el socket espera como máximo 5 s en cada operación bloqueante (conectar, enviar, cada `recv`). Responde a "¿cuánto espero la respuesta?".
- *Servidor* (`READ_TIMEOUT = 10.0` en `attend`): limita cuánto espera el servidor a recibir la petición completa. Sin él, un cliente que conecta y no envía nada bloquearía un hilo del pool indefinidamente; con diez clientes así el servidor dejaría de atender. Responde a "¿cuánto espero a que lleguen datos?".

El script `client/client_error_example.py` provoca los tres casos más representativos: `sumar(4, 7, 8)` → `INVALID_ARGUMENTS`, `raiz_cuadrada(-64)` → `FAILED_PROCEDURE_EXECUTION` y `tarea_lenta(10)` → `timed out` en el cliente a los 5 s. Este último ilustra la semántica de fallos propia de RPC: el cliente informa de un error, pero el servidor termina la tarea a los 10 s y entonces falla al enviar la respuesta porque el cliente ya cerró. **La llamada se ejecutó aunque el cliente la vio fallar.** Para procedimientos no idempotentes (por ejemplo, uno que escribiera en una base de datos) esto obligaría a añadir identificadores de petición para evitar ejecuciones duplicadas al reintentar.

## 6. Concurrencia

El servidor atiende cada conexión en un hilo de un `ThreadPoolExecutor(max_workers=10)`: el bucle principal solo hace `accept()` y entrega el socket al pool. Se prefirió un pool a crear un hilo por conexión porque acota los recursos: una avalancha de conexiones no puede agotar la memoria del servidor; las que exceden el tamaño del pool quedan encoladas y se atienden en cuanto se libera un hilo.

El GIL de Python no es un problema aquí: las tareas son de E/S (`recv`, `sendall`, `time.sleep`), y todas esas operaciones liberan el GIL, de modo que los hilos avanzan realmente en paralelo mientras esperan. No ha sido necesario ningún cerrojo: el diccionario de procedimientos es de solo lectura una vez arrancado el servidor y los procedimientos no comparten estado mutable. Si se añadiera estado compartido (un contador de llamadas, una caché), habría que protegerlo con `threading.Lock`.

**Verificación.** `client/client_threads_example.py` lanza 15 llamadas simultáneas a `tarea_lenta(2)` desde 15 hilos cliente y mide el tiempo total. Resultado medido: **4,01 s** frente a los 30 s que tardaría en secuencia. Los clientes 0-9 terminan a los 2,00 s y los clientes 10-14 a los 4,00 s: los diez primeros ocupan el pool completo y los cinco restantes esperan una ronda. La prueba demuestra a la vez que el servidor es concurrente y que el pool tiene el límite esperado.

## 7. Despliegue en EC2

- **Instancia:** EC2 en la región NA Virginia, con AMI Amazon Linux (usuario `ec2-user`).
- **Grupo de seguridad:** reglas de entrada TCP 22 (SSH) y TCP 5000 (servidor RPC). El resto del tráfico entrante está cerrado.
- **Acceso y arranque:** `ssh -i clave.pem ec2-user@<IP_pública>`, clonado del repositorio y `python3 -m server.server`.

El servidor hace `bind("0.0.0.0", 5000)` para escuchar en todas las interfaces. Es necesario porque la instancia solo conoce su dirección privada (`172.31.x.x`); la IP pública la traduce AWS mediante NAT y no existe en ninguna interfaz de la máquina, así que un `bind` a ella fallaría. En el cliente basta con `RPCClient("<IP_pública>", 5000)`. El vídeo muestra el servidor recibiendo en EC2 conexiones desde la IP pública del ordenador local.

## 8. Pruebas y demostración

`tests/test_rpc.py` contiene una prueba unitaria del protocolo (`socketpair`: lo que entra por `send_json` sale idéntico por `recv_json`) y una prueba de integración que arranca el servidor como subproceso y comprueba que `sumar(4, 7)` devuelve `11`. Se ejecutan con `python -m unittest discover -s tests`. Los tres scripts de `client/` (`client_example`, `client_error_example`, `client_threads_example`) cubren respectivamente el funcionamiento normal, los errores y la concurrencia; sus ejecuciones están grabadas en los GIF del README y en el vídeo enlazado al principio.

## 9. Decisiones de diseño, limitaciones y mejoras

- **Errores como valor de retorno en el cliente.** `call` devuelve una cadena descriptiva en lugar de lanzar excepciones. Simplifica los scripts de demostración, pero impide distinguir programáticamente un error de un resultado que sea una cadena. Una versión de biblioteca lanzaría una jerarquía `RPCError` / `RPCTimeoutError` / `RPCRemoteError`.
- **Sin límite de tamaño de mensaje.** La cabecera admite hasta 4 GiB; un cliente malicioso podría forzar al servidor a reservar esa memoria. Bastaría con rechazar cabeceras por encima de un `MAX_MESSAGE_SIZE`.
- **JSON mal formado.** Si la petición no es JSON válido, `recv_json` lanza `ValueError` y el servidor cierra la conexión sin responder; sería más correcto devolver un código `PARSE_ERROR`.
- **Sin timeout de ejecución en el servidor.** `READ_TIMEOUT` cubre la recepción, no la ejecución: un `tarea_lenta(600)` ocupa un hilo diez minutos aunque el cliente haya abandonado.
- **Sin seguridad.** No hay autenticación ni cifrado; el puerto 5000 queda expuesto a Internet. En producción se restringiría el grupo de seguridad a IPs conocidas y se añadiría TLS.
- **Otras extensiones:** argumentos con nombre (`kwargs`), identificador de petición para reintentos seguros, conexión persistente, tamaño del pool configurable y un procedimiento de introspección que liste los procedimientos registrados.

## 10. Conclusión

La práctica muestra que una capa RPC útil cabe en unas pocas decenas de líneas si el protocolo está bien definido: el enmarcado con longitud prefijada resuelve el problema del flujo TCP, JSON da un formato neutral, y un dispatcher que nunca lanza excepciones concentra toda la gestión de errores en un punto. La parte menos evidente, y la más instructiva, ha sido la semántica de los timeouts: en un sistema distribuido un fallo visible en el cliente no implica que la operación no se haya ejecutado, y esa incertidumbre es inherente a cualquier RPC, no un defecto de esta implementación.
