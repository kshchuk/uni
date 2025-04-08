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
        return None
    # Коректне обчислення:
    x = (B1 * C2 - B2 * C1) / D
    y = (A2 * C1 - A1 * C2) / D
    return (x, y)

def normalize_point(point):
    """
    Нормалізує кортеж (x, y) у рядок формату "(x, y)" з форматуванням до 6 знаків після коми.
    Якщо значення знаходиться дуже близько до нуля, воно формується як 0.000000.
    """
    x, y = point
    # Якщо значення практично рівні нулю, встановити 0.0
    if abs(x) < 1e-8:
        x = 0.0
    if abs(y) < 1e-8:
        y = 0.0
    return f"{x:.6f}, {y:.6f}"