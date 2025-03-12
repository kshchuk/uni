import os
import cv2
import numpy as np
import glob
import random
import shutil


# Function to add Gaussian noise to an image
def add_gaussian_noise(image, mean=0, var=0.01):
    # image is expected to be float32 in range [0, 1]
    sigma = var ** 0.5
    gaussian = np.random.normal(mean, sigma, image.shape)
    noisy = image + gaussian
    noisy = np.clip(noisy, 0, 1)
    return noisy


# Function to add speckle noise to an image
def add_speckle_noise(image, mean=0, var=0.04):
    # speckle noise: output = image + image * noise
    sigma = var ** 0.5
    noise = np.random.normal(mean, sigma, image.shape)
    noisy = image + image * noise
    noisy = np.clip(noisy, 0, 1)
    return noisy


# Function to add salt & pepper noise to an image
def add_salt_and_pepper_noise(image, salt_vs_pepper=0.5, amount=0.05):
    # image is expected to be float32 in range [0, 1]
    noisy = image.copy()
    # Salt noise
    num_salt = np.ceil(amount * image.size * salt_vs_pepper)
    coords = [np.random.randint(0, i - 1, int(num_salt))
              for i in image.shape[:2]]
    noisy[coords[0], coords[1]] = 1.0

    # Pepper noise
    num_pepper = np.ceil(amount * image.size * (1.0 - salt_vs_pepper))
    coords = [np.random.randint(0, i - 1, int(num_pepper))
              for i in image.shape[:2]]
    noisy[coords[0], coords[1]] = 0.0
    return noisy


# Function to randomly choose and add a noise type to an image
def add_random_noise(image):
    noise_types = ['gaussian', 'speckle', 'salt_pepper']
    noise_type = random.choice(noise_types)
    if noise_type == 'gaussian':
        return add_gaussian_noise(image, mean=0, var=0.01)
    elif noise_type == 'speckle':
        return add_speckle_noise(image, mean=0, var=0.04)
    elif noise_type == 'salt_pepper':
        return add_salt_and_pepper_noise(image, salt_vs_pepper=0.5, amount=0.05)
    else:
        return image


# Main function to process images recursively
def process_images(input_root, output_root, target_size=(640, 640)):
    # Create output root if it doesn't exist
    if os.path.exists(output_root):
        shutil.rmtree(output_root)  # remove if exists
    os.makedirs(output_root, exist_ok=True)

    # Recursively traverse directories
    for dirpath, dirnames, filenames in os.walk(input_root):
        # Create corresponding output directory
        relative_path = os.path.relpath(dirpath, input_root)
        output_dir = os.path.join(output_root, relative_path)
        os.makedirs(output_dir, exist_ok=True)

        for filename in filenames:
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
                input_file = os.path.join(dirpath, filename)
                output_file = os.path.join(output_dir, filename)

                # Read the image
                image = cv2.imread(input_file)
                if image is None:
                    print(f"Failed to read {input_file}")
                    continue

                # Resize image to target_size
                resized = cv2.resize(image, target_size)
                # resized = image

                # Convert to float32 in range [0,1]
                resized_float = resized.astype(np.float32) / 255.0

                # Add noise using random noise type
                noisy_float = add_random_noise(resized_float)

                # Convert back to uint8
                noisy = (noisy_float * 255).astype(np.uint8)

                # Save the noisy image
                cv2.imwrite(output_file, noisy)
                print(f"Processed and saved: {output_file}")


if __name__ == "__main__":
    # Input dataset directory (change if needed)
    input_dataset = os.path.join("dataset", "images")
    # Output directory for noisy images
    output_dataset = "dataset_noisy"
    # Process images: resize to 640x640 and add realistic noise
    process_images(input_dataset, output_dataset, target_size=(640, 640))
