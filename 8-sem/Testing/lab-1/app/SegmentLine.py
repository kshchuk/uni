from line import Line
from utils import is_zero, InvalidLineException


class SegmentLine(Line):
    def __init__(self, a, b):
        if is_zero(a) or is_zero(b):
            raise InvalidLineException \
                ("Для відрізкового представлення прямої параметри a та b не можуть бути нульовими.")
        self.a = a
        self.b = b

    def get_coefficients(self):
        # Отримаємо рівняння: x/a + y/b = 1  <=>  b*x + a*y - a*b = 0
        A = self.b
        B = self.a
        C = -self.a * self.b
        return (A, B, C)

    def __str__(self):
        return f"SegmentLine(a={self.a}, b={self.b})"