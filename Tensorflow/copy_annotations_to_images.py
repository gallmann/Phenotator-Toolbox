# -*- coding: utf-8 -*-
"""
Created on Thu Jun 27 13:32:49 2019

@author: johan
"""


from utils import constants


annotated_folder = "C:/Users/johan/Desktop/AnnotationData"
to_be_annotated_folder = "C:/Users/johan/Desktop/Agisoft2/single_shot_ortho_photos"
output_folder = "C:/Users/johan/Desktop/annotated_orthophotos"


import os
from utils import apply_annotations
from utils import file_utils
import subprocess



def copy_annotations_to_images(annotated_folder, to_be_annotated_folder, output_folder):
    
    apply_annotations.apply_annotations_to_images(annotated_folder, to_be_annotated_folder,output_folder)
    
    
    
def check_images(output_folder):
    all_images = file_utils.get_all_images_in_folder(output_folder)
    for image_path in all_images:
        annotations = file_utils.get_annotations(image_path)
        file_utils.annotations_to_labelme_file(annotations,image_path[:-4] + ".json",image_path)
    
    subprocess.call(["labelme", output_folder, "--nodata", "--autosave", "--labels", "roi"])
    
    
    
#copy_annotations_to_images(annotated_folder,to_be_annotated_folder,output_folder)
check_images(output_folder)