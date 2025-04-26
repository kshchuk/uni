import os
from PIL import Image

from noiser import *
class DatasetImageConverter:
    """
    Цей клас обробляє всі .jpg зображення в заданій директорії,
    конвертує їх у формат PNG,
    та зберігає у дзеркальній структурі в цільовій директорії.
    Також виводить інформацію про прогрес виконання.
    """

    def __init__(self, source_dir, target_dir):
        """
        Ініціалізація конвертера з директоріями-джерелом та цільовою директорією.
        :param source_dir: Шлях до директорії з оригінальними зображеннями (.jpg).
        :param target_dir: Шлях до директорії, куди будуть збережені зображення у форматі PNG.
        """
        self.source_dir = source_dir
        self.target_dir = target_dir
        self.total_images = 0
        self.processed_images = 0

    def convert_image(self, img_path, save_path):
        """
        Відкриває зображення та зберігає його у форматі PNG.
        :param img_path: Повний шлях до вихідного .jpg зображення.
        :param save_path: Повний шлях для збереження конвертованого зображення (.png).
        """
        with Image.open(img_path) as img:
            img.save(save_path, format="PNG")

    def count_images(self):
        """
        Підраховує кількість .jpg файлів у директорії-джерелі.
        :return: Загальна кількість .jpg файлів.
        """
        count = 0
        for root, dirs, files in os.walk(self.source_dir):
            for file in files:
                if file.lower().endswith('.jpg'):
                    count += 1
        return count

    def run(self):
        """
        Рекурсивно проходить по директорії, конвертує кожне .jpg зображення в PNG,
        та зберігає його у дзеркальній структурі в цільовій директорії.
        Також виводить інформацію про прогрес конвертації.
        """
        self.total_images = self.count_images()
        self.processed_images = 0

        for root, dirs, files in os.walk(self.source_dir):
            # Обчислюємо відносний шлях від директорії-джерела
            relative_path = os.path.relpath(root, self.source_dir)
            # Формуємо відповідну директорію в цільовій структурі
            target_root = os.path.join(self.target_dir, relative_path)
            os.makedirs(target_root, exist_ok=True)

            for file in files:
                if file.lower().endswith('.jpg'):
                    source_file_path = os.path.join(root, file)
                    # Змінюємо розширення файлу на .png
                    target_file_name = os.path.splitext(file)[0] + '.png'
                    target_file_path = os.path.join(target_root, target_file_name)
                    self.convert_image(source_file_path, target_file_path)
                    self.processed_images += 1

                    if self.processed_images % 100 == 0:
                        print(f"Converted {self.processed_images}/{self.total_images} images.")


if __name__ == "__main__":
    # Приклад використання:
    source_dir = "/media/yaroslav/dataset/0.1v/video-cropped"  # Вкажіть шлях до директорії з .jpg файлами
    target_dir = "/media/yaroslav/dataset/0.1v/video-cropped-png"  # Вкажіть шлях до директорії, куди зберігатимуться .png файли

    converter = DatasetImageConverter(source_dir, target_dir)
    converter.run()

    source_dir = "/media/yaroslav/dataset/0.1v/video-cropped-png"
    # target_dir = "/media/yaroslav/dataset/0.1v/video-cropped-noisy-gaussian-20-poisson-1-speckle-0.02"
    target_dir = "/media/yaroslav/dataset/0.1v/video-cropped-png-noisy-gaussian-20-poisson-1-speckle-0.02"

    # 2) Create noise objects (you can customize parameters)
    gaussian_noise = GaussianNoise(mean=0, std=20)
    poisson_noise = PoissonNoise(scale=1.0)
    speckle_noise = SpeckleNoise(std=0.02)

    # 3) Initialize DatasetNoiser with a list of noise objects
    #    They will be applied in the given order
    noiser = DatasetNoiser([gaussian_noise, poisson_noise, speckle_noise])

    # 4) Process the dataset
    noiser.process_dataset(source_dir, target_dir)



