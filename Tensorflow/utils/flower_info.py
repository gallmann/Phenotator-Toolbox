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
'Margarite'   : 4,
'achillea millefolium': 20,
'anthyllis vulneraria'   : 16,
'agrimonia eupatoria': 15,
'carum carvi'   : 22,
'centaurea jacea': 14,
'cerastium caespitosum'   : 7,
'crepis biennis'   : 17,
'daucus carota': 23,
'galium mollugo'   : 4,
'knautia arvensis'   : 17,
'medicago lupulina'   : 4,
'leucanthemum vulgare'   : 20,
'lotus corniculatus'   : 8,
'lychnis flos cuculi'   : 15,
'myosotis arvensis'   : 6,
'onobrychis viciifolia'   : 10,
'picris hieracioides': 13,
'plantago lanceolata'   : 8,
'plantago major'   : 11,
'prunella vulgaris': 13,
'ranunculus acris'   : 11,
'ranunculus bulbosus'   : 11,
'ranunculus friesianus'   : 11,
'ranunculus'   : 11,
'salvia pratensis'   : 15,
'tragopogon pratensis'   : 17,
'trifolium pratense'   : 10,
'veronica chamaedris'   : 4,
'vicia sativa'   : 6,
'vicia sepium'   : 4,
'dianthus carthusianorum': 11,
'lathyrus pratensis' : 8,
'leontodon hispidus' : 18,
'rhinanthus alectorolophus': 20,
'trifolium repens': 10,
'orchis sp': 20
}


from matplotlib import colors

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



def get_color_for_flower(flower_name, get_rgb_value=False):
    flower_name = correct_spelling_errors(flower_name)
    return_color = STANDARD_COLORS[40]
    for i,name in enumerate(flower_bounding_box_size):
        if name == flower_name:
            return_color = STANDARD_COLORS[i]
            
    if get_rgb_value:
        rgba = list(colors.to_rgba(return_color))
        for i in range(0,3):
            rgba[i] = int(rgba[i]*255)
        rgba[3] = 64
        return rgba
    else:
        return return_color
    
    
def correct_spelling_errors(s):
    #get rid of ä, ö, ü, upper case letters or trailing whitespaces
    s = s.encode(encoding='iso-8859-1').decode(encoding='utf-8').replace('ö','oe').replace('ä','ae').replace('ü','ue').lower().rstrip(" ,.:")
    
    #correct spelling errors
    if "dianthus carthusionorum" in s:
        return "dianthus carthusianorum"
    if "rhinantus alectorolophus" in s:
        return "rhinanthus alectorolophus"
    if "flos" in s and "cuculi" in s:
        return "lychnis flos cuculi"
    
    return s
    
    
def clean_string(s):
    
    s = correct_spelling_errors(s)    
    
    #different types of ranunculus cannot be distinguished from the image alone, therefore 
    #just combine them to ranunculus
    if "ranunculus" in s:
        return "ranunculus"
    if "lathyrus pratensis" in s:
        return "lotus corniculatus"
    if "carum carvi" in s:
        return "galium mollugo"
    if "leontodon hispidus" in s or "tragopogon pratensis" in s :
        return "crepis biennis"
    else:
        return s




