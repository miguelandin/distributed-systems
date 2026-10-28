# Documentación de la entrega RPC
### Arquitectura
Una petición funcionaría de la siguiente manera:
`client_example` → `rpc_client` → `TCP` → `server` → `rpc.dispatch` → `procedures` . 