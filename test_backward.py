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
time.sleep(1)

def stopCar():
    control_car_obj.stop()
    exit()

#__PROCESSING__
control_car_obj.reverse_car()

time.sleep(3)

stopCar()
