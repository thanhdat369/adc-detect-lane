import cv2 
import numpy as np

CENTER_POINT = 320
H_2 = 400
THRESHOLD_RED_PIXEL = 500
def crop_region_pos():
    x_c = int(CENTER_POINT)
    y_c = int(HIGH_H)

    x1 = x_c-200 if (x_c-200 > 0) else 0
    y1 = y_c-100
    x2 = x_c+200 if (x_c+200 < 639) else 638
    y2 = y_c-50
    
    return (x1,y1),(x2,y2)

def getCropImage(image,center_point):
    p1,p2 = crop_region_pos()
    x1,y1 = p1
    x2,y2 = p2
    crop_img = frame[y1:y2,x1:x2]
    return crop_img


def detect_redline_in_front(img_crop):
    lower = np.array([30,30 , 80],dtype=np.uint8)
    upper = np.array([80, 80, 150],dtype=np.uint8)
    detect_image = cv2.inRange(img_crop,lower,upper)
    return detect_image
    
def get_number_red_pixel(detect_image):
    num_mask = detect_image.shape[0]*detect_image.shape[1]
    value_red = np.count_nonzero(detect_image)
    return value_red

def is_redline_in_front(image):
    cropImage = getCropImage(image)
    detect_image = detect_redline_in_front(cropImage)
    number_red_pixel = get_number_red_pixel(detect_image)
    if number_red_pixel > THRESHOLD_RED_PIXEL:
        return True
    else:
        return False        