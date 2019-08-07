# -*- coding: utf-8 -*-
"""
Created on Tue Apr 16 14:52:32 2019

@author: johan



This file contains some helper functions which are used by multiple scripts such as enumerating all images
in a folder or reading a json file.
"""
import os
import json
import shutil
import xml.etree.cElementTree as ET
from PIL import Image, ImageDraw
from utils import flower_info
import numpy
import gdal
import numpy as np
import matplotlib.pyplot as plt

def read_json_file(file_path):
    """Reads a json file into a dict

    Parameters:
        file_path (str): path to json file
    
    Returns:
        dict: a dictionary containing the json file data (or None if the 
            file does not exist)
    """

    if file_path and os.path.isfile(file_path):
        with open(file_path, 'r') as f:
            try:
                jsondata = json.load(f)
                return jsondata
            except Exception as e:
                print(e)
                print(file_path)
                return None
    else:
        return None


def save_json_file(dictionary, output_path):
    """Saves a dictionary to a json file

    Parameters:
        dictionary (dict): the dictionary containing the data
        output_path (str): the path of the output json file
    
    Returns:
        None
    """

    with open(output_path, 'w') as fp:
        json.dump(dictionary, fp)
        



def get_all_images_in_folder(folder_path):
    """Finds all images (png, jpg or tif) inside a folder

    Parameters:
        folder_path (str): the folder path to look for images inside
    
    Returns:
        list: a list of image_paths (strings)
    """
    
    images = []
    if not os.path.isdir(folder_path):
        return images
    for file in os.listdir(folder_path):
        if file.endswith(".png") or file.endswith(".jpg") or file.endswith(".tif"):
            images.append(os.path.join(folder_path, file))
    return images



def delete_folder_contents(folder_path):
    """Deletes all files and subfolders within a folder

    Parameters:
        folder_path (str): the folder path to delete all contents in
    
    Returns:
        None
    """

    for the_file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path): shutil.rmtree(file_path)
        except Exception as e:
            print(e)
                
    
    
def get_annotations_from_xml(xml_path):
    """Reads annotations from an xml file

    Parameters:
        xml_path (str): the file path to the xml file containing the annotations
    
    Returns:
        list: a list of dicts containing all annotations
    """
    
    annotations = []
    if not os.path.isfile(xml_path):
        return annotations
    tree = ET.parse(xml_path)
    root = tree.getroot()
    for child in root:
        if(child.tag == "object"):
            flower = {}
            for att in child:
                if(att.tag == "name"):
                    flower["name"] = att.text
                if(att.tag == "bndbox"):
                    left=right=top=bottom = 0
                    for bound in att:
                        if(bound.tag == "xmin"):
                            left = int(bound.text)
                        if(bound.tag == "ymin"):
                            top = int(bound.text)
                        if(bound.tag == "xmax"):
                            right = int(bound.text)
                        if(bound.tag == "ymax"):
                            bottom = int(bound.text)
                    flower["bounding_box"] = [top,left,bottom,right]
                    flower["isPolygon"] = True
                    polygon = [{"x":left, "y":top},{"x":right, "y":bottom}]
                    flower["polygon"] = polygon
            annotations.append(flower)
    return annotations

    
def get_annotations(image_path):
    """Reads the annotations from either the tablet annotations (imagename_annotations.json),
        the LabelMe annotations (imagename.json) or tensorflow xml format annotations (imagename.xml)

    Parameters:
        image_path (str): path to the image of which the annotations should be read
    
    Returns:
        list: a list containing all annotations corresponding to that image.
            Returns the empty list if no annotation file is present
    """
    annotation_path = image_path[:-4] + "_annotations.json"
    annotation_data = read_json_file(annotation_path)
    if(not annotation_data):
        annotation_data = get_annotations_from_labelme_file(image_path[:-4]+".json")
        if(not annotation_data):
            annotations = get_annotations_from_xml(image_path[:-4]+".xml")
            annotation_data= {"annotatedFlowers":annotations}
            if(not annotation_data):
                return []
    annotations = annotation_data["annotatedFlowers"]
    return annotations


def annotations_to_labelme_file(annotations,output_path,image_path):
    """Saves a list of annotations to a labelme file

    Parameters:
        annotations (list): list of dicts containing all annotations
        output_path (str): file path of the output (labelme json) file
        image_path (str): path of the image to which the annotations correspond
    Returns:
        None
    """
    max_pixels = Image.MAX_IMAGE_PIXELS
    Image.MAX_IMAGE_PIXELS = 5000000000
    image = Image.open(image_path)    
    width, height = image.size
    Image.MAX_IMAGE_PIXELS = max_pixels

    label_me_dict_template = {"version":"3.15.2","flags":{},"shapes":[],"lineColor":[0,255,0,64],"fillColor":[255,0,0,64],"imagePath":os.path.basename(image_path), "imageData":None,"imageHeight":height,"imageWidth":width}
    if annotations:
        for flower in annotations:
            col = flower_info.get_color_for_flower(flower["name"], get_rgb_value=True)
            flower_dict = {"label":flower["name"], "line_color":col,"fill_color":col,"points":[],"shape_type":"rectangle","flags":{}}
            if flower["name"] == "roi":
                flower_dict["shape_type"] = "polygon"
                for point in flower["polygon"]:
                    flower_dict["points"].append([point["x"],point["y"]])
            else:
                [top,left,bottom,right] = flower_info.get_bbox(flower)
                flower_dict["points"] = [[left,top],[right,bottom]]
            label_me_dict_template["shapes"].append(flower_dict)
        
    save_json_file(label_me_dict_template,output_path)
    
