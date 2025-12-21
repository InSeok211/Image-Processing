"""이미지 변환 함수들"""
import cv2
import numpy as np


def adjust_brightness(image, value):
    """밝기 조절"""
    return cv2.convertScaleAbs(image, alpha=1, beta=value)


def adjust_contrast(image, value):
    """명암 대비 조절"""
    return cv2.convertScaleAbs(image, alpha=value, beta=0)


def scale_image(image, scale_percent):
    """확대/축소"""
    scale_factor = scale_percent / 100.0
    height, width = image.shape[:2]
    new_width = int(width * scale_factor)
    new_height = int(height * scale_factor)
    return cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_LINEAR)


def translate_image(image, tx, ty):
    """평행이동"""
    height, width = image.shape[:2]
    M = np.float32([[1, 0, tx], [0, 1, ty]])
    return cv2.warpAffine(image, M, (width, height))


def rotate_image(image, angle):
    """회전"""
    height, width = image.shape[:2]
    center = (width // 2, height // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    return cv2.warpAffine(image, M, (width, height))


