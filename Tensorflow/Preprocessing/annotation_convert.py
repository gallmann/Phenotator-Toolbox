# -*- coding: utf-8 -*-
"""
Created on Mon Apr  1 11:25:16 2019

@author: johan
"""

import os
import json
import xml.etree.cElementTree as ET
from PIL import Image

bounding_box_size = 20 


def convert_annotation_folder(folder_path):
    
    image_paths = get_all_images_in_folder(folder_path)
    for image_path in image_paths:
        annotation_path = image_path[:-4] + "_annotations.json"
        xml_path = image_path[:-4] + ".xml"
        annotation_data = read_json_file(annotation_path)
        if(not annotation_data):
            continue
        annotations = annotation_data["annotatedFlowers"]
        annotations_xml = build_xml_tree(annotations, image_path)  
        annotations_xml.write(xml_path)
        


def build_xml_tree(flowers, image_path):
    root = ET.Element("annotation")
    image = Image.open(image_path)
    width, height = image.size
    size = ET.SubElement(root, "size")
    ET.SubElement(size, "width").text = str(width)
    ET.SubElement(size, "height").text = str(height)
    
    for flower in flowers:
        if flower["isPolygon"]:
            continue
            #TODO!!
            
        else:
            annotation_object = ET.SubElement(root, "object")
            ET.SubElement(annotation_object, "name").text = flower["name"]
            bndbox = ET.SubElement(annotation_object, "bndbox")
            x = round(flower["polygon"][0]["x"])
            y = round(flower["polygon"][0]["y"])
            ET.SubElement(bndbox, "xmin").text = str(x - bounding_box_size)
            ET.SubElement(bndbox, "ymin").text = str(y - bounding_box_size)
            ET.SubElement(bndbox, "xmax").text = str(x + bounding_box_size)
            ET.SubElement(bndbox, "ymax").text = str(y + bounding_box_size)

    tree = ET.ElementTree(root)
    return tree


def get_all_images_in_folder(folder_path):
    images = []
    for file in os.listdir(folder_path):
        if file.endswith(".png"):
            images.append(os.path.join(folder_path, file))
    return images

    
    
def read_json_file(file_path):
    if file_path and os.path.isfile(file_path):
        with open(file_path, 'r', encoding='iso-8859-1') as f:
            jsondata = json.load(f)
        return jsondata
    else:
        return None


convert_annotation_folder("C:/Users/johan/Downloads/eschlikon")
