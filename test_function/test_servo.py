import pigpio
import time
pi = pigpio.pi()

pi.set_servo_pulsewidth(12, 0)    # off
pi.set_servo_pulsewidth(13, 0)    # off1

time.sleep(1)
pi.set_servo_pulsewidth(13, 1500)    # off

while(True):
    print('enter: ')
    x = input()
    val = int(x)
    if(val == 1700):
        break
    if(val == 0):
        pi.set_servo_pulsewidth(13,0) 
    if(val == 1):
        pi.set_servo_pulsewidth(13,1605) 

    print(val)
    if(val>1000 and val < 1900):
        pi.set_servo_pulsewidth(12,val) # right
        
    time.sleep(0.5)

pi.set_servo_pulsewidth(13, 0)    # off

pi.set_servo_pulsewidth(12, 0)    # off
pi.stop()
