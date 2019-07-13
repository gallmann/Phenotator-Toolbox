# -*- coding: utf-8 -*-
"""
Created on Mon May 27 18:33:31 2019

@author: johan
"""

print("Loading libraries...")
import subprocess
from tkinter import messagebox
import tkinter
from utils import file_utils
import progressbar
from utils import constants




def check_annotations(folder, roi_strip = True):
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
    
    #create labelme annotation file that displays all annotations to the user
    image_paths = file_utils.get_all_images_in_folder(folder)
    for image_path in image_paths:
        annotations = file_utils.get_annotations(image_path)
        #if not os.path.isfile(image_path[:-4] + ".json"):
        file_utils.annotations_to_labelme_file(annotations,image_path[:-4] + ".json",image_path)
    
    # hide main window
    root = tkinter.Tk()
    root.withdraw()
    # message box display
    messagebox.showinfo("Information","A window will open with the LabelMe Program. Within that program click through all images by using the 'Next Image' button. On each image draw one or more Polygons around the region of interest and label them 'roi'. Once done simply close the labelme program. All your selections will be saved and further processed. \n\nAdditionally all annotations are displayed as bounding boxes. If necessary these can be adjusted.")
    subprocess.call(["labelme", folder, "--nodata", "--autosave", "--labels", "roi"])
        
    
    
def copy_labelme_annotations_to_tablet_annotation_file(image_path):
    annotations = file_utils.get_annotations_from_labelme_file(image_path[:-4] + ".json")
    file_utils.save_json_file(annotations, image_path[:-4] + "_annotations.json")



if __name__ == '__main__':
    input_folder = constants.input_folders[0]
    input_folder = "C:/Users/johan/Desktop/MaskedAnnotatedSingleOrthoPhotos"
    check_annotations(input_folder)
    