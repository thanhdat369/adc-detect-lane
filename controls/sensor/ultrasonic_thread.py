from config.configDTO import ConfigDTO
from threading import Thread, Lock,Event
import time
import pigpio

class UltraSonicSensorThread:
    def __init__(self,pi,config):
        # config = ConfigDTO(*config)
        self.hardware_config = config.hardware_config
        self.TRIGGER_PORT = self.hardware_config.trigger_port
        self.ECHO_PORT = self.hardware_config.echo_port
        print(f"TRIGGER {self.TRIGGER_PORT} ECHO {self.ECHO_PORT}")
        self.pi = pi
        self.started = False
        self.distance = -1
        self.__init_hardware()
        self.done = Event()
        self.read_lock = Lock() 

    def __init_hardware(self,):
        self.pi.set_mode(self.TRIGGER_PORT, pigpio.OUTPUT)
        self.pi.set_mode(self.ECHO_PORT, pigpio.INPUT)
        self.pi.callback(self.ECHO_PORT, pigpio.RISING_EDGE, self.rise)
        self.pi.callback(self.ECHO_PORT, pigpio.FALLING_EDGE, self.fall)
    
    def rise(self,gpio, level, tick):
        global high
        high = tick

    def fall(self,gpio, level, tick):
        global low
        low = tick - high
        self.done.set()

    def read_distance(self,):
        global low
        self.done.clear()
        if self.pi is None:
            return None
        else:
            self.pi.gpio_trigger(self.TRIGGER_PORT, 50, 1)
            if self.done.wait(timeout=5):
                return low / 58.0 


    def start(self):
        if self.started :
            print("UltraSonicSensorThread start")
            return None
        self.started = True
        self.thread = Thread(target=self.update, args=())
        self.thread.start()
        return self
    
    def update(self) :
        while self.started:
            self.read_lock.acquire()
            num_measure = 5
            distance = 0
            isFail = False
            for i in range(num_measure):
                time.sleep(0.05)
                curr_distance = self.read_distance()
                if curr_distance is None:
                    isFail = True
                    continue
                else:
                    distance = distance + curr_distance
            if isFail:
                self.distance = None
            else:
                self.distance = distance/num_measure
            # print(self.distance)
            self.read_lock.release()

    def stop(self) :
        self.started = False

    def __exit__(self, exc_type, exc_value, traceback) :
        pass
        
