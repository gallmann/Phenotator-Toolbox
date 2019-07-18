# -*- coding: utf-8 -*-
"""
Created on Fri May 10 11:42:56 2019

@author: johan

Given a folder with annotations (Made with tablet or LabelMe application), the script
converts the annotations to shape files.


"""

print("Loading libraries...")
import os
import json
import shapefile
import pyproj
import gdal
import cv2
from utils import file_utils
from utils import flower_info
import progressbar



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

def make_shape_files(input_folder, output_location):
    """
    Given a folder with annotations (Made with tablet or LabelMe application), the script
    converts the annotations to shape files.

    
    Parameters:
        input_folder (str): path to the input folder with annotations (images and json files)
        output_location (str): path of the output folder
        
    Returns:
        None
    """

    #Some sanity checks
    if not os.path.isdir(input_folder):
        print("Input Directory not found!")
        return
    if not os.path.isdir(output_location):
        print("Output Directory not found!")
        return
    
    output_location_points = os.path.join(output_location,"points.shp")
    output_location_poly = os.path.join(output_location,"polygons.shp")

    image_paths = file_utils.get_all_images_in_folder(input_folder)
    point_writer = shapefile.Writer(output_location_points)
    point_writer.field('name', 'C')
    poly_writer = shapefile.Writer(output_location_poly)
    poly_writer.field('name', 'C')

    print("Exporting annotations...")
    for i in progressbar.progressbar(range(len(image_paths))):
        image_path = image_paths[i]
        annotations = file_utils.get_annotations(image_path)
        swiss_coords = get_geo_coordinates(image_path)
        
        #get size information of the annotated_image
        img = cv2.imread(image_path,0)
        height, width = img.shape[:2]

        
        for flower in annotations:
            if flower["isPolygon"]:
                points = []
                for point in flower["polygon"]:
                    point_in_swiss_coords = convert_pixel_coords_go_swiss_geo_coords(point["x"],point["y"],swiss_coords,height,width)
                    points.append(point_in_swiss_coords)
                
                poly_writer.poly([points])
                poly_writer.record(flower_info.clean_string(flower["name"]))
                    
            else:
                x = flower["polygon"][0]["x"]
                y = flower["polygon"][0]["y"]

                point_in_swiss_coords = convert_pixel_coords_go_swiss_geo_coords(x,y,swiss_coords,height,width)
                point_writer.point(point_in_swiss_coords[0], point_in_swiss_coords[1]) 
                point_writer.record(flower_info.clean_string(flower["name"]))
    
    point_writer.close()
    poly_writer.close()   
    return ""




def convert_pixel_coords_go_swiss_geo_coords(x,y,image_geo_info,height,width):
    """
    Converts pixel coordinates x and y to swiss geo coordinates in the lv95+ coordinate system

    
    Parameters:
        x (float or int): x coordinate of pixel
        y (float or int): y coordinate of pixel
        image_geo_info (GeoInformation): GeoInformation object of image containing
            upper-left and lower-right geo coordinates of the image
        height (int): height of the image
        width (int): width of the image
        
    Returns:
        list: [x,y] in swiss (lv95+) coordinates
    """


    rel_x = x/width
    rel_y = y/height
    geo_x = (image_geo_info.lr_lon-image_geo_info.ul_lon) * rel_x + image_geo_info.ul_lon
    geo_y = (image_geo_info.ul_lat-image_geo_info.lr_lat) * (1-rel_y) + image_geo_info.lr_lat
    
    return [geo_x,geo_y]



def get_geo_coordinates(input_image):
    """
    Reads the geo coordinates of the upper-left and lower-right corner of the image and coverts them
    to the lv95+ format (if not already) and returns it as a GeoInformation object. The input image must
    be in the jpg or png format with a imagename_geoinfo.json file in the same folder
    or otherwise can be a georeferenced tif.

    
    Parameters:
        input_image (str): path to the image
        
    Returns:
        GeoInformation: GeoInformation object containing the upper-left and lower-right geo coordinates
            in lv95+ coordinate system
    """

    if input_image.endswith(".png") or input_image.endswith(".jpg"):
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
        ds = gdal.Open(input_image)
        inSRS_wkt = ds.GetProjection()  # gives SRS in WKT
        inSRS_converter = osr.SpatialReference()  # makes an empty spatial ref object
        inSRS_converter.ImportFromWkt(inSRS_wkt)  # populates the spatial ref object with our WKT SRS
        inSRS_forPyProj = inSRS_converter.ExportToProj4()  # Exports an SRS ref as a Proj4 string usable by PyProj
        
        input_coord_system = pyproj.Proj(inSRS_forPyProj) 
        swiss = pyproj.Proj("+init=EPSG:2056")
        
        ulx, xres, xskew, uly, yskew, yres  = ds.GetGeoTransform()
        lrx = ulx + (ds.RasterXSize * xres)
        lry = uly + (ds.RasterYSize * yres)
        geo_info = GeoInformation()
        geo_info.lr_lon = lrx
        geo_info.lr_lat = lry
        geo_info.ul_lon = ulx
        geo_info.ul_lat = uly
        geo_info.lr_lon,geo_info.lr_lat = pyproj.transform(input_coord_system, swiss, geo_info.lr_lon, geo_info.lr_lat)
        geo_info.ul_lon,geo_info.ul_lat = pyproj.transform(input_coord_system, swiss, geo_info.ul_lon, geo_info.ul_lat)

        return geo_info

    