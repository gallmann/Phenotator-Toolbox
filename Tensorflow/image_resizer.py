# -*- coding: utf-8 -*-
"""
Created on Wed May 29 18:47:24 2019

@author: johan
"""
import os
from PIL import Image
from utils import file_utils
Image.MAX_IMAGE_PIXELS = None
import progressbar



def change_resolution(input_folder,output_folder,scale_factor,keep_image_size=True):
    all_images = file_utils.get_all_images_in_folder(input_folder)
    print("Changing resolution for all images in " + input_folder + "...")
    for i in progressbar.progressbar(range(len(all_images))):
        image_path = all_images[i]
        image = Image.open(image_path)
        
        image = change_pil_image_resolution(image,scale_factor)
        if keep_image_size:
            image = change_pil_image_resolution(image,1/scale_factor)
            
        
        image.save(os.path.join(output_folder,os.path.basename(image_path))[:-4] + ".png", format="png")


def change_pil_image_resolution(image,scale_factor):
    new_width = int((float(image.size[0])*float(scale_factor)))
    new_height = int((float(image.size[1])*float(scale_factor)))
    
    image = image.resize((new_width,new_height), Image.ANTIALIAS)
    image = image.convert("RGBA")
    datas = image.getdata()
    
    newData = []
    for item in datas:
        if item[0] == 255 and item[1] == 255 and item[2] == 255:
            newData.append((255, 255, 255, 0))
        else:
            newData.append(item)
    
    image.putdata(newData)
    return image


if __name__ == '__main__':
    input_folder = "C:/Users/johan/Desktop/MaskedAnnotationData"
    output_folder = "C:/Users/johan/Desktop/test"
    scale_factor = 0.1
    

    change_resolution(input_folder,output_folder,scale_factor)
