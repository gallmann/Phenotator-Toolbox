# -*- coding: utf-8 -*-
"""
Created on Wed Apr  3 23:39:23 2019

This script takes all images in the input_folder, draws the bounding boxes onto the images and saves 
them to the output_folder. Alongside each image either a json file or an xml file with the annotation
data has to be provided. 
@author: johan
"""


input_folder = "C:/Users/johan/Desktop/MasterThesis/Data/June_06/MaskedAnnotationData"

output_folder = "C:/Users/johan/Desktop/vis_im"



from object_detection.utils import visualization_utils
from PIL import Image
from utils import file_utils
from utils import flower_info
import os
import progressbar
import matplotlib


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
                flower_name = flower_info.clean_string(flower["name"])
                [top,left,bottom,right] = flower_info.get_bbox(flower)
                if not flower_name in flowers:
                    flowers.append(flower_name)
                col = get_color_for_index(flowers.index(flower_name))
                visualization_utils.draw_bounding_box_on_image(image,top,left,bottom,right,display_str_list=(), color=col, use_normalized_coordinates=False, thickness=1)
                
        
        elif annotation_path_xml and os.path.isfile(annotation_path_xml):
            annotations = file_utils.get_annotations_from_xml(annotation_path_xml)
            for flower in annotations:
                flower_name = flower_info.clean_string(flower["name"])
                [top,left,bottom,right] = flower["bounding_box"]
                if not flower_name in flowers:
                    flowers.append(flower_name)
                col = get_color_for_index(flowers.index(flower_name))
                visualization_utils.draw_bounding_box_on_image(image,top,left,bottom,right,display_str_list=(), color=col, use_normalized_coordinates=False, thickness=1)

        image_name = os.path.basename(image_path)
        image.save(os.path.join(output_folder,image_name))
    print("Done!")
    


draw_bounding_boxes(input_folder,output_folder)
