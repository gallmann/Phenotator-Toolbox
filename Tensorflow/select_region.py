# -*- coding: utf-8 -*-
"""
Created on Mon May 27 18:33:31 2019

@author: johan

This script lets the user edit annotations inside the LabelMe application.

"""

print("Loading libraries...")
import subprocess
from tkinter import messagebox
import tkinter
from utils import file_utils
import progressbar
from utils import constants
from PIL import Image
import os
import shutil
import gdal



def check_annotations(folder, roi_strip = True):
    """
    First lets the user create or edit annotations of all images in the folder with the
    LabelMe application. Then optionally turns all image pixels black which are
    not within a roi polygon annotation.
    
    Parameters:
        folder (str): path of the folder containing the images for which the 
            annotations should be created or checked
        roi_strip (bool): If true, strips the image after the user closes the 
            LabelMe application. Stripping means turning all pixels black that
            are not within a roi labelled polygon annotation.
    
    Returns:
        None
    """
    select_roi_in_images(folder)
    
    images = file_utils.get_all_images_in_folder(folder)
    
    if roi_strip:
        print("Stripping images (only keeping regions of interest):")
    else:
        print("Postprocessing...")
    for i in progressbar.progressbar(range(len(images))):
        image_path = images[i]
        copy_labelme_annotations_to_tablet_annotation_file(image_path)
        if roi_strip:
            file_utils.strip_image(image_path, image_path[:-4] + ".json", image_path)


def select_roi_in_images(folder):
    """
    First makes sure that all annotations are converted into the LabelMe specific
    json format. Then starts the LabelMe application with the images in the folder
    preloaded.
    
    Parameters:
        folder (str): path of the folder containing the images for which the 
            annotations should be created or checked
    
    Returns:
        None
    """

    image_paths = file_utils.get_all_images_in_folder(folder)          
    temp_folder = os.path.join(folder,"temp_large_images")
    scale_map = {}

    #create labelme annotation file that displays all annotations to the user
    for image_path in image_paths:
        
        if is_image_too_large(image_path):
            print("Scaling image...")
            temp_image_path = os.path.join(temp_folder,os.path.basename(image_path))
            os.makedirs(temp_folder,exist_ok=True)
            shutil.move(image_path, temp_image_path)
            scale = scale_image_down(temp_image_path,folder)
            scale_map[temp_image_path] = scale
            scale_annotation_file(image_path,scale)
        
        annotations = file_utils.get_annotations(image_path)
        #if not os.path.isfile(image_path[:-4] + ".json"):
        file_utils.annotations_to_labelme_file(annotations,image_path[:-4] + ".json",image_path)
    
    # hide main window
    root = tkinter.Tk()
    root.withdraw()
    # message box display
    messagebox.showinfo("Information","A window will open with the LabelMe Program. Within that program click through all images by using the 'Next Image' button. On each image draw one or more Polygons around the region of interest and label them 'roi'. Once done simply close the labelme program. All your selections will be saved and further processed. \n\nAdditionally all annotations are displayed as bounding boxes. If necessary these can be adjusted.")
    subprocess.call(["labelme", folder, "--nodata", "--autosave", "--labels", "roi"])
    
    
    if os.path.isdir(temp_folder):
        temp_images = file_utils.get_all_images_in_folder(temp_folder)
        for temp_image_path in temp_images:
            dest_image_path = os.path.join(folder,os.path.basename(temp_image_path))
            shutil.move(temp_image_path, dest_image_path)
            scale_annotation_file(dest_image_path,1.0/scale_map[temp_image_path])
        os.rmdir(temp_folder)

    
    
def scale_annotation_file(image_path,scale):
    copy_labelme_annotations_to_tablet_annotation_file(image_path)
    annotations = file_utils.get_annotations(image_path)
    for annotation in annotations:
        for coord in annotation["polygon"]:
            coord["x"] = coord["x"] *scale
            coord["y"] = coord["y"] *scale
    file_utils.annotations_to_labelme_file(annotations,image_path[:-4]+ ".json",image_path)
    copy_labelme_annotations_to_tablet_annotation_file(image_path)

def scale_image_down(image_path, dest_folder):
    
    image_output_path = os.path.join(dest_folder,os.path.basename(image_path))
    ds = gdal.Open(image_path)
    band = ds.GetRasterBand(1)
    width = band.XSize
    height = band.YSize
    if width > height:
        new_width = 7000
        new_height = new_width/width*height
    else:
        new_height = 7000
        new_width = new_height/height*width
    
    gdal.Translate(image_output_path,ds, options=gdal.TranslateOptions(width=int(new_width),height=int(new_height), bandList=[1,2,3]))
    scale_factor = new_width/width
    return scale_factor

def is_image_too_large(image_path):
    try:
        Image.open(image_path)
        return False
    except Image.DecompressionBombError:
        return True
        
    
    
    
def copy_labelme_annotations_to_tablet_annotation_file(image_path):
    """
    Copies annotations from the LabelMe json files to the tablet app annotation
    file format and saves it.
    
    Parameters:
        image_path (str): path of the image whose annotations should be converted
            to the tablet annotation json format
    
    Returns:
        None
    """

    annotations = file_utils.get_annotations_from_labelme_file(image_path[:-4] + ".json")
    file_utils.save_json_file(annotations, image_path[:-4] + "_annotations.json")



if __name__ == '__main__':
    input_folder = constants.input_folders[0]
    input_folder = "C:/Users/johan/Desktop/MaskedAnnotatedSingleOrthoPhotos"
    check_annotations(input_folder)
    