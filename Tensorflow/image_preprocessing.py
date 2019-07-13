# -*- coding: utf-8 -*-
"""
Created on Mon Apr  1 11:25:16 2019

@author: johan




This script takes as input an input_folder which should contain images alongside 
with annotations made by the Android-Annotation-Tool. 
Additionally an output folder has to be specified. 
Optionally a folder containing more ortho photos can be specified. If specified, 
the script will use these orthophotos for training as well.

From this input it generates multiple outputs:
    
    1. It will place the correctly tiled images alongside with annotations_xml files into
    the images/train and images/test folder.
    2. Other Tensorflow model input files such as labelmap.pbtxt and .record files will be generated
    and placed into the model_inputs folder.
    3. The eval, training, trained_inference_graphs and pre-trained-model folders are prepared.
"""


print("Loading libraries...")
from utils import constants
import os
import xml.etree.cElementTree as ET
from PIL import Image
from shutil import move
from shutil import copy
import utils.xml_to_csv as xml_to_csv
import random
import utils.generate_tfrecord as generate_tfrecord
from utils import flower_info
from utils import file_utils
import progressbar
import sys




def convert_annotation_folders(input_folders, splits, output_dir, tile_size, split_mode, min_flowers):
    
    """Converts the contents of a list of input folders into tensorflow readable format ready for training

    Parameters:
        input_folders (list): A list of strings containing all input_folders. 
            The input folders should contain images alongside with annotation
            files. The images can be in png, jpg or tif format. The annotation
            files can either be created with the LabelMe application (imagename.json)
            or with the AnnotationApp (imagename_annotations.json).
        splits (list): A list of floats between 0 and 1 of the same length as 
            input_folders. Each boolean indicates what portion of the images
            inside the corresponding input folder should be used for testing and
            not for training
        output_dir (string): Path of the output directory
        tile_size (int): Image Tile size to use as Tensorflow input
        split_mode (str): If split_mode is "random", the images are split
            randomly into test and train directory. If split_mode is "deterministic",
            the images will be split in the same way every time this script is 
            executed and therefore making different configurations comparable
        min_flowers (int): Minimum amount of flower needed for including it in the
            training
    
    Returns:
        A filled output_dir with all necessary inputs for the Tensorflow model training
    """

    if len(input_folders) != len(splits):
        print("Error: Make sure that you provide the same number of input folders and split values")
        return

    make_training_dir_folder_structure(output_dir)
    
    labels = {}
    train_images_dir = os.path.join(os.path.join(output_dir, "images"),"train")
    test_images_dir = os.path.join(os.path.join(output_dir, "images"),"test")
    test_images_dir_full_size = os.path.join(os.path.join(output_dir, "images"),"test_full_size")

    for input_folder_index in range(0,len(input_folders)):
        
        input_folder = input_folders[input_folder_index]
                
        image_paths = file_utils.get_all_images_in_folder(input_folder)
        
        print("")
        print("Tiling images (and annotations) into chunks suitable for Tensorflow training: (" + input_folder + ")")
        sys.stdout.flush()
        for i in progressbar.progressbar(range(len(image_paths))):
            image_path = image_paths[i]
    
            tile_image_and_annotations(image_path,train_images_dir, labels, input_folder_index, tile_size)
        
    
    
    
    
    
    flowers_to_use = filter_labels(labels,min_flowers)
        
    print("Creating Labelmap file...")
    annotations_dir = os.path.join(output_dir, "model_inputs")
    write_labels_to_labelmapfile(flowers_to_use,annotations_dir)
    
    print("Splitting train and test dir...")
    labels_test = {}
    split_train_dir(train_images_dir,test_images_dir, labels, labels_test,split_mode,input_folders,splits,test_dir_full_size = test_images_dir_full_size)
    
    print("Converting Annotation data into tfrecord files...")
    train_csv = os.path.join(annotations_dir, "train_labels.csv")
    test_csv = os.path.join(annotations_dir, "test_labels.csv")
    xml_to_csv.xml_to_csv(train_images_dir,train_csv,flowers_to_use=flowers_to_use)
    xml_to_csv.xml_to_csv(test_images_dir,test_csv,flowers_to_use=flowers_to_use)
    
    train_tf_record = os.path.join(annotations_dir, "train.record")
    generate_tfrecord.make_tfrecords(train_csv,train_tf_record,train_images_dir, labels)
    test_tf_record = os.path.join(annotations_dir, "test.record")
    generate_tfrecord.make_tfrecords(test_csv,test_tf_record,test_images_dir, labels)
    
    print("tfrecord training files generated from the follwing amount of flowers:")
    print_labels(labels, flowers_to_use)
    print("the test data contains the following amount of flowers:")
    print_labels(labels_test, flowers_to_use)
    print(str(len(flowers_to_use)) + " classes usable for training.")
    print("Done!")


    
