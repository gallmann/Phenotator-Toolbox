# -*- coding: utf-8 -*-
"""
Created on Fri May 17 18:05:50 2019

@author: johan
"""

print("Loading libraries...")
from utils import constants
from utils import file_utils
from object_detection.utils import visualization_utils
from PIL import Image
import os
from object_detection.utils import label_map_util
import progressbar
import numpy as np
from object_detection.utils import object_detection_evaluation
from object_detection.core import standard_fields
from object_detection.utils import per_image_evaluation
from utils import constants



def evaluate(input_folder, output_folder,iou_threshold=constants.iou_threshold,generate_visualizations=False,print_confusion_matrix=False):
    
    
    PATH_TO_LABELS = constants.train_dir + "/model_inputs/label_map.pbtxt"
    (flower_names,labelmap) = get_flower_names_from_labelmap(PATH_TO_LABELS)
    object_detection_evaluator = object_detection_evaluation.ObjectDetectionEvaluator(labelmap, matching_iou_threshold=iou_threshold,evaluate_precision_recall=True,use_weighted_mean_ap=False)
    confusion_matrix = np.zeros(shape=(len(flower_names) + 1, len(flower_names) + 1))

    stats = {}
    for flower_name in flower_names:
        stats[flower_name] = {"tp": 0, "fp": 0, "fn": 0, "mAP": 0}

    images = file_utils.get_all_images_in_folder(input_folder)

    for i in progressbar.progressbar(range(len(images))):
        image_path = images[i]
        
        predictions_path = image_path[:-4] + "_predictions.json"
        ground_truth_path = image_path[:-4] + "_ground_truth.json"
        
        predictions = file_utils.read_json_file(predictions_path)
        ground_truths = file_utils.read_json_file(ground_truth_path)
        if not predictions or not ground_truths:
            continue

        ground_truths = filter_ground_truth(ground_truths,flower_names)
        
        
        
        for gt in ground_truths:
            gt["hits"] = 0
                
                
        predictions = sorted(predictions, key=lambda k: -k['score']) 



        #first compute mAP using the Tensorflow implementation
        bounding_boxes_gt, classes_gt, _ = to_numpy_representations(ground_truths, labelmap)
        bounding_boxes_p, classes_p, scores_p = to_numpy_representations(predictions, labelmap)
        gt_dict = {standard_fields.InputDataFields.groundtruth_boxes: bounding_boxes_gt, standard_fields.InputDataFields.groundtruth_classes:classes_gt, standard_fields.InputDataFields.groundtruth_difficult: np.full((len(bounding_boxes_gt)), False) }
        prediction_dict = {standard_fields.DetectionResultFields.detection_boxes: bounding_boxes_p,standard_fields.DetectionResultFields.detection_scores: scores_p, standard_fields.DetectionResultFields.detection_classes:classes_p}
        
        object_detection_evaluator.add_single_ground_truth_image_info(image_path,gt_dict)
        object_detection_evaluator.add_single_detected_image_info(image_path,prediction_dict)

        
        #update confusion matrix
        matches = []
                
        for i in range(len(bounding_boxes_gt)):
            for j in range(len(bounding_boxes_p)):
                curr_iou = iou(bounding_boxes_gt[i], bounding_boxes_p[j])
                
                if curr_iou > iou_threshold:
                    matches.append([i, j, curr_iou])
                
        matches = np.array(matches)
        if matches.shape[0] > 0:
            # Sort list of matches by descending IOU so we can remove duplicate detections
            # while keeping the highest IOU entry.
            matches = matches[matches[:, 2].argsort()[::-1][:len(matches)]]
            
            # Remove duplicate detections from the list.
            matches = matches[np.unique(matches[:,1], return_index=True)[1]]
            
            # Sort the list again by descending IOU. Removing duplicates doesn't preserve
            # our previous sort.
            matches = matches[matches[:, 2].argsort()[::-1][:len(matches)]]
            
            # Remove duplicate ground truths from the list.
            matches = matches[np.unique(matches[:,0], return_index=True)[1]]
            
        for i in range(len(bounding_boxes_gt)):
            if matches.shape[0] > 0 and matches[matches[:,0] == i].shape[0] == 1:
                confusion_matrix[classes_gt[i] - 1][classes_p[int(matches[matches[:,0] == i, 1][0])] - 1] += 1 
            else:
                confusion_matrix[classes_gt[i] - 1][confusion_matrix.shape[1] - 1] += 1
                
        for i in range(len(bounding_boxes_p)):
            if matches.shape[0] > 0 and matches[matches[:,1] == i].shape[0] == 0:
                confusion_matrix[confusion_matrix.shape[0] - 1][classes_p[i] - 1] += 1

        
        
        
        
        
        
        
        

        #compute TP FP and FN
        for prediction in predictions:
            max_val = 0
            max_i = -1
            for gt_i,ground_truth in enumerate(ground_truths):
                if ground_truth["name"] == prediction["name"]:
                    val = iou(prediction["bounding_box"], ground_truth["bounding_box"])
                    if(val>iou_threshold and val > max_val):
                        max_val = val
                        max_i = gt_i
            
            if max_val > 0 and ground_truths[max_i]["hits"] < 1:
                prediction["label"] = "tp"
                stats[prediction["name"]]["tp"] += 1
                ground_truths[max_i]["hits"] +=  1
            else:
                prediction["label"] = "fp"
                stats[prediction["name"]]["fp"] += 1

        for gt in ground_truths:
            if gt["hits"] < 1:
                stats[gt["name"]]["fn"] += 1
                gt["label"] = "fn"
            else:
                gt["label"] = "tp"

        if generate_visualizations:            
            image = Image.open(image_path)
            
            for prediction in predictions:
                for gt in ground_truths:
                    if prediction["label"] == "fp" and gt["label"] == "fn":
                        if iou(prediction["bounding_box"], gt["bounding_box"])>iou_threshold:
                            [top,left,bottom,right] = gt["bounding_box"]
                            visualization_utils.draw_bounding_box_on_image(image,top,left,bottom,right,display_str_list=["Misclassification", "is: " + gt["name"] , "pred: " + prediction["name"]],thickness=2, color="DarkOrange", use_normalized_coordinates=False)          
                            ground_truths.remove(gt)
                            predictions.remove(prediction)
            
            
            for prediction in predictions:
                [top,left,bottom,right] = prediction["bounding_box"]
                if prediction["label"] == "fp":
                    visualization_utils.draw_bounding_box_on_image(image,top,left,bottom,right,display_str_list=["FP", prediction["name"]],thickness=2, color="red", use_normalized_coordinates=False)          
            for gt in ground_truths:
                if gt["label"] == "fn":
                    [top,left,bottom,right] = gt["bounding_box"]
                    visualization_utils.draw_bounding_box_on_image(image,top,left,bottom,right,display_str_list=["FN", gt["name"]],thickness=2, color="MediumVioletRed", use_normalized_coordinates=False)          
            image_output_path = os.path.join(output_folder, os.path.basename(image_path))
            image.save(image_output_path)

    
    tensorflow_evaluations = object_detection_evaluator.evaluate()
        
    flower_names.sort()
    stat_overall = {"tp": 0, "fp": 0, "fn": 0, "mAP": tensorflow_evaluations["Precision/mAP@" +str(iou_threshold)+"IOU"]}
    for flower_name in flower_names:
        stat = stats[flower_name]
        stat_overall["tp"] += stat["tp"]
        stat_overall["fp"] += stat["fp"]
        stat_overall["fn"] += stat["fn"]
        stat["mAP"] = tensorflow_evaluations["PerformanceByCategory/AP@" +str(iou_threshold)+"IOU/b'" + flower_name + "'"]
        print_stats(stat,flower_name)

    print_stats(stat_overall,"Overall")
    
    if print_confusion_matrix:
        display(confusion_matrix,labelmap,iou_threshold)
    
    return stat_overall


