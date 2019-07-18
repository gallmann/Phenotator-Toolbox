# -*- coding: utf-8 -*-
"""
Created on Wed May 29 18:47:24 2019

@author: johan
"""
import os
from PIL import Image

input_folder = "C:/Users/johan/Desktop/Agisoft"
output_folder = "C:/Users/johan/Desktop/vis_im"
basewidth = 2000
Image.MAX_IMAGE_PIXELS = None

def get_all_tifs_in_folder(folder_path):
    images = []
    for file in os.listdir(folder_path):
        if file.endswith(".tif"):
            images.append(os.path.join(folder_path, file))
    return images



images = get_all_tifs_in_folder(input_folder)
for image_path in images:
    image = Image.open(image_path)
    wpercent = (basewidth/float(image.size[0]))
    hsize = int((float(image.size[1])*float(wpercent)))
    image = image.resize((basewidth,hsize), Image.ANTIALIAS)
    image = image.convert("RGBA")
    datas = image.getdata()
    
    newData = []
    for item in datas:
        if item[0] == 255 and item[1] == 255 and item[2] == 255:
            newData.append((255, 255, 255, 0))
        else:
            newData.append(item)
    
    image.putdata(newData)

    
    image.save(os.path.join(output_folder,os.path.basename(image_path))[:-4] + ".png", format="png")
