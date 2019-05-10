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


#Annotation Folder with Annotations made with the Android App
input_folder = "C:/Users/johan/Desktop/eschikon"
input_folder = "C:/Users/gallmanj.KP31-21-161/Desktop/eschikon"


#All outputs will be printed into this folder
output_folder = "C:/Users/johan/Desktop/output/"
#output_folder = "C:/Users/johan/Desktop/MasterThesis/Tensorflow/workspace/faster_rcnn_resnet101_coco/"
output_folder = "C:/Users/gallmanj.KP31-21-161/Desktop/output/"

#if for the training not the images in the input_folder should be used but the single shot orthophotos,
#set this variable to the path to the directory with the single shot orthophotos
#If you do not wish to use the orthophotos, put the empty string ("")
single_shot_ortho_photos_path = "C:/Users/johan/Desktop/Resources/orthophotos"
single_shot_ortho_photos_path = "C:/Users/gallmanj.KP31-21-161/Desktop/orthophotos"
single_shot_ortho_photos_path = ""

#set the tile size of the images to do the tensorflow training on. This value should be chosen to suit your 
#GPU capabilities
tile_size = 320

#what portion of the images should be used for testing and not for training
test_set_size = 0.2





import os
import xml.etree.cElementTree as ET
from PIL import Image
from shutil import move
import utils.xml_to_csv as xml_to_csv
import random
import utils.generate_tfrecord as generate_tfrecord
from utils import flower_info
from utils import apply_annotations
from utils import file_utils
from object_detection.utils import visualization_utils
import progressbar






def convert_annotation_folder(input_folder, output_dir):
    
    print("Preparing output folder structure...")
    make_training_dir_folder_structure(output_dir)
    
    if(single_shot_ortho_photos_path != ""):
        annotated_ortho_photos_path = os.path.join(os.path.join(output_dir,"images"),"annotated_ortho_photos")
        apply_annotations.apply_annotations_to_images(input_folder, single_shot_ortho_photos_path,annotated_ortho_photos_path)
        input_folder = annotated_ortho_photos_path
    
    image_paths = file_utils.get_all_images_in_folder(input_folder)
    labels = {}
    train_images_dir = os.path.join(os.path.join(output_dir, "images"),"train")
    test_images_dir = os.path.join(os.path.join(output_dir, "images"),"test")

    print("Tiling images into chunks suitable for Tensorflow training:")
    for i in progressbar.progressbar(range(len(image_paths))):
        image_path = image_paths[i]
        annotation_path = image_path[:-4] + "_annotations.json"

        tile_image_and_annotations(image_path,annotation_path,train_images_dir, labels)
        
        
    print("Creating Labelmap file...")
    annotations_dir = os.path.join(output_dir, "model_inputs")
    write_labels_to_labelmapfile(labels,annotations_dir)
    
    print("Splitting train and test dir...")
    labels_test = {}
    split_train_dir(train_images_dir,test_images_dir,labels, labels_test)
    
    print("Converting Annotation data into tfrecord files...")
    train_csv = os.path.join(annotations_dir, "train_labels.csv")
    test_csv = os.path.join(annotations_dir, "test_labels.csv")
    xml_to_csv.xml_to_csv(train_images_dir,train_csv)
    xml_to_csv.xml_to_csv(test_images_dir,test_csv)
    
    train_tf_record = os.path.join(annotations_dir, "train.record")
    generate_tfrecord.make_tfrecords(train_csv,train_tf_record,train_images_dir, labels)
    test_tf_record = os.path.join(annotations_dir, "test.record")
    generate_tfrecord.make_tfrecords(test_csv,test_tf_record,test_images_dir, labels)
    
    print("tfrecord training files generated from the follwing amount of flowers:")
    print(labels)
    print("the test data contains the following amount of flowers:")
    print(labels_test)
    print("Done!")

        
    
    
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
    annotation_data = file_utils.read_json_file(annotation_path)
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


    
    
def split_train_dir(train_dir,test_dir, labels, labels_test):
    
    #shuffle the images randomly
    images = file_utils.get_all_images_in_folder(train_dir)
    random.shuffle(images)
    
    #and move the first few images to the test folder
    for i in range(0,int(len(images)*test_set_size)):
        image_name = os.path.basename(images[i])
        xml_name = os.path.basename(images[i])[:-4] + ".xml"

        #update the labels count to represent the counts of the training data
        xmlTree = ET.parse(images[i][:-4] + ".xml")
        for elem in xmlTree.iter():
            if(elem.tag == "name"):
                flower_name = elem.text
                labels[flower_name] = labels[flower_name]-1
                add_label_to_labelcount(flower_name,labels_test)
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
            
            

def build_xml_tree(flowers, image_path, labels):
    root = ET.Element("annotation")
    
    image = Image.open(image_path)
    ET.SubElement(root, "filename").text = os.path.basename(image_path)
    
    width, height = image.size
    size = ET.SubElement(root, "size")
    ET.SubElement(size, "width").text = str(width)
    ET.SubElement(size, "height").text = str(height)
    
    for flower in flowers:
        flower_name = file_utils.clean_string(flower["name"])
        add_label_to_labelcount(flower_name, labels)
        
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
            
            #visualization_utils.draw_bounding_box_on_image(image,y - bounding_box_size,x - bounding_box_size,y + bounding_box_size,x + bounding_box_size,display_str_list=(),thickness=1, use_normalized_coordinates=False)

    #image.save(image_path)
    tree = ET.ElementTree(root)
    return tree

def add_label_to_labelcount(flower_name, label_count):
    if(label_count.get(flower_name) == None):
        label_count[flower_name] = 1
    else:
        label_count[flower_name] = label_count[flower_name] + 1


def make_training_dir_folder_structure(root_folder):
    images_folder = os.path.join(root_folder, "images")
    os.makedirs(images_folder,exist_ok=True)
    file_utils.delete_folder_contents(images_folder)
    os.makedirs(os.path.join(images_folder,"test"),exist_ok=True)
    os.makedirs(os.path.join(images_folder,"train"),exist_ok=True)
    os.makedirs(os.path.join(images_folder,"annotated_ortho_photos"),exist_ok=True)
    os.makedirs(os.path.join(root_folder,"model_inputs"),exist_ok=True)
    os.makedirs(os.path.join(root_folder,"pre-trained-model"),exist_ok=True)
    os.makedirs(os.path.join(root_folder,"trained_inference_graphs"),exist_ok=True)
    os.makedirs(os.path.join(root_folder,"training"),exist_ok=True)


    
    

convert_annotation_folder(input_folder, output_folder)

