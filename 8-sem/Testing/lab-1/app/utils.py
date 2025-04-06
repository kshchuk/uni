# Функція порівняння чисел з допуском
def is_zero(value, eps=1e-8):
    return abs(value) < eps

# Виняток для некоректного задання прямої
class InvalidLineException(Exception):
    pass

# Функція для обчислення точки перетину двох прямих за їх коефіцієнтами
def compute_intersection(coeffs1, coeffs2):
    A1, B1, C1 = coeffs1
    A2, B2, C2 = coeffs2
    D = A1 * B2 - A2 * B1
    if is_zero(D):
        # Прямі паралельні або співпадають — унікальна точка відсутня
        return None
    x = (B1 * (-C2) - B2 * (-C1)) / D
    y = (A2 * (-C1) - A1 * (-C2)) / D
    return (x, y)