def tile_image_and_annotations(image_path, output_folder,labels,input_folder_index, tile_size):
    
    """Tiles the image and the annotations into square shaped tiles of size tile_size
        Requires the image to have either a tablet annotation file (imagename_annotations.json)
        or the LabelMe annotation file (imagename.json) stored in the same folder

    Parameters:
        image_path (str): The image path 
        output_folder (string): Path of the output directory
        labels (dict): a dict inside of which the flowers are counted
        input_folder_index (int): the index of the input folder
        tile_size (int): the tile size 
    
    Returns:
        Fills the output_folder with all tiles (and annotation files in xml format)
        that contain any flowers.
    """

    image = Image.open(image_path)
    image_name = os.path.basename(image_path)
    
    currentx = 0
    currenty = 0
    while currenty < image.size[1]:
        while currentx < image.size[0]:
            filtered_annotations = get_flowers_within_bounds(image_path, currentx,currenty,tile_size)
            if len(filtered_annotations) == 0:
                #Ignore image tiles without any annotations
                currentx += tile_size
                continue
            tile = image.crop((currentx,currenty,currentx + tile_size,currenty + tile_size))
            output_image_path = os.path.join(output_folder, image_name + "_subtile_" + "x" + str(currentx) + "y" + str(currenty) + "_inputdir" + str(input_folder_index) + ".png")
            tile.save(output_image_path,"PNG")
            
            xml_path = output_image_path[:-4] + ".xml"
            annotations_xml = build_xml_tree(filtered_annotations,output_image_path,labels)
            annotations_xml.write(xml_path)
            
            currentx += tile_size
        currenty += tile_size
        currentx = 0



def get_flowers_within_bounds(image_path, x_offset, y_offset, tile_size):
    
    """Returns a list of all annotations that are located within the specified bounds of the image

    Parameters:
        image_path (str): path of the image file
        x_offset (int): the left bound of the tile to search in
        y_offset (int): the top bound of the tile to search in
        tile_size (int): the tile size 
    
    Returns:
        list: a list of dicts containing all annotations within the specified bounds
    """

    filtered_annotations = []
    annotations = file_utils.get_annotations(image_path)

    for flower in annotations:
        if flower["name"] == "roi":
            continue
        
        [top,left,bottom,right] = flower_info.get_bbox(flower)
        [top,left,bottom,right] = [top-y_offset, left -x_offset, bottom-y_offset, right - x_offset]
        if is_bounding_box_within_image(tile_size, top,left,bottom,right):
            flower["bounding_box"] = [max(-1,top),max(-1,left),min(tile_size+1,bottom),min(tile_size+1,right)]  
            filtered_annotations.append(flower)
    return filtered_annotations


def is_bounding_box_within_image(tile_size, top, left, bottom, right):
    """Checks if a specified bounding box intersects with the image tile

    Parameters:
        tile_size (int): the tile size 
        top (int): top bound of bounding box 
        left (int): left bound of bounding box 
        bottom (int): bottom bound of bounding box 
        right (int): right bound of bounding box 
    
    Returns:
        bool: True if the specified bounding box is within the image bounds,
            False otherwise
    """

    
    if left < 0 and right < 0:
        return False
    if left >= tile_size and right >= tile_size:
        return False
    if bottom < 0 and top < 0:
        return False
    if bottom >= tile_size and top >= tile_size:
        return False
    return True