def display(confusion_matrix, categories, iou_threshold):
    
    def short_name(name):
        if " " in name:
            if "faded" in name:
                return "centaurea j. f."
            return name[0:name.find(" ") + 2] + "."
        else:
            return name
    
    print("\nConfusion Matrix:")
    
    categories.append({"id":0, "name":"background"})
    top_line = ""
    for category in categories:
        top_line += " & \\rotatebox[origin=c]{90}{" + short_name(category["name"]) + "}"
    print(top_line + "\\\\")
    print("\\hline")
    for i,line in enumerate(confusion_matrix):
        line_string = short_name(categories[i]["name"])
        for number in line:
            line_string += " & " + str(int(number))
        line_string += " \\\\"
        print(line_string)
        
        
        
'''
    for i in range(len(categories)):
        id = categories[i]["id"] - 1
        name = categories[i]["name"]
        
        total_target = np.sum(confusion_matrix[id,:])
        total_predicted = np.sum(confusion_matrix[:,id])
        
        precision = float(confusion_matrix[id, id] / total_predicted)
        recall = float(confusion_matrix[id, id] / total_target)
        
        print('precision_{}@{}IOU: {:.2f}'.format(name, iou_threshold, precision))
        print('recall_{}@{}IOU: {:.2f}'.format(name, iou_threshold, recall))
    '''


