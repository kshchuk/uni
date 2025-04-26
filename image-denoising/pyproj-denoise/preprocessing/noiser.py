import os
import numpy as np
from PIL import Image


class Noise:
    """
    Базовий клас для шумів.
    Кожен похідний клас має реалізувати метод 'apply'.
    """

    def apply(self, image_array: np.ndarray) -> np.ndarray:
        """
        Застосовує шум до NumPy масиву, що представляє зображення.
        Має повернути зашумлене зображення як NumPy масив.
        """
        raise NotImplementedError("Цей метод має бути перевизначений у підкласах.")


class GaussianNoise(Noise):
    """
    Додає гауссовий (нормальний) шум до зображення.
    mean: середнє значення для нормального розподілу
    std: стандартне відхилення для нормального розподілу
    """

    def __init__(self, mean: float = 0.0, std: float = 10.0):
        self.mean = mean
        self.std = std

    def apply(self, image_array: np.ndarray) -> np.ndarray:
        # Перетворюємо зображення в float для безпечних арифметичних операцій
        float_img = image_array.astype(np.float32)

        # Генеруємо гауссовий шум
        gauss = np.random.normal(self.mean, self.std, float_img.shape)

        # Додаємо шум до зображення
        noisy = float_img + gauss

        # Обмежуємо значення та перетворюємо назад в uint8
        noisy = np.clip(noisy, 0, 255)
        return noisy.astype(np.uint8)


class PoissonNoise(Noise):
    """
    Додає Пуассонівський шум до зображення.
    scale: коефіцієнт масштабування зображення перед застосуванням розподілу Пуассона
           (чим вищий scale, тим виразніше ефект Пуассона)
    """

    def __init__(self, scale: float = 1.0):
        self.scale = scale

    def apply(self, image_array: np.ndarray) -> np.ndarray:
        float_img = image_array.astype(np.float32)

        # Масштабуємо зображення для явнішого ефекту Пуассона
        scaled_img = float_img * self.scale

        # Генеруємо Пуассонівський шум
        noisy = np.random.poisson(scaled_img).astype(np.float32)

        # Масштабуємо назад до діапазону [0, 255]
        noisy = noisy / self.scale

        # Обмежуємо значення та перетворюємо
        noisy = np.clip(noisy, 0, 255)
        return noisy.astype(np.uint8)


class SpeckleNoise(Noise):
    """
    Додає плямистий (мультиплікативний) шум, який часто зустрічається в радарних або ультразвукових зображеннях.
    std: стандартне відхилення для випадкового шуму
    """

    def __init__(self, std: float = 0.1):
        self.std = std

    def apply(self, image_array: np.ndarray) -> np.ndarray:
        float_img = image_array.astype(np.float32)

        # Плямистий шум: результат = зображення + зображення * шум
        # шум ~ N(0, std)
        noise = np.random.randn(*float_img.shape) * self.std
        noisy = float_img + float_img * noise

        # Обмежуємо значення та перетворюємо
        noisy = np.clip(noisy, 0, 255)
        return noisy.astype(np.uint8)


class DatasetNoiser:
    """
    Застосовує один або декілька об'єктів Noise до всіх PNG зображень у датасеті,
    зберігаючи структуру папок в цільовій директорії.
    """

    def __init__(self, noises: list):
        """
        noises: список об'єктів Noise, які застосовуються послідовно.
        Наприклад: [GaussianNoise(...), PoissonNoise(...)]
        """
        self.noises = noises

    def apply_noises(self, image_array: np.ndarray) -> np.ndarray:
        """
        Послідовно застосовує кожен шум з self.noises до зображення.
        """
        noisy_img = image_array
        for noise in self.noises:
            noisy_img = noise.apply(noisy_img)
        return noisy_img

    def count_images(self, source_dir):
        """
        Підраховує кількість PNG файлів у директорії-джерелі.
        :return: Загальна кількість .png файлів.
        """
        count = 0
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                if file.lower().endswith('.png'):
                    count += 1
        return count

    def process_dataset(self, input_dir: str, output_dir: str):
        """
        Рекурсивно проходить по 'input_dir', застосовує шуми до кожного PNG файлу,
        та зберігає результат у 'output_dir' з тією ж структурою папок.
        """
        total_images = self.count_images(input_dir)
        processed_images = 0

        for root, dirs, files in os.walk(input_dir):
            # Обчислюємо відносний шлях для відтворення структури папок
            rel_path = os.path.relpath(root, input_dir)
            out_root = os.path.join(output_dir, rel_path)

            # Створюємо відповідну директорію для вихідних файлів
            os.makedirs(out_root, exist_ok=True)

            for file_name in files:
                if file_name.lower().endswith(".png"):
                    input_path = os.path.join(root, file_name)
                    output_path = os.path.join(out_root, file_name)

                    # Відкриваємо зображення
                    with Image.open(input_path) as img:
                        # Перетворюємо зображення з PIL у NumPy масив
                        img_array = np.array(img)

                        # Застосовуємо шуми
                        noisy_array = self.apply_noises(img_array)

                        # Перетворюємо назад у PIL зображення
                        noisy_img = Image.fromarray(noisy_array)

                        # Зберігаємо зашумлене зображення
                        noisy_img.save(output_path)

                        # Оновлюємо інформацію про виконану роботу
                        processed_images += 1
                        remaining = total_images - processed_images

                        if processed_images % 100 == 0:
                            print(f"Processed {processed_images}/{total_images} images. Remaining: {remaining}")


# if __name__ == "__main__":
#     # Приклад використання:
#     source_dir = "/media/yaroslav/dataset/0.1v/video-cropped"  # Директорія з PNG файлами
#     target_dir = "/home/yaroslav/tmp/noised_dataset"
#
#     # 1) Створюємо об'єкти шуму (параметри можна налаштовувати)
#     gaussian_noise = GaussianNoise(mean=0, std=20)
#     poisson_noise = PoissonNoise(scale=1.0)
#     speckle_noise = SpeckleNoise(std=0.02)
#
#     # 2) Ініціалізуємо DatasetNoiser з переліком шумів, які будуть застосовані послідовно
#     noiser = DatasetNoiser([gaussian_noise, poisson_noise, speckle_noise])
#
#     # 3) Обробляємо датасет
#     noiser.process_dataset(source_dir, target_dir)
