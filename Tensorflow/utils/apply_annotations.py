# -*- coding: utf-8 -*-
"""
Created on Thu Apr 11 13:48:04 2019

@author: johan
"""

import gdal
import os
import pyproj
import json
from PIL import Image
from utils import file_utils
import progressbar
from shapely.geometry import Polygon
from shapely.geometry import box




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






# This function takes all images together with the annotation files in the annotated_folder
# and based on this annotation data generates the annotation files for all images (.tif) in the
# images_folder. The newly generated annotated images will be saved to the output_folder
def apply_annotations_to_images(annotated_folder, images_folder, output_folder):
    
    all_ortho_tifs = file_utils.get_all_tifs_in_folder(images_folder)
    all_annotated_images = file_utils.get_all_images_in_folder(annotated_folder)
    
    print("Adding Annotations to all ortho images:")
    
    # loop through all images in the images_folder
    for i in progressbar.progressbar(range(len(all_ortho_tifs))):
        
        ortho_tif = all_ortho_tifs[i]

        #convert all images in images_folder to png and copy them to output folder. Also create empty annotation.json files
        im = Image.open(ortho_tif)
        im.thumbnail(im.size)
        ortho_png = os.path.join(output_folder, os.path.basename(ortho_tif)[:-4] + ".png")
        im.save(ortho_png, quality=100)
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
                
    
# copies all annotations from the annotated_image to the ortho_png image.
def copy_annotations(annotated_image_path, annotation_path, ortho_png, ortho_tif_coordinates, annotated_image_coordinates):
    
    # read the annotation_data
    annotation_data = file_utils.read_json_file(annotation_path)
    if(not annotation_data):
        return
    
    #get size information of the annotated_image
    image = Image.open(annotated_image_path)
    width = image.size[0]
    height = image.size[1]
    
    #get size information of the ortho_png image
    orthoTif = Image.open(ortho_png)
    ortho_width = orthoTif.size[0]
    ortho_height = orthoTif.size[1]
    
    #read the output_annotations_file (it could already contain annotation information)
    output_annotations_path = ortho_png[:-4] + "_annotations.json"
    output_annotations = file_utils.read_json_file(output_annotations_path)
    
    
    #loop through all annotations
    for i in range(len(annotation_data["annotatedFlowers"])-1,-1,-1):
        
        annotation = annotation_data["annotatedFlowers"][i]
        should_be_added = True
        translated_annotation = translate_annotation(annotation,height,width,annotated_image_coordinates, ortho_tif_coordinates,ortho_height,ortho_width)

        if annotation["name"] == "roi":
            
            result_polygon = get_intersection_of_polygon_and_image_bounds(ortho_width,ortho_height,annotation["polygon"])
            if result_polygon:
                translated_annotation["polygon"] = result_polygon
                output_annotations["annotatedFlowers"].append(translated_annotation)
            continue
        
        for coord_ind in range(0,len(translated_annotation["polygon"])):
            # get pixel coordinates of annotation
            x = translated_annotation["polygon"][coord_ind]["x"]
            y = translated_annotation["polygon"][coord_ind]["y"]
                        
            #check if the translation of the annotation has pixel coordinates within the bounds of the image to be annotated
            if(not are_coordinates_within_image_bounds(x,y,ortho_width,ortho_height)):
                should_be_added = False
                break
            #check if the output pixel is completely white. If so, the flower is most probably not within the
            #bounds of the image but outside where the image is white (because of orthorectification)
            elif is_pixel_white(x,y,image):
                should_be_added = False
                break
        if should_be_added:
            output_annotations["annotatedFlowers"].append(translated_annotation)
                
    #save annotation file
    with open(output_annotations_path, 'w') as outfile:
        json.dump(output_annotations, outfile)
        
        
        
def translate_annotation(annotation,height,width,annotated_image_coordinates, ortho_tif_coordinates,ortho_height,ortho_width):
    output_annotation = annotation
    for coord_ind in range(0,len(annotation["polygon"])):
        # get pixel coordinates of annotation
        x = annotation["polygon"][coord_ind]["x"]
        y = annotation["polygon"][coord_ind]["y"]
        # translate the annotation pixels to the ortho_png image
        (x_target,y_target) = translate_pixel_coordinates(x,y,height,width,annotated_image_coordinates, ortho_tif_coordinates,ortho_height,ortho_width)
        
        output_annotation["polygon"][coord_ind]["x"] = x_target
        output_annotation["polygon"][coord_ind]["y"] = y_target
    return output_annotation
        
        
        
def get_intersection_of_polygon_and_image_bounds(image_width,image_height,roi_polygon):
        
    image_box = box(0,0,image_width,image_height)
    roi_polygon_array = []
    for coord_ind in range(0,len(roi_polygon)):
        roi_polygon_array.append([roi_polygon[coord_ind]["x"],roi_polygon[coord_ind]["y"]])
    roi_polygon = Polygon(roi_polygon_array)
    intersection = image_box.intersection(roi_polygon)
    
    if intersection.is_empty:
        return None
    intersection_array = list(intersection.exterior.coords)
    
    result_polygon = []
    for coord_ind in range(0,len(intersection_array)-1):
        result_polygon.append({"x":intersection_array[coord_ind][0],"y":intersection_array[coord_ind][1]})
    return result_polygon

    
def are_coordinates_within_colorful_image(x,y,image,width,height):
    return not is_pixel_white(x,y,image) and are_coordinates_within_image_bounds(x,y,width,height)

def are_coordinates_within_image_bounds(x,y,width,height):
    #check if the (x,y) coordinates lay within the image bounds
    if(x < width and y < height and x > 0 and y > 0):
        return True
    return False
        
def is_pixel_white(x,y,image):
    if not are_coordinates_within_image_bounds(x,y,image.width,image.height):
        return False
    if image.load()[x,y] == (255,255,255):
        return True
    return False

def get_roi_annotation(annotation):
    return 0

#convenience method
def translate_pixel_coordinates_conv(annotation,coord_ind,height,width,source_geo_coords,target_geo_coords,height_target,width_target):
    x = annotation["polygon"][coord_ind]["x"]
    y = annotation["polygon"][coord_ind]["y"]
            
    # translate the annotation pixels to the ortho_png image
    return translate_pixel_coordinates(x,y,height,width,annotated_image_coordinates, ortho_tif_coordinates,ortho_height,ortho_width)

    
# translates the coordinates of an annotation from one geo annotated image to the other
def translate_pixel_coordinates(x,y,height,width,source_geo_coords,target_geo_coords,height_target,width_target):
    rel_x = x/width
    rel_y = y/height
    geo_x = (source_geo_coords.lr_lon-source_geo_coords.ul_lon) * rel_x + source_geo_coords.ul_lon
    geo_y = (source_geo_coords.ul_lat-source_geo_coords.lr_lat) * (1-rel_y) + source_geo_coords.lr_lat
    
    rel_x_target = (geo_x-target_geo_coords.ul_lon)/(target_geo_coords.lr_lon-target_geo_coords.ul_lon)
    rel_y_target = 1-(geo_y-target_geo_coords.lr_lat)/(target_geo_coords.ul_lat-target_geo_coords.lr_lat)
    x_target = rel_x_target* width_target
    y_target = rel_y_target* height_target  
    return (x_target,y_target)
    
    
    


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


        

#returns the intersection rectangle of two GeoInformation objects (defined at top of this file)
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
    
