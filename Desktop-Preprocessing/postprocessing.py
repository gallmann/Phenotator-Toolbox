# -*- coding: utf-8 -*-
"""
Created on Fri May 10 11:42:56 2019

@author: johan
"""

import os
import json
import shapefile
import pyproj
import gdal
from PIL import Image



output_location = "C:/Users/johan/Desktop/coords.shp"
output_location_poly = "C:/Users/johan/Desktop/poly.shp"


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

class PostprocessTool(object):

    def make_shape_files(self, input_folder, output_location):
        
        #Some sanity checks
        if not os.path.isdir(input_folder):
            return "Input Directory not found!"
        if not os.path.isdir(output_location):
            return "Output Directory not found!"
        
        output_location_points = os.path.join(output_location,"points.shp")
        output_location_poly = os.path.join(output_location,"polygons.shp")

        image_paths = self.get_all_images_in_folder(input_folder)
        point_writer = shapefile.Writer(output_location_points)
        point_writer.field('name', 'C')
        poly_writer = shapefile.Writer(output_location_poly)
        poly_writer.field('name', 'C')
    
        for image_path in image_paths:
            annotation_path = image_path[:-4] + "_annotations.json"
            annotation_data = self.read_json_file(annotation_path)
            if(not annotation_data):
                continue
            annotations = annotation_data["annotatedFlowers"]
            swiss_coords = self.get_geo_coordinates(image_path)
            
            #get size information of the annotated_image
            image = Image.open(image_path)
            width = image.size[0]
            height = image.size[1]
    
            
            for flower in annotations:
                if flower["isPolygon"]:
                    points = []
                    for point in flower["polygon"]:
                        point_in_swiss_coords = self.convert_pixel_coords_go_swiss_geo_coords(point["x"],point["y"],swiss_coords,height,width)
                        points.append(point_in_swiss_coords)
                    
                    poly_writer.poly([points])
                    poly_writer.record(self.clean_string(flower["name"]))
                        
                else:
                    x = flower["polygon"][0]["x"]
                    y = flower["polygon"][0]["y"]
    
                    point_in_swiss_coords = self.convert_pixel_coords_go_swiss_geo_coords(x,y,swiss_coords,height,width)
                    point_writer.point(point_in_swiss_coords[0], point_in_swiss_coords[1]) 
                    point_writer.record(self.clean_string(flower["name"]))
        
        point_writer.close()
        poly_writer.close()   
        return ""
    
    
    
    def read_json_file(self, file_path):
        if file_path and os.path.isfile(file_path):
            with open(file_path, 'r') as f:
                try:
                    jsondata = json.load(f)
                    return jsondata
                except:
                    return None
        else:
            return None
    
    
    
    def convert_pixel_coords_go_swiss_geo_coords(self,x,y,image_geo_info,height,width):
        rel_x = x/width
        rel_y = y/height
        geo_x = (image_geo_info.lr_lon-image_geo_info.ul_lon) * rel_x + image_geo_info.ul_lon
        geo_y = (image_geo_info.ul_lat-image_geo_info.lr_lat) * (1-rel_y) + image_geo_info.lr_lat
        
        return [geo_x,geo_y]
    
    
    def get_all_images_in_folder(self, folder_path):
        images = []
        for file in os.listdir(folder_path):
            if file.endswith(".png"):
                images.append(os.path.join(folder_path, file))
        return images
    
    def clean_string(self, s):
        return s.encode(encoding='iso-8859-1').decode(encoding='utf-8').replace('ö','oe').replace('ä','ae').replace('ü','ue')
    
    
    #returns geo_coordinates in swiss coordinate system
    def get_geo_coordinates(self, input_image):
        
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
    
    