import timeit
from cv2 import cv2
import time

from detect_lane.two_middle.two_middile_manager import TwoMidMethodManager
from camera.camera import CameraGet
from controls.control_car import ControlCar
from config.debug_device import RUN_ON_PI
from config.config_load import *


time.sleep(4)
if RUN_ON_PI:
    import pigpio
    pi = pigpio.pi()
else:
    pi = None

#Prepair_for_running
control_car_obj = ControlCar(NORMAL_SPEED_VAL,pi,all_config)
control_car_obj.prepair_run()
time.sleep(1)

#Start_motor
control_car_obj.car_state.set_motor_value(NORMAL_SPEED_VAL)
control_car_obj.control_speed()

#Start_Camera
cam = CameraGet(CAMERA_INDEX).start() 

#Proccess_detect_lane (1st Thread)
detect_lane = TwoMidMethodManager(cam.frame,all_config)
detect_lane.start()

#Check_Lane_Missing_Variable
is_missing_lane = False

#End_processing_car
def stopCar():
    control_car_obj.stop()
    cam.stop()
    detect_lane.stop()
    exit()
curr_speed = NORMAL_SPEED_VAL

isChange = False

star_time = timeit.default_timer()
#__PROCESSING__
while(True):
    try:
        #set_key
        key = cv2.waitKey(1)
        if(key==ord('q')):
            break
        #Set_frame
        if timeit.default_timer()- star_time >6:
            isChange = True
        frame = cam.frame
        detect_lane.frame = frame
        #Set_image
        final_image = detect_lane.final_image
        #Set_l1
        l1 = detect_lane.l1
        #Set_servo
        servo_value = detect_lane.servo_val
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
                if isChange:
                    control_car_obj.car_state.set_motor_value(SLOW_DOWN_VAL)
                    control_car_obj.control_speed()
                    print("Change")
                if is_missing_lane:
                    print("Detecting lanes")
                    control_car_obj.car_state.set_motor_value(curr_speed)
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
    except KeyboardInterrupt:
        stopCar()
stopCar()
