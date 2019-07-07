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
from PIL import Image, ImageDraw
from utils import flower_info
import numpy


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
            flower_dict = {"label":flower["name"], "line_color":col,"fill_color":col,"points":[],"shape_type":"rectangle","flags":{}}
            if flower["name"] == "roi":
                flower_dict["shape_type"] = "polygon"
                for point in flower["polygon"]:
                    flower_dict["points"].append([point["x"],point["y"]])
            else:
                [top,left,bottom,right] = flower_info.get_bbox(flower)
                flower_dict["points"] = [[left,top],[right,bottom]]
            label_me_dict_template["shapes"].append(flower_dict)
        
    save_json_file(label_me_dict_template,output_path)
    
def get_annotations_from_labelme_file(labelme_file):
    labelme_dict = read_json_file(labelme_file)
    annotations = {"annotatedFlowers":[]}
    
    
    for annotation in labelme_dict["shapes"]:
        result_annotation = {}
        result_annotation["isPolygon"] = True
        result_annotation["name"] = annotation["label"]
        polygon = []
        for point in annotation["points"]:
            polygon.append({"x":point[0], "y":point[1]})
        result_annotation["polygon"] = polygon
        annotations["annotatedFlowers"].append(result_annotation)
    return annotations

    
def check_all_json_files_in_folder(folder_path):
    for file in os.listdir(folder_path):
        if file.endswith(".json"):
            read_json_file(file)
    print("if no errors were printed, everything is fine")
    
#turns all pixels that are not within a roi polygon black
def strip_image(input_image_path, roi_file, output_image_path):
    
    polygons_json = read_json_file(roi_file)["shapes"]
    polygons = []
    
    for polygon_json in polygons_json:
        if polygon_json["label"] == "roi":
            polygon = []
            for point in polygon_json["points"]:
                polygon.append((point[0],point[1]))
            polygons.append(polygon)

    # read image as RGB (without alpha)
    img = Image.open(input_image_path).convert("RGB")
    
    # convert to numpy (for convenience)
    img_array = numpy.asarray(img)
    
    # create new image ("1-bit pixels, black and white", (width, height), "default color")
    mask_img = Image.new('1', (img_array.shape[1], img_array.shape[0]), 0)
    
    for polygon in polygons:
        ImageDraw.Draw(mask_img).polygon(polygon, outline=1, fill=1)

    mask = numpy.array(mask_img)
    
    # assemble new image (uint8: 0-255)
    new_img_array = numpy.empty(img_array.shape, dtype='uint8')
    
    # copy color values (RGB)
    new_img_array[:,:,:3] = img_array[:,:,:3]
    
    # filtering image by mask
    new_img_array[:,:,0] = new_img_array[:,:,0] * mask
    new_img_array[:,:,1] = new_img_array[:,:,1] * mask
    new_img_array[:,:,2] = new_img_array[:,:,2] * mask
    
    # back to Image from numpy
    newIm = Image.fromarray(new_img_array, "RGB")
    newIm.save(output_image_path, format="png")

