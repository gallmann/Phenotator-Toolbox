# -*- coding: utf-8 -*-
"""
Created on Wed Apr  3 23:39:23 2019

This script takes all images in the input_folder, draws the bounding boxes onto the images and saves 
them to the output_folder
@author: johan
"""


input_folder = "C:/Users/johan/Desktop/output/images/train"
#input_folder = "C:/Users/gallmanj.KP31-21-161/Desktop/eschikon"
output_folder = "C:/Users/johan/Desktop/vis_im"
#output_folder = "C:/Users/gallmanj.KP31-21-161/Desktop/vis_im"


from object_detection.utils import visualization_utils
from PIL import Image
from utils import file_utils
from utils import flower_info
import os
import progressbar
import matplotlib
import xml.etree.cElementTree as ET


def get_color_for_index(index):
    label = list(matplotlib.colors.cnames.keys())[index]
    return label


def draw_bounding_boxes(input_folder, output_folder):
    flowers = []
    images = file_utils.get_all_images_in_folder(input_folder)
    print("Drawing bounding boxes on images:")
    file_utils.delete_folder_contents(output_folder)
    for i in progressbar.progressbar(range(len(images))):
        image_path = images[i]
        image = Image.open(image_path)
        
        annotation_path = image_path[:-4] + "_annotations.json"
        annotation_path_xml = image_path[:-4] + ".xml"
        if annotation_path and os.path.isfile(annotation_path):
            annotation_data = file_utils.read_json_file(annotation_path)
            annotations = annotation_data["annotatedFlowers"]
            for flower in annotations:
                flower_name = file_utils.clean_string(flower["name"])
                [left,right,top,bottom] = flower_info.get_bbox(flower)
                if not flower_name in flowers:
                    flowers.append(flower_name)
                col = get_color_for_index(flowers.index(flower_name))
                visualization_utils.draw_bounding_box_on_image(image,top,left,bottom,right,display_str_list=(), color=col, use_normalized_coordinates=False, thickness=1)
                
        
        elif annotation_path_xml and os.path.isfile(annotation_path_xml):
            annotations = get_annotations_from_xml(annotation_path_xml)
            for flower in annotations:
                flower_name = file_utils.clean_string(flower["name"])
                [left,right,top,bottom] = flower["bounding_box"]
                if not flower_name in flowers:
                    flowers.append(flower_name)
                col = get_color_for_index(flowers.index(flower_name))
                visualization_utils.draw_bounding_box_on_image(image,top,left,bottom,right,display_str_list=(), color=col, use_normalized_coordinates=False, thickness=1)


        image_name = os.path.basename(image_path)
        image.save(os.path.join(output_folder,image_name))
    print("Done!")
    

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
                    flower["bounding_box"] = [left,right,top,bottom]
                            
            annotations.append(flower)
    return annotations


draw_bounding_boxes(input_folder,output_folder)
