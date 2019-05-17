# -*- coding: utf-8 -*-
"""
Created on Tue Apr  9 13:57:31 2019

@author: johan
"""

flower_bounding_box_size = {
        
'Loewenzahn' : 6,
'Margarite'   : 4
}



import file_utils

def get_bbox_size(flower_name):
    return flower_bounding_box_size[flower_name]

def get_bbox(flower):
    if(flower["isPolygon"]):
        [left,right,top,bottom] = polygon_to_bounding_box(flower)
        return [left,right,top,bottom]
    else:
        [left,right,top,bottom] = coords_to_bounding_box(flower)
        return [left,right,top,bottom]
    
def coords_to_bounding_box(flower):
    flower_name = file_utils.clean_string(flower["name"])
    x = round(flower["polygon"][0]["x"])
    y = round(flower["polygon"][0]["y"])
    bounding_box_size = get_bbox_size(flower_name)
    left = x - bounding_box_size
    top = y - bounding_box_size
    right = x + bounding_box_size
    bottom = y + bounding_box_size
    return [left,right,top,bottom]

    
def polygon_to_bounding_box(flower):
    if not flower["isPolygon"]:
        raise ValueError('flower passed to polygon_to_bounding_box must be a polygon')
    left = flower["polygon"][0]["x"]
    right = flower["polygon"][0]["x"]
    top = flower["polygon"][0]["y"]
    bottom = flower["polygon"][0]["y"]
    
    for vertex in flower["polygon"]:
        if vertex["x"] < left:
            left = vertex["x"]
        if vertex["x"] > right:
            right = vertex["x"]
        if vertex["y"] < top:
            top = vertex["y"]
        if vertex["y"] > bottom:
            bottom = vertex["y"]
            
    return [round(left),round(right),round(top),round(bottom)]