def split_train_dir(train_dir,test_dir,labels, labels_test,split_mode,input_folders,splits, test_dir_full_size = None):
    """Splits all annotated images into training and testing directory

    Parameters:
        train_dir (str): the directory path containing all images and xml annotation files 
        test_dir (str): path to the test directory where the test images (and 
                 annotations will be copied to) 
        labels (dict): a dict inside of which the flowers are counted
        labels_test (dict): a dict inside of which the flowers are counted that
            moved to the test directory
        split_mode (str): If split_mode is "random", the images are split
            randomly into test and train directory. If split_mode is "deterministic",
            the images will be split in the same way every time this script is 
            executed and therefore making different configurations comparable
        input_folders (list): A list of strings containing all input_folders. 
        splits (list): A list of floats between 0 and 1 of the same length as 
            input_folders. Each boolean indicates what portion of the images
            inside the corresponding input folder should be used for testing and
            not for training
        test_dir_full_size (str): path of folder to which all full size original
            images that are moved to the test directory should be copied to.
            (this folder can be used for evaluation after training) (default is None)
    
    Returns:
        None
    """

    images = file_utils.get_all_images_in_folder(train_dir)

    for input_folder_index in range(0,len(input_folders)):
        portion_to_move_to_test_dir = float(splits[input_folder_index])
        images_in_current_folder = []
        image_names_in_current_folder = []
        

        #get all image_paths in current folder
        for image_path in images:
            if "inputdir" + str(input_folder_index) in image_path:
                images_in_current_folder.append(image_path)
                image_name = os.path.basename(image_path).split("_subtile",1)[0] 
                if not image_name in image_names_in_current_folder:
                    image_names_in_current_folder.append(image_name)
            
        if split_mode == "random":
        
            #shuffle the images randomly
            random.shuffle(images_in_current_folder)
            #and move the first few images to the test folder
            for i in range(0,int(len(images_in_current_folder)*portion_to_move_to_test_dir)):
                move_image_and_annotations_to_folder(images_in_current_folder[i],test_dir,labels,labels_test)
    
        elif split_mode == "deterministic":
                    
            #move every 1/portion_to_move_to_test_dir-th image to the test_dir
            split_counter = 0.5
            #loop through all image_names (corresponding to untiled original images)
            for image_name in image_names_in_current_folder:
                split_counter = split_counter + portion_to_move_to_test_dir
                #if the split_counter is greater than one, all image_tiles corresponding to that original image should be
                #moved to the test directory
                if split_counter >= 1:
                    if test_dir_full_size:
                        original_image_name = os.path.join(input_folders[input_folder_index], image_name)
                        copy(original_image_name,os.path.join(test_dir_full_size,"inputdir" + str(input_folder_index) + "_" +image_name))
                        copy(original_image_name[:-4] + "_annotations.json",os.path.join(test_dir_full_size,"inputdir" + str(input_folder_index) + "_" +image_name[:-4] + "_annotations.json"))

                    for image_tile in images_in_current_folder:
                        if image_name in os.path.basename(image_tile):
                            move_image_and_annotations_to_folder(image_tile,test_dir,labels,labels_test)
                    split_counter = split_counter -1
                    
            

            

def move_image_and_annotations_to_folder(image_path,dest_folder, labels, labels_test):
    """Moves and image alonside with its annotation file to another folder and updates the flower counts

    Parameters:
        image_path (str): path to the image
        dest_folder (str): path to the destination folder
        labels (dict): a dict inside of which the flowers are counted
        labels_test (dict): a dict inside of which the flowers are counted that
            moved to the test directory
    
    Returns:
        None
    """

    image_name = os.path.basename(image_path)
    xml_name = os.path.basename(image_path)[:-4] + ".xml"

    #update the labels count to represent the counts of the training data
    xmlTree = ET.parse(image_path[:-4] + ".xml")
    for elem in xmlTree.iter():
        if(elem.tag == "name"):    
            flower_name = elem.text
            labels[flower_name] = labels[flower_name]-1
            add_label_to_labelcount(flower_name,labels_test)
    move(image_path,os.path.join(dest_folder,image_name))
    move(image_path[:-4] + ".xml",os.path.join(dest_folder,xml_name))


def write_labels_to_labelmapfile(labels, output_path):
    """Given a list of labels, prints them to a labelmap file needed by tensorflow

    Parameters:
        labels (dict): a dict inside of which the flowers are counted
        output_path (str): a directory path where the labelmap.pbtxt file should be saved to
    
    Returns:
        None
    """

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
    """Given a list of flowers, this function builds an xml tree from it. The XML tree is needed to create the tensorflow .record files

    Parameters:
        flowers (list): a list of flower dicts
        image_path (str): the path of the corresponding image
        labels (dict): a dict inside of which the flowers are counted

    Returns:
        None
    """

    root = ET.Element("annotation")
    
    image = Image.open(image_path)
    ET.SubElement(root, "filename").text = os.path.basename(image_path)
    
    width, height = image.size
    size = ET.SubElement(root, "size")
    ET.SubElement(size, "width").text = str(width)
    ET.SubElement(size, "height").text = str(height)
    
    for flower in flowers:
        flower_name = flower_info.clean_string(flower["name"])
        add_label_to_labelcount(flower_name, labels)
        
        annotation_object = ET.SubElement(root, "object")
        ET.SubElement(annotation_object, "name").text = flower_name
        ET.SubElement(annotation_object, "pose").text = "Unspecified"
        ET.SubElement(annotation_object, "truncated").text = str(0)
        ET.SubElement(annotation_object, "difficult").text = str(0)            
        bndbox = ET.SubElement(annotation_object, "bndbox")

        [top,left,bottom,right] = flower["bounding_box"]
        ET.SubElement(bndbox, "xmin").text = str(left)
        ET.SubElement(bndbox, "ymin").text = str(top)
        ET.SubElement(bndbox, "xmax").text = str(right)
        ET.SubElement(bndbox, "ymax").text = str(bottom)
            
            
        #visualization_utils.draw_bounding_box_on_image(image,y - bounding_box_size,x - bounding_box_size,y + bounding_box_size,x + bounding_box_size,display_str_list=(),thickness=1, use_normalized_coordinates=False)

    #image.save(image_path)
    tree = ET.ElementTree(root)
    return tree

