import numpy as np
from cv2 import cv2
from config import detectlane_config as cfg
from detect_lane.image_process import image_process as img_process

def get_point(img):
    L = cfg.WIDTH_CENTER_POINT
    while True:
        if img[cfg.HEIGHT_CENTER_POINT,L] > 250:
            break
        if L <= 5:
            break
        L = L - 1
    R = cfg.WIDTH_CENTER_POINT
    while True:
        if img[cfg.HEIGHT_CENTER_POINT,R]  > 250:
            break
        if R >= 635:
            break
        R = R + 1     
    center = (L+R)/2
    return center,L,R

def process(image):
    
    gray_img = img_process.grayscale(image)

    h, w  = gray_img.shape

    #BLUR
    kernel_size = 5
    blurred_gray = img_process.gaussian_blur(gray_img, kernel_size)
    
    #CANNY
    low_threshold = 20
    high_threshold = 255
    edges_image = cv2.Canny(blurred_gray, low_threshold, high_threshold)

    #GET CENTER AND WEIGHT
    center,L,R = get_point(edges_image)


    #DRAW IMAGE
    final_image = cv2.cvtColor(edges_image,cv2.COLOR_GRAY2BGR)
    final_image = cv2.circle(final_image,(L,cfg.HEIGHT_CENTER_POINT),5,(255,0,0),-1)
    final_image = cv2.circle(final_image,(R,cfg.HEIGHT_CENTER_POINT),5,(255,0,0),-1)

    final_image = cv2.line(final_image,(int(w/2),int(h)),(int(center),cfg.HEIGHT_CENTER_POINT),(255,0,0),6)

    return final_image,blurred_gray,center
