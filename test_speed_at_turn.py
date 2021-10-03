from cv2 import cv2
import time
#CONFIG 
from config import speed_config as speed_cfg
from config import system_config as sys_cfg

from detect_lane.two_middle.two_middile_manager import TwoMidMethodManager
from camera.camera import CameraGet
from controls.control_car import ControlCar
# from controls.car_state_dto import CarStateDTO

CAMERA_INDEX = sys_cfg.CAMERA_INDEX

#set_default_config
SPEED_UP_VAL = speed_cfg.SPEED_UP_SPEED_VAL
SLOW_DOWN_VAL = speed_cfg.SLOW_DOWN_SPEED_VAL
NORMAL_SPEED_VAL = speed_cfg.NORMAL_SPEED_VAL
PAUSE_SPEED_VAL = speed_cfg.PAUSE_SPEED_VAL

#Prepair_for_running
control_car_obj = ControlCar(NORMAL_SPEED_VAL)
control_car_obj.prepair_run()
time.sleep(1)

#Start_motor
control_car_obj.car_state.set_motor_value(NORMAL_SPEED_VAL)
control_car_obj.control_speed()

#Start_Camera
cam = CameraGet(CAMERA_INDEX).start() 

#Proccess_detect_lane (1st Thread)
detect_lane = TwoMidMethodManager(cam.frame)
detect_lane.start()

#Check_Lane_Missing_Variable
is_missing_lane = False

#End_processing_car
def stopCar():
    control_car_obj.stop()
    cam.stop()
    detect_lane.stop()
    exit()

#__PROCESSING__
while(True):
    try:
        #set_key
        key = cv2.waitKey(1)
        if(key==ord('q')):
            break
        #Set_frame
        frame = cam.frame
        detect_lane.frame = frame
        #Set_image
        final_image = detect_lane.final_image
        #Set_l1
        l1 = detect_lane.l1
        #Set_servo
        servo_value = detect_lane.servo_val
        if(servo_value is None):
            continue
        #xu ly chay nhanh cham
        if(servo_value<1300 or servo_value>1700):
            control_car_obj.car_state.set_motor_value(SLOW_DOWN_VAL) 
            control_car_obj.control_speed()
        elif(servo_value>1300 and servo_value<1700):
            control_car_obj.car_state.set_motor_value(NORMAL_SPEED_VAL) 
            control_car_obj.control_speed()
            
        if servo_value is not None:
            control_car_obj.car_state.set_servo_value(servo_value) 
            control_car_obj.control_servo()

        
        

        #Check the lane width
        if(l1 is not None):
            if(l1>620):
                # print('no lane detect')
                is_missing_lane = True
                control_car_obj.car_state.set_motor_value(PAUSE_SPEED_VAL)
                control_car_obj.control_speed()
            else:
                if is_missing_lane:
                    print("Detecting lanes")
                    control_car_obj.car_state.set_motor_value(NORMAL_SPEED_VAL)
                    control_car_obj.control_speed()
                    is_missing_lane = False                           
        else:
            print("Sleep")
            time.sleep(0.2)

        if frame is not None and final_image is not None:
            cv2.imshow('frame',frame)
            cv2.imshow('fn2',final_image)
            #cv2.imshow('fn_2',final2)
        if (cam.grabbed==False):
            break

    except Exception as e:
        print("ERRRORR")
        print(e)
        stopCar()
stopCar()
