# -*- coding: utf-8 -*-
"""
Created on Mon May 20 13:51:26 2019

@author: johan
"""


input_folder = "C:/Users/johan/Desktop/predictions"
iou_threshold = 0.6



from utils import file_utils
import numpy as np
from object_detection.utils import object_detection_evaluation


def evaluate():
    images = file_utils.get_all_images_in_folder(input_folder)
    
    for image_path in images:
        
        predictions_path = image_path[:-4] + "_predictions.json"
        ground_truth_path = image_path[:-4] + "_ground_truth.json"
        
        predictions = file_utils.read_json_file(predictions_path)
        ground_truths = file_utils.read_json_file(ground_truth_path)
                
        if not predictions or not ground_truths:
            continue
        
        bounding_boxes_gt = to_numpy_representations(ground_truths)
        print(bounding_boxes_gt)
        
        

        categories = [{"id": 1, "name": "Loewenzahn"}, {"id": 2, "name": "Margarite"}]

        object_detection_evaluator = object_detection_evaluation.ObjectDetectionEvaluator(categories, matching_iou_threshold=iou_threshold)
        #object_detection_evaluator.add_single_ground_truth_image_info(image_path, )

        
        
def to_numpy_representations(annotations):
    bounding_boxes = np.array([])
    for annotation in annotations:
        continue
    return bounding_boxes







evaluate()


