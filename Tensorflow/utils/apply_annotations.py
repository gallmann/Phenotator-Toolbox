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
import osr




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
    """
    Copies all annotations from the annotated_folder to all images in the to_be_annotated_folder and saves
    them into the output_folder. Note that the images in the annotated_folder and the
    to_be_annotated_folder have to be geo referenced. (either georeferenced tifs) or
    jpg/png with imagename_geoinfo.json files in the same folder

    Parameters:
        annotated_folder (str): path of the folder containing annotations
        to_be_annotated_folder (str) path to the folder containing the images that
            are to be annotated
        output_folder (str): path to the folder where the annotated images from the 
            to_be_annotated_folder are saved to
    
    Returns:
        None
    """

    all_ortho_tifs = file_utils.get_all_images_in_folder(images_folder)
    
    print("Adding Annotations to all ortho images:")
    
    # loop through all images in the images_folder
    for i in progressbar.progressbar(range(len(all_ortho_tifs))):
        apply_annotations_to_image(annotated_folder,all_ortho_tifs[i],output_folder)
    
def apply_annotations_to_image(annotated_folder, image_path, output_folder):
    """
    Copies all annotations from the annotated_folder to the image at image_path and saves
    it into the output_folder.

    Parameters:
        annotated_folder (str): path of the folder containing annotations
        image_path (str): path to the image onto which the annotations should be copied
        output_folder (str): path to the folder where the annotated images from the 
            to_be_annotated_folder are saved to
    
    Returns:
        None
    """

    all_annotated_images = file_utils.get_all_images_in_folder(annotated_folder)
    
    ortho_tif = image_path

    #convert the georeferenced tif to png and copy it to the output folder. Also create empty imagename_annotations.json file
    im = Image.open(ortho_tif)
    im.thumbnail(im.size)
    ortho_png = os.path.join(output_folder, os.path.basename(ortho_tif)[:-4] + ".png")
    im.save(ortho_png, quality=100)
    annotation_template = {"annotatedFlowers": []}
    with open(os.path.join(output_folder,os.path.basename(ortho_tif)[:-4] + "_annotations.json"), 'w') as outfile:
        json.dump(annotation_template, outfile)

    #loop through all images in annotated_folder and call copy_annotations() if the two
    #images share a common area
    c = get_geo_coordinates(ortho_tif)
    for annotated_image in all_annotated_images:
        d = get_geo_coordinates(annotated_image)
        intersection = get_intersection(c,d)
        if intersection:
            copy_annotations(annotated_image, ortho_png, c, d)  
                    
    
def copy_annotations(annotated_image_path, ortho_png, ortho_tif_coordinates, annotated_image_coordinates):
    """
    Copies all annotations from the annotated_image to the ortho_png image and
    saves them to the ortho_png annotation file.

    Parameters:
        annotated_image_path (str): path of annotated image
        ortho_png (str): path to the image onto which the annotations should be copied
        ortho_tif_coordinates (GeoInformation): GeoInformation object belonging
            to the ortho_png
        annotated_image_coordinates (GeoInformation): GeoInformation object belonging
            to the annotated_image
    
    Returns:
        None
    """

    # read the annotation_data
    annotations = file_utils.get_annotations(annotated_image_path)
    if(not annotations):
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
    for i in range(len(annotations)-1,-1,-1):
        
        annotation = annotations[i]
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
            elif is_pixel_white(x,y,orthoTif):
                should_be_added = False
                break
        if should_be_added:
            output_annotations["annotatedFlowers"].append(translated_annotation)
                
    #save annotation file
    with open(output_annotations_path, 'w') as outfile:
        json.dump(output_annotations, outfile)
        
        
        
def translate_annotation(annotation,height,width,annotated_image_coordinates, ortho_tif_coordinates,ortho_height,ortho_width):
    """
    Translates the pixel coordinates of the from one image to pixel coordinates of another image,
    given the height, width and geo coordinates of both images.

    Parameters:
        annotation (dict): annotation dict.
        height (int): height of annotated image
        width (int): width of annotated image
        annotated_image_coordinates (GeoInformation): GeoInformation object of annotated image
        ortho_tif_coordinates (GeoInformation): GeoInformation object of to_be_annotated image
        ortho_height (int): height of to_be_annotated image
        ortho_width (int): width of to_be_annotated image
    
    Returns:
        dict: Annotation dict with translated x and y coordinates
    """

    
    
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
    
    """
    Given an image_height and image_with and a polygon, the function computes the intersection
    polygon of the image and the polygon and returns the intersection polygon.
    
    Parameters:
        image_height (int): height of annotated image
        image_width (int): width of annotated image
        roi_polygon (list): list of coordinates defining the polygon
    
    Returns:
        list: list of coordinates difining the intersection polygon,
            None if they do not intersect
    """

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

    
def are_coordinates_within_image_bounds(x,y,width,height):
    """
    Given an height and with of an image and x and y coordinates, the function checks
    if the coordinates lay within the image bounds.
    
    Parameters:
        x (int): x coordinate
        y (int): y coordinate
        height (int): height of the image
        width (int): width of the image
    
    Returns:
        bool: True, if coordinates are within image, False otherwise
    """

    #check if the (x,y) coordinates lay within the image bounds
    if(x < width and y < height and x > 0 and y > 0):
        return True
    return False
        
def is_pixel_white(x,y,image):
    """
    Checks whether the pixel has at (x,y) is white in the image
    
    Parameters:
        x (int): x coordinate
        y (int): y coordinate
        image (PIL-image): PIL image to check
    
    Returns:
        bool: True, if pixel at (x,y) coordinate is white, False otherwise
    """

    if not are_coordinates_within_image_bounds(x,y,image.width,image.height):
        return False
    if image.load()[x,y] == (255,255,255):
        return True
    return False


    
def translate_pixel_coordinates(x,y,height,width,source_geo_coords,target_geo_coords,height_target,width_target):
    """
    Translates one pixel coordinate of the from one image to pixel coordinates of another image,
    given the height, width and geo coordinates of both images.

    Parameters:
        x (int): x coordinate
        y (int): y coordinate
        height (int): height of annotated image
        width (int): width of annotated image
        source_geo_coords (GeoInformation): GeoInformation object of annotated image
        target_geo_coords (GeoInformation): GeoInformation object of to_be_annotated image
        height_target (int): height of to_be_annotated image
        width_target (int): width of to_be_annotated image
    
    Returns:
        tuple: (x,y) translated coordinates
    """

    rel_x = x/width
    rel_y = y/height
    geo_x = (source_geo_coords.lr_lon-source_geo_coords.ul_lon) * rel_x + source_geo_coords.ul_lon
    geo_y = (source_geo_coords.ul_lat-source_geo_coords.lr_lat) * (1-rel_y) + source_geo_coords.lr_lat
    
    rel_x_target = (geo_x-target_geo_coords.ul_lon)/(target_geo_coords.lr_lon-target_geo_coords.ul_lon)
    rel_y_target = 1-(geo_y-target_geo_coords.lr_lat)/(target_geo_coords.ul_lat-target_geo_coords.lr_lat)
    x_target = rel_x_target* width_target
    y_target = rel_y_target* height_target  
    return (x_target,y_target)
    
    
    


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


        

def get_intersection(geo1,geo2):
    """
    Returns the intersection rectangle of two GeoInformation objects (defined at top of this file)
    
    Parameters:
        geo1 (GeoInformation): first GeoInformation object
        geo2 (GeoInformation): second GeoInformation object
    Returns:
        GeoInformation: intersection rectangle
    """


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
    
