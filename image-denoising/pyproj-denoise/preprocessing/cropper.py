import os
from PIL import Image

class DatasetImageCropper:
    """
    This class processes all .jpg images in a given source directory,
    crops them to the desired aspect ratio (4:3),
    then resizes them to the specified width and height,
    and finally saves them to a mirrored directory structure in the target directory.
    It also provides a simple progress indicator.
    """

    def __init__(self, source_dir, target_dir, width=640, height=480):
        """
        Initialize the cropper with source and target directories and desired dimensions.
        :param source_dir: Path to the source directory with images.
        :param target_dir: Path to the target directory where cropped images will be saved.
        :param width: Desired width of the final images (default 640).
        :param height: Desired height of the final images (default 480).
        """
        self.source_dir = source_dir
        self.target_dir = target_dir
        self.target_width = width
        self.target_height = height
        self.target_aspect_ratio = width / height

        # Will be calculated in run() before processing
        self.total_images = 0
        self.processed_images = 0

    def unify_aspect_ratio(self, img):
        """
        Crop the image to the desired aspect ratio (4:3) before resizing.
        We perform a center crop to maintain the main content of the image.
        :param img: PIL Image object.
        :return: Cropped PIL Image object with the target aspect ratio.
        """
        w, h = img.size
        current_ratio = w / h

        if current_ratio > self.target_aspect_ratio:
            # The image is too wide -> crop horizontally
            new_width = int(h * self.target_aspect_ratio)
            left = (w - new_width) // 2
            right = left + new_width
            top = 0
            bottom = h
            cropped_img = img.crop((left, top, right, bottom))
        else:
            # The image is too tall or matches ratio -> crop vertically
            new_height = int(w / self.target_aspect_ratio)
            top = (h - new_height) // 2
            bottom = top + new_height
            left = 0
            right = w
            cropped_img = img.crop((left, top, right, bottom))

        return cropped_img

    def process_image(self, img_path, save_path):
        """
        Open an image, crop it to the target aspect ratio, then resize and save.
        :param img_path: Full path to the source image.
        :param save_path: Full path to save the processed image.
        """
        with Image.open(img_path) as img:
            # Step 1: Unify aspect ratio (crop).
            cropped_img = self.unify_aspect_ratio(img)

            # Step 2: Resize to the desired dimensions (640x480 by default).
            resized_img = cropped_img.resize((self.target_width, self.target_height), Image.Resampling.LANCZOS)

            # Save the final image.
            resized_img.save(save_path)

    def count_images(self):
        """
        Count the total number of .jpg images in the source directory.
        :return: The total count of .jpg files.
        """
        count = 0
        for root, dirs, files in os.walk(self.source_dir):
            for file in files:
                if file.lower().endswith('.jpg'):
                    count += 1
        return count

    def run(self):
        """
        Walk through the source directory, process each .jpg image,
        and save it to the mirrored structure in the target directory.
        Also shows progress in the console.
        """
        # First, count how many .jpg images there are in total
        self.total_images = self.count_images()
        self.processed_images = 0

        for root, dirs, files in os.walk(self.source_dir):
            # Compute the relative path from the source directory.
            relative_path = os.path.relpath(root, self.source_dir)
            # Build the corresponding path in the target directory.
            target_root = os.path.join(self.target_dir, relative_path)

            # Create the mirrored directory if it does not exist.
            os.makedirs(target_root, exist_ok=True)

            for file in files:
                if file.lower().endswith('.jpg'):
                    source_file_path = os.path.join(root, file)
                    target_file_path = os.path.join(target_root, file)

                    # Process the image and save it.
                    self.process_image(source_file_path, target_file_path)

                    # Update progress
                    self.processed_images += 1
                    remaining = self.total_images - self.processed_images

                    if (self.processed_images % 100 == 0):
                        print(f"Processed {self.processed_images}/{self.total_images} images. Remaining: {remaining}")

if __name__ == "__main__":
    # Example usage:
    # Suppose we have:
    #   source_dir = "/media/yaroslav/dataset/0.1v/video-original"
    #   target_dir = "/media/yaroslav/dataset/0.1v/video-cropped"
    #
    # This will create a mirrored structure in 'video-cropped' where each image

    source_dir = "/media/yaroslav/dataset/0.1v/video-original"
    target_dir = "/media/yaroslav/dataset/0.1v/video-cropped"

    cropper = DatasetImageCropper(source_dir, target_dir, width=640, height=480)
    cropper.run()
