# -*- coding: utf-8 -*-
"""
Created on Mon Apr 20 11:40:24 2020

@author: johan
"""

import os
import json
import shutil
from PIL import Image
import progressbar


def convert_coco_annotations(coco_annotations_file, output_folder):
    coco_annotations = read_json_file(coco_annotations_file)
    categories = coco_annotations["categories"]
    images = coco_annotations["images"]
    annotations = coco_annotations["annotations"]
    
    category_map = {}
    for category in categories:
        category_map[category["id"]] = category["name"]
    
    my_annotations = {}
    
    print("Copying images to destination folder...",flush=True)
    for image in progressbar.progressbar(images):
        image_path = image["path"]
        dst_path = os.path.join(output_folder,os.path.basename(image_path))
        shutil.copyfile(image_path,dst_path)
        my_annotations[image["id"]] = {"path": dst_path, "annotations":[]}
    
    print("Reading annotations...",flush=True)
    for annotation in progressbar.progressbar(annotations):
        name = category_map[annotation["category_id"]]
        bounding_box = annotation["bbox"]
        
        my_annotation = {"name": name, "bounding_box" : bounding_box}
        
        my_annotations[annotation["image_id"]]["annotations"].append(my_annotation)
        
    print("Saving annotations...",flush=True)
    for image_id in progressbar.progressbar(my_annotations.keys()):
        dst_path = my_annotations[image_id]["path"]
        annotation_path = dst_path[:-4] + ".json"
        annotations = my_annotations[image_id]["annotations"]
        annotations_to_labelme_file(annotations,annotation_path,dst_path)
        


def annotations_to_labelme_file(annotations,output_path,image_path):

    image = Image.open(image_path)    
    width, height = image.size

    label_me_dict_template = {"version":"3.15.2","flags":{},"shapes":[],"lineColor":[0,255,0,64],"fillColor":[255,0,0,64],"imagePath":os.path.basename(image_path), "imageData":None,"imageHeight":height,"imageWidth":width}
    if annotations:
        for annotation in annotations:
            col = [255,0,0,64]
            flower_dict = {"label":annotation["name"], "line_color":col,"fill_color":col,"points":[],"shape_type":"rectangle","flags":{}}
            
            [left,top,width,height] = annotation["bounding_box"]
            right = left+width
            bottom = top+height
            
            flower_dict["points"] = [[left,top],[right,bottom]]
            label_me_dict_template["shapes"].append(flower_dict)
        
    save_json_file(label_me_dict_template,output_path)

        
    
def save_json_file(dictionary, output_path):
    """Saves a dictionary to a json file

    Parameters:
        dictionary (dict): the dictionary containing the data
        output_path (str): the path of the output json file
    
    Returns:
        None
    """

    with open(output_path, 'w') as fp:
        json.dump(dictionary, fp)

    
def read_json_file(file_path):
    """Reads a json file into a dict

    Parameters:
        file_path (str): path to json file
    
    Returns:
        dict: a dictionary containing the json file data (or None if the 
            file does not exist)
    """

    if file_path and os.path.isfile(file_path):
        with open(file_path, 'r') as f:
            try:
                jsondata = json.load(f)
                return jsondata
            except Exception as e:
                print(e)
                print(file_path)
                return None
    else:
        return None

    

    
if __name__== "__main__":
    coco_annotations_file = "C:/Users/johan/Downloads/ETHZ/zurich_dataset_1_filtered.json"
    output_folder = "C:/Users/johan/Downloads/ETHZ/output"
    
    convert_coco_annotations(coco_annotations_file,output_folder)