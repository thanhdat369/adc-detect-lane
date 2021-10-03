from sign_detect.yolo.detect import YoloDetect
from threading import Thread, Lock
import cv2
import logging
import time
detect_sign = YoloDetect()

class YOLOThread:
    def __init__(self, frame) :
        self.started = False
        self.frame = frame
        self.sign_name = None
        self.final_image = None
        self.read_lock = Lock() 

    def start(self) :
        if self.started :
            logging.info("already started!!")
            return None
        self.started = True
        self.thread = Thread(target=self.update, args=())
        self.thread.start()
        return self

    def update(self) :
        while self.started:
            self.read_lock.acquire()
            sign_name = detect_sign.detect_return_sign_name(self.frame)
            #sign_name = None
            #self.final_image = detect_sign.detect_return_image(self.frame)
            self.sign_name = sign_name
            self.read_lock.release()
            time.sleep(0.1)

    def read(self) :
        self.read_lock.acquire()
        frame = self.frame.copy()
        self.read_lock.release()
        return frame

    def stop(self) :
        self.started = False
        self.thread.join()

    
