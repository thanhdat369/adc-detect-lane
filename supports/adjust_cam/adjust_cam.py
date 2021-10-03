CAMERA_INDEX = 0
STD_IMAGE_PATH = 'supports/adjust_cam/std_image.jpg'
SIZE = (640,480)
import cv2
std_img = cv2.imread(STD_IMAGE_PATH)
std_img = cv2.resize(std_img,SIZE)
def overlay(org_img):
    org_img = cv2.resize(org_img,SIZE)
    im_result = cv2.addWeighted(org_img,0.6,std_img,0.7,0)
    return im_result


cap = cv2.VideoCapture(CAMERA_INDEX)

while True:
    ret,frame = cap.read()
    img_result = overlay(frame)
    cv2.imshow('mat',img_result)
    key = cv2.waitKey(1)
    if key == ord('q'):
        break
