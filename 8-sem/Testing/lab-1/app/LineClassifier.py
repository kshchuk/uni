from utils import compute_intersection, is_zero, normalize_point, InvalidLineException


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

        # Перевірка на співпадання: якщо всі коефіцієнти пропорційні
        if self._are_coincident(coeffs[0], coeffs[1]) and \
           self._are_coincident(coeffs[0], coeffs[2]) and \
           self._are_coincident(coeffs[1], coeffs[2]):
            raise InvalidLineException("Усі 3 прямі не можуть співпадати")

        # Перевіряємо, чи є прямі з однаковими коефіцієнтами
        if coeffs[0] == coeffs[1]:
            raise InvalidLineException("Прямі 1 і 2 не можуть бути однаковими.")
        if coeffs[0] == coeffs[2]:
            raise InvalidLineException("Прямі 1 і 3 не можуть бути однаковими.")
        if coeffs[1] == coeffs[2]:
            raise InvalidLineException("Прямі 2 і 3 не можуть бути однаковими.")

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
            point_str = normalize_point(unique_points[0])
            return f"Прямі перетинаються в одній точці ({point_str})"
        elif num_points == 2:
            point1_str = normalize_point(unique_points[0])
            point2_str = normalize_point(unique_points[1])
            return f"Прямі перетинаються в двох точках ({point1_str}) та ({point2_str})"
        elif num_points == 3:
            point1_str = normalize_point(unique_points[0])
            point2_str = normalize_point(unique_points[1])
            point3_str = normalize_point(unique_points[2])
            s = f"({point1_str}), ({point2_str}), ({point3_str})"
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