def get_annotations_from_labelme_file(labelme_file):
    """Reads the annotations from a LabelMe annotation file (imagename.json)

    Parameters:
        labelme_file (str): path to the labelme annotation file
    
    Returns:
        list: a list containing all annotations corresponding to that image.
            (Returns the empty list if no annotation file is present)
    """

    labelme_dict = read_json_file(labelme_file)
    if not labelme_dict:
        return []
    annotations = {"annotatedFlowers":[]}
    
    
    for annotation in labelme_dict["shapes"]:
        result_annotation = {}
        result_annotation["isPolygon"] = True
        result_annotation["name"] = annotation["label"]
        polygon = []
        for point in annotation["points"]:
            polygon.append({"x":point[0], "y":point[1]})
        result_annotation["polygon"] = polygon
        annotations["annotatedFlowers"].append(result_annotation)
    return annotations

    
def check_all_json_files_in_folder(folder_path):
    """Checks all json files within the provided folder to have the correct format

    Parameters:
        folder_path (str): path to the folder containing json files
    
    Returns:
        None
    """

    for file in os.listdir(folder_path):
        if file.endswith(".json"):
            read_json_file(file)
    print("if no errors were printed, everything is fine")
    
    
def get_image_array(image_path, xoff=0, yoff=0, xsize=None, ysize=None):
    '''
    try:
        image = Image.open(image_path)
        width, height = image.size
        img = Image.open(image_path).convert("RGB")
        img_array = numpy.asarray(img)
        return img_array
    except Image.DecompressionBombError:
    '''
    ds = gdal.Open(image_path)
    image_array = ds.ReadAsArray(xoff, yoff, xsize, ysize).astype(np.uint8)
    image_array = np.swapaxes(image_array,0,1)
    image_array = np.swapaxes(image_array,1,2)
    return image_array
  


def save_array_as_image(image_path,image_array, tile_size = None):

    image_array = image_array.astype(np.uint8)
    if not image_path.endswith(".png") and not image_path.endswith(".jpg") and not image_path.endswith(".tif"):
        print("Error! image_path has to end with .png, .jpg or .tif")
    height = image_array.shape[0]
    width = image_array.shape[1]
    if height*width < Image.MAX_IMAGE_PIXELS:
        newIm = Image.fromarray(image_array, "RGB")
        newIm.save(image_path)
    
    else:
        gdal.AllRegister()
        driver = gdal.GetDriverByName( 'MEM' )
        ds1 = driver.Create( '', width, height, 3, gdal.GDT_Byte)
        ds = driver.CreateCopy(image_path, ds1, 0)
            
        image_array = np.swapaxes(image_array,2,1)
        image_array = np.swapaxes(image_array,1,0)
        ds.GetRasterBand(1).WriteArray(image_array[0], 0, 0)
        ds.GetRasterBand(2).WriteArray(image_array[1], 0, 0)
        ds.GetRasterBand(3).WriteArray(image_array[2], 0, 0)

        if not tile_size:
            gdal.Translate(image_path,ds, options=gdal.TranslateOptions(bandList=[1,2,3], format="png"))

        else:
            for i in range(0, width, tile_size):
                for j in range(0, height, tile_size):
                    #define paths of image tile and the corresponding json file containing the geo information
                    out_path_image = image_path[:-4] + "row" + str(int(j/tile_size)) + "_col" + str(int(i/tile_size)) + ".png"
                    #tile image with gdal (copy bands 1, 2 and 3)
                    gdal.Translate(out_path_image,ds, options=gdal.TranslateOptions(srcWin=[i,j,tile_size,tile_size], bandList=[1,2,3]))
                    
    
def strip_image(input_image_path, roi_file, output_image_path):
    """Turns all pixels that are not within a roi polygon black

    Parameters:
        input_image_path (str): path to the image
        roi_file (str): path to the roi_file (labelme file containing polygons 
                 that are labelled 'roi')
        output_image_path (str): where to save the stripped image to
    
    Returns:
        None
    """

    polygons_json = read_json_file(roi_file)["shapes"]
    polygons = []
    
    for polygon_json in polygons_json:
        if polygon_json["label"] == "roi":
            polygon = []
            for point in polygon_json["points"]:
                polygon.append((point[0],point[1]))
            polygons.append(polygon)

    # read image as RGB (without alpha)
    img_array = get_image_array(input_image_path)
    # create new image ("1-bit pixels, black and white", (width, height), "default color")
    mask_img = Image.new('1', (img_array.shape[1], img_array.shape[0]), 0)
    
    for polygon in polygons:
        ImageDraw.Draw(mask_img).polygon(polygon, outline=1, fill=1)

    mask = numpy.array(mask_img)
    
    
    
    # assemble new image (uint8: 0-255)
    new_img_array = numpy.empty(img_array.shape, dtype='uint8')
    
    # copy color values (RGB)
    new_img_array[:,:,:3] = img_array[:,:,:3]
    
    # filtering image by mask
    new_img_array[:,:,0] = new_img_array[:,:,0] * mask
    new_img_array[:,:,1] = new_img_array[:,:,1] * mask
    new_img_array[:,:,2] = new_img_array[:,:,2] * mask
    
    save_array_as_image(input_image_path[:-4] + ".png", new_img_array)
    
    
    
    print("Fraction of area inside polygons: " + str( np.count_nonzero(mask) / (img_array.shape[1]* img_array.shape[0])) )
    print("Pixels inside polygons: "+ str( np.count_nonzero(mask)))
    
    
    