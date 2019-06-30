# -*- coding: utf-8 -*-
"""
Created on Mon May 27 18:33:31 2019

@author: johan
"""


import subprocess
from tkinter import messagebox
import tkinter
from utils import file_utils
import progressbar
from utils import constants

input_folder = constants.input_folders[0]
input_folder = "C:/Users/johan/Desktop/AnnotationData"


def select_roi_in_images(folder):
    
    #create labelme annotation file that displays all annotations to the user
    image_paths = file_utils.get_all_images_in_folder(input_folder)
    for image_path in image_paths:
        annotations = file_utils.get_annotations(image_path)
        #if not os.path.isfile(image_path[:-4] + ".json"):
        file_utils.annotations_to_labelme_file(annotations,image_path[:-4] + ".json",image_path)
    
    # hide main window
    root = tkinter.Tk()
    root.withdraw()
    # message box display
    messagebox.showinfo("Information","A window will open with the LabelMe Program. Within that program click through all images by using the 'Next Image' button. On each image draw one or more Polygons around the region of interest and label them 'roi'. Once done simply close the labelme program. All your selections will be saved and further processed. \n\n Additionally all annotations are displayed as bounding boxes. If necessary these can be adjusted.")
    subprocess.call(["labelme", folder, "--nodata", "--autosave", "--labels", "roi"])
    


def get_annotations_from_labelme_file(labelme_file):
    labelme_dict = file_utils.read_json_file(labelme_file)
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
    
    
def copy_labelme_annotations_to_tablet_annotation_file(image_path):
    annotations = get_annotations_from_labelme_file(image_path[:-4] + ".json")
    file_utils.save_json_file(annotations, image_path[:-4] + "_annotations.json")


select_roi_in_images(input_folder)

images = file_utils.get_all_images_in_folder(input_folder)

for i in progressbar.progressbar(range(len(images))):
    image_path = images[i]
    file_utils.strip_image(image_path, image_path[:-4] + ".json", image_path)
    copy_labelme_annotations_to_tablet_annotation_file(image_path)

    