import pigpio
import time
pi = pigpio.pi()

pi.set_servo_pulsewidth(12, 0)  
pi.set_servo_pulsewidth(13, 0) 