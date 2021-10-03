import tensorflow as tf
import sign_detect.yolo.config as cfg
from PIL import Image
import cv2
import numpy as np
import threading
import timeit
from tensorflow.lite.python.interpreter import Interpreter


iou_threshole = 0.1
class SSDDetect:
    def __init__(self,model_path = './sign_detect/ssd/v2/detect.tflite',label_path='./sign_detect/ssd/v2/labelmap.txt',score_threshole=0.7):
        self.score_threshole = score_threshole
        # load model
        self.model_path = model_path
        self.interpreter = Interpreter(model_path=model_path)
        self.interpreter.allocate_tensors()
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()
        with open(label_path, 'r') as f:
            self.labels = [line.strip() for line in f.readlines()]
        if self.labels[0] == '???':
            del(self.labels[0])
        self.height= self.input_details[0]['shape'][1]
        self.width = self.input_details[0]['shape'][2]
    
    def __preprocess_image(self,original_image,input_size):
        original_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB)
        image_data = cv2.resize(original_image, (input_size, input_size))
        image_data = image_data / 255.

        images_data = []
        images_data.append(image_data)
        images_data = np.asarray(images_data).astype(np.float32)
        return images_data
    
    def __doInference(self,interpreter,images_data,input_details,output_details,input_size):
        interpreter.set_tensor(input_details[0]['index'], images_data)
        interpreter.invoke()
        pred = [interpreter.get_tensor(output_details[i]['index']) for i in range(len(output_details))]
        boxes, pred_conf = self.__filter_boxes(pred[0], pred[1], score_threshold=self.score_threshole, input_shape=tf.constant([input_size, input_size]))

        boxes, scores, classes, valid_detections = tf.image.combined_non_max_suppression(
            boxes=tf.reshape(boxes, (tf.shape(boxes)[0], -1, 1, 4)),
            scores=tf.reshape(
                pred_conf, (tf.shape(pred_conf)[0], -1, tf.shape(pred_conf)[-1])),
            max_output_size_per_class=50,
            max_total_size=50,
            iou_threshold=iou_threshole,
            score_threshold=self.score_threshole
        )

        pred_bbox = [boxes.numpy(), scores.numpy(), classes.numpy(), valid_detections.numpy()]
        return pred_bbox

    def __filter_boxes(self,box_xywh, scores, score_threshold=0.4, input_shape = tf.constant([416,416])):
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
    
    
    def __get_biggest_bbox_index(self,image,pred_bbox):
        image_h, image_w, _ = image.shape
        out_boxes, out_scores, out_classes, num_boxes = pred_bbox
        area_list = np.array([])
        class_name_list = []
        if(num_boxes[0]<1):
            return None
        for i in range(num_boxes[0]):
            # if int(out_classes[0][i]) < 0 or int(out_classes[0][i]) > 3: continue
            coor = out_boxes[0][i]
            coor[0] = int(coor[0] * image_h)
            coor[2] = int(coor[2] * image_h)
            coor[1] = int(coor[1] * image_w)
            coor[3] = int(coor[3] * image_w)
            class_ind = int(out_classes[0][i])
            class_name = CLASS[class_ind]
            area = abs(coor[3]-coor[1])*abs(coor[2]-coor[0])
            area_list= np.append(area_list, area)
            class_name_list.append(class_name)

        idx = np.argmax(area_list)
        rs = class_name_list[idx]
        return rs
    
    def detect_return_sign_name(self,original_image):
        starttime = timeit.default_timer()
        images_data =self.__preprocess_image(original_image,self.input_size)
        pred_bbox = self.__doInference(self.interpreter,images_data,self.input_details,self.output_details,self.input_size)
        sign_name =  self.__get_biggest_bbox_index(original_image, pred_bbox)
        print(timeit.default_timer()-starttime)
        return sign_name

    

    def detect_single_image(self,image):
        input_mean = 127.5
        input_std = 127.5
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        imH, imW, _ = image.shape 
        image_resized = cv2.resize(image_rgb, (self.width, self.height))
        input_data = np.expand_dims(image_resized, axis=0)

        input_data = (np.float32(input_data) - input_mean) / input_std
        # input_data = (np.float32(input_data)) / 255.

        # Perform the actual detection by running the model with the image as input
        self.interpreter.set_tensor(self.input_details[0]['index'],input_data)
        self.interpreter.invoke()

        # Retrieve detection results
        boxes = self.interpreter.get_tensor(self.output_details[0]['index'])[0] # Bounding box coordinates of detected objects
        classes = self.interpreter.get_tensor(self.output_details[1]['index'])[0] # Class index of detected objects
        scores = self.interpreter.get_tensor(self.output_details[2]['index'])[0] # Confidence of detected objects
        #num = interpreter.get_tensor(output_details[3]['index'])[0]  # Total number of detected objects (inaccurate and not needed)

        # Loop over all detections and draw detection box if confidence is above minimum threshold
        for i in range(len(scores)):
            if ((scores[i] > self.score_threshole) and (scores[i] <= 1.0)):

                # Get bounding box coordinates and draw box
                # Interpreter can return coordinates that are outside of image dimensions, need to force them to be within image using max() and min()
                ymin = int(max(1,(boxes[i][0] * imH)))
                xmin = int(max(1,(boxes[i][1] * imW)))
                ymax = int(min(imH,(boxes[i][2] * imH)))
                xmax = int(min(imW,(boxes[i][3] * imW)))
                
                cv2.rectangle(image, (xmin,ymin), (xmax,ymax), (10, 255, 0), 2)

                # Draw label
                object_name = self.labels[int(classes[i])] # Look up object name from "labels" array using class index
                label = '%s: %d%%' % (object_name, int(scores[i]*100)) # Example: 'person: 72%'
                labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2) # Get font size
                label_ymin = max(ymin, labelSize[1] + 10) # Make sure not to draw label too close to top of window
                cv2.rectangle(image, (xmin, label_ymin-labelSize[1]-10), (xmin+labelSize[0], label_ymin+baseLine-10), (255, 255, 255), cv2.FILLED) # Draw white box to put label text in
                cv2.putText(image, label, (xmin, label_ymin-7), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2) # Draw label text
            
            return image 