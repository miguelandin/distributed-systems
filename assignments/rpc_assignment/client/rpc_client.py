from __future__ import annotations

import socket
from typing import Any

from common.protocol import send_json, recv_json


class ServerError(Exception):
    """Server couldn't process properly the petition"""


def get_data(response: dict[str, Any]) -> str:
    status = response.get('status')

    if status == 'ok':
        return str(response.get('result'))
    elif status == 'error':
        message = response.get('message')
        error = response.get('error')
        return f"{error} : {message}"

    raise ServerError("Couldn't process properly the petition")


class RPCClient:
    def __init__(self, host: str, port: int, timeout: float = 5.0):
        self.host = host
        self.port = port
        self.timeout = timeout

    def call(self, function: str, *args: Any) -> Any:
        message = {'function': function, 'args': args}

        with socket.create_connection((self.host, self.port), timeout=self.timeout) as c:
            c.settimeout(self.timeout)

            try:
                send_json(c, message)
                response = recv_json(c)
                return get_data(response)
            except Exception as e:
                print("An error ocurred: ", str(e))
