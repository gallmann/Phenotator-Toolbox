# -*- coding: utf-8 -*-
"""
Created on Mon Apr  1 11:25:16 2019

@author: johan
"""

import os
import json
import xml.etree.cElementTree as ET
from PIL import Image
from shutil import copy
import xml_to_csv


bounding_box_size = 20 

tile_size = 512



def convert_annotation_folder(folder_path, training_dir):
    
    image_paths = get_all_images_in_folder(folder_path)
    labels = []
    for image_path in image_paths:
        annotation_path = image_path[:-4] + "_annotations.json"
        train_images_dir = os.path.join(os.path.join(training_dir, "images"),"train")

        tile_image_and_annotations(image_path,annotation_path,train_images_dir, labels)
        '''
        copy(xml_path,train_images_dir)
        copy(image_path,train_images_dir)
    
    annotations_dir = os.path.join(training_dir, "annotations")
    write_labels_to_labelmapfile(labels,annotations_dir)
    test_images_dir = os.path.join(os.path.join(training_dir, "images"),"test")
    split_train_dir(train_images_dir, test_images_dir)

    xml_to_csv.xml_to_csv(train_images_dir,os.path.join(annotations_dir, "train_labels.csv"))
    xml_to_csv.xml_to_csv(test_images_dir,os.path.join(annotations_dir, "test_labels.csv"))
    '''
    
    
    
def tile_image_and_annotations(image_path, annotation_path, output_folder,labels):
    
            
    image = Image.open(image_path)
    image_name = os.path.basename(image_path)[:-4]
    
    if image.size[0] % tile_size == 0 and image.size[1] % tile_size ==0 :
        currentx = 0
        currenty = 0
        while currenty < image.size[1]:
            while currentx < image.size[0]:
                filtered_annotations = get_flowers_within_bounds(annotation_path, currentx,currenty)
                if len(filtered_annotations) == 0:
                    #Ignore image tiles without any annotations
                    currentx += tile_size
                    continue
                tile = image.crop((currentx,currenty,currentx + tile_size,currenty + tile_size))
                output_image_path = os.path.join(output_folder, image_name + "_subtile_" + "x" + str(currentx) + "y" + str(currenty) + ".png")
                tile.save(output_image_path,"PNG")
                
                xml_path = output_image_path[:-4] + ".xml"
                annotations_xml = build_xml_tree(filtered_annotations,output_image_path,labels)
                annotations_xml.write(xml_path)
                
                currentx += tile_size
            currenty += tile_size
            currentx = 0
    else:
        print ("sorry your image does not fit neatly into",tile_size,"*",tile_size,"tiles")



def get_flowers_within_bounds(annotation_path, x_offset, y_offset):
    filtered_annotations = []
    annotation_data = read_json_file(annotation_path)
    if(not annotation_data):
        return filtered_annotations
    annotations = annotation_data["annotatedFlowers"]

    for flower in annotations:
        if flower["isPolygon"]:
            continue
            #TODO!!   
        else:
            x = round(flower["polygon"][0]["x"])
            y = round(flower["polygon"][0]["y"])
            if x < x_offset + tile_size and x >=x_offset and y < y_offset + tile_size and y >= y_offset:
                flower["polygon"][0]["x"] = x - x_offset
                flower["polygon"][0]["y"] = y - y_offset
                filtered_annotations.append(flower)
    
    return filtered_annotations


    
    
def split_train_dir(train_dir,test_dir):
    print("TODO")


    
def write_labels_to_labelmapfile(labels, output_path):
    
    output_name = os.path.join(output_path, "label_map.pbtxt")
    end = '\n'
    s = ' '
    out = ''

    for ID, name in enumerate(labels):
        out += 'item' + s + '{' + end
        out += s*2 + 'id:' + ' ' + (str(ID+1)) + end
        out += s*2 + 'name:' + ' ' + '\'' + name + '\'' + end
        out += '}' + end*3
        
    
    with open(output_name, 'w') as f:
        f.write(out)
            
    
    
def build_xml_tree(flowers, image_path, labels):
    root = ET.Element("annotation")
    

    image = Image.open(image_path)
    ET.SubElement(root, "filename").text = os.path.basename(image_path)
    
    width, height = image.size
    size = ET.SubElement(root, "size")
    ET.SubElement(size, "width").text = str(width)
    ET.SubElement(size, "height").text = str(height)
    
    for flower in flowers:
        if flower["name"] not in labels:
            labels.append(flower["name"])
        
        if flower["isPolygon"]:
            continue
            #TODO!!
            
        else:
            annotation_object = ET.SubElement(root, "object")
            ET.SubElement(annotation_object, "name").text = flower["name"]
            ET.SubElement(annotation_object, "pose").text = "Unspecified"
            ET.SubElement(annotation_object, "truncated").text = str(0)
            ET.SubElement(annotation_object, "difficult").text = str(0)            
            bndbox = ET.SubElement(annotation_object, "bndbox")
            x = round(flower["polygon"][0]["x"])
            y = round(flower["polygon"][0]["y"])
            ET.SubElement(bndbox, "xmin").text = str(x - bounding_box_size)
            ET.SubElement(bndbox, "ymin").text = str(y - bounding_box_size)
            ET.SubElement(bndbox, "xmax").text = str(x + bounding_box_size)
            ET.SubElement(bndbox, "ymax").text = str(y + bounding_box_size)

    tree = ET.ElementTree(root)
    return tree


def get_all_images_in_folder(folder_path):
    images = []
    for file in os.listdir(folder_path):
        if file.endswith(".png"):
            images.append(os.path.join(folder_path, file))
    return images

    
    
def read_json_file(file_path):
    if file_path and os.path.isfile(file_path):
        with open(file_path, 'r', encoding='iso-8859-1') as f:
            jsondata = json.load(f)
        return jsondata
    else:
        return None


convert_annotation_folder("C:/Users/johan/Downloads/eschlikon", "C:/Users/johan/Desktop/MasterThesis/Tensorflow/workspace/training1")
