from supports.date_time_file_name import get_time_full
from threading import Thread, Lock
import cv2
import time
from communicate.issue_api import send_issue


class IssueThread:
    def __init__(self,carID) :
        self.started = False
        self.canSend =None
        self.carID = carID
        self.issueType = None
        self.frame_issue = None
        self.isEnable = True
        self.read_lock = Lock() 

    def start(self) :
        if self.started :
            return None
        self.started = True
        self.thread = Thread(target=self.update, args=())
        self.thread.start()
        return self

    def update(self) :
        while self.started:
            self.read_lock.acquire()
            self.send_issue()
            self.read_lock.release()
    
    def reset_status(self,):
        self.canSend = None
        self.frame_issue = None
        time.sleep(0.1)
    
    def set_set_issue(self,frame,issueType):
        if self.canSend == None:
            self.canSend = True
        self.frame_issue = frame
        self.issueType = issueType
        
    
    def send_issue(self):
        if self.isEnable:
            if self.canSend and self.frame_issue is not None:
                print("issue")
                self.canSend = False
                name_save = get_time_full() + "__" +str(self.issueType) + ".jpg"
                msg = "Can't detect lane ahead, the car has stopped automatically" 
                if self.issueType == 2:
                    msg = "Detected obstacle ahead, the car has stopped automatically"
                # print(name_save)
                temp = cv2.imwrite(f'logging/{name_save}',self.frame_issue)
                with open(f'logging/{name_save}','rb') as f:
                    response = send_issue(self.issueType,self.carID, 'location', msg,f)
                print(response.content)
                if(response.status_code==201):
                    print("send issue success")
                time.sleep(0.1)


    def read(self) :
        self.read_lock.acquire()
        frame = self.frame.copy()
        self.read_lock.release()
        return frame

    def stop(self) :
        self.started = False
        self.thread.join()

    
