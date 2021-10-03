from communicate.mock_session import MockSession
from controls.sensor.ultrasonic_thread import UltraSonicSensorThread
from cv2 import cv2
import time
import timeit

from communicate.signalR_car import SignalR
from detect_lane.two_middle.two_middile_manager import TwoMidMethodManager
from camera.camera import CameraGet
from controls.control_car import ControlCar
from sign_detect.yolo_tpu.yolo_tpu_thread import YOLOTPUThread
#CONFIG
from config.debug_device import RUN_ON_PI
from config.config_load import *
from communicate.issue_thread import IssueThread
import communicate.issueType as issueType

if RUN_ON_PI:
    import pigpio
    pi = pigpio.pi()
else:
    pi = None

def handle_car_run(car_obj,speed):
    car_obj.car_state.set_motor_value(speed)
    car_obj.control_speed()


NO_TURN = 0
LEFT_TURN = 2003
RIGHT_TURN = 1003
FORWARD = 1503
turn_mode = NO_TURN
has_turned = False
def process_traffic_sign(class_name):
    global curr_speed
    global turn_mode 
    if class_name == "turn_left":
        print("HHHHH")
        turn_mode = LEFT_TURN
    elif class_name == "turn_right":
        turn_mode = RIGHT_TURN
    elif class_name == "foward":
        turn_mode = FORWARD
    elif class_name == "slow_down":
        curr_speed = SLOW_DOWN_VAL
    elif class_name == "speed_up":
        curr_speed = SPEED_UP_VAL


#getSignalR
stopBySignalR = True
# stopBySignalR = False

signalR = SignalR('https://avc-api.azurewebsites.net/hub')
signalR.connect()
start_time = timeit.default_timer()
while stopBySignalR:
    stopBySignalR = signalR.stopSignal
    # if MockSession.deviceDTO is not None:
    #     print(MockSession.deviceDTO.modelUrl)
    print("Wating .",end = '\r')
    if(timeit.default_timer()-start_time>TIMEOUT):
        print("time out")
        exit()


#Start_Camera
cam = CameraGet(CAMERA_INDEX).start()
frame = cam.frame
#Prepair_for_running
control_car_obj = ControlCar(NORMAL_SPEED_VAL,pi,all_config)

#Proccess_detect_lane (1st Thread)
detect_lane = TwoMidMethodManager(cam.frame,all_config)
detect_lane.start()

#ULTRASONIC
ultrasonic_distance_thread = UltraSonicSensorThread(pi,all_config)
ultrasonic_distance_thread.start()
time.sleep(1)

control_car_obj.prepair_run()
time.sleep(1)
#Start_motor


detect_sign = YOLOTPUThread(frame)
detect_sign.frame = frame
detect_sign.start()

issue_thread = IssueThread(MockSession.deviceDTO.id)
issue_thread.start()
issue_thread.isEnable = True

# Check_Lane_Missing_Variable
is_missing_lane = False

isStopBySignalR = False

isStopByObstacle = False

isStopByRedLight = False

curr_speed = NORMAL_SPEED_VAL
control_car_obj.car_state.set_motor_value(curr_speed)
control_car_obj.control_speed()

# #End_processing_car
def stopCar():
    ultrasonic_distance_thread.stop()
    control_car_obj.stop()
    detect_sign.stop()
    detect_lane.stop()
    signalR.stop()
    issue_thread.stop()
    #SLEEP FOR TURN OFF THREAD REF TO PI
    time.sleep(1)
    if pi is not None:
        pi.stop()
    cam.stop()
    exit()
final_image = None

#__PROCESSING__
while(True):
    try:
        if frame is not None and final_image is not None:
            cv2.imshow('frame',frame)
            cv2.imshow('fn2',final_image)
            #cv2.imshow('fn_2',final2)
        if (cam.grabbed==False):
            break
        #set_key
        key = cv2.waitKey(1)
        if(key==ord('q')):
            break
        #Set_frame
        frame = cam.frame
        detect_sign.frame = frame
        
        final_detect_image = detect_sign.final_image
        class_name = detect_sign.sign_name
       
        if class_name =="stop":
            break

        if signalR.stopSignal:
            isStopBySignalR = True
            print("STOP BY SIGNAL R",end = '\r')
        else:
            if isStopBySignalR:
                isStopBySignalR = False
                handle_car_run(car_obj=control_car_obj,speed=curr_speed)


        if class_name == "red":
            print("STOP BY RED LIGHT",end='\r')
            isStopByRedLight = True
        
        if class_name == "green" and isStopByRedLight:
            print("GREEN LIGHT",end='\r')
            isStopByRedLight = False
            handle_car_run(car_obj=control_car_obj,speed=curr_speed)
        
        process_traffic_sign(class_name=class_name)
        # print(class_name)

        distance2obstacle = ultrasonic_distance_thread.distance
        if distance2obstacle is not None:
            if distance2obstacle<50:
                print(f"stop by obstacle {distance2obstacle}",end='\r')
                isStopByObstacle = True
                issue_thread.set_set_issue(frame,issueType.OBSTACLE_DETECTED)
            else:
                if isStopByObstacle:
                    issue_thread.reset_status()
                    isStopByObstacle = False
                    handle_car_run(car_obj=control_car_obj,speed=curr_speed)

        if isStopBySignalR or isStopByRedLight or isStopByObstacle:
            handle_car_run(car_obj=control_car_obj,speed=PAUSE_SPEED_VAL)
            continue
        
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
                if(turn_mode!=NO_TURN and has_turned==False):
                    count_to_deactivate = 0
                    control_car_obj.car_state.set_servo_value(turn_mode) 
                    control_car_obj.control_servo()
                    has_turned = True
                    time.sleep(2.5)
                else:
                    print('no lane detect',end='\r')
                    is_missing_lane = True
                    handle_car_run(car_obj=control_car_obj,speed=PAUSE_SPEED_VAL)
                    issue_thread.set_set_issue(frame,issueType.NO_LANE_DETECT)
            else:
                if(turn_mode!=NO_TURN and has_turned):
                    count_to_deactivate += 1
                    if(count_to_deactivate > 5):
                        turn_mode = NO_TURN
                        has_turned = True
                if is_missing_lane:
                    print("Detecting lanes")
                    handle_car_run(car_obj=control_car_obj,speed=curr_speed)
                    is_missing_lane = False                           
                    issue_thread.reset_status()
        else:
            print("Sleep")
            time.sleep(0.2)

    except Exception as e:
        print("ERRRORR")
        print(e)
        stopCar()
    except KeyboardInterrupt:
        stopCar()
stopCar()
