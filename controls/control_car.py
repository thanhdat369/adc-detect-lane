#LIBRARY_IMPORT
from config.configDTO import ConfigDTO
import time
#PACKAGE_IMPORT
from controls.car_state_dto import CarStateDTO
#DEVICE RUN
from config.debug_device import RUN_ON_PI

MOTOR_OFF = 0
SERVO_OFF = 0

#__MOTOR_CONSTANT__
#GPIO

#OFF_VALUE

#DELAY_TIME_ON_PROCESS
PROCESS_DELAY = 1

#__CLASS_CONTROL_CAR__
class ControlCar:
    #INIT
    def __init__(self,speed,pi,config):
        self.pi = pi
        # config = ConfigDTO(*config)
        self.MOTOR_PORT = config.hardware_config.motor_port
        self.SERVO_PORT = config.hardware_config.servo_port
        self.motor_config = config.speed_config
        self.servo_config = config.servo_config
        self.MOTOR_PREPAIR = self.motor_config.pause_speed_val
        #OFF_CAR
        self.__set_servo_pulsewidth(self.MOTOR_PORT, MOTOR_OFF)    
        self.__set_servo_pulsewidth(self.SERVO_PORT, SERVO_OFF)
        self.__set_servo_pulsewidth(self.MOTOR_PORT, self.MOTOR_PREPAIR) 
        #WAITING

        self.car_state = CarStateDTO(motor_value=speed,servo_value=SERVO_OFF)

        time.sleep(PROCESS_DELAY)
        
    #SET_VALUE_CAR
    def __set_servo_pulsewidth(self,gpio_port,value):
        # pass
        if RUN_ON_PI:
            # if gpio_port==self.MOTOR_PORT:
            #     print(f"RUN : {gpio_port} - {value}") 
            if self.pi is not None:
                self.pi.set_servo_pulsewidth(gpio_port, value)
        else:
            print(f"RUN: {gpio_port} - {value}") 

    #BOOTING_PREPAIR
    def prepair_run(self,):
        print("PREPAIR")
        self.__set_servo_pulsewidth(self.MOTOR_PORT, self.MOTOR_PREPAIR) 

    def reverse_car(self,):
        self.__set_servo_pulsewidth(self.MOTOR_PORT,self.MOTOR_PREPAIR)
        time.sleep(0.05)
        self.__set_servo_pulsewidth(self.MOTOR_PORT,self.motor_config.backward_speed_val)
        time.sleep(0.05)
        self.__set_servo_pulsewidth(self.MOTOR_PORT,self.MOTOR_PREPAIR)
        time.sleep(0.05)
        self.__set_servo_pulsewidth(self.MOTOR_PORT,self.motor_config.backward_speed_val)

    #STOP_CAR
    def stop(self,):
        self.__set_servo_pulsewidth(self.MOTOR_PORT, MOTOR_OFF)
        self.__set_servo_pulsewidth(self.SERVO_PORT, SERVO_OFF)

    #SET_VALUE_SERVO
    def control_servo(self,):
        cal_val = self.car_state.get_servo_value()
        if(cal_val>=self.servo_config.max_right and cal_val <= self.servo_config.max_left):
            self.__set_servo_pulsewidth(self.SERVO_PORT,cal_val)
        else:
            print("OVER_SERVO_ERROR ",cal_val)
            self.stop()
    #SET_VALUE_MOTOR
    def control_speed(self,):
        speed_val = self.car_state.get_motor_value()
        if(speed_val>1400 and speed_val < 1630):
            self.__set_servo_pulsewidth(self.MOTOR_PORT,speed_val)
        else:
            print("OVER_MOTOR_ERROR")
            self.stop()
