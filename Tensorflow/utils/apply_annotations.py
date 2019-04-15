# -*- coding: utf-8 -*-
"""
Created on Thu Apr 11 13:48:04 2019

@author: johan
"""

import gdal
import os
import osr
import pyproj
import json
from PIL import Image


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




def apply_annotations_to_images(annotated_folder, images_folder, output_folder):
    all_ortho_tifs = get_all_tifs_in_folder(images_folder)
    all_annotated_images = get_all_images_in_folder(annotated_folder)
    for ortho_tif in all_ortho_tifs:
        
        #convert all images in image folder to png and copy them to output folder. Also create empty annotation.json files
        im = Image.open(ortho_tif)
        im.thumbnail(im.size)
        ortho_png = os.path.join(output_folder, os.path.basename(ortho_tif)[:-4] + ".png")
        im.save(ortho_png, "JPEG", quality=100)
        annotation_template = {"annotatedFlowers": []}
        with open(os.path.join(output_folder,os.path.basename(ortho_tif)[:-4] + "_annotations.json"), 'w') as outfile:
            json.dump(annotation_template, outfile)

        #loop through all images in annotated_folder and images_folder and call copy_annotations() if the two
        #images share a common area
        c = get_geo_coordinates(ortho_tif)
        for annotated_image in all_annotated_images:
            d = get_geo_coordinates(annotated_image)
            annotation_path = annotated_image[:-4] + "_annotations.json"
            intersection = get_intersection(c,d)
            if intersection:
                copy_annotations(annotated_image,annotation_path, ortho_png, c, d)            
    
def copy_annotations(annotated_image_path, annotation_path, ortho_png, ortho_tif_coordinates, annotated_image_coordinates, ):
    annotation_data = read_json_file(annotation_path)
    if(not annotation_data):
        return
    image = Image.open(annotated_image_path)
    width = image.size[0]
    height = image.size[1]
    

    orthoTif = Image.open(ortho_png)
    ortho_width = orthoTif.size[0]
    ortho_height = orthoTif.size[1]
    print(ortho_png + " "+ str(ortho_width) + " " + str(ortho_height))
    
    output_annotations_path = ortho_png[:-4] + "_annotations.json"
    output_annotations = read_json_file(output_annotations_path)
    
    #TODO Polygon
    for i in range(len(annotation_data["annotatedFlowers"])-1,-1,-1):
        x = annotation_data["annotatedFlowers"][i]["polygon"][0]["x"]
        y = annotation_data["annotatedFlowers"][i]["polygon"][0]["y"]
        (x_target,y_target) = translate_pixel_coordinates(x,y,height,width,annotated_image_coordinates, ortho_tif_coordinates,ortho_height,ortho_width)
        if(x_target < width and y_target < height and x_target > 0 and y_target > 0):
            annotation_data["annotatedFlowers"][i]["polygon"][0]["x"] = x_target
            annotation_data["annotatedFlowers"][i]["polygon"][0]["y"] = y_target
            output_annotations["annotatedFlowers"].append(annotation_data["annotatedFlowers"][i])
    
    with open(output_annotations_path, 'w') as outfile:
        json.dump(output_annotations, outfile)
