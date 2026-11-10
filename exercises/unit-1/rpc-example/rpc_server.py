from typing import Callable


class RPCServer:
    def __init__(self): self.procedures: dict[str, Callable] = {}

    def register(self, name: str, function: Callable):
        self.procedures[name] = function

    def dispatch(self, r):
        name = r.get("function")
        args = r.get("args", [])

        if name not in self.procedures:
            raise TypeError("nombre de funcion no existe")

        try:
            result = self.procedures[name](*args)
            return {"status": "ok", "result": result}
        except Exception as e:
            return {"status": "error", "error": "EXECUTION_ERROR", "message": str(e)}
