import math
import numpy as np
from cv2 import cv2
from supports.draw import draw_line
import supports.draw as draw
from detect_lane.image_process import image_process as img_process

from config.configDTO import ConfigDTO

#Threadholds
LOW_THRESHOLD = 100
HIGH_THRESHOLD = 255


#CENTER_SERVO

#Kernel_size
kernel_size = 3

coff = math.atan(50/(100))        

class Method2Middle:
    def __init__(self,config):
        # config = ConfigDTO(*config)
        self.servo_config = config.servo_config
        self.speed_config = config.speed_config
        self.detect_lane_config = config.detect_lane_config

    def preprocess(self,img):
        #GRAYSCALE
        gray_img = img_process.grayscale(img)
        # h, w  = gray_img.shape
        
        #BLUR
        blurred_gray = img_process.gaussian_blur(gray_img,kernel_size)

        #remove thin line
        kernel_erosion = np.ones((2, 2), np.uint8)
        kernel_dilate = np.ones((3, 3), np.uint8)
        dilate = cv2.dilate(
            blurred_gray,  kernel_dilate, iterations=1)
        erosion = cv2.erode(
            dilate,  kernel_erosion, iterations=2)
        
        # CANNY
        edges_image = cv2.Canny(erosion, LOW_THRESHOLD, HIGH_THRESHOLD)

        return edges_image

    def calculate_weight(self,center_point):
        res_val = self.servo_config.center_servo
        # threshold = 35
        threshold = self.detect_lane_config.threshold_lane_px

        # nếu camera bị khuất góc khi nhìn rẽ thì sẽ như vậy
        # fig1
        if abs(320-center_point[1]) > 150:
            if(320-center_point[1] > 150):
                # print("L")
                return self.servo_config.max_left
            else: 
                # print("R")
                return self.servo_config.max_right

        cal_val = center_point[0]-center_point[1]

        #Process_servo_value
        if(cal_val > threshold):
            # print("R")
            return self.servo_config.max_right
        elif (cal_val < -threshold):
            # print("L")
            return self.servo_config.max_left
        else:
            res_val = self.servo_config.center_servo - int((math.atan((cal_val)/(threshold*2))*500)/coff)
        return res_val
   

    #FUNCTION GET LEFT RIGHT POINT

    def getLeftRightPoint(self,img,CENTER_W,CENTER_H):
        L = CENTER_W
        while True:
            if img[CENTER_H,L] > 250:
                break
            if L <= 5:
                break
            L = L - 1
        R = CENTER_W
        while True:                               
            if img[CENTER_H,R]  > 250:
                break
            if R >= 635:
                break
            R = R + 1
        return L,R

    def get_point(self,img):
        MID_W = self.detect_lane_config.width_center_point 
        LOW_H = self.detect_lane_config.low_h 
        HIGH_H = self.detect_lane_config.high_h 
        L2,R2 = self.getLeftRightPoint(img,MID_W,LOW_H)
        C2 = (L2+R2)/2
        M2 = int(C2)
        L1,R1 = self.getLeftRightPoint(img,M2,HIGH_H)
        C1 = (L1+R1)/2
        return (C1,C2),(L1,R1),(L2,R2)


    def process(self,image):
        LOW_H = self.detect_lane_config.low_h 
        HIGH_H = self.detect_lane_config.high_h 
        #GET CENTER AND WEIGHT
        edges_image = self.preprocess(image)
        center,X1,X2 = self.get_point(edges_image)
        #DRAW IMAGE
        final_image = cv2.cvtColor(edges_image,cv2.COLOR_GRAY2BGR)
        final_image = draw_line(final_image,(X1[0],HIGH_H),(X2[0],LOW_H),draw.COLOR_BLUE)
        final_image = draw_line(final_image,(X1[1],HIGH_H),(X2[1],LOW_H),draw.COLOR_BLUE)
        # final_image = draw_lines_2(final_image,(center[0],HIGH_H),(center[1],LOW_H))
        final_image = draw_line(final_image,(center[0],HIGH_H),(center[1],LOW_H),draw.COLOR_RED)
        l1  = X1[1]-X1[0]
        return final_image,center,l1
