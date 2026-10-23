"""Pruebas básicas proporcionadas.

Ejecutar desde la raíz del proyecto:

    python -m unittest discover -s tests
"""

from __future__ import annotations

import socket
import unittest
import subprocess
from time import sleep

from common.protocol import send_json, recv_json
from client.rpc_client import RPCClient



class ProtocolTests(unittest.TestCase):
    def test_send_and_receive_json(self):
        left, right = socket.socketpair()

        try:
            expected = {
                "function": "sumar",
                "args": [4, 7],
            }

            send_json(left, expected)
            received = recv_json(right)

            self.assertEqual(received, expected)

        finally:
            left.close()
            right.close()


class StudentTests(unittest.TestCase):
    def test_rpc_sumar(self):
        HOST = '127.0.0.1'
        PORT = 5000

        server = subprocess.Popen(["python","-m", "server.server"])
        sleep(0.5)

        try:
            result = RPCClient(HOST,PORT).call("sumar",4,7)
            self.assertEqual(result, 11)

        finally:
            server.terminate()
            server.wait()

if __name__ == "__main__":
    unittest.main()
