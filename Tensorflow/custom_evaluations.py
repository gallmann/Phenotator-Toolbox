# -*- coding: utf-8 -*-
"""
Created on Fri May 17 18:05:50 2019

@author: johan


This script carries out all kinds of evaluations on prediction results. Read the
description of the main function evaluate(...) for more details.

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
from utils import eval_utils



def evaluate(project_folder, input_folder, output_folder,iou_threshold=constants.iou_threshold,generate_visualizations=False,should_print_confusion_matrix=False,min_score=0.5,visualize_info=False):
    """
    Evaluates all predictions within the input_folder. The input folder should contain images
    alongside with prediction (imagename_prediction.json) and ground truth (imagename_ground_truth.json)
    files. Prints statistics such as precision, recall, mAP or f1 score for the overall
    prediction preformance as well as for every class seperate.

    Parameters:
        project_folder (str): path to the project folder
        input_folder (str): path of the input folder
        output_folder (str): path of the output folder. To this folder visualizations
            are printed.
        iou_threshold (float): intersection over union threshold to use for the evaluations
        generate_visualizations (bool): Whether or not the visualizations should be generated
        should_print_confusion_matrix (bool): If true, the confusion matrix is printed to the console in
            a format that can directly be imported into a latex table.
        min_score (float): The minimum score a prediction must have to be 
            included in the evaluation
    Returns:
        None
    """

    
    PATH_TO_LABELS = project_folder + "/model_inputs/label_map.pbtxt"
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
        
        if predictions == None:
            predictions = []
        if ground_truths == None:
            ground_truths = []

        ground_truths = filter_ground_truth(ground_truths,flower_names)
        predictions = filter_predictions(predictions,min_score)
        #predictions = eval_utils.non_max_suppression(predictions,0.3)
        
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
                curr_iou = eval_utils.iou(bounding_boxes_gt[i], bounding_boxes_p[j])
                
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
                    val = eval_utils.iou(prediction["bounding_box"], ground_truth["bounding_box"])
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
                        if eval_utils.iou(prediction["bounding_box"], gt["bounding_box"])>iou_threshold:
                            [top,left,bottom,right] = gt["bounding_box"]
                            vis_string = []
                            if visualize_info:
                                vis_string = ["Misclassification", "is: " + gt["name"] , "pred: " + prediction["name"]]
                            visualization_utils.draw_bounding_box_on_image(image,top,left,bottom,right,display_str_list=vis_string,thickness=3, color="DarkOrange", use_normalized_coordinates=False)          
                            ground_truths.remove(gt)
                            predictions.remove(prediction)
            
            
            for prediction in predictions:
                [top,left,bottom,right] = prediction["bounding_box"]
                if prediction["label"] == "fp":
                    vis_string = []
                    if visualize_info:
                        vis_string = ["FP", prediction["name"]]
                    visualization_utils.draw_bounding_box_on_image(image,top,left,bottom,right,display_str_list=vis_string,thickness=3, color="red", use_normalized_coordinates=False)          
            for gt in ground_truths:
                if gt["label"] == "fn":
                    [top,left,bottom,right] = gt["bounding_box"]
                    vis_string = []
                    if visualize_info:
                        vis_string = ["FN", gt["name"]]
                    visualization_utils.draw_bounding_box_on_image(image,top,left,bottom,right,display_str_list=vis_string,thickness=3, color="MediumVioletRed", use_normalized_coordinates=False)          
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
    
    if should_print_confusion_matrix:
        print_confusion_matrix(confusion_matrix,labelmap)
    
    stats["overall"] = stat_overall
    return stats


def print_confusion_matrix(confusion_matrix, categories, percentage=True):
    """
    Prints the confusion matrix to the console in latex format
    
    Parameters:
        confusion_matrix (np.list): numpy matrix representing the confusion matrix
        categories (dict): list of dicts containing all flowers. Example: [{id:1,name:"flowername"},...]
        precentage (bool): If the matrix entries should be printed in percentage or absolute values
    Returns:
        None
    """
    
    
    

    def short_name(name):
        if " " in name:
            if "faded" in name:
                return "centaurea j. f."
            return name[0:name.find(" ") + 2] + "."
        else:
            return name
    
    print("\nConfusion Matrix:")
    categories = sorted(categories, key = lambda i: i['name'])
    categories.append({"id":0, "name":"background"})
    
    '''
    for category in categories:
        if category["id"] == 15 or category["id"] == 16:
            categories.remove(category)
    '''        
            
    top_line = ""
    for category in categories:
        top_line += " & \\rotatebox[origin=c]{90}{\\textbf{" + short_name(category["name"]) + "}}"
    print(top_line + "\\\\")
    print("\\hline")
    
    
    for category_side in categories:
        line_string = "\\textbf{" + short_name(category_side["name"]) + "}"
        for category_top in categories:
            id_top = category_top["id"] -1
            id_side = category_side["id"] -1    
            
            value = confusion_matrix[id_side][id_top]
            percentage_value = 0
            for c in categories:
                percentage_value += confusion_matrix[c["id"]][id_top]
            if percentage_value != 0:
                percentage_value = value/percentage_value
            
            color = "Black"
            
            if id_top == id_side and value != 0:
                color = "ForestGreen"
            elif id_top == -1 and value != 0:
                color = "Orange"
            elif id_side == -1 and value != 0:
                color = "Red"
            elif value != 0:
                color = "Brown"
               
            if color == "Black":
                cell_string = " & -"
            else:
                if percentage:
                    cell_string = " & \\color{" + color + "}\\textbf{" + '{:.1f}'.format(round(percentage_value*100,ndigits=1)) + "}"
                else:
                    cell_string = " & \\color{" + color + "}\\textbf{" + str(int(value)) + "}"
            
            
            line_string += cell_string
                
                
            
            
        line_string += " \\\\"
        print(line_string)

    


        

def print_stats(stat, flower_name, print_latex_format = False):
    """
    Prints precision, recall, mAP, f1, TP, FP and FN to the console
    
    Parameters:
        stat (dict): dict containing TP, FP, FN and mAP. Example: {"tp": 5, "fp": 10, "fn": 1, "mAP": 0.76}
        flower_name (str): string of the flower name
    Returns:
        None
    """

    n = stat["tp"] + stat["fn"]
    if float(stat["fp"]+stat["tp"]) == 0:
        precision = "-"
    else:
        precision = float(stat["tp"]) / float(stat["fp"]+stat["tp"])
    if float(stat["tp"] + stat["fn"]) == 0:
        recall = "-"
    else:
        recall = float(stat["tp"]) / float(stat["tp"] + stat["fn"])

    f1 = "-"
    if recall != "-" and precision != "-" and ((recall >0) or (precision > 0)):
        f1 = 2 * (precision*recall)/(precision+recall)
    
    if print_latex_format:
        def short_name(name):
            if " " in name:
                if "faded" in name:
                    return "centaurea j. f."
                return name[0:name.find(" ") + 2] + "."
            else:
                return name

        if recall == "-":
            recall = 0
        if precision == "-":
            precision = 0
        if f1 == "-":
            f1 = 0
        print(short_name(flower_name) + " & " + str(n) + " & " + str(round(precision*100,1)) + " \\% & " + str(round(recall*100,1)) + " \\% & " + str(round(stat["mAP"],3)) + " & " + str(round(f1,3)) + " \\\\" )
    else:
        print(flower_name + " (n=" + str(n) + "):")
        print("   precision: " + str(precision))
        print("   recall: " + str(recall))
        print("   mAP: " + str(stat["mAP"]))
        print("   f1: " + str(f1))
        print("   TP: " + str(stat["tp"]) + " FP: " + str(stat["fp"]) + " FN: " + str(stat["fn"]))

        
def filter_ground_truth(ground_truths, flower_names):
    """ 
    Helper function that filters all entries of the ground truth which names are not
    in the flower_names list.
    
    Parameters:
        ground_truths (list): list of annotation dicts.
        flower_names (list): list of strings with all names that should be kept

    Returns:
        list: The list of ground truth annotations whose names are present in the flower_names list
    """

    filtered_ground_truths = []
    for gt in ground_truths:
        if gt["name"] in flower_names:
            filtered_ground_truths.append(gt)
    return filtered_ground_truths


def filter_predictions(predictions, min_score):
    """ 
    Helper function that that removes all predictions from the predictions list
    that have a score of less than min_score
    
    Parameters:
        predictions (list): list of annotation dicts.
        min_score (float): minimum score to be kept in the list

    Returns:
        list: The list of predictions whose score is >= min_score
    """

    filtered_predictions = []
    for prediction in predictions:
        if prediction["score"] >= min_score:
            #if prediction["name"] != "lotus corniculatus" and prediction["name"] != "leucanthemum vulgare" and prediction["name"] != "knautia arvensis":
            filtered_predictions.append(prediction)
    return filtered_predictions


                
def get_flower_names_from_labelmap(labelmap_path):
    """ 
    Helper function that converts a labelmap dict to a flower_names list
    
    Parameters:
        labelmap_path (str): path to the tensorflow labelmap file

    Returns:
        tuple: A tuple (flower_names,categories), where flower names is a list of 
            strings containing all flower names and categories is a list of dicts 
            in which each dict contains the id and the name of the flower
    """

    flower_names = []
    categories = []
    category_index = label_map_util.create_category_index_from_labelmap(labelmap_path, use_display_name=True)
    for d in category_index:
        flower_names.append(category_index[d]["name"])
        categories.append({"id":category_index[d]["id"], "name":category_index[d]["name"]})
    return (flower_names,categories)
          
def to_numpy_representations(annotations, categories):
    """ 
    Helper function that converts a list of annotations into a numpy representation
    that is required by tensorflow's evaluation classes
    
    Parameters:
        annotations (list): list of annotations
        categories (list): list of dicts in which each dict contains the id and
            the name of the flower

    Returns:
        tuple: numpy arrays of all bounding_boxes, all classes and all scores of the 
            provided annotations
    """

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
    """ 
    Helper function that returns the id used by tensorflow of a certain flower_name
    
    Parameters:
        categories (list): list of dicts in which each dict contains the id and
            the name of the flower
        flower_name (str): string of the flower name

    Returns:
        int: the tensorflow id of the flower_name
    """

    for flower in categories:
        if flower["name"] == flower_name:
            return flower["id"]
    raise ValueError('flower_name does not exist in categories dict')


if __name__ == '__main__':
    project_folder = constants.project_folder
    input_folder = constants.predictions_folder
    output_folder = constants.prediction_evaluation_folder
    iou_threshold = constants.iou_threshold
    evaluate(project_folder,input_folder, output_folder,iou_threshold)