'''
    print("hello")
    print(output_annotations_path)
    print(output_annotations)
'''
    
    
def translate_pixel_coordinates(x,y,height,width,source_geo_coords,target_geo_coords,height_target,width_target):
    rel_x = x/width
    rel_y = y/height
    geo_x = (source_geo_coords.lr_lon-source_geo_coords.ul_lon) * rel_x + source_geo_coords.ul_lon
    geo_y = (source_geo_coords.ul_lat-source_geo_coords.lr_lat) * (1-rel_y) + source_geo_coords.lr_lat
    
    rel_x_target = (geo_x-target_geo_coords.ul_lon)/(target_geo_coords.lr_lon-target_geo_coords.ul_lon)
    rel_y_target = 1-(geo_y-target_geo_coords.lr_lat)/(target_geo_coords.ul_lat-target_geo_coords.lr_lat)
    x_target = rel_x_target* width_target
    y_target = rel_y_target* height_target
    print("")
    print(str(x_target) + "/" + str(y_target) + " (target_coords)")
    #print(str(source_geo_coords.ul_lon) + " " + str(source_geo_coords.lr_lon))
    #print(str(target_geo_coords.ul_lon) + " " + str(target_geo_coords.lr_lon))
    #print(str(geo_x) + " " + str(geo_y))
    #print(str(rel_x) + " " + str(rel_y))
    #print(str(rel_x_target) + " " + str(rel_y_target))
    print("")
    
    rel_x = 4039.0/5006.0
    print((target_geo_coords.lr_lon - target_geo_coords.ul_lon)*rel_x + target_geo_coords.ul_lon)
    rel_x = 4122.0/5033.0
    #print((target_geo_coords.lr_lon - target_geo_coords.ul_lon)*rel_x + target_geo_coords.ul_lon)

    #print(geo_x)
    print("")

    
    return (x_target,y_target)
    
    
    
    
def get_all_images_in_folder(folder_path):
    images = []
    for file in os.listdir(folder_path):
        if file.endswith(".png"):
            images.append(os.path.join(folder_path, file))
    return images


def get_all_tifs_in_folder(folder_path):
    images = []
    for file in os.listdir(folder_path):
        if file.endswith(".tif"):
            images.append(os.path.join(folder_path, file))
    return images


def get_geo_coordinates(input_image):
    
    if input_image.endswith(".png"):
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
    
        inDS = gdal.Open(input_image)
            
        inSRS_wkt = inDS.GetProjection()  # gives SRS in WKT
        inSRS_converter = osr.SpatialReference()  # makes an empty spatial ref object
        inSRS_converter.ImportFromWkt(inSRS_wkt)  # populates the spatial ref object with our WKT SRS
        inSRS_forPyProj = inSRS_converter.ExportToProj4()  # Exports an SRS ref as a Proj4 string usable by PyProj
        
        
        swiss = pyproj.Proj("+init=EPSG:2056")
        wgs84=pyproj.Proj("+init=EPSG:4326") # LatLon with WGS84 datum used by GPS units and Google Earth
        #wgs84 = pyproj.Proj("+units=m +init=epsg:4326 +proj=longlat +datum=WGS84 +no_defs +ellps=WGS84 +towgs84=0,0,0")
        ulx, xres, xskew, uly, yskew, yres  = inDS.GetGeoTransform()
        lrx = ulx + (inDS.RasterXSize * xres)
        lry = uly + (inDS.RasterYSize * yres)
        geo_info = GeoInformation()
        geo_info.lr_lon = lrx
        geo_info.lr_lat = lry
        geo_info.ul_lon = ulx
        geo_info.ul_lat = uly
        '''
        print(str(lrx) + " " + str(lry) + " swiss coordinate system (lower right)")

        geo_info.lr_lon,geo_info.lr_lat  = pyproj.transform(swiss, wgs84, lrx, lry)
        geo_info.ul_lon,geo_info.ul_lat = pyproj.transform(swiss, wgs84, ulx, uly)
        print(str(geo_info.lr_lon) + " " + str(geo_info.lr_lat) + " wgs84 (lower right)")
        '''
        return geo_info


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


def get_intersection(geo1,geo2):

    leftX   = max( geo1.ul_lon, geo2.ul_lon);
    rightX  = min( geo1.lr_lon, geo2.lr_lon);
    topY    = min( geo1.ul_lat, geo2.ul_lat);
    bottomY = max( geo1.lr_lat, geo2.lr_lat);
    
    if leftX < rightX and topY > bottomY:
        intersectionRect = GeoInformation()
        intersectionRect.ul_lon = leftX
        intersectionRect.ul_lat = topY
        intersectionRect.lr_lon = rightX
        intersectionRect.lr_lat = bottomY

        return intersectionRect
    else:
        return None
    







apply_annotations_to_images("C:/Users/johan/Desktop/Test", "C:/Users/johan/Desktop/Resources/orthophotos1", "C:/Users/johan/Desktop/Resources/Test")