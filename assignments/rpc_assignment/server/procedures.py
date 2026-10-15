"""Procedimientos remotos de ejemplo proporcionados."""

from __future__ import annotations
import time
import math


def sumar(a, b):
    return a + b


def multiplicar(a, b):
    return a * b


def potencia(a, b):
    return a ** b


def tarea_lenta(segundos):
    """Útil para comprobar posteriormente la concurrencia."""
    time.sleep(segundos)
    return segundos


def raiz_cuadrada(a):
    return math.sqrt(a)


def logaritmo_neperiano(a):
    return math.log(a)
