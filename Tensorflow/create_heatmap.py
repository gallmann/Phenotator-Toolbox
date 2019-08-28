# -*- coding: utf-8 -*-
"""
Created on Sun Aug  4 00:53:01 2019

@author: johan
"""

print("Loading libraries...")
import sys
sys.stdout.flush()
from utils import file_utils
import numpy as np
import math
from PIL import Image
import os
import gdal
from utils import apply_annotations
import progressbar
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.image as mpimg
from matplotlib.colors import LinearSegmentedColormap


def get_height_width_of_image(image_path):
    max_pixels = Image.MAX_IMAGE_PIXELS
    Image.MAX_IMAGE_PIXELS = 5000000000
    image = Image.open(image_path)    
    width, height = image.size
    Image.MAX_IMAGE_PIXELS = max_pixels
    return (height,width)




def create_heatmap_from_multiple(predictions_folder, background_image, output_folder, heatmap_width=100, max_val=None ,flower_list=None, min_score=0.5, overlay=True, output_image_width=1000, window=None, with_colorbar=True):
    """
    Creates heatmaps for the background_image using all georeferenced images in the
    predictions_folder and saves them to the output_folder. The input images must
    be in the jpg or png format with a imagename_geoinfo.json file in the same folder
    or otherwise can be a georeferenced tif.
    
    Paramters:
        predictions_folder (str): Path to the folder containing the georeferenced
            images with the prediction json files
        background_image (str): Path of the background image onto which the heatmaps
            should be painted.
        output_folder (str): Path to the folder where the heatmaps should be saved to
        heatmap_width (int): Defines the the number of pixels the heatmap will 
            have on the x axis. The height of the heatmap is chosen such that 
            the width/height ratio is preserved. This heatmap will finally be 
            resized to the size of the background image.
        max_val (int): If defined, it denotes the maximum value of the heatmap,
            meaning that all values in the heatmap array that are larger than
            this max_val will be painted as red.
        flower_list (list): list of flowers for which the heatmaps should be 
            generated. If None, only the overall heatmap is generated.
        min_score (float): Minimum prediction score to include a prediction in 
            the heatmap.
        overlay (bool): If true, the heatmap is painted onto the image
        output_image_width (int): The width of the output image, the height is
            resizes such that the width/height ratio is preserved
        window (list): list of four float values indicating the [ulx, uly, lrx, lry]
            coordinates in the swiss coordinate system LV95+ of the area that should
            be used for the heatmap.
    Returns:
        None
    
    """
    all_images = file_utils.get_all_images_in_folder(predictions_folder)
    create_heatmap_internal(all_images, background_image, output_folder, heatmap_width, max_val, flower_list, min_score, overlay, output_image_width, window,with_colorbar)




def create_heatmap(predictions_folder, output_folder, heatmap_width=100, max_val=None ,flower_list=None, min_score=0.5, overlay=True, output_image_width=1000,window=None,with_colorbar=True):
    """
    Creates heatmaps for all images in the predictions_folder and saves them to
    the output_folder.
    
    Paramters:
        predictions_folder (str): Path to the folder containing the images with
            the predictino json files
        output_folder (str): Path to the folder where the heatmaps should be saved to
        heatmap_width (int): Defines the the number of pixels the heatmap will 
            have on the x axis. The height of the heatmap is chosen such that 
            the width/height ratio is preserved. This heatmap will finally be 
            resized to the size of the input image.
        max_val (int): If defined, it denotes the maximum value of the heatmap,
            meaning that all values in the heatmap array that are larger than
            this max_val will be painted as red.
        flower_list (list): list of flowers for which the heatmaps should be 
            generated. If None, only the overall heatmap is generated.
        min_score (float): Minimum prediction score to include a prediction in 
            the heatmap.
        overlay (bool): If true, the heatmap is painted onto the image
        output_image_width (int): The width of the output image, the height is
            resizes such that the width/height ratio is preserved
        window (list): list of four float values indicating the [ulx, uly, lrx, lry]
            coordinates in the swiss coordinate system LV95+ of the area that should
            be used for the heatmap.
            
    Returns:
        None
    
    """
    
    all_images = file_utils.get_all_images_in_folder(predictions_folder)
    for image_path in all_images:
        create_heatmap_internal([image_path], image_path, output_folder, heatmap_width, max_val, flower_list, min_score, overlay, output_image_width, window,with_colorbar)
    return
    
    
    
    

