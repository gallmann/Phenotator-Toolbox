# -*- coding: utf-8 -*-
"""
Created on Sun Aug  4 00:53:01 2019

@author: johan
"""

from utils import file_utils
import numpy as np
import math
from PIL import Image
import os
import gdal



def create_heatmap_from_multiple(predictions_folder):
    print("TODO")
    image_array = file_utils.get_image_array(image_path)
    height = image_array.shape[0]
    width = image_array.shape[1]


def create_heatmap(predictions_folder, stride=500, flower_list=None, min_score=0.5, overlay=True):
    
    
    
    #loop through all images in the input folder
    all_images = file_utils.get_all_images_in_folder(predictions_folder)
    for image_path in all_images:
        
        #get height and width of image
        max_pixels = Image.MAX_IMAGE_PIXELS
        Image.MAX_IMAGE_PIXELS = 5000000000
        image = Image.open(image_path)    
        width, height = image.size
        Image.MAX_IMAGE_PIXELS = max_pixels
        
        
        #initialize the overall heatmap
        heatmap_size_y = int(math.ceil(height/stride))
        heatmap_size_x = int(math.ceil(width/stride))
        heatmaps = {}
        heatmaps["overall"] = np.zeros((heatmap_size_y,heatmap_size_x))
        




        predictions = file_utils.read_json_file(image_path[:-4] + "_predictions.json")
        if predictions == None:
            continue
        
        for prediction in predictions:
            score = prediction["score"]
            if score < min_score:
                continue
            name = prediction["name"]
            [top,left,bottom,right]  = prediction["bounding_box"]
            center_x = int((left+right)/2)
            center_y = int((top+bottom)/2)
            
            if not name in heatmaps:
                heatmaps[name] = np.zeros((heatmap_size_y,heatmap_size_x))
            
            heatmap_y = int(math.ceil(center_y/stride))-1
            heatmap_x = int(math.ceil(center_x/stride))-1
            heatmaps[name][heatmap_y][heatmap_x] += 1
            heatmaps["overall"][heatmap_y][heatmap_x] += 1
            
        background = None
        if overlay:
            background = scale_image(image_path,image_path[:-4] + "_scaled.png")

        
        for heatmap in heatmaps:
            if flower_list != None and not heatmap in flower_list and not heatmap == "overall":
                continue
            out_path = image_path[:-4] + "_heatmap_" + heatmap + ".png"
            save_heatmap_as_image(heatmaps[heatmap],out_path,background)
            
            

color_ramp = [

[255,255,255,0],
[255,237,160,100],
[254,217,118,110],
[254,178,76,120],
[253,141,60,130],
[252,78,42,140],
[227,26,28,150],
[189,0,38,150],
[128,0,38,150]
]

color_ramp = [
   [255,255,255,0],
   [0,128,255,100],	#0080FF
   [63,159,191,100],	#3F9FBF
   [127,191,127,100],	#7FBF7F
   [191,223,63,100],	#BFDF3F
   [255,255,0,100],	#FFFF00
   [255,191,0,100],	#FFBF00
   [255,127,0,100],	#FF7F00
   [255,63,0,100], #FF3F00
   [255,0,0,100]
]

def save_heatmap_as_image(heatmap,output_path,background_image=None):
    height = heatmap.shape[0]
    width = heatmap.shape[1]
    image_array = np.zeros((height,width,4), dtype=np.uint8)
    max_val = np.max(heatmap)
    for y in range(0,height):
        for x in range(0,width):
            color_ramp_index = int(heatmap[y][x]/max_val*(len(color_ramp)-1))
            [r,g,b,a] = color_ramp[color_ramp_index]
            image_array[y][x] = [r,g,b,a]
    
    newIm = Image.fromarray(image_array, "RGBA")
    if background_image == None:
        newIm = newIm.convert("RGB")
        newIm = newIm.resize((height*5,width*5), Image.ANTIALIAS)
        
    if background_image != None:
        newIm = newIm.resize(background_image.size,Image.ANTIALIAS)
        newIm = overlay_images(background_image,newIm)
        
    newIm.save(output_path)
    
    newIm.show()

    #file_utils.save_array_as_image(output_path,image_array)
 
    
    

def scale_image(image_to_scale, image_output_path, new_width=10000):
    
    ds = gdal.Open(image_to_scale)
    band = ds.GetRasterBand(1)
    width = band.XSize
    height = band.YSize
    new_height = new_width/width*height
    
    gdal.Translate(image_output_path,ds, options=gdal.TranslateOptions(width=int(new_width),height=int(new_height), bandList=[1,2,3]))
    return Image.open(image_output_path)
    
    

def overlay_images(background,overlay):
   
    background = background.convert("RGBA")
    overlay = overlay.convert("RGBA")

    '''
    overlay_array = np.array(overlay)
    
    width = overlay_array.shape[1]
    height = overlay_array.shape[0]
    
    for x in range(width):
        for y in range(height): 
            [r,g,b,a] = overlay_array[y][x]
            if (r == 255 and g == 255 and b == 255):
                overlay_array[y][x] = [255,255,255,0]
            else:
                overlay_array[y][x][3] = 40
                
    overlay = Image.fromarray(overlay_array)
    '''
    background.paste(overlay, (0, 0), overlay)
    return background
    
    

def is_within_image(x,y,image_array,radius=5):
    
    height = image_array.shape[0]
    width = image_array.shape[1]
    
    
    for x in range(max(0,x-radius),min(width,x+radius)):
        for y in range(max(0,y-radius),min(height,y+radius)):
            [r,g,b] = image_array[y][x]
            if not((r == 0 and g == 0 and b == 0) or (r == 255 and g == 255 and b == 255)):
                return True
    else:
        return False

    
    
    
    
    
    
    
    
    
    
    
create_heatmap("C:/Users/johan/Desktop/FullFieldPrediction/test1",overlay=True,flower_list=["leucanthemum vulgare","lotus corniculatus","knautia arvensis"])
    