def print_stats(stat, flower_name):
    
    n = stat["tp"] + stat["fn"]
    print(flower_name + " (n=" + str(n) + "):")
    if float(stat["fp"]+stat["tp"]) == 0:
        precision = "-"
    else:
        precision = float(stat["tp"]) / float(stat["fp"]+stat["tp"])
    if float(stat["tp"] + stat["fn"]) == 0:
        recall = "-"
    else:
        recall = float(stat["tp"]) / float(stat["tp"] + stat["fn"])

    print("   precision: " + str(precision))
    print("   recall: " + str(recall))
    print("   mAP: " + str(stat["mAP"]))
    print("   TP: " + str(stat["tp"]) + " FP: " + str(stat["fp"]) + " FN: " + str(stat["fn"]))
    
        
def iou(a, b, epsilon=1e-5):
    """ Given two boxes `a` and `b` defined as a list of four numbers:
            [x1,y1,x2,y2]
        where:
            x1,y1 represent the upper left corner
            x2,y2 represent the lower right corner
        It returns the Intersect of Union score for these two boxes.

    Args:
        a:          (list of 4 numbers) [x1,y1,x2,y2]
        b:          (list of 4 numbers) [x1,y1,x2,y2]
        epsilon:    (float) Small value to prevent division by zero

    Returns:
        (float) The Intersect of Union score.
    """
    # COORDINATES OF THE INTERSECTION BOX
    x1 = max(a[0], b[0])
    y1 = max(a[1], b[1])
    x2 = min(a[2], b[2])
    y2 = min(a[3], b[3])

    # AREA OF OVERLAP - Area where the boxes intersect
    width = (x2 - x1)
    height = (y2 - y1)
    # handle case where there is NO overlap
    if (width<0) or (height <0):
        return 0.0
    area_overlap = width * height

    # COMBINED AREA
    area_a = (a[2] - a[0]) * (a[3] - a[1])
    area_b = (b[2] - b[0]) * (b[3] - b[1])
    area_combined = area_a + area_b - area_overlap

    # RATIO OF AREA OF OVERLAP OVER COMBINED AREA
    iou = area_overlap / (area_combined+epsilon)
    return iou

def filter_ground_truth(ground_truths, flower_names):
    filtered_ground_truths = []
    for gt in ground_truths:
        if gt["name"] in flower_names:
            filtered_ground_truths.append(gt)
    return filtered_ground_truths

                
def get_flower_names_from_labelmap(labelmap_path):
    
    flower_names = []
    categories = []
    category_index = label_map_util.create_category_index_from_labelmap(labelmap_path, use_display_name=True)
    for d in category_index:
        flower_names.append(category_index[d]["name"])
        categories.append({"id":category_index[d]["id"], "name":category_index[d]["name"]})
    return (flower_names,categories)
          
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


if __name__ == '__main__':
    input_folder = constants.predictions_folder
    output_folder = constants.prediction_evaluation_folder
    iou_threshold = constants.iou_threshold
    evaluate(input_folder, output_folder,iou_threshold)

