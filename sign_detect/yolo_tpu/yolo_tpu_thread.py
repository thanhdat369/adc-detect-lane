from sign_detect.yolo_tpu.detect_class import TrafficDetector
from threading import Thread, Lock
import cv2
import logging
import time

class YOLOTPUThread:
    def __init__(self, frame) :
        self.started = False
        self.detect_sign = TrafficDetector(model_path='sign_detect/yolo_tpu/model/last_yolo_edgetpu.tflite',
                                            edge_tpu=True,threshold=0.8)
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
            # frame = cv2.cvtColor(self.frame,cv2.COLOR_BGR2RGB)
            final_image,sign_name = self.detect_sign.draw_image(self.frame)
            self.final_image = cv2.resize(final_image,(1280,960))
            # self.final_image = final_image
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
        # self.detect_sign.stop()
        self.thread.join()

    
