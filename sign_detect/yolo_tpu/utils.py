'''
 copy from
 guichristmann/edge-tpu-tiny-yolo
 utils.py
 
 update by nishi 2021.2.25

'''
import numpy as np
import os
import cv2
# Maximum number of boxes. Only the top scoring ones will be considered.
MAX_BOXES = 30

def sigmoid(x):
    temp = 1. / (1 + np.exp(-x))
    return temp

'''
  letterbox_image(imagex, size):
    size : width , height
 update by nishi 2021.2.25
'''
def letterbox_image(imagex, size):
    # add by nishi
    image=cv2.cvtColor(imagex,cv2.COLOR_BGR2RGB)
    '''resize image with unchanged aspect ratio using padding'''
    iw, ih = image.shape[0:2][::-1]
    #print('iw=',iw,',ih=',ih)
    w, h = size   # width , height
    scale = min(w/iw, h/ih)
    # test by nishi
    #print(">>scale = %f"%(scale))
    nw = int(iw*scale)
    nh = int(ih*scale)
    image = cv2.resize(image, (nw,nh), interpolation=cv2.INTER_CUBIC)
    new_image = np.zeros((size[1], size[0], 3), np.uint8)
    new_image.fill(128)
    dx = (w-nw)//2
    dy = (h-nh)//2
    new_image[dy:dy+nh, dx:dx+nw,:] = image
    return new_image

'''
 orginal dosn't work correctly
 update by nishi 2021.2.25
'''
def featuresToBoxes(outputs, anchors, n_classes, net_input_shape, 
        img_orig_shape, threshold):
    grid_shape = outputs.shape[1:3]
    n_anchors = len(anchors)

    # Numpy screwaround to get the boxes in reasonable amount of time
    grid_y = np.tile(np.arange(grid_shape[0]).reshape(-1, 1), grid_shape[0]).reshape(1, grid_shape[0], grid_shape[0], 1).astype(np.float32)
    grid_x = grid_y.copy().T.reshape(1, grid_shape[0], grid_shape[1], 1).astype(np.float32)
    outputs = outputs.reshape(1, grid_shape[0], grid_shape[1], n_anchors, -1)
    _anchors = anchors.reshape(1, 1, 3, 2).astype(np.float32)

    # Get box parameters from network output and apply transformations
    bx = (sigmoid(outputs[..., 0]) + grid_x) / grid_shape[0] 
    by = (sigmoid(outputs[..., 1]) + grid_y) / grid_shape[1]
    # Should these be inverted?
    bw = np.multiply(_anchors[..., 0] / net_input_shape[1], np.exp(outputs[..., 2]))
    bh = np.multiply(_anchors[..., 1] / net_input_shape[2], np.exp(outputs[..., 3]))
    
    # Get the scores 
    scores = sigmoid(np.expand_dims(outputs[..., 4], -1)) * \
             sigmoid(outputs[..., 5:])
    scores = scores.reshape(-1, n_classes)

    # Reshape boxes and scale back to original image size
    #ratio = net_input_shape[2] / img_orig_shape[1]
    # changed by nishi
    ratio = min(net_input_shape[2] / img_orig_shape[1], net_input_shape[1] / img_orig_shape[0])
    #print("ratio = %f" % ratio)
    
    letterboxed_height = ratio * img_orig_shape[0]
    scale_h = net_input_shape[1] / letterboxed_height
    # add by nishi
    letterboxed_width = ratio * img_orig_shape[1] 
    scale_w = net_input_shape[2] / letterboxed_width
    #print("scale_h = %f" % scale_h)
    #print("scale_w = %f" % scale_w)

    offset_y = (net_input_shape[1] - letterboxed_height) / 2 / net_input_shape[1]
    # add by nishi
    offset_x = (net_input_shape[2] - letterboxed_width) / 2 / net_input_shape[2]
    
    #bx = bx.flatten()
    # changed by nishi
    bx = (bx.flatten() - offset_x) * scale_w
    by = (by.flatten() - offset_y) * scale_h
    #bw = bw.flatten()
    # changed by nishi
    bw = bw.flatten() * scale_w
    bh = bh.flatten() * scale_h
    half_bw = bw / 2.
    half_bh = bh / 2.

    tl_x = np.multiply(bx - half_bw, img_orig_shape[1])
    tl_y = np.multiply(by - half_bh, img_orig_shape[0]) 
    br_x = np.multiply(bx + half_bw, img_orig_shape[1])
    br_y = np.multiply(by + half_bh, img_orig_shape[0])

    # Get indices of boxes with score higher than threshold
    indices = np.argwhere(scores >= threshold)
    selected_boxes = []
    selected_scores = []
    for i in indices:
        i = tuple(i)
        selected_boxes.append( ((tl_x[i[0]], tl_y[i[0]]), (br_x[i[0]], br_y[i[0]])) )
        selected_scores.append(scores[i])

    selected_boxes = np.array(selected_boxes)
    selected_scores = np.array(selected_scores)
    selected_classes = indices[:, 1]

    return selected_boxes, selected_scores, selected_classes

'''
 orginal dosn't work correctly
 update by nishi 2021.3.2
'''
def featuresToBoxes2(outputs, anchors, n_classes, net_input_shape, threshold):
    grid_shape = outputs.shape[1:3]
    n_anchors = len(anchors)

    # Numpy screwaround to get the boxes in reasonable amount of time
    grid_y = np.tile(np.arange(grid_shape[0]).reshape(-1, 1), grid_shape[0]).reshape(1, grid_shape[0], grid_shape[0], 1).astype(np.float32)
    grid_x = grid_y.copy().T.reshape(1, grid_shape[0], grid_shape[1], 1).astype(np.float32)
    outputs = outputs.reshape(1, grid_shape[0], grid_shape[1], n_anchors, -1)
    _anchors = anchors.reshape(1, 1, 3, 2).astype(np.float32)

    # Get box parameters from network output and apply transformations
    bx = (sigmoid(outputs[..., 0]) + grid_x) / grid_shape[0] 
    by = (sigmoid(outputs[..., 1]) + grid_y) / grid_shape[1]
    # Should these be inverted?
    bw = np.multiply(_anchors[..., 0] / net_input_shape[1], np.exp(outputs[..., 2]))
    bh = np.multiply(_anchors[..., 1] / net_input_shape[2], np.exp(outputs[..., 3]))
    
    # Get the scores 
    scores = sigmoid(np.expand_dims(outputs[..., 4], -1)) * \
             sigmoid(outputs[..., 5:])
    scores = scores.reshape(-1, n_classes)

    bx = bx.flatten()
    by = by.flatten()

    bw = bw.flatten()
    bh = bh.flatten()
    half_bw = bw / 2.
    half_bh = bh / 2.

    tl_x = bx - half_bw
    tl_y = by - half_bh 
    br_x = bx + half_bw
    br_y = by + half_bh

    # Get indices of boxes with score higher than threshold
    indices = np.argwhere(scores >= threshold)
    selected_boxes = []
    selected_scores = []
    for i in indices:
        i = tuple(i)
        selected_boxes.append( ((tl_x[i[0]], tl_y[i[0]]), (br_x[i[0]], br_y[i[0]])) )
        selected_scores.append(scores[i])

    selected_boxes = np.array(selected_boxes)
    selected_scores = np.array(selected_scores)
    selected_classes = indices[:, 1]

    return selected_boxes, selected_scores, selected_classes
    
def get_anchors(path):
    anchors_path = os.path.expanduser(path)
    with open(anchors_path) as f:
        anchors = f.readline()
    anchors = [float(x) for x in anchors.split(',')]
    return np.array(anchors).reshape(-1, 2)

def get_classes(path):
    classes_path = os.path.expanduser(path)
    with open(classes_path) as f:
        classes = [line.strip('\n') for line in f.readlines()]
    return classes

def nms_boxes(boxes, scores, classes):
    present_classes = np.unique(classes)

    assert(boxes.shape[0] == scores.shape[0])
    assert(boxes.shape[0] == classes.shape[0])

    # Sort based on score
    indices = np.arange(len(scores))
    scores, sorted_is = (list(l) for l in zip(*sorted(zip(scores, indices), reverse=True)))
    boxes = list(boxes[sorted_is])
    classes = list(classes[sorted_is])

    # Run nms for each class
    i = 0
    while True:
        if len(boxes) == 1 or i >= len(boxes) or i == MAX_BOXES:
            break

        # Get box with highest score
        best_box = boxes[i]
        best_cl = classes[i]

        # Iterate over other boxes
        to_remove = []
        for j in range(i+1, len(boxes)):
            other_cl = classes[j]
            #if other_cl != best_cl:
            #    continue

            other_box = boxes[j]
            box_iou = iou(best_box, other_box)
            if box_iou > 0.15:
                to_remove.append(j)

        if len(to_remove) == 0:
            break
        else:
            # Remove boxes
            for r in to_remove[::-1]:
                del boxes[r]
                del scores[r]
                del classes[r]
        i += 1

    return boxes[:MAX_BOXES], scores[:MAX_BOXES], classes[:MAX_BOXES]

def iou(box1, box2):
    xi1 = max(box1[0][0], box2[0][0])
    yi1 = max(box1[0][1], box2[0][1])
    xi2 = min(box1[1][0], box2[1][0])
    yi2 = min(box1[1][1], box2[1][1])
    
    if(((xi2 - xi1) < 0) or ((yi2 - yi1) < 0)):
        IoU = 0
        return IoU
    else:
        inter_area = (xi2 - xi1)*(yi2 - yi1)
        
        # Formula: Union(A,B) = A + B - Inter(A,B)
        box1_area = (box1[1][1] - box1[0][1])*(box1[1][0]- box1[0][0])
        box2_area = (box2[1][1] - box2[0][1])*(box2[1][0]- box2[0][0])
        union_area = (box1_area + box2_area) - inter_area
        # compute the IoU
        IoU = inter_area / union_area
    
        return IoU