def create_heatmap_internal(input_images, background_image, output_folder, heatmap_width=100, max_val=None ,flower_list=None, min_score=0.5, overlay=True, output_image_width=1000, window=None,with_colorbar=True):
    """
    Creates heatmaps for the background_image using all georeferenced images in the
    predictions_folder and saves them to the output_folder. The input images must
    be in the jpg or png format with a imagename_geoinfo.json file in the same folder
    or otherwise can be a georeferenced tif.
    
    Paramters:
        input_images (list): List of paths denoting the input images which should
            be used as inputs for the heatmap
        background_image (str): Path of the background image onto which the heatmaps
            should be painted.
        output_folder (str): Path to the folder where the heatmaps should be saved to
        heatmap_width (int): Defines the the number of pixels the heatmap will 
            have on the x axis. The height of the heatmap is chosen such that 
            the width/height ratio is preserved. This heatmap will finally be 
            resized to the size of the background image.
        max_val (int): If defined, it denotes the maximum value of the heatmap,
            meaning that all values in the heatmap array that are larger than
            this max_val will be painted as red.
        flower_list (list): list of flowers for which the heatmaps should be 
            generated. If None, only the overall heatmap is generated.
        min_score (float): Minimum prediction score to include a prediction in 
            the heatmap.
        overlay (bool): If true, the heatmap is painted onto the image
        output_image_width (int): The width of the output image, the height is
            resizes such that the width/height ratio is preserved
        window (list): list of four float values indicating the [ulx, uly, lrx, lry]
            coordinates in the swiss coordinate system LV95+ of the area that should
            be used for the heatmap.
    Returns:
        None
    
    """
    
    
    output_image = os.path.join(output_folder,os.path.basename(background_image))
    background_image_coords = apply_annotations.get_geo_coordinates(background_image)
    #print some info to the user
    if background_image_coords:
        print("Coordinates of background image: " + str(background_image_coords.ul_lon) + " " + str(background_image_coords.ul_lat) + " " + str(background_image_coords.lr_lon) + " " + str(background_image_coords.lr_lat))
        if window:
            print("Coordinates of projected background image: " + str(window[0]) + " " + str(window[1]) + " " + str(window[2]) + " " + str(window[3]))  
            if overlay:
                print("Creating background image from provided window and output-image-width...")
        else:
            if overlay:
                print("Scaling background image...")
    
    
    #get height and width of image
    (background_height,background_width) = get_height_width_of_image(background_image)


    
    
    background = None
    if overlay:
        background = scale_image(background_image,output_image[:-4] + "_background.tif",output_image_width, window)
        background_image = output_image[:-4] + "_background.tif"
    
    (background_height,background_width) = get_height_width_of_image(background_image)
    background_image_coords = apply_annotations.get_geo_coordinates(background_image)
    stride=background_width/heatmap_width
    #initialize the overall heatmap
    heatmap_size_y = int(math.ceil(background_height/stride))
    heatmap_size_x = int(math.ceil(background_width/stride))
    heatmaps = {}
    heatmaps["overall"] = np.zeros((heatmap_size_y,heatmap_size_x))
    coverage_counter = np.zeros((heatmap_size_y,heatmap_size_x))
    
    
    
    
    #loop through all images in the input folder
    print("Adding the annotations to the heatmaps...")
    for i in progressbar.progressbar(range(len(input_images))):
        
        image_path = input_images[i]
        (height,width) = get_height_width_of_image(image_path)
        image_coords = apply_annotations.get_geo_coordinates(image_path)
        image_array = file_utils.get_image_array(image_path)
        
        #update coverage counter
        for x in range(heatmap_size_x):
            for y in range(heatmap_size_y):
                (target_x,target_y)=apply_annotations.translate_pixel_coordinates(x,y,heatmap_size_y,heatmap_size_x,background_image_coords,image_coords,height,width)
                target_x = int(target_x)
                target_y = int(target_y)
                if is_within_image(target_x,target_y,image_array):
                    coverage_counter[y][x] += 1
        
        
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
            
            (center_x,center_y)=apply_annotations.translate_pixel_coordinates(center_x,center_y,height,width,image_coords,background_image_coords,background_height,background_width)
            heatmap_y = int(math.ceil(center_y/stride))-1
            heatmap_x = int(math.ceil(center_x/stride))-1
            if not apply_annotations.are_coordinates_within_image_bounds(heatmap_x,heatmap_y,heatmap_size_x,heatmap_size_y):
                continue
            
            if name == "lotus corniculatus":
                heatmaps[name][heatmap_y][heatmap_x] += 2.6
                heatmaps["overall"][heatmap_y][heatmap_x] += 2.6
            else: 
                heatmaps[name][heatmap_y][heatmap_x] += 1
                heatmaps["overall"][heatmap_y][heatmap_x] += 1
            
            
    coverage_out_path = output_image[:-4] + "_coverage.png"
    save_heatmap_as_image(coverage_counter,coverage_out_path,background, output_image_width,None,with_colorbar)


    for heatmap_name in heatmaps:
        if flower_list != None and not heatmap_name in flower_list and not heatmap_name == "overall":
            continue
        out_path = output_image[:-4] + "_heatmap_" + heatmap_name + ".png"
        
        heatmap = heatmaps[heatmap_name]
        coverage_counter[coverage_counter==0] = 100000
        heatmap = np.divide(heatmap,coverage_counter)
        
        print(heatmap_name + ": " + str(np.sum(heatmap)))
        save_heatmap_as_image(heatmap,out_path,background, output_image_width,max_val,with_colorbar)

                


