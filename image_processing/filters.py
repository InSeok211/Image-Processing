"""이미지 필터 함수들"""
import cv2
import numpy as np


def apply_grayscale(image):
    """그레이스케일 변환"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)


def apply_gaussian_blur(image, kernel_size=(15, 15)):
    """가우시안 블러"""
    return cv2.GaussianBlur(image, kernel_size, 0)


def apply_sharpening(image):
    """샤프닝 효과"""
    kernel = np.array([[-1, -1, -1],
                      [-1,  9, -1],
                      [-1, -1, -1]])
    return cv2.filter2D(image, -1, kernel)


def apply_canny(image, threshold1=100, threshold2=200):
    """Canny 엣지 검출"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, threshold1, threshold2)
    return cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)


def apply_sobel(image):
    """Sobel 엣지 검출"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    sobel = np.sqrt(sobelx**2 + sobely**2)
    sobel = np.uint8(sobel)
    return cv2.cvtColor(sobel, cv2.COLOR_GRAY2BGR)


def apply_laplacian(image):
    """라플라시안 필터"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    laplacian = cv2.Laplacian(gray, cv2.CV_64F)
    laplacian = np.uint8(np.abs(laplacian))
    return cv2.cvtColor(laplacian, cv2.COLOR_GRAY2BGR)


def apply_erode(image, kernel_size=(5, 5), iterations=1):
    """침식 효과"""
    kernel = np.ones(kernel_size, np.uint8)
    return cv2.erode(image, kernel, iterations=iterations)


def apply_dilate(image, kernel_size=(5, 5), iterations=1):
    """팽창 효과"""
    kernel = np.ones(kernel_size, np.uint8)
    return cv2.dilate(image, kernel, iterations=iterations)


def apply_threshold(image, threshold=127):
    """이진화"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)
    return cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)


def apply_histogram_stretching(image):
    """히스토그램 스트레칭"""
    if len(image.shape) == 3:
        result = np.zeros_like(image)
        for i in range(3):
            channel = image[:, :, i]
            min_val = np.min(channel)
            max_val = np.max(channel)
            if max_val > min_val:
                stretched = ((channel - min_val) / (max_val - min_val) * 255).astype(np.uint8)
                result[:, :, i] = stretched
            else:
                result[:, :, i] = channel
        return result
    else:
        min_val = np.min(image)
        max_val = np.max(image)
        if max_val > min_val:
            return ((image - min_val) / (max_val - min_val) * 255).astype(np.uint8)
        return image


def apply_histogram_eq(image):
    """히스토그램 평활화"""
    yuv = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
    yuv[:, :, 0] = cv2.equalizeHist(yuv[:, :, 0])
    return cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR)


def apply_sepia(image):
    """세피아 톤 효과"""
    kernel = np.array([[0.272, 0.534, 0.131],
                      [0.349, 0.686, 0.168],
                      [0.393, 0.769, 0.189]])
    result = cv2.transform(image, kernel)
    return np.clip(result, 0, 255).astype(np.uint8)


def apply_emboss(image):
    """엠보싱 효과"""
    kernel = np.array([[-2, -1, 0],
                      [-1,  1, 1],
                      [ 0,  1, 2]])
    return cv2.filter2D(image, -1, kernel)


def apply_median_blur(image, ksize=9):
    """미디언 블러"""
    return cv2.medianBlur(image, ksize)


def apply_unsharp_mask(image, sigma=2.0, strength=1.5):
    """언샤프 마스크 (샤프닝)"""
    blurred = cv2.GaussianBlur(image, (0, 0), sigma)
    return cv2.addWeighted(image, strength, blurred, -(strength - 1), 0)


def apply_opening(image, kernel_size=(5, 5)):
    """모폴로지 열림 (Opening) = 침식 후 팽창"""
    kernel = np.ones(kernel_size, np.uint8)
    return cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)


def apply_closing(image, kernel_size=(5, 5)):
    """모폴로지 닫힘 (Closing) = 팽창 후 침식"""
    kernel = np.ones(kernel_size, np.uint8)
    return cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)

