# -*- coding: utf-8 -*-
"""
Created on Thu Jun 27 13:32:49 2019

@author: johan
"""


from utils import constants


annotated_folder = "C:/Users/johan/Desktop/MaskedAnnotationData"
to_be_annotated_folder = "C:/Users/johan/Desktop/flight2/Agisoft/single_ortho_tifs"
output_folder = "C:/Users/johan/Desktop/MaskedAnnotatedSingleOrthoPhotos"


from utils import apply_annotations
from utils import file_utils
import subprocess
import os
import tkinter
from tkinter import messagebox
import random
import progressbar

#copies all annotations from the annotated_folder to all images in the to_be_annotated_folder and saves
#them into the output_folder
def copy_annotations_to_images(annotated_folder, to_be_annotated_folder, output_folder):
    
    apply_annotations.apply_annotations_to_images(annotated_folder, to_be_annotated_folder,output_folder)
    
    
# lets the user check and adjust all images within a folder.
def check_images(output_folder):
    all_images = file_utils.get_all_images_in_folder(output_folder)
    for image_path in all_images:
        annotations = file_utils.get_annotations(image_path)
        file_utils.annotations_to_labelme_file(annotations,image_path[:-4] + ".json",image_path)
    
    subprocess.call(["labelme", output_folder, "--nodata", "--autosave", "--labels", "roi"])
    
    
#this function lets the user check all copied annotations one by one. Once one image is checked it is saved to the
#output_folder. If one image inside the to_be_annotated_folder is already in the output_folder, nothing is done.
#This allows the user to inerrupt this process and continue on at a later time. 
def copy_annotations_to_images_one_by_one(annotated_folder, to_be_annotated_folder, output_folder):
    all_images = file_utils.get_all_tifs_in_folder(to_be_annotated_folder)
    random.shuffle(all_images)

    # hide main window
    root = tkinter.Tk()
    root.withdraw()
    # message box display
    messagebox.showinfo("Information","A window will open with the LabelMe Program. It will show one single image with the annotations. Please check all annotations and modify them if necessary! Also make sure the 'roi' polygon is set correctly. Only the regions within a 'roi' polygon will be further processed. The rest of the image is discarded. Once this is done, simply close the LabelMe program and a new image will be opened in a new LabelMe program instance.")
    
    for i in progressbar.progressbar(range(len(all_images))):
        image_path = all_images[i]
        image_path_in_output_folder = os.path.join(output_folder,os.path.basename(image_path)[:-4]+".png")
        roi_file_path = image_path_in_output_folder[:-4] + ".json"
        annotations_file_path_in_output_folder = image_path_in_output_folder[:-4] + "_annotations.json"
        
        if os.path.isfile(image_path_in_output_folder):
            continue
        
        
        apply_annotations.apply_annotations_to_image(annotated_folder,image_path,output_folder)
        annotations = file_utils.get_annotations(image_path_in_output_folder)
        roi_file_path = image_path_in_output_folder[:-4] + ".json"
        file_utils.annotations_to_labelme_file(annotations,roi_file_path,image_path_in_output_folder)
        if(len(annotations) == 0):
            file_utils.strip_image(image_path_in_output_folder,roi_file_path,image_path_in_output_folder)
            continue
        
        subprocess.call(["labelme", image_path_in_output_folder, "--nodata", "--autosave", "--labels", "roi"])
        file_utils.strip_image(image_path_in_output_folder,roi_file_path,image_path_in_output_folder)
        
        annotations = file_utils.get_annotations_from_labelme_file(roi_file_path)
        file_utils.save_json_file(annotations, annotations_file_path_in_output_folder)


copy_annotations_to_images_one_by_one(annotated_folder,to_be_annotated_folder,output_folder)
#check_images(output_folder)