def save_heatmap_as_image(heatmap,output_path,background_image=None, output_image_width=1000, max_val=None,with_colorbar=True):
    """
    Saves a heatmap numpy array as an image.
    
    Parameters:
        heatmap (np.array): Numpy array of shape (h,w,1) representing the heatmap
        output_path (str): Image path where the heatmap image should be saved to
        background_image (PIL.Image): An image representing the background onto
            which the heatmap should be pasted
        output_image_width (int): The width of the ouput heatmap image. If a 
            background_image is provided, this parameter is ignored and the 
            heatmap is scaled to the size of the background image.
        max_val (int): If defined, it denotes the maximum value of the heatmap,
            meaning that all values in the heatmap array that are larger than
            this max_val will be painted as red.
        
    Returns:
        None
    
    """
    

    height = heatmap.shape[0]
    width = heatmap.shape[1]
    image_array = np.zeros((height,width,4), dtype=np.uint8)
    if max_val == None:
        max_val = np.max(heatmap)
    print(max_val)
    float_color_ramp = np.array(color_ramp)/255
    #cmap = mpl.colors.ListedColormap(float_color_ramp,N=len(float_color_ramp)-1)
    cmap = LinearSegmentedColormap.from_list("bla", float_color_ramp, N=max(2,max_val))
    cmap.set_over('red',100/255)
        
        
    for y in range(0,height):
        for x in range(0,width):
            if heatmap[y][x] < 0.5:
                color_ramp_index = 0
            else:
                color_ramp_index = min(math.ceil(heatmap[y][x]/max_val*((len(color_ramp)-1))),len(color_ramp)-1)
                color_ramp_index = heatmap[y][x]/max_val
            #[r,g,b,a] = color_ramp[color_ramp_index]
            [r,g,b,a] = np.array(list(cmap(color_ramp_index)))*255
            image_array[y][x] = [r,g,b,a]
    
    newIm = Image.fromarray(image_array, "RGBA")
    if background_image == None:
        newIm = newIm.convert("RGB")
        newIm = newIm.resize((int(output_image_width/width*height),output_image_width), Image.ANTIALIAS)
        
    if background_image != None:
        newIm = newIm.resize(background_image.size,Image.ANTIALIAS)
        newIm = overlay_images(background_image,newIm)
        
    newIm.save(output_path)
    
    
    
    #save with colorbar  
        

    if with_colorbar:
        plt.figure(figsize = (output_image_width/300,int(output_image_width/width*height)/300))
        ax = plt.gca()
    
        img = mpimg.imread(output_path)
        imgplot = plt.imshow(img)
        plt.axis('off')
        
        imgplot.set_cmap(cmap)
        imgplot.set_clim(0,max_val)
        
        
        from mpl_toolkits.axes_grid1 import make_axes_locatable
    
        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="5%", pad=0.05)
        
    
        colorbar = plt.colorbar(imgplot,extend='max',cax=cax)
        colorbar.ax.set_ylabel('Flowers per square meter')
    
        plt.savefig(output_path,dpi=300,bbox_inches='tight')
        
        #newIm.show()
    
        #file_utils.save_array_as_image(output_path,image_array)
    
    

