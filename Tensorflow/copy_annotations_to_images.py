# -*- coding: utf-8 -*-
"""
Created on Thu Jun 27 13:32:49 2019

@author: johan

This script copies annotations saved in one folder onto images saved in another folder.
Read the descriptions of the three functions for more information.
"""

print("Loading libraries...")
from utils import apply_annotations
from utils import file_utils
import subprocess
import os
import tkinter
from tkinter import messagebox
import random
import progressbar
import signal                         
terminate = False                            


def copy_annotations_to_images(annotated_folder, to_be_annotated_folder, output_folder):
    """
    Copies all annotations from the annotated_folder to all images in the to_be_annotated_folder and saves
    them into the output_folder. Note that the images in the annotated_folder and the
    to_be_annotated_folder have to be geo referenced. (either georeferenced tifs) or
    jpg/png with imagename_geoinfo.json files in the same folder

    Parameters:
        annotated_folder (str): path of the folder containing annotations
        to_be_annotated_folder (str) path to the folder containing the images that
            are to be annotated
        output_folder (str): path to the folder where the annotated images from the 
            to_be_annotated_folder are saved to
    
    Returns:
        None
    """

    apply_annotations.apply_annotations_to_images(annotated_folder, to_be_annotated_folder,output_folder)
    
    
# lets the user check and adjust all images within a folder.
def check_images(output_folder):
    """
    Lets the user see and edit all annotated images in the output_folder in the LabelMe application

    Parameters:
        output_folder (str): path of the folder containing annotated images
    
    Returns:
        None
    """

    
    
    all_images = file_utils.get_all_images_in_folder(output_folder)
    for image_path in all_images:
        annotations = file_utils.get_annotations(image_path)
        file_utils.annotations_to_labelme_file(annotations,image_path[:-4] + ".json",image_path)
    
    subprocess.call(["labelme", output_folder, "--nodata", "--autosave", "--labels", "roi"])
    
def has_only_roi_annotations(annotations):
    """
    Helper function returning True if all annotations within the annotations list
    are labelled as 'roi'
    
    Parameters:
        annotations (list): list of annotation dicts
    
    Returns:
        bool: True if all annotations within the input list are labelled as 'roi', False otherwise
    """

    
    for annotation in annotations:
        if annotation["name"] != "roi":
            return False
    return True
    
def copy_annotations_to_images_one_by_one(annotated_folder, to_be_annotated_folder, output_folder):
    """
    This function copies the annotations onto one image at a time. After the copying, 
    the user is shown the copy results in the LabelMe application, so he can check and adjust
    them. Once done, the process continues with the next image.
    If one image inside the to_be_annotated_folder is already in the output_folder, nothing is done.
    This allows the user to inerrupt this process and continue on at a later time. 
    
    Parameters:
        annotated_folder (str): path of the folder containing annotations
        to_be_annotated_folder (str) path to the folder containing the images that
            are to be annotated
        output_folder (str): path to the folder where the annotated images from the 
            to_be_annotated_folder are saved to
    
    Returns:
        None
    """

    
    
    
    all_images = file_utils.get_all_images_in_folder(to_be_annotated_folder)
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
        if(len(annotations) == 0 or has_only_roi_annotations(annotations)):
            file_utils.strip_image(image_path_in_output_folder,roi_file_path,image_path_in_output_folder)
            continue
        
        subprocess.call(["labelme", image_path_in_output_folder, "--nodata", "--autosave", "--labels", "roi"])
        file_utils.strip_image(image_path_in_output_folder,roi_file_path,image_path_in_output_folder)
        
        annotations = file_utils.get_annotations_from_labelme_file(roi_file_path)
        file_utils.save_json_file(annotations, annotations_file_path_in_output_folder)
        if terminate:
            print("Exiting...")
            break





def signal_handling(signum,frame):           
    global terminate                         
    terminate = True       

signal.signal(signal.SIGINT,signal_handling) 

            
if __name__ == '__main__':
    annotated_folder = "C:/Users/johan/Desktop/MaskedAnnotationData"
    to_be_annotated_folder = "D:/MasterThesis/Data/July_03/Agisoft/single_ortho_tifs"
    output_folder = "D:/MasterThesis/Data/July_03/MaskedAnnotatedSingleOrthoPhotos"
    copy_annotations_to_images_one_by_one(annotated_folder,to_be_annotated_folder,output_folder)
#check_images(output_folder)


