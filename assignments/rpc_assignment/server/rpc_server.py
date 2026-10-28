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

        if not isinstance(function, str) or not isinstance(args, list):
            return {"status": "error", "error": "INVALID_REQUEST", "message": "'function' must be a string and 'args' a list"}

        procedure = self._procedures.get(function)

        if procedure is None:
            return {"status": "error", "error": "PROCEDURE_NOT_FOUND", "message": f"procedure '{function}' not found"}
        try:
            return {"status": "ok", "result": procedure(*args)}
        except TypeError as e:
            return {"status": "error", "error":"INVALID_ARGUMENTS", "message":str(e)}
        except Exception as e:
            return {"status": "error", "error": "FAILED_PROCEDURE_EXECUTION", "message": str(e)}
