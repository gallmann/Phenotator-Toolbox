# -*- coding: utf-8 -*-
"""
Created on Fri Aug  9 12:56:20 2019

@author: gallmanj
"""

from utils import file_utils
from utils import flower_info
from object_detection.utils import label_map_util


# Malisiewicz et al.
def non_max_suppression(detections, iou_thresh):
    detections = reversed(sorted(detections, key = lambda i: i['score']))
    keep = []
    
    for detection in detections:
        
        add_this_one = True
        for added in keep:
            if iou(added["bounding_box"],detection["bounding_box"]) >= iou_thresh:
                add_this_one = False
                break
        if add_this_one:
            keep.append(detection)
    
    return keep


def iou(a, b, epsilon=1e-5):
    """ Given two boxes `a` and `b` defined as a list of four numbers:
            [x1,y1,x2,y2]
        where:
            x1,y1 represent the upper left corner
            x2,y2 represent the lower right corner
        It returns the Intersect of Union score for these two boxes.

    Parameters:
        a (list): (list of 4 numbers) [x1,y1,x2,y2]
        b (list): (list of 4 numbers) [x1,y1,x2,y2]
        epsilon (float): Small value to prevent division by zero

    Returns:
        (float) The Intersection over Union score.
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


def get_ground_truth_annotations(image_path):
    """Reads the ground_thruth information from either the tablet annotations (imagename_annotations.json),
        the LabelMe annotations (imagename.json) or tensorflow xml format annotations (imagename.xml)

    Parameters:
        image_path (str): path to the image of which the annotations should be read
    
    Returns:
        list: a list containing all annotations corresponding to that image.
            Returns the None if no annotation file is present
    """
    ground_truth = file_utils.get_annotations(image_path)
    for fl in ground_truth:
        fl["name"] = flower_info.clean_string(fl["name"])
        fl["bounding_box"] = flower_info.get_bbox(fl)
    
    if len(ground_truth) == 0:                     
        return None
    return ground_truth


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
            filtered_predictions.append(prediction)
    return filtered_predictions
