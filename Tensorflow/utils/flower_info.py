# -*- coding: utf-8 -*-
"""
Created on Tue Apr  9 13:57:31 2019

@author: johan
"""

flower_bounding_box_size = {
        
'Loewenzahn' : 6,
'Margarite'   : 3
}

def get_bbox_size(flower):
    return flower_bounding_box_size[flower]