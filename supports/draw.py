import cv2 

#BGR COLOR
COLOR_RED = (0,0,255)
COLOR_GREEN = (0,255,0)
COLOR_BLUE = (255,0,0)

#POSITION
POS_TOP_LEFT = (0, 30)
POS_TOP_RIGHT = (600, 30)
POS_BOTTOM_LEFT = (0,460)
POS_BOTTOM_RIGHT = (0, 30)

def draw_line(img,p1,p2,COLOR):
    p1 = (int(p1[0]),int(p1[1]))
    p2 = (int(p2[0]),int(p2[1]))
    final_image = cv2.line(img,p1,p2,COLOR,6)
    return final_image

def draw_dot(img,p):
    p = (int(p[0]),int(p[1]))
    final_image = cv2.circle(img,p,5,(255,0,0),-1)    
    return final_image

def put_text(img,content,POSITION,COLOR):
    #TODO
    font = cv2.FONT_HERSHEY_SIMPLEX 
    org = POSITION
    fontScale = 1
    color = COLOR
    thickness = 2
    image_final = cv2.putText(image_final, content, org, font, fontScale,  
                     color, thickness, cv2.LINE_AA, False) 
    return image_final