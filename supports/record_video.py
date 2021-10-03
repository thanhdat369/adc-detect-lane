import numpy as np
import cv2
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--name", "-n", help="name")
args = parser.parse_args()
if args.name:
    print(args.name)
    
fourcc = cv2.VideoWriter_fourcc(*'XVID')
# out = cv2.VideoWriter('output.avi',fourcc, 1.0, (640,480))
out = cv2.VideoWriter(args.name,fourcc, 30.0,(640,480))
cap = cv2.VideoCapture(0)
record = False
while(True):
    ret, frame = cap.read()
    if record:
        out.write(frame)

    cv2.imshow('frame',frame)
    key = cv2.waitKey(1)
    if(key==ord('p')):
        record = True
    if(key==ord('q')):
        break

cap.release()
out.release()
cv2.destroyAllWindows()