from cv2 import cv2
import time
from config import system_config as sys_cfg
from camera.camera import CameraGet
from sign_detect.ssd.ssd_detect_thread import SSDDetectThread
CAMERA_INDEX = sys_cfg.CAMERA_INDEX


cam = CameraGet(CAMERA_INDEX).start() 
frame = cam.frame
detect_sign = SSDDetectThread(frame)
detect_sign.start()
while(True):
    try:
       
        key = cv2.waitKey(1)
        if(key==ord('q')):
            break
        #Set_frame
        frame = cam.frame
        detect_sign.frame = frame
        #Set_image
        final_image = detect_sign.final_image
        
 
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