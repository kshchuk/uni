# Клас для прямої, заданої рівнянням: y = kx + b
from line import Line
from utils import is_zero, InvalidLineException


class SlopeInterceptLine(Line):
    def __init__(self, k, b):
        # За умовою роботи b не може бути нульовим
        if is_zero(b):
            raise InvalidLineException("Для прямої з кутовим коефіцієнтом параметр b не може бути нульовим.")
        self.k = k
        self.b = b

    def get_coefficients(self):
        # Перетворення: y = kx + b  <=>  kx - y + b = 0
        A = self.k
        B = -1
        C = self.b
        return (A, B, C)

    def __str__(self):
        return f"SlopeInterceptLine(k={self.k}, b={self.b})"