# -*- coding: utf-8 -*-
"""
Created on Wed Apr  3 23:39:23 2019

@author: johan
"""

from object_detection.utils import visualization_utils
from PIL import Image

image = Image.open("C:/Users/johan/Desktop/tile_row2_col0.png")


visualization_utils.draw_bounding_box_on_image(image,10,10,100,100,display_str_list=["hello"], use_normalized_coordinates=False)
image.save("C:/Users/johan/Desktop/tile_row2_col1.png")

visualization_utils.draw_bounding_box_on_image(image,y - bounding_box_size,x - bounding_box_size,y + bounding_box_size,x + bounding_box_size, display_str_list=(), use_normalized_coordinates=False, thickness=1)
image.save(image_path)
