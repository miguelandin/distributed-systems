import socket
import json


class RPCError(Exception):
    pass


class RPCClient:
    def __init__(self, host, port,
                 timeout=3): self.host, self.port, self.timeout = host, port, timeout

    def call(self, function, *args):
        req = {'function': function, 'args': list(args)}  # json obj
        with socket.create_connection((self.host, self.port), timeout=self.timeout) as c:
            c.settimeout(self.timeout)
            c.sendall(json.dumps(req).encode())
            rbytes = c.recv(4096)
            r = json.loads(rbytes.decode())
            if r.get('status') == 'ok':
                return r.get('result')
            raise (RPCError("Error desde el otro lado"))
