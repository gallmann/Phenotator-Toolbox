# -*- coding: utf-8 -*-
"""
Created on Tue Apr 16 14:52:32 2019

@author: johan



This file contains some helper functions which are used by multiple scripts such as enumerating all images
in a folder or reading a json file.
"""
import os
import json
import shutil
import xml.etree.cElementTree as ET
from PIL import Image
from utils import flower_info



def read_json_file(file_path):
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


def save_json_file(dictionary, output_path):
    with open(output_path, 'w') as fp:
        json.dump(dictionary, fp)
        



def get_all_images_in_folder(folder_path):
    images = []
    for file in os.listdir(folder_path):
        if file.endswith(".png"):
            images.append(os.path.join(folder_path, file))
    return images



def get_all_tifs_in_folder(folder_path):
    images = []
    for file in os.listdir(folder_path):
        if file.endswith(".tif"):
            images.append(os.path.join(folder_path, file))
    return images


def delete_folder_contents(folder_path):
    for the_file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path): shutil.rmtree(file_path)
        except Exception as e:
            print(e)
                
    
    
def get_annotations_from_xml(xml_path):
    annotations = []
    tree = ET.parse(xml_path)
    root = tree.getroot()
    for child in root:
        if(child.tag == "object"):
            flower = {}
            for att in child:
                if(att.tag == "name"):
                    flower["name"] = att.text
                if(att.tag == "bndbox"):
                    left=right=top=bottom = 0
                    for bound in att:
                        if(bound.tag == "xmin"):
                            left = int(bound.text)
                        if(bound.tag == "ymin"):
                            top = int(bound.text)
                        if(bound.tag == "xmax"):
                            right = int(bound.text)
                        if(bound.tag == "ymax"):
                            bottom = int(bound.text)
                    flower["bounding_box"] = [top,left,bottom,right]
                            
            annotations.append(flower)
    return annotations

    
def get_annotations(image_path):
    annotation_path = image_path[:-4] + "_annotations.json"
    annotation_data = read_json_file(annotation_path)
    if(not annotation_data):
        return []
    annotations = annotation_data["annotatedFlowers"]
    return annotations


def annotations_to_labelme_file(annotations,output_path,image_path):
    image = Image.open(image_path)    
    width, height = image.size
    label_me_dict_template = {"version":"3.15.2","flags":{},"shapes":[],"lineColor":[0,255,0,64],"fillColor":[255,0,0,64],"imagePath":os.path.basename(image_path), "imageData":None,"imageHeight":height,"imageWidth":width}
    if annotations:
        for flower in annotations:
            col = flower_info.get_color_for_flower(flower["name"], get_rgb_value=True)
            flower_dict = {"label":flower["name"], "line_color":col,"fill_color":col,"points":[],"shape_type":"polygon","flags":{}}
            if flower["name"] == "roi":
                flower_dict["points"] = []
                for point in flower["polygon"]:
                    flower_dict["points"].append([point["x"],point["y"]])
            else:
                [top,left,bottom,right] = flower_info.get_bbox(flower)
                flower_dict["points"] = [[left,top],[left,bottom],[right,bottom],[right,top]]
            label_me_dict_template["shapes"].append(flower_dict)
        
    save_json_file(label_me_dict_template,output_path)
    
    
def check_all_json_files_in_folder(folder_path):
    for file in os.listdir(folder_path):
        if file.endswith(".json"):
            read_json_file(file)
    print("if no errors were printed, everything is fine")
    
