# -*- coding: utf-8 -*-
"""
Created on Tue Apr  9 13:57:31 2019

@author: johan


This file contains some helper functions to get the bounding box from an annotation.
Please specify the radios (in px) of each flower species in the flower_bounding_box_size
dictionary!
"""


#Set the radius (not diameter) of each flower species
flower_bounding_box_size = {
        
'Loewenzahn' : 6,
'Margarite'   : 4
}


def get_bbox_size(flower_name):
    return flower_bounding_box_size[flower_name]

def get_bbox(flower):
    if(flower["isPolygon"]):
        [top,left,bottom,right] = polygon_to_bounding_box(flower)
        return [top,left,bottom,right]
    else:
        [top,left,bottom,right] = coords_to_bounding_box(flower)
        return [top,left,bottom,right]
    
def coords_to_bounding_box(flower):
    flower_name = clean_string(flower["name"])
    x = round(flower["polygon"][0]["x"])
    y = round(flower["polygon"][0]["y"])
    bounding_box_size = get_bbox_size(flower_name)
    left = x - bounding_box_size
    top = y - bounding_box_size
    right = x + bounding_box_size
    bottom = y + bounding_box_size
    return [top,left,bottom,right]

    
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
            
    return [round(top),round(left),round(bottom),round(right)]

def clean_string(s):
    return s.encode(encoding='iso-8859-1').decode(encoding='utf-8').replace('ö','oe').replace('ä','ae').replace('ü','ue')
