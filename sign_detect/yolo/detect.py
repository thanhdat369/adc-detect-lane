import tensorflow as tf
import sign_detect.yolo.config as cfg
from PIL import Image
import cv2
import numpy as np
from tensorflow.compat.v1 import ConfigProto
from tensorflow.compat.v1 import InteractiveSession
import threading
import timeit

framework = 'tflite'
iou_threshole = 0.1
CLASS = ['SLOWDOWN','SPEED UP','STOP']

class YoloDetect:
    def __init__(self,model_path = './sign_detect/yolo/tflite/yolov4-tiny-416.tflite',score_threshole=0.7):
        self.config = ConfigProto()
        self.config.gpu_options.allow_growth = True
        self.session = InteractiveSession(config=self.config)
        # STRIDES, ANCHORS, NUM_CLASS, XYSCALE = load_config() 
        self.input_size = 416
        self.score_threshole = score_threshole
        # load model
        # model_path = 'tflite/yolov4-tiny-416.tflite'
        self.model_path = model_path
        
        self.interpreter = tf.lite.Interpreter(model_path=self.model_path)
        
        self.interpreter.allocate_tensors()
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()
    
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

    def __draw_bbox(self,image,pred_bbox):
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
            # if(class_name == "STOP"):
            #     print("HEEEEEEE")
            image = cv2.putText(image, f'{class_name}', c1, cv2.FONT_HERSHEY_SIMPLEX,
                                fontScale, (0, 0, 0), 1, lineType=cv2.LINE_AA)
            
        return image
    
    
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


    def detect_return_image(self,original_image):
        starttime = timeit.default_timer()
        images_data =self.__preprocess_image(original_image,self.input_size)
        pred_bbox = self.__doInference(self.interpreter,images_data,self.input_details,self.output_details,self.input_size)
        image =  self.__draw_bbox(original_image, pred_bbox)
        print(timeit.default_timer()-starttime)
        return image
    
    def detect_return_sign_name(self,original_image):
        starttime = timeit.default_timer()
        images_data =self.__preprocess_image(original_image,self.input_size)
        pred_bbox = self.__doInference(self.interpreter,images_data,self.input_details,self.output_details,self.input_size)
        sign_name =  self.__get_biggest_bbox_index(original_image, pred_bbox)
        print(timeit.default_timer()-starttime)
        return sign_name
