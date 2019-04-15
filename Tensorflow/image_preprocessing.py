# -*- coding: utf-8 -*-
"""
Created on Mon Apr  1 11:25:16 2019

@author: johan




This script takes as inputs an input_folder which should contain images alongside 
with annotations made by the Android-Annotation-Tool. The output_folder is expected to 
have the following structure:

output_folder
    images
        test
        train
    model_inputs

This script will place the correctly tiled images alongside with annotations_xml files into
the images/train and images/test folder. 
Other Tensorflow model input files such as labelmap.pbtxt and .record files will be generated
and placed into the model_inputs folder.
"""



input_folder = "C:/Users/johan/Desktop/Resources/Test"
#output_folder = "C:/Users/johan/Desktop/MasterThesis/Tensorflow/workspace/faster_rcnn_resnet101_coco/"
output_folder = "C:/Users/johan/Desktop/MasterThesis/Tensorflow/workspace/test/"

use_single_shot_ortho_photos = False #set this to True or False
single_shot_ortho_photos_path = ""

tile_size = 320
test_set_size = 0.2




import os
import json
import xml.etree.cElementTree as ET
from PIL import Image
from shutil import move
import utils.xml_to_csv as xml_to_csv
import random
import utils.generate_tfrecord as generate_tfrecord
from utils import flower_info
from utils import apply_annotations
from object_detection.utils import visualization_utils






def convert_annotation_folder(folder_path, training_dir):
    
    if(use_single_shot_ortho_photos):
        apply_annotations.apply_annotations_to_images(folder_path, single_shot_ortho_photos_path)
        folder_path = single_shot_ortho_photos_path
        
    image_paths = get_all_images_in_folder(folder_path)
    labels = []
    train_images_dir = os.path.join(os.path.join(training_dir, "images"),"train")
    test_images_dir = os.path.join(os.path.join(training_dir, "images"),"test")
    delete_folder_contents(train_images_dir)
    delete_folder_contents(test_images_dir)

    for image_path in image_paths:
        annotation_path = image_path[:-4] + "_annotations.json"

        tile_image_and_annotations(image_path,annotation_path,train_images_dir, labels)
        
    
    
    annotations_dir = os.path.join(training_dir, "model_inputs")
    write_labels_to_labelmapfile(labels,annotations_dir)
    
    split_train_dir(train_images_dir,test_images_dir)
    train_csv = os.path.join(annotations_dir, "train_labels.csv")
    test_csv = os.path.join(annotations_dir, "test_labels.csv")
    xml_to_csv.xml_to_csv(train_images_dir,train_csv)
    xml_to_csv.xml_to_csv(test_images_dir,test_csv)
    
    train_tf_record = os.path.join(annotations_dir, "train.record")
    generate_tfrecord.make_tfrecords(train_csv,train_tf_record,train_images_dir, labels)
    test_tf_record = os.path.join(annotations_dir, "test.record")
    generate_tfrecord.make_tfrecords(test_csv,test_tf_record,test_images_dir, labels)

        
    
    
def tile_image_and_annotations(image_path, annotation_path, output_folder,labels):
    
    image = Image.open(image_path)
    image_name = os.path.basename(image_path)[:-4]
    
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



#TODO: return also flowers on the border
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
    images = get_all_images_in_folder(train_dir)
    random.shuffle(images)
    for i in range(0,int(len(images)*test_set_size)):
        image_name = os.path.basename(images[i])
        xml_name = os.path.basename(images[i])[:-4] + ".xml"
        move(images[i],os.path.join(test_dir,image_name))
        move(images[i][:-4] + ".xml",os.path.join(test_dir,xml_name))
            


    
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
            
        
def clean_string(s):
    return s.encode(encoding='iso-8859-1').decode(encoding='utf-8').replace('ö','oe').replace('ä','ae').replace('ü','ue')
    

def build_xml_tree(flowers, image_path, labels):
    root = ET.Element("annotation")
    
    image = Image.open(image_path)
    ET.SubElement(root, "filename").text = os.path.basename(image_path)
    
    width, height = image.size
    size = ET.SubElement(root, "size")
    ET.SubElement(size, "width").text = str(width)
    ET.SubElement(size, "height").text = str(height)
    
    for flower in flowers:
        flower_name = clean_string(flower["name"])
        if flower_name not in labels:
            labels.append(flower_name)
        
        if flower["isPolygon"]:
            continue
            #TODO!!
            
        else:
            annotation_object = ET.SubElement(root, "object")
            ET.SubElement(annotation_object, "name").text = flower_name
            ET.SubElement(annotation_object, "pose").text = "Unspecified"
            ET.SubElement(annotation_object, "truncated").text = str(0)
            ET.SubElement(annotation_object, "difficult").text = str(0)            
            bndbox = ET.SubElement(annotation_object, "bndbox")
            x = round(flower["polygon"][0]["x"])
            y = round(flower["polygon"][0]["y"])
            bounding_box_size = flower_info.get_bbox_size(flower_name)
            ET.SubElement(bndbox, "xmin").text = str(x - bounding_box_size)
            ET.SubElement(bndbox, "ymin").text = str(y - bounding_box_size)
            ET.SubElement(bndbox, "xmax").text = str(x + bounding_box_size)
            ET.SubElement(bndbox, "ymax").text = str(y + bounding_box_size)
                        
            visualization_utils.draw_bounding_box_on_image(image,y - bounding_box_size,x - bounding_box_size,y + bounding_box_size,x + bounding_box_size,display_str_list=(),thickness=1, use_normalized_coordinates=False)

    image.save(image_path)
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
        with open(file_path, 'r') as f:
            try:
                jsondata = json.load(f)
                return jsondata
            except:
                return None
    else:
        return None

def delete_folder_contents(folder_path):
    for the_file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            #elif os.path.isdir(file_path): shutil.rmtree(file_path)
        except Exception as e:
            print(e)

convert_annotation_folder(input_folder, output_folder)
