# -*- coding: utf-8 -*-
"""
Created on Mon May 20 13:51:26 2019

@author: johan
"""


input_folder = "C:/Users/johan/Desktop/predictions"
iou_threshold = 0.5



from utils import file_utils
import numpy as np
from object_detection.utils import object_detection_evaluation
from object_detection.core import standard_fields
from object_detection.utils import per_image_evaluation


def evaluate():
    images = file_utils.get_all_images_in_folder(input_folder)
    
    for image_path in images:
        
        predictions_path = image_path[:-4] + "_predictions.json"
        ground_truth_path = image_path[:-4] + "_ground_truth.json"
        
        predictions = file_utils.read_json_file(predictions_path)
        ground_truths = file_utils.read_json_file(ground_truth_path)
                
        if not predictions or not ground_truths:
            continue
        
        categories = [{"id": 1, "name": "Loewenzahn"}, {"id": 2, "name": "Margarite"}]
        bounding_boxes_gt, classes_gt, _ = to_numpy_representations(ground_truths, categories)
        bounding_boxes_p, classes_p, scores_p = to_numpy_representations(predictions, categories)
        
        gt_dict = {standard_fields.InputDataFields.groundtruth_boxes: bounding_boxes_gt, standard_fields.InputDataFields.groundtruth_classes:classes_gt}
        prediction_dict = {standard_fields.DetectionResultFields.detection_boxes: bounding_boxes_p,standard_fields.DetectionResultFields.detection_scores: scores_p, standard_fields.DetectionResultFields.detection_classes:classes_p}

        

        object_detection_evaluator = object_detection_evaluation.ObjectDetectionEvaluator(categories, matching_iou_threshold=iou_threshold,evaluate_precision_recall=True)
        object_detection_evaluator.add_single_ground_truth_image_info(image_path,gt_dict)
        object_detection_evaluator.add_single_detected_image_info(image_path,prediction_dict)
        print(object_detection_evaluator.evaluate())
        

        print(object_detection_evaluator._evaluation.recalls_per_class)
        
        per_image_eval = per_image_evaluation.PerImageEvaluation(2)
        #per_image_eval._compute_tp_fp(bounding_boxes_p, scores_p, classes_p, bounding_boxes_gt, classes_gt, None, None)
        #object_detection_evaluator = object_detection_evaluation.WeightedPascalDetectionEvaluator(categories, matching_iou_threshold=iou_threshold)
        #object_detection_evaluator.add_single_ground_truth_image_info(image_path,gt_dict)
        #object_detection_evaluator.add_single_detected_image_info(image_path,prediction_dict)
        #print(object_detection_evaluator.evaluate())

        
def to_numpy_representations(annotations, categories):
    bounding_boxes = np.ndarray((len(annotations), 4))
    classes = np.empty((len(annotations)), dtype=int)
    scores = np.empty((len(annotations)), dtype=int)

    for i,annotation in enumerate(annotations):
        bounding_boxes[i] = annotation["bounding_box"]
        classes[i] = get_index_for_flower(categories, annotation["name"]) 
        if("score" in annotation):
            scores[i] = annotation["score"]
    return bounding_boxes,classes, scores



def get_index_for_flower(categories, flower_name):
    for flower in categories:
        if flower["name"] == flower_name:
            return flower["id"]
    raise ValueError('flower_name does not exist in categories dict')

    

evaluate()


