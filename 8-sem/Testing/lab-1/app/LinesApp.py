# Основний клас застосунку, який відповідає за взаємодію з користувачем
import sys

from LineClassifier import LineClassifier
from SegmentLine import SegmentLine
from SlopeInterceptLine import SlopeInterceptLine
from utils import InvalidLineException


class LinesApp:
    def __init__(self):
        pass

    def run(self):
        print("=== КАЛЬКУЛЯТОР ПЕРЕТИНІВ ПРЯМИХ ===")
        print("Введіть параметри для трьох прямих:")
        print("\nДля прямих 1 і 2 (формат: x/a + y/b = 1):")
        while True:
            try:
                # Зчитування параметрів для прямих 1 та 2
                a1 = self._input_number("Введіть значення a1 для прямої 1: ")
                b1 = self._input_number("Введіть значення b1 для прямої 1: ")
                a2 = self._input_number("Введіть значення a2 для прямої 2: ")
                b2 = self._input_number("Введіть значення b2 для прямої 2: ")
                # Зчитування параметрів для прямої 3
                print("\nДля прямої 3 (формат: y = kx + b):")
                k3 = self._input_number("Введіть значення k3 для прямої 3: ")
                b3 = self._input_number("Введіть значення b3 для прямої 3: ")

                # Створення об'єктів прямих (з перевіркою коректності параметрів)
                line1 = SegmentLine(a1, b1)
                line2 = SegmentLine(a2, b2)
                line3 = SlopeInterceptLine(k3, b3)

                # Класифікація взаємного розташування прямих
                classifier = LineClassifier(line1, line2, line3)
                result = classifier.classify()

                print("\nРезультат:")
                print(result)
                break  # Якщо все пройшло коректно, завершуємо цикл вводу
            except InvalidLineException as e:
                print(f"\nПомилка: {e}")
                print("Спробуйте ввести дані ще раз.\n")
            except ValueError:
                print("\nНекоректний формат вводу. Будь ласка, введіть числове значення.\n")

    def _input_number(self, prompt):
        # Зчитування числа з консолі з обробкою винятків
        while True:
            user_input = input(prompt)
            # Дозволяємо завершення роботи, якщо користувач вводить 'e'
            if user_input.strip().lower() == 'e':
                print("Завершення роботи програми.")
                sys.exit(0)
            try:
                return float(user_input)
            except ValueError:
                print("Некоректний формат вводу. Спробуйте ще раз.")

if __name__ == "__main__":
    app = LinesApp()
    app.run()