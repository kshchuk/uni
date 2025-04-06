from abc import ABC, abstractmethod

# Абстрактний клас, який задає інтерфейс для представлення прямої
class Line(ABC):
    @abstractmethod
    def get_coefficients(self):
        """
        Повертає коефіцієнти (A, B, C) загального рівняння прямої: Ax + By + C = 0
        """
        pass