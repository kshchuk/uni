import numpy as np
from skimage.metrics import structural_similarity as ssim_metric
from skimage.metrics import peak_signal_noise_ratio as psnr_metric
from skimage.metrics import mean_squared_error as mse_metric
from PIL import Image


class ImageQualityMetrics:
    """
    A class to compute image quality metrics between two images.
    The images are assumed to be NumPy arrays.
    """

    @staticmethod
    def mse(imageA: np.ndarray, imageB: np.ndarray) -> float:
        """
        Compute the Mean Squared Error (MSE) between two images.
        Lower values indicate higher similarity.
        """
        return mse_metric(imageA, imageB)

    @staticmethod
    def psnr(imageA: np.ndarray, imageB: np.ndarray) -> float:
        """
        Compute the Peak Signal-to-Noise Ratio (PSNR) between two images.
        Higher values indicate better quality.
        """
        # Calculate the data range from imageA
        data_range = imageA.max() - imageA.min()
        return psnr_metric(imageA, imageB, data_range=data_range)

    @staticmethod
    def ssim(imageA: np.ndarray, imageB: np.ndarray) -> float:
        """
        Compute the Structural Similarity Index (SSIM) between two images.
        SSIM is a value between -1 and 1; higher values indicate better similarity.
        """
        # The 'multichannel' flag is set to True for color images.
        data_range = imageA.max() - imageA.min()
        return ssim_metric(imageA, imageB, data_range=data_range, multichannel=True)

    @staticmethod
    def mae(imageA: np.ndarray, imageB: np.ndarray) -> float:
        """
        Compute the Mean Absolute Error (MAE) between two images.
        Lower values indicate higher similarity.
        """
        return np.mean(np.abs(imageA.astype(np.float32) - imageB.astype(np.float32)))

    @staticmethod
    def nrmse(imageA: np.ndarray, imageB: np.ndarray) -> float:
        """
        Compute the Normalized Root Mean Squared Error (NRMSE) between two images.
        It is the RMSE divided by the data range.
        """
        mse_val = ImageQualityMetrics.mse(imageA, imageB)
        rmse = np.sqrt(mse_val)
        data_range = imageA.max() - imageA.min()
        return rmse / data_range if data_range != 0 else 0.0


if __name__ == "__main__":
    # Load two images that you want to compare. Make sure they are the same size.
    image_path1 = "/path/to/image1.jpg"
    image_path2 = "/path/to/image2.jpg"

    # Open images using PIL and convert them to NumPy arrays
    img1 = np.array(Image.open(image_path1))
    img2 = np.array(Image.open(image_path2))

    # Calculate metrics
    mse_value = ImageQualityMetrics.mse(img1, img2)
    psnr_value = ImageQualityMetrics.psnr(img1, img2)
    ssim_value = ImageQualityMetrics.ssim(img1, img2)
    mae_value = ImageQualityMetrics.mae(img1, img2)
    nrmse_value = ImageQualityMetrics.nrmse(img1, img2)

    # Print the computed metrics
    print(f"MSE:   {mse_value:.4f}")
    print(f"PSNR:  {psnr_value:.4f} dB")
    print(f"SSIM:  {ssim_value:.4f}")
    print(f"MAE:   {mae_value:.4f}")
    print(f"NRMSE: {nrmse_value:.4f}")
