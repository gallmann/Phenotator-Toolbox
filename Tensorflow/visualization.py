# -*- coding: utf-8 -*-
"""
Created on Wed Apr  3 23:39:23 2019

This script takes all images in the input_folder, draws the bounding boxes onto the images and saves 
them to the output_folder. Alongside each image either a json file or an xml file with the annotation
data has to be provided. 
@author: johan
"""
print("Loading libraries...")

from utils import constants
from object_detection.utils import visualization_utils
from PIL import Image
from utils import file_utils
from utils import flower_info
import os
import progressbar
import numpy as np
from object_detection.core import preprocessor
from matplotlib import pyplot as plt
import tensorflow as tf




def draw_bounding_boxes(input_folder, output_folder, with_name_info=True, clean_output_folder=True):
    """
    Draws all annotations onto the images in the input_folder and saves them to 
    the output_folder. The input folder must contain images (jpg, png or tif) 
    and along with each image a json file containing the annotations. These 
    json files can either be created with the LabelMe Application
    or with the AnnotationApp available for Android Tablets. Alternatively they
    can also be xml files. For example as they are created by the image-preprocessing
    command (saved to the project_folder/images folder by the image-preprocessing script).
    
    Parameters:
        input_folder (str): path to the input folder containing the images with
            annotation files
        output_folder (str): path to the output folder where to images with the
            visualized bounding boxes should be saved to
        with_name_info (bool): If True, not only the bounding box is drawn onto the 
            image but also with each bounding box the class label
        clean_output_folder (bool): If True, all contents of the output_folder 
            are deleted before the new images are saved 
    
    Returns:
        None
    """
    flowers = []
    images = file_utils.get_all_images_in_folder(input_folder)
    print("Drawing bounding boxes on images:")
    if clean_output_folder:
        file_utils.delete_folder_contents(output_folder)
    for i in progressbar.progressbar(range(len(images))):
        image_path = images[i]
        image = Image.open(image_path)
        '''
        annotations = file_utils.get_annotations(image_path)
        for flower in annotations:
            flower_name = flower_info.clean_string(flower["name"])
            [top,left,bottom,right] = flower_info.get_bbox(flower)
            if not flower_name in flowers:
                flowers.append(flower_name)
            col = get_color_for_index(flowers.index(flower_name))
            if with_name_info:
                visualization_utils.draw_bounding_box_on_image(image,top,left,bottom,right,display_str_list=[flower_name], color=col, use_normalized_coordinates=False, thickness=1)
            else:
                visualization_utils.draw_bounding_box_on_image(image,top,left,bottom,right,display_str_list=[], color=col, use_normalized_coordinates=False, thickness=1)
        
        image_name = os.path.basename(image_path)
        #image.save(os.path.join(output_folder,image_name))
        '''
        with tf.Session() as sess:

            image_name = os.path.basename(image_path)
            
            numpy_image = load_image_into_numpy_array(image)
            adjusted_image = preprocessor.random_adjust_saturation(numpy_image,min_delta=5,max_delta=5)
            
            #final_image = np.squeeze(tf.convert_to_tensor(adjusted_image).eval(session=sess))
            final_image = adjusted_image.eval(session=sess).astype(np.uint8)
            print(final_image.shape)

            new_im = Image.fromarray(final_image)
            new_im.save(os.path.join(output_folder,"sat_" + image_name))

        '''
        print(type(adjusted_image))
        print(adjusted_image)

        plt.imshow(final_image)
        plt.savefig(os.path.join(output_folder,"sat_" + image_name))
        '''
        #new_im = Image.fromarray(adjusted_image)

        # Visualization of the results of a detection.
        #plt.figure(figsize=(5000,5000))
        #plt.imshow(adjusted_image)

        
        

        
        
    print("Done!")
    
    
def load_image_into_numpy_array(image):
  """
  Helper function that loads an image into a numpy array.
  
  Parameters:
      image (PIL image): a PIL image
      
  Returns:
      np.array: a numpy array representing the image
  """
  (im_width, im_height) = image.size
  return np.array(image.getdata()).reshape(
      (im_height, im_width, 3)).astype(np.uint8)


def get_color_for_index(index):
    return STANDARD_COLORS[index]
    #label = list(matplotlib.colors.cnames.keys())[index]
    #return label

STANDARD_COLORS = [
    'AliceBlue', 'Chartreuse', 'Aqua', 'Aquamarine', 'Azure', 'Beige', 'Bisque',
    'BlanchedAlmond', 'BlueViolet', 'BurlyWood', 'CadetBlue', 'AntiqueWhite',
    'Chocolate', 'Coral', 'CornflowerBlue', 'Cornsilk', 'Crimson', 'Cyan',
    'DarkCyan', 'DarkGoldenRod', 'DarkGrey', 'DarkKhaki', 'DarkOrange',
    'DarkOrchid', 'DarkSalmon', 'DarkSeaGreen', 'DarkTurquoise', 'DarkViolet',
    'DeepPink', 'DeepSkyBlue', 'DodgerBlue', 'FireBrick', 'FloralWhite',
    'ForestGreen', 'Fuchsia', 'Gainsboro', 'GhostWhite', 'Gold', 'GoldenRod',
    'Salmon', 'Tan', 'HoneyDew', 'HotPink', 'IndianRed', 'Ivory', 'Khaki',
    'Lavender', 'LavenderBlush', 'LawnGreen', 'LemonChiffon', 'LightBlue',
    'LightCoral', 'LightCyan', 'LightGoldenRodYellow', 'LightGray', 'LightGrey',
    'LightGreen', 'LightPink', 'LightSalmon', 'LightSeaGreen', 'LightSkyBlue',
    'LightSlateGray', 'LightSlateGrey', 'LightSteelBlue', 'LightYellow', 'Lime',
    'LimeGreen', 'Linen', 'Magenta', 'MediumAquaMarine', 'MediumOrchid',
    'MediumPurple', 'MediumSeaGreen', 'MediumSlateBlue', 'MediumSpringGreen',
    'MediumTurquoise', 'MediumVioletRed', 'MintCream', 'MistyRose', 'Moccasin',
    'NavajoWhite', 'OldLace', 'Olive', 'OliveDrab', 'Orange', 'OrangeRed',
    'Orchid', 'PaleGoldenRod', 'PaleGreen', 'PaleTurquoise', 'PaleVioletRed',
    'PapayaWhip', 'PeachPuff', 'Peru', 'Pink', 'Plum', 'PowderBlue', 'Purple',
    'Red', 'RosyBrown', 'RoyalBlue', 'SaddleBrown', 'Green', 'SandyBrown',
    'SeaGreen', 'SeaShell', 'Sienna', 'Silver', 'SkyBlue', 'SlateBlue',
    'SlateGray', 'SlateGrey', 'Snow', 'SpringGreen', 'SteelBlue', 'GreenYellow',
    'Teal', 'Thistle', 'Tomato', 'Turquoise', 'Violet', 'Wheat', 'White',
    'WhiteSmoke', 'Yellow', 'YellowGreen'
]

if __name__ == '__main__':
    
    input_folder = "C:/Users/johan/Desktop/test"
    output_folder = "C:/Users/johan/Desktop/test2"
    
    draw_bounding_boxes(input_folder,output_folder,clean_output_folder=False)
    