#small helper function to keep track of how many flowers of each species have been annotated 
def add_label_to_labelcount(flower_name, label_count):
    """Small helper function to to add a flower to a label_count dict
    
    Parameters:
        flower_name (str): name of the flower to add to the dict
        label_count (dict): a dict inside of which the flowers are counted

    Returns:
        None
    """

    if(label_count.get(flower_name) == None):
        label_count[flower_name] = 1
    else:
        label_count[flower_name] = label_count[flower_name] + 1


def make_training_dir_folder_structure(root_folder):
    """Creates the whole folder structure of the output. All subsequent scripts such as train.py, predict.py, export_inference_graph.py or eval.py rely on this folder structure
    
    Parameters:
        root_folder (str): path to a folder inside of which the project folder structure is created

    Returns:
        None
    """

    images_folder = os.path.join(root_folder, "images")
    os.makedirs(images_folder,exist_ok=True)
    file_utils.delete_folder_contents(images_folder)
    os.makedirs(os.path.join(images_folder,"test"),exist_ok=True)
    os.makedirs(os.path.join(images_folder,"train"),exist_ok=True)
    os.makedirs(os.path.join(images_folder,"test_full_size"),exist_ok=True)
    prediction_folder = os.path.join(root_folder,"predictions")
    os.makedirs(prediction_folder,exist_ok=True)
    os.makedirs(os.path.join(prediction_folder,"evaluations"),exist_ok=True)
    os.makedirs(os.path.join(root_folder,"model_inputs"),exist_ok=True)
    os.makedirs(os.path.join(root_folder,"predictions"),exist_ok=True)
    os.makedirs(os.path.join(root_folder,"pre-trained-model"),exist_ok=True)
    os.makedirs(os.path.join(root_folder,"trained_inference_graphs"),exist_ok=True)
    os.makedirs(os.path.join(root_folder,"training"),exist_ok=True)
    os.makedirs(os.path.join(root_folder,"eval"),exist_ok=True)


    #This function takes the labels map and returns an array with the flower names that have more than min_instances instances
def filter_labels(labels, min_instances=50):
    """Creates an array with the flower names that have more than min_instances instances
    
    Parameters:
        labels (dict): a dict inside of which the flowers are counted
        min_instances (int): minimum instances to pass the filter (default is 50)
    Returns:
        list: a list containing all flower names that have more than min_instances instances
    """

    flowers_to_use = []
    for key, value in labels.items():
        if value >= min_instances:
            flowers_to_use.append(key)
    return flowers_to_use


def print_labels(labels, flowers_to_use):
    """Prints the label_count dict to the console in readable format
    
    Parameters:
        labels (dict): a dict inside of which the flowers are counted
        flowers_to_use (list): list of strings of the flower names that should
            be used for training
    Returns:
        None
    """

    print("used:")
    for key,value in labels.items():
        if key in flowers_to_use:
            print("    " + key + ": " + str(value))
    
    print("not used due to lack of enough annotation data:")
    for key,value in labels.items():
        if not (key in flowers_to_use):
            print("    " + key + ": " + str(value))



if __name__== "__main__":
    #Annotation Folder with Annotations made with the Android App
    input_folders = constants.input_folders
    
    splits = constants.input_folders_splits
    
    #All outputs will be printed into this folder
    output_dir = constants.train_dir
    
    #set the tile size of the images to do the tensorflow training on. This value should be chosen to suit your 
    #GPU capabilities and ground resolution (the higher the ground resolution, the greater this tile_size can 
    #be chosen.)
    tile_size = constants.tile_size
    
    #choose between "random" and "deterministic" splitting
    split_mode = "deterministic"
    
    #minimum amount of flower instances to include species in training
    min_flowers = constants.min_flowers

    convert_annotation_folders(input_folders, splits, output_dir, tile_size, split_mode, min_flowers)

