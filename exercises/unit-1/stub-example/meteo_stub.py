import socket
import json


class MeteoStub:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def _request(self, op, ciudad):
        with socket.create_connection((self.host, self.port), timeout=3) as c:
            c.sendall(json.dumps({'operacion': op, 'ciudad': ciudad}).encode())
            response = json.loads(c.recv(4096).decode())

            if response.get('status') != 'ok':
                raise RuntimeError(response.get('message'))
            return response.get('result')

    def temperatura(self, ciudad):
        return self._request('temperatura', ciudad)

    def humedad(self, ciudad):
        return self._request('humedad', ciudad)

    def pronostico(self, ciudad):
        return self._request('pronostico', ciudad)

    def futuro(self, ciudad):
        return self._request('futuro', ciudad)
