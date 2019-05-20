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

#This function removes all ä, ö and ü from a provided string. (Important for tensorflow)
def clean_string(s):
    return s.encode(encoding='iso-8859-1').decode(encoding='utf-8').replace('ö','oe').replace('ä','ae').replace('ü','ue')


def read_json_file(file_path):
    if file_path and os.path.isfile(file_path):
        with open(file_path, 'r') as f:
            try:
                jsondata = json.load(f)
                return jsondata
            except Exception as e:
                print(e)
                return None
    else:
        return None


def save_json_file(dictionary, output_path):
    with open(output_path, 'w') as fp:
        json.dump(dictionary, fp)
        



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


def delete_folder_contents(folder_path):
    for the_file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path): shutil.rmtree(file_path)
        except Exception as e:
            print(e)
                
    
    
def get_annotations_from_xml(xml_path):
    annotations = []
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
                    flower["bounding_box"] = [left,right,top,bottom]
                            
            annotations.append(flower)
    return annotations

    
    
    
    
    
    
    
    
