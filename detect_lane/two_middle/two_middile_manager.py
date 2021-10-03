import logging
# from camera.camera import CameraGet
from threading import Thread, Lock
from detect_lane.two_middle.two_middle import Method2Middle
# import time

class TwoMidMethodManager:
    def __init__(self,frame,config):
        self.detect_lane = Method2Middle(config)
        self.started = False
        self.frame = frame
        self.l1 = None
        self.final_image = None
        self.center = None
        self.servo_val = None
        self.read_lock = Lock() 
    
    def start(self):
        if self.started :
            logging.info("already started hello!!")
            return None
        self.started = True
        self.thread = Thread(target=self.update, args=())
        self.thread.start()
        return self
    
    def update(self) :
        while self.started:
            self.read_lock.acquire()
            final_image,center,l1 = self.detect_lane.process(self.frame)
            self.l1 = l1
            self.final_image = final_image
            self.center = center
            self.servo_val = self.detect_lane.calculate_weight(center)
            #time.sleep(0.01)
            self.read_lock.release()

    def stop(self) :
        self.started = False
        self.thread.join()

    def __exit__(self, exc_type, exc_value, traceback) :
        pass
        
