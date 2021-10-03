from cv2 import cv2
import time
from camera.camera import CameraGet
# from sign_detect.ssd.ssd_detect_thread import SSDDetectThread
from sign_detect.yolo_tpu.yolo_tpu_thread import YOLOTPUThread
from config.config_load import *


cam = CameraGet(CAMERA_INDEX).start() 
frame = cam.frame
detect_sign = YOLOTPUThread(frame)
detect_sign.frame = frame
detect_sign.start()
final_image = None
while(True):
    try:
        key = cv2.waitKey(1)
        if(key==ord('q')):
            break
        if(key==ord('p')):
            cv2.imwrite('frame.jpg',frame)
            cv2.imwrite('fn.jpg',final_image)
        #Set_frame
        frame = cam.frame
        detect_sign.frame = frame
        #Set_image
        final_image = detect_sign.final_image
        class_name = detect_sign.sign_name
        if class_name is not None:
            print(class_name,end = "\r")

        if frame is not None and final_image is not None:
            cv2.imshow('frame',frame)
            cv2.imshow('fn2',final_image)
        if (cam.grabbed==False):
            break

    except Exception as e:
        cam.stop()
        detect_sign.stop()
        cv2.destroyAllWindows()
        print("ERRRORR")
        print(e)

detect_sign.stop()
cam.stop()
cv2.destroyAllWindows()
exit()