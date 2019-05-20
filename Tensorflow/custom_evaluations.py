# -*- coding: utf-8 -*-
"""
Created on Fri May 17 18:05:50 2019

@author: johan
"""

from utils import file_utils
import numpy as np

input_folder = "C:/Users/johan/Desktop/predictions"

iou_threshold = 0.5


def evaluate():

    images = file_utils.get_all_images_in_folder(input_folder)
    
    for image_path in images:
        
        predictions_path = image_path[:-4] + "_predictions.json"
        ground_truth_path = image_path[:-4] + "_ground_truth.json"
        
        predictions = file_utils.read_json_file(predictions_path)
        ground_truths = file_utils.read_json_file(ground_truth_path)
        
        if not predictions or not ground_truths:
            continue
        
        
        for prediction in predictions:
            prediction["hits"] = 0
        
        flower_names = []
        for ground_truth in ground_truths:
            if not ground_truth["name"] in flower_names:
                flower_names.append(ground_truth["name"])
        
        stats = {}
        
        for flower_name in flower_names:
            stats[flower_name] = {"tp": 0, "fp": 0, "fn": 0}
                
        for ground_truth in ground_truths:
            max_val = 0
            max_i = -1
            for p_i,prediction in enumerate(predictions):
                if ground_truth["name"] == prediction["name"]:
                    val = iou(prediction["bounding_box"], ground_truth["bounding_box"])
                    if(val>iou_threshold and val > max_val):
                        max_val = val
                        max_i = p_i
            
            if max_val > 0:
                stats[ground_truth["name"]]["tp"] += 1
                predictions[max_i]["hits"] +=  1
            else:
                stats[ground_truth["name"]]["fn"] += 1
        
        for prediction in predictions:
            if prediction["hits"] == 0:
                stats[prediction["name"]]["fp"] += 1
            elif prediction["hits"] > 1:
                print("Damn, a prediction hit more than one ground truths")
        
        
        for flower_name in flower_names:
            print(flower_name + ":")
            stat = stats[flower_name]
            precision = float(stat["tp"]) / float(stat["fp"]+stat["tp"])
            recall = float(stat["tp"]) / float(stat["tp"] + stat["fn"])
        
            print("   precision: " + str(precision))
            print("   recall: " + str(recall))

        
        '''
        overlaps = {}
        for index,ground_truth in enumerate(ground_truths):
            overlaps[index] = []
            for prediction in predictions:
                if ground_truth["name"] == prediction["name"]:
                    val = iou(prediction["bounding_box"], ground_truth["bounding_box"])
                    if(val>iou_threshold):
                        overlaps[index].append({"prediction": prediction, "iou": val})
        
        
        for index,overlap in enumerate(overlaps):
            overlaps[index] = sorted(overlaps[index], key=lambda k: -k['iou']) 
        
        overlaps = sorted(overlaps, key=lambda k)
        print(overlaps)
        '''

def iou(box1, box2):
    """
    calculate intersection over union cover percent
    :param box1: box1 with shape (N,4) or (N,2,2) or (2,2) or (4,). first shape is preferred
    :param box2: box2 with shape (N,4) or (N,2,2) or (2,2) or (4,). first shape is preferred
    :return: IoU ratio if intersect, else 0
    """
    box1 = np.array(box1)
    box2 = np.array(box2)

    # first unify all boxes to shape (N,4)
    if box1.shape[-1] == 2 or len(box1.shape) == 1:
        box1 = box1.reshape(1, 4) if len(box1.shape) <= 2 else box1.reshape(box1.shape[0], 4)
    if box2.shape[-1] == 2 or len(box2.shape) == 1:
        box2 = box2.reshape(1, 4) if len(box2.shape) <= 2 else box2.reshape(box2.shape[0], 4)
    point_num = max(box1.shape[0], box2.shape[0])
    b1p1, b1p2, b2p1, b2p2 = box1[:, :2], box1[:, 2:], box2[:, :2], box2[:, 2:]

    # mask that eliminates non-intersecting matrices
    base_mat = np.ones(shape=(point_num,))
    base_mat *= np.all(np.greater(b1p2 - b2p1, 0), axis=1)
    base_mat *= np.all(np.greater(b2p2 - b1p1, 0), axis=1)

    # I area
    intersect_area = np.prod(np.minimum(b2p2, b1p2) - np.maximum(b1p1, b2p1), axis=1)
    # U area
    union_area = np.prod(b1p2 - b1p1, axis=1) + np.prod(b2p2 - b2p1, axis=1) - intersect_area
    # IoU
    intersect_ratio = intersect_area / union_area

    return (base_mat * intersect_ratio)[0]

                
                
evaluate()
#predictions = file_utils.read_json(input_folder)

