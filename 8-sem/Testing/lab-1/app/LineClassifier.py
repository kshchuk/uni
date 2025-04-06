# Клас для класифікації взаємного розташування трьох прямих
from utils import compute_intersection, is_zero


class LineClassifier:
    def __init__(self, line1, line2, line3):
        self.line1 = line1
        self.line2 = line2
        self.line3 = line3

    def classify(self):
        # Отримуємо коефіцієнти для кожної прямої
        coeffs = [
            self.line1.get_coefficients(),
            self.line2.get_coefficients(),
            self.line3.get_coefficients()
        ]

        # Перевірка на співпадання: якщо для хоча б однієї пари коефіцієнти пропорційні
        if self._are_coincident(coeffs[0], coeffs[1]) or \
           self._are_coincident(coeffs[0], coeffs[2]) or \
           self._are_coincident(coeffs[1], coeffs[2]):
            return "Прямі співпадають"

        # Обчислюємо точки перетину для кожної пари (якщо існують)
        intersections = []
        pairs = [(0, 1), (0, 2), (1, 2)]
        for i, j in pairs:
            pt = compute_intersection(coeffs[i], coeffs[j])
            if pt is not None:
                intersections.append(pt)

        # Видаляємо дублікати (з урахуванням допуску)
        unique_points = []
        for pt in intersections:
            if not any(self._points_equal(pt, upt) for upt in unique_points):
                unique_points.append(pt)

        num_points = len(unique_points)
        if num_points == 0:
            return "Прямі не перетинаються"
        elif num_points == 1:
            x, y = unique_points[0]
            return f"Прямі перетинаються в одній точці ({x:.6f}, {y:.6f})"
        elif num_points == 2:
            (x1, y1), (x2, y2) = unique_points
            return f"Прямі перетинаються в двох точках ({x1:.6f}, {y1:.6f}) та ({x2:.6f}, {y2:.6f})"
        elif num_points == 3:
            s = ", ".join(f"({x:.6f}, {y:.6f})" for x, y in unique_points)
            return f"Прямі перетинаються в трьох точках {s}"
        else:
            return f"Прямі перетинаються в {num_points} точках"

    def _are_coincident(self, coeffs1, coeffs2):
        A1, B1, C1 = coeffs1
        A2, B2, C2 = coeffs2

        # Для перевірки співпадання обчислюємо відношення коефіцієнтів (якщо знаменник ненульовий)
        ratios = []
        if not is_zero(A2):
            ratios.append(A1 / A2)
        if not is_zero(B2):
            ratios.append(B1 / B2)
        if not is_zero(C2):
            ratios.append(C1 / C2)
        # Якщо всі отримані відношення практично рівні, прямі співпадають
        return all(is_zero(r - ratios[0]) for r in ratios)

    def _points_equal(self, pt1, pt2, tol=1e-6):
        x1, y1 = pt1
        x2, y2 = pt2
        return is_zero(x1 - x2, tol) and is_zero(y1 - y2, tol)