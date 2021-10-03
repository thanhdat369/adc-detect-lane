#LIBRARY_IMPORT
from cv2 import cv2

#CONVERT_IMAGE_TO_GRAYSCALE
def grayscale(img):
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

#APPLY_CANNY
def canny(img, low_threshold, high_threshold):
    return cv2.Canny(img, low_threshold, high_threshold)

#APPLY_GAUSSIAN_BLUR
def gaussian_blur(img, kernel_size):
    return cv2.GaussianBlur(img, (kernel_size, kernel_size), 0)

