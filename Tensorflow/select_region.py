# -*- coding: utf-8 -*-
"""
Created on Mon May 27 18:33:31 2019

@author: johan
"""


import subprocess
from tkinter import messagebox
import tkinter
import numpy
from PIL import Image, ImageDraw
from utils import file_utils
import progressbar


input_folder = "G:/Johannes/Data/May_23/test"



def select_roi_in_images(folder):
    
    # hide main window
    root = tkinter.Tk()
    root.withdraw()
    # message box display
    messagebox.showinfo("Information","A window will open with the LabelMe Program. Within that program click through all images by using the 'Next Image' button. On each image draw one or more Polygons around the region of interest and label them 'roi'. Once done simply close the labelme program. All your selections will be saved and further processed.")
    subprocess.call(["labelme", folder, "--nodata", "--autosave", "--labels", "roi"])
    

def strip_image(input_image_path, roi_file, output_image_path):
    
    polygons_json = file_utils.read_json_file(roi_file)["shapes"]
    polygons = []
    
    for polygon_json in polygons_json:
        polygon = []
        for point in polygon_json["points"]:
            polygon.append((point[0],point[1]))
            polygons.append(polygon)

    # read image as RGB (without alpha)
    img = Image.open(input_image_path).convert("RGB")
    
    # convert to numpy (for convenience)
    img_array = numpy.asarray(img)
    
    # create new image ("1-bit pixels, black and white", (width, height), "default color")
    mask_img = Image.new('1', (img_array.shape[1], img_array.shape[0]), 0)
    
    for polygon in polygons:
        ImageDraw.Draw(mask_img).polygon(polygon, outline=1, fill=1)

    mask = numpy.array(mask_img)
    
    # assemble new image (uint8: 0-255)
    new_img_array = numpy.empty(img_array.shape, dtype='uint8')
    
    # copy color values (RGB)
    new_img_array[:,:,:3] = img_array[:,:,:3]
    
    # filtering image by mask
    new_img_array[:,:,0] = new_img_array[:,:,0] * mask
    new_img_array[:,:,1] = new_img_array[:,:,1] * mask
    new_img_array[:,:,2] = new_img_array[:,:,2] * mask
    
    # back to Image from numpy
    newIm = Image.fromarray(new_img_array, "RGB")
    newIm.save(output_image_path, format="png")

    


select_roi_in_images(input_folder)

images = file_utils.get_all_images_in_folder(input_folder)

for i in progressbar.progressbar(range(len(images))):
    image = images[i]
    strip_image(image, image[:-4] + ".json", image)
    
    
    