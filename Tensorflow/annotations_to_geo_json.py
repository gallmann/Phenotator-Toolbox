# -*- coding: utf-8 -*-
"""
Created on Thu Jun 20 17:06:44 2019

@author: johan
"""

# -*- coding: utf-8 -*-
"""
Created on Fri May 10 11:42:56 2019

@author: johan
"""

import os
import json
import pyproj
import gdal
from utils import flower_info
#from PIL import Image
import numpy as np
import cv2
from geojson import Polygon, Feature, FeatureCollection, dump



input_folder = "C:/Users/johan/Desktop/Annotations_high_quali"
output_file = "C:/Users/johan/Desktop/script_generated.geojson"




class GeoInformation(object):
    def __init__(self,dictionary=None):
        if not dictionary:
            self.lr_lon = 0
            self.lr_lat = 0
            self.ul_lon = 0
            self.ul_lat = 0
        else:
            for key in dictionary:
                setattr(self, key, dictionary[key])







def make_geo_json_file(input_folder, output_file):
    
    #Some sanity checks
    if not os.path.isdir(input_folder):
        return "Input Directory not found!"
    
    
    image_paths = get_all_images_in_folder(input_folder)
    
    
    
    features = []
    id_counter = 0

    for image_path in image_paths:
        annotation_path = image_path[:-4] + "_annotations.json"
        annotation_data = read_json_file(annotation_path)
        if(not annotation_data):
            continue
        annotations = annotation_data["annotatedFlowers"]
        swiss_coords = get_geo_coordinates(image_path)
        
        #get size information of the annotated_image
        img = cv2.imread(image_path,0)
        height, width = img.shape[:2]

        
        for flower in annotations:
            flower["name"] = flower_info.clean_string(flower["name"])
            [top,left,bottom,right] = flower_info.get_bbox(flower)
            left_top = convert_pixel_coords_go_swiss_geo_coords(left,top,swiss_coords,height,width)
            left_bottom = convert_pixel_coords_go_swiss_geo_coords(left,bottom,swiss_coords,height,width)
            right_top = convert_pixel_coords_go_swiss_geo_coords(right,top,swiss_coords,height,width)
            right_bottom = convert_pixel_coords_go_swiss_geo_coords(right,bottom,swiss_coords,height,width)
            
            polygon = Polygon([[left_top,left_bottom,right_bottom,right_top]])
            idstring = flower["name"] + "_" + str(id_counter)
            idnumber = str(id_counter)
            
            props = {"design_id": id_counter, "design_label": idstring, "id":idnumber, "plot_label":idstring,
                     "plot_number":idnumber, "range":idnumber, "range_in_lot":idnumber,"row":idnumber,"row_in_lot":idnumber,
                     "showing_number":idnumber, "plant_height":idnumber}
            
            id_counter = id_counter + 1

            features.append(Feature(geometry=polygon, properties=props, id=idnumber))
                        
    feature_collection = FeatureCollection(features)
    with open(output_file, 'w') as f:
       dump(feature_collection, f)

    return ""



def read_json_file(file_path):
    if file_path and os.path.isfile(file_path):
        with open(file_path, 'r') as f:
            try:
                jsondata = json.load(f)
                return jsondata
            except:
                return None
    else:
        return None



def convert_pixel_coords_go_swiss_geo_coords(x,y,image_geo_info,height,width):
    rel_x = x/width
    rel_y = y/height
    geo_x = (image_geo_info.lr_lon-image_geo_info.ul_lon) * rel_x + image_geo_info.ul_lon
    geo_y = (image_geo_info.ul_lat-image_geo_info.lr_lat) * (1-rel_y) + image_geo_info.lr_lat
    
    return [geo_x,geo_y]


def get_all_images_in_folder(folder_path):
    images = []
    for file in os.listdir(folder_path):
        if file.endswith(".png"):
            images.append(os.path.join(folder_path, file))
    return images


#returns geo_coordinates in swiss coordinate system
def get_geo_coordinates(input_image):
    
    if input_image.endswith(".png"):
        #if the input_image is a .png file, there should be a geoinfo.json file in the same folder
        #where the geo information is read from
        geo_info_path = input_image[:-4] +  "_geoinfo.json"
        with open(geo_info_path, 'r') as f:
            datastore = json.load(f)
            geo_info = GeoInformation(datastore)
            swiss = pyproj.Proj("+init=EPSG:2056")
            wgs84=pyproj.Proj("+init=EPSG:4326") # LatLon with WGS84 datum used by GPS units and Google Earth
            geo_info.lr_lon,geo_info.lr_lat  = pyproj.transform(wgs84, swiss, geo_info.lr_lon, geo_info.lr_lat)
            geo_info.ul_lon,geo_info.ul_lat = pyproj.transform(wgs84, swiss, geo_info.ul_lon, geo_info.ul_lat)
            return geo_info
    else:
        #if the input_image is a geo-annotated .tif file, read the geo information using gdal
        inDS = gdal.Open(input_image)
            
        ulx, xres, xskew, uly, yskew, yres  = inDS.GetGeoTransform()
        lrx = ulx + (inDS.RasterXSize * xres)
        lry = uly + (inDS.RasterYSize * yres)
        geo_info = GeoInformation()
        geo_info.lr_lon = lrx
        geo_info.lr_lat = lry
        geo_info.ul_lon = ulx
        geo_info.ul_lat = uly
        return geo_info




make_geo_json_file(input_folder,output_file)
