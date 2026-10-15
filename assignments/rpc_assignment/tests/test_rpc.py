"""Pruebas básicas proporcionadas.

Ejecutar desde la raíz del proyecto:

    python -m unittest discover -s tests
"""

from __future__ import annotations

import socket
import unittest

from common.protocol import send_json, recv_json


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
    @unittest.skip("Activar cuando RPCClient y RPCServer estén implementados.")
    def test_rpc_sumar(self):
        # TODO (alumno):
        # Añadir una prueba de integración o de dispatch.
        self.fail("Pendiente")


if __name__ == "__main__":
    unittest.main()
