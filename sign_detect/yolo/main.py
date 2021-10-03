import tensorflow as tf
import config as cfg
from PIL import Image
import cv2
import numpy as np
from tensorflow.compat.v1 import ConfigProto
from tensorflow.compat.v1 import InteractiveSession

framework = 'tflite'
score_threshole = 0.8
iou_threshole = 0.15
CLASS = ['SLOWDOWN','SPEED UP','STOP']

def load_config():
    STRIDES = np.array([16, 32])
    anchors = np.array([23,27, 37,58, 81,82, 81,82, 135,169, 344,319])
    ANCHORS = anchors.reshape(2, 3, 2)
    XYSCALE = [1.05, 1.05]
    NUM_CLASS = 3
    return STRIDES, ANCHORS, NUM_CLASS, XYSCALE
def filter_boxes(box_xywh, scores, score_threshold=0.4, input_shape = tf.constant([416,416])):
    scores_max = tf.math.reduce_max(scores, axis=-1)

    mask = scores_max >= score_threshold
    class_boxes = tf.boolean_mask(box_xywh, mask)
    pred_conf = tf.boolean_mask(scores, mask)
    class_boxes = tf.reshape(class_boxes, [tf.shape(scores)[0], -1, tf.shape(class_boxes)[-1]])
    pred_conf = tf.reshape(pred_conf, [tf.shape(scores)[0], -1, tf.shape(pred_conf)[-1]])

    box_xy, box_wh = tf.split(class_boxes, (2, 2), axis=-1)

    input_shape = tf.cast(input_shape, dtype=tf.float32)

    box_yx = box_xy[..., ::-1]
    box_hw = box_wh[..., ::-1]

    box_mins = (box_yx - (box_hw / 2.)) / input_shape
    box_maxes = (box_yx + (box_hw / 2.)) / input_shape
    boxes = tf.concat([
        box_mins[..., 0:1],  # y_min
        box_mins[..., 1:2],  # x_min
        box_maxes[..., 0:1],  # y_max
        box_maxes[..., 1:2]  # x_max
    ], axis=-1)
    # return tf.concat([boxes, pred_conf], axis=-1)
    return (boxes, pred_conf)

def draw_bbox(image,pred_bbox):
    
    image_h, image_w, _ = image.shape

    out_boxes, out_scores, out_classes, num_boxes = pred_bbox

    for i in range(num_boxes[0]):
        # if int(out_classes[0][i]) < 0 or int(out_classes[0][i]) > 3: continue
        coor = out_boxes[0][i]
        coor[0] = int(coor[0] * image_h)
        coor[2] = int(coor[2] * image_h)
        coor[1] = int(coor[1] * image_w)
        coor[3] = int(coor[3] * image_w)
        fontScale = 0.25
        score = out_scores[0][i]
        c1, c2 = (coor[1], coor[0]), (coor[3], coor[2])
        image = cv2.rectangle(image, c1, c2, (0,255,255), 2)
        class_ind = int(out_classes[0][i])
        class_name = CLASS[class_ind]
        if(class_name == "STOP"):
            print("HEEEEEEE")
        image = cv2.putText(image, f'{class_name}', c1, cv2.FONT_HERSHEY_SIMPLEX,
                            fontScale, (0, 0, 0), 1, lineType=cv2.LINE_AA)
        
    return image

def preprocess_image(original_image,input_size):
    original_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB)
    image_data = cv2.resize(original_image, (input_size, input_size))
    image_data = image_data / 255.

    images_data = []
    images_data.append(image_data)
    images_data = np.asarray(images_data).astype(np.float32)
    return images_data

def doInference(interpreter,images_data,input_details,output_details,input_size):
    interpreter.set_tensor(input_details[0]['index'], images_data)
    interpreter.invoke()
    pred = [interpreter.get_tensor(output_details[i]['index']) for i in range(len(output_details))]
    boxes, pred_conf = filter_boxes(pred[0], pred[1], score_threshold=0.25, input_shape=tf.constant([input_size, input_size]))
 

    boxes, scores, classes, valid_detections = tf.image.combined_non_max_suppression(
        boxes=tf.reshape(boxes, (tf.shape(boxes)[0], -1, 1, 4)),
        scores=tf.reshape(
            pred_conf, (tf.shape(pred_conf)[0], -1, tf.shape(pred_conf)[-1])),
        max_output_size_per_class=50,
        max_total_size=50,
        iou_threshold=iou_threshole,
        score_threshold=score_threshole
    )

    pred_bbox = [boxes.numpy(), scores.numpy(), classes.numpy(), valid_detections.numpy()]
    return pred_bbox

def main():

    # Config model
    config = ConfigProto()
    config.gpu_options.allow_growth = True
    session = InteractiveSession(config=config)
    STRIDES, ANCHORS, NUM_CLASS, XYSCALE = load_config()
    input_size = 416

    # load model
    # model_path = 'tflite/yolov4-tiny-416.tflite'
    model_path = 'tflite/yolov4-tiny-tflite-416-fp16.tflite'
    
    interpreter = tf.lite.Interpreter(model_path=model_path)
    
    interpreter.allocate_tensors()
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    cap = cv2.VideoCapture('http://10.1.122.224:4747/mjpegfeed?640x480')
    while True:
        ret,original_image = cap.read()
        # Preprocess
        images_data = preprocess_image(original_image,input_size)
        # predict    
        pred_bbox = doInference(interpreter,images_data,input_details,output_details,input_size)
        
        img = draw_bbox(original_image,pred_bbox)
        cv2.imshow('mat',img)
        key = cv2.waitKey(1)
        if key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    exit()



main()

