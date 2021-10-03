import numpy as np
import tensorflow.lite as tflite
import sys
import cv2
from time import time
from sign_detect.yolo_tpu.utils import *

EDGETPU_SHARED_LIB = "libedgetpu.so.1"

quant = True
def make_interpreter(model_path,edge_tpu):
    # Load the TF-Lite model and delegate to Edge TPU
    if edge_tpu:
        interpreter = tflite.Interpreter(model_path=model_path,
                experimental_delegates=[
                    tflite.experimental.load_delegate(EDGETPU_SHARED_LIB)
                    ])
    else:
        interpreter = tflite.Interpreter(model_path=model_path)
    return interpreter

# Run YOLO inference on the image, returns detected boxes
def inference(interpreter, img, anchors, n_classes, threshold):
    input_details, output_details, net_input_shape = \
            get_interpreter_details(interpreter)

    img_orig_shape = img.shape
    # Crop frame to network input shape
    img = letterbox_image(img.copy(), (416, 416))
    # Add batch dimension
    img = np.expand_dims(img, 0)

    if not quant:
        # Normalize image from 0 to 1
        img = np.divide(img, 255.).astype(np.float32)

    # Set input tensor
    interpreter.set_tensor(input_details[0]['index'], img)
    # start = time()
    interpreter.invoke()
    # inf_time = time() - start
    # print(f"Net forward-pass time: {inf_time*1000} ms.")

    # Retrieve outputs of the network
    out1 = interpreter.get_tensor(output_details[0]['index'])
    out2 = interpreter.get_tensor(output_details[1]['index'])

    # If this is a quantized model, dequantize the outputs
    if quant:
        # Dequantize output
        o1_scale, o1_zero = output_details[0]['quantization']
        out1 = (out1.astype(np.float32) - o1_zero) * o1_scale
        o2_scale, o2_zero = output_details[1]['quantization']
        out2 = (out2.astype(np.float32) - o2_zero) * o2_scale

    # Get boxes from outputs of network
    # start = time()
    _boxes1, _scores1, _classes1 = featuresToBoxes(out1, anchors[[3, 4, 5]], 
            n_classes, net_input_shape, img_orig_shape, threshold)
    _boxes2, _scores2, _classes2 = featuresToBoxes(out2, anchors[[1, 2, 3]], 
            n_classes, net_input_shape, img_orig_shape, threshold)
    # inf_time = time() - start
    # print(f"Box computation time: {inf_time*1000} ms.")

    # This is needed to be able to append nicely when the output layers don't
    # return any boxes
    if _boxes1.shape[0] == 0:
        _boxes1 = np.empty([0, 2, 2])
        _scores1 = np.empty([0,])
        _classes1 = np.empty([0,])
    if _boxes2.shape[0] == 0:
        _boxes2 = np.empty([0, 2, 2])
        _scores2 = np.empty([0,])
        _classes2 = np.empty([0,])

    boxes = np.append(_boxes1, _boxes2, axis=0)
    scores = np.append(_scores1, _scores2, axis=0)
    classes = np.append(_classes1, _classes2, axis=0)

    if len(boxes) > 0:
        boxes, scores, classes = nms_boxes(boxes, scores, classes)

    return boxes, scores, classes

def draw_boxes(image, boxes, scores, classes, class_names,colors):
    i = 0
    max_area = 0
    big_class = None
    for topleft, botright in boxes:
        # Detected class
        cl = int(classes[i])
        # This stupid thing below is needed for opencv to use as a color
        color = tuple(map(int, colors[cl])) 

        # Box coordinates
        topleft = (int(topleft[0]), int(topleft[1]))
        botright = (int(botright[0]), int(botright[1]))

        # Draw box and class
        cv2.rectangle(image, topleft, botright, color, 2)
        textpos = (topleft[0]-2, botright[1] - 3)
        # textpos = (topleft[0]-2, topleft[1] - 3)
        score = scores[i] * 100
        cl_name = class_names[cl]
        text = f"{cl_name} ({score:.1f}%)"
        cv2.putText(image, text, textpos, cv2.FONT_HERSHEY_DUPLEX,
                0.45, color, 1, cv2.LINE_AA)
        
        width = int(botright[0]) - int(topleft[0])
        height = int(topleft[1]) - int(botright[1])
        area = abs(width*height)
        if area> max_area:
            max_area = area
            big_class = cl_name
        i += 1
    return image,big_class

def get_biggest_boxes(image, boxes, scores, classes, class_names):
    i = 0
    max_area = 0
    for topleft, botright in boxes:
        # Detected class
        cl = int(classes[i])
        # This stupid thing below is needed for opencv to use as a color
        # Box coordinates
        topleft = int(botright[0]) - int(topleft[0])
        botright = int(topleft[1]) - int(botright[1])
        area = abs(topleft*botright)
        if area> max_area:
            max_area = area
            cl_name = class_names[cl]
        i += 1
    return cl_name

def get_interpreter_details(interpreter):
    # Get input and output tensor details
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    input_shape = input_details[0]["shape"]

    return input_details, output_details, input_shape

def webcam_inf(interpreter, anchors, classes, threshold=0.25):
    cap = cv2.VideoCapture(0)

    input_details, output_details, input_shape = \
            get_interpreter_details(interpreter)

    n_classes = len(classes)

    while True:
        ret, frame = cap.read()

        boxes, scores, pred_classes = inference(interpreter, frame, anchors, n_classes, threshold)

        if len(boxes) > 0:
            draw_boxes(frame, boxes, scores, pred_classes, classes)

        cv2.imshow("Image", frame)
        k = cv2.waitKey(1) & 0xFF
        if k == ord('q'):
            break

    cap.release()

