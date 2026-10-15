"""Esqueleto del servidor RPC.

El alumno debe completar el registro, dispatch, gestión de errores
y posteriormente la concurrencia.
"""

from __future__ import annotations

from typing import Any, Callable


class RPCServer:
    def __init__(self):
        self._procedures: dict[str, Callable[..., Any]] = {}

    def register(self, name: str, function: Callable[..., Any]) -> None:
        self._procedures.update({name: function})

    def dispatch(self, request: dict[str, Any]) -> dict[str, Any]:
        function = request.get("function")
        args = request.get("args", [])

        if function not in self._procedures:
            raise TypeError("function doesn't exists")
        try:
            return {"status": "ok", "result": self._procedures[function](*args)}
        except TypeError as e:
            return {"status": "error", "error": "EXECUTION_ERROR", "message": str(e)}