def scale_image(image_to_scale, image_output_path, new_width=1000, window=None):
    """
    Scales the image_to_scale such that its new width is new_width.
    
    Parameters:
        image_to_scale (str): Path to the image to scale
        image_output_path (str): Path where the image should be saved to
        new_width (int): the new width of the scaled image
        
    Returns:
        PIL.Image: A scaled PIL Image
    
    """
    
    
    if window:
        ds = gdal.Open(image_to_scale)
        temp_image_path = image_output_path[:-4] + "_temp.tif"
        gdal.Translate(temp_image_path,ds, options=gdal.TranslateOptions(projWin=window))
        ds = gdal.Open(temp_image_path)
    else:
        ds = gdal.Open(image_to_scale)
    
    band = ds.GetRasterBand(1)
    width = band.XSize
    height = band.YSize
    new_height = int(new_width/width*height)
    
    gdal.Translate(image_output_path,ds, options=gdal.TranslateOptions(width=int(new_width),height=int(new_height)))
    
    ds = None
    
    if os.path.isfile(image_output_path[:-4] + "_temp.tif"):
        os.remove(image_output_path[:-4] + "_temp.tif")
    
    return Image.open(image_output_path)
    
    

def overlay_images(background,overlay):
    """
    Pastes the overlay image onto the background image. Make sure the alpha 
    values are set correctly in the overlay image.
    
    Parameters:
        background (PIL.Image): Background image
        overlay (PIL.Image): Overlay image
    
    Returns:
        PIL.Image: The resulting PIL image
    
    """
    background = background.convert("RGBA")
    overlay = overlay.convert("RGBA")
    background.paste(overlay, (0, 0), overlay)
    return background
    
    

def is_within_image(x,y,image_array,radius=3):
    """
    Given an x,y pixel coordinate checks if the coordinates are within the image
    and if so checks whether all pixels within a given radius
    are completely white or completely black.
    
    Parameters:
        x (int): x coordinate
        y (int): y coordinate
        image_array (np.array): numpy array of shape (h,w,3)
        radius (int): the radius of the area around the x,y position that should
            be checked if it is completely white or completely black
    
    Returns:
        Boolean: True, if the x,y coordinate is within the actual image, False otherwise
    
    """
    height = image_array.shape[0]
    width = image_array.shape[1]
        
    for x in range(max(0,x-radius),min(width,x+radius)):
        for y in range(max(0,y-radius),min(height,y+radius)):
            [r,g,b] = image_array[y][x]
            if not((r == 0 and g == 0 and b == 0) or (r == 255 and g == 255 and b == 255)):
                return True
    
    return False

    
    
    
    
    
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

    

'''
    
create_heatmap("G:/Johannes/Experiments/025/ortho_tif/ortho_tif_14_june",
               "G:/Johannes/Experiments/025/ortho_tif/heatmaps",
               stride=400, 
               overlay=True,
               flower_list=["leucanthemum vulgare","lotus corniculatus","knautia arvensis"],
               output_image_width=5000,
               max_val=15)

create_heatmap_from_multiple("G:/Johannes/Experiments/025/ortho_tif/single_images_14_june",
               "G:/Johannes/Experiments/025/ortho_tif/ortho_tif_14_june/Linn_190613_3b.tif",               
               "G:/Johannes/Experiments/025/ortho_tif/heatmaps",
               stride=400, 
               overlay=True,
               flower_list=["leucanthemum vulgare","lotus corniculatus","knautia arvensis"],
               output_image_width=5000,
               max_val=15)
'''