import sign_detect.yolo_tpu.inference as inference
import numpy as np
class_len = 8
# colors = np.random.uniform(220, 255, size=(class_len, 3))
colors = [
        (70,70,229),(134,248,254),
        (134,248,254),(191,178,0),
        (191,178,0), (191,178,0),
        (112,204,45),(90,90,229)
        ]
class TrafficDetector:
    def __init__(self,model_path,edge_tpu,threshold):
        self.model = model_path
        self.edge_tpu = edge_tpu
        self.threshold = threshold
        anchor_path = 'sign_detect/yolo_tpu/cfg/tiny_yolo_anchors.txt'
        self.anchors = inference.get_anchors(anchor_path)
        classes_path = 'sign_detect/yolo_tpu/cfg/coco.names'
        self.classes = inference.get_classes(classes_path)
        self.__get_inference()


    def __get_inference(self,):
        self.interpreter = inference.make_interpreter(self.model, self.edge_tpu)
        self.interpreter.allocate_tensors()
        self.input_details, self.output_details, self.input_shape = inference.get_interpreter_details(self.interpreter)
        self.n_classes = len(self.classes)

    def detect(self,frame):
        boxes, scores, pred_classes = inference.inference(self.interpreter, frame, self.anchors, self.n_classes, self.threshold)
        return boxes, scores, pred_classes

    def draw_image(self,frame):
        boxes, scores, pred_classes = self.detect(frame)
        # print(scores)
        image,class_name = inference.draw_boxes(frame, boxes, scores, pred_classes, self.classes,colors)
        return image,class_name

    def detect_get_bigest_class(self,frame):
        boxes, scores, pred_classes = self.detect(frame)
        sign = inference.get_biggest_boxes(frame, boxes, scores, pred_classes, self.classes)
        return sign

    def close(self,):
        self.interpreter.close()