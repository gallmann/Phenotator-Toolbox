# -*- coding: utf-8 -*-
"""
Created on Wed Apr  3 23:39:23 2019

This script takes all images in the input_folder, draws the bounding boxes onto the images and saves 
them to the output_folder
@author: johan
"""


input_folder = "C:/Users/johan/Desktop/output/images/annotated_ortho_photos"
input_folder = "C:/Users/gallmanj.KP31-21-161/Desktop/output/images/annotated_ortho_photos"
output_folder = "C:/Users/johan/Desktop/vis_im"
output_folder = "C:/Users/gallmanj.KP31-21-161/Desktop/vis_im"


from object_detection.utils import visualization_utils
from PIL import Image
from utils import file_utils
from utils import flower_info
import os
import progressbar



def draw_bounding_boxes(input_folder, output_folder):
    images = file_utils.get_all_images_in_folder(input_folder)
    print("Drawing bounding boxes on images:")
    file_utils.delete_folder_contents(output_folder)
    for i in progressbar.progressbar(range(len(images))):
        image_path = images[i]
        image = Image.open(image_path)
        
        annotation_path = image_path[:-4] + "_annotations.json"
        annotation_data = file_utils.read_json_file(annotation_path)
        annotations = annotation_data["annotatedFlowers"]
        for flower in annotations:
            if flower["isPolygon"]:
                continue
                #TODO!!   
            else:
                
                flower_name = file_utils.clean_string(flower["name"])
                x = round(flower["polygon"][0]["x"])
                y = round(flower["polygon"][0]["y"])
                bounding_box_size = flower_info.get_bbox_size(flower_name)
                xmin = x - bounding_box_size
                ymin = y - bounding_box_size
                xmax = x + bounding_box_size
                ymax = y + bounding_box_size
                visualization_utils.draw_bounding_box_on_image(image,ymin,xmin,ymax,xmax,display_str_list=(), use_normalized_coordinates=False, thickness=1)
              
        image_name = os.path.basename(image_path)
        image.save(os.path.join(output_folder,image_name))
    print("Done!")
    

draw_bounding_boxes(input_folder,output_folder)
