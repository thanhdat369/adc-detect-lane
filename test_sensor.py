from controls.sensor.ultrasonic_thread import UltraSonicSensorThread
import timeit
import pigpio
import time
from config.config_load import *
pi = pigpio.pi()
time.sleep(0.5)
ultrasonic_distance_thread = UltraSonicSensorThread(pi,all_config)
ultrasonic_distance_thread.start()
time.sleep(0.5)
start_time = timeit.default_timer()
while True:
    distance = ultrasonic_distance_thread.distance
    print('distance ', distance)
    if(timeit.default_timer()-start_time>10):
        break

ultrasonic_distance_thread.stop()
