# -*- coding: utf-8 -*-
"""
Created on Wed Jun 12 12:47:43 2019

@author: johan
"""

import csv
from utils import file_utils
from utils import flower_info
from utils import constants



input_folders = constants.input_folders

'''
csv_file = 'C:/Users/johan/Desktop/MasterThesis/Data/May_23/AnnotationData/tile_row0_col0_groundtruth1.csv'

folder = 'C:/Users/johan/Desktop/MasterThesis/Data/June_06/AnnotationData'


images = file_utils.get_all_images_in_folder(folder)
for image in images:
    csv_file_dest = image[:-4] + "_groundtruth.csv"
    copyfile(csv_file, csv_file_dest)
'''


#small helper function to keep track of how many flowers of each species have been annotated 
def add_label_to_labelcount(flower_name, label_count, times_to_add=1):
    if times_to_add != 0:
        flower_name = flower_info.clean_string(flower_name)
        if(label_count.get(flower_name) == None):
            label_count[flower_name] = times_to_add
        else:
            label_count[flower_name] = label_count[flower_name] + times_to_add


def count_annotations(annotations_file):
    labels = {}
    annotation_data = file_utils.read_json_file(annotations_file)
    if(not annotation_data):
        return []
    annotations = annotation_data["annotatedFlowers"]
    
    for flower in annotations:
        add_label_to_labelcount(flower["name"], labels)
    
    return labels


def get_ground_truth(ground_truth_file):
    ground_truth = {}
    with open(ground_truth_file,encoding='utf-8-sig') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';', dialect=csv.excel)
        for row in csv_reader:
            add_label_to_labelcount(row[0],ground_truth,times_to_add=int(row[1]))
    return ground_truth


sum_ground_truth = {}
sum_annotations = {}

for folder in input_folders:
    images = file_utils.get_all_images_in_folder(folder)
    
    for image in images:
        #print("")
        #print(image)
        ground_truth_file = image[:-4] + "_groundtruth.csv"
        annotation_file = image[:-4] + "_annotations.json"
        annotations = count_annotations(annotation_file)
        ground_truth = get_ground_truth(ground_truth_file)
        
        for key,value in annotations.items():
            add_label_to_labelcount(key,sum_annotations,value)
        for key,value in ground_truth.items():
            add_label_to_labelcount(key,sum_ground_truth,value)
    
     
        '''
        for key,value in annotations.items():
            if key in ground_truth:
                value_g = ground_truth[key]
                if value_g != 0 or value != 0:
                    print("   " + key + ": "+ str(value) + " vs. " + str(value_g))
                ground_truth.pop(key)
            else:
                if not value==0:
                    print("   " + key + ": "+ str(value) + " vs. 0")
                
        for key,value in ground_truth.items():
            if value != 0:
                print("   " + key + ": 0 vs. "+ str(value))
    
        '''
    
for key,value in sum_annotations.items():
    if key in sum_ground_truth:
        value_g = sum_ground_truth[key]
        if value_g != 0 or value != 0:
            print("   " + key + ": "+ str(value) + " vs. " + str(value_g))
        sum_ground_truth.pop(key)
    else:
        if not value==0:
            print("   " + key + ": "+ str(value) + " vs. 0")
        
for key,value in sum_ground_truth.items():
    if value != 0:
        print("   " + key + ": 0 vs. "+ str(value))


