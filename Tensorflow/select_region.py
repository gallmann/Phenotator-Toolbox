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


input_folder = "C:/Users/johan/Desktop/MasterThesis/Data/May_23/MaskedAnnotationData"



def select_roi_in_images(folder):
    
    # hide main window
    root = tkinter.Tk()
    root.withdraw()
    # message box display
    messagebox.showinfo("Information","A window will open with the LabelMe Program. Within that program click through all images by using the 'Next Image' button. On each image draw one or more Polygons around the region of interest and label them 'roi'. Once done simply close the labelme program. All your selections will be saved and further processed.")
    subprocess.call(["labelme", folder, "--nodata", "--autosave", "--labels", "roi"])
    

def strip_image(input_image_path, roi_file, output_image_path):
    # read image as RGB and add alpha (transparency)
    im = Image.open(input_image_path).convert("RGBA")
    # convert to numpy (for convenience)
    imArray = numpy.asarray(im)
    # create mask
    
    polygons_json = file_utils.read_json_file(roi_file)["shapes"]
    polygons = []
    
    for polygon_json in polygons_json:
        polygon = []
        for point in polygon_json["points"]:
            polygon.append((point[0],point[1]))
            polygons.append(polygon)
    
    
    
    
    maskIm = Image.new('L', (imArray.shape[1], imArray.shape[0]), 0)
    for polygon in polygons:
        ImageDraw.Draw(maskIm).polygon(polygon, outline=1, fill=1)
    mask = numpy.array(maskIm)
    # assemble new image (uint8: 0-255)
    newImArray = numpy.empty(imArray.shape,dtype='uint8')
    
    # colors (three first columns, RGB)
    newImArray[:,:,:3] = imArray[:,:,:3]
    
    # transparency (4th column)
    newImArray[:,:,3] = mask*255
    
    # back to Image from numpy
    newIm = Image.fromarray(newImArray, "RGBA")
    newIm.save(output_image_path, format="png")





select_roi_in_images(input_folder)

images = file_utils.get_all_images_in_folder(input_folder)

for i in progressbar.progressbar(range(len(images))):
    image = images[i]
    strip_image(image, image[:-4] + ".json", image)
    
    
    