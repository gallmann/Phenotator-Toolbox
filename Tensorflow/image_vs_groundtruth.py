# -*- coding: utf-8 -*-
"""
Created on Wed Jun 12 12:47:43 2019

@author: johan

This script compares the groundtruth annotations to the groundtruth hand counted
results.
"""

import csv
from utils import file_utils
from utils import flower_info
from utils import constants



input_folders = ["G:/Johannes/Data/June_14/MaskedAnnotatedSquaresOnSingleImages"]


#small helper function to keep track of how many flowers of each species have been annotated 
def add_label_to_labelcount(flower_name, label_count, times_to_add=1):
    if times_to_add != 0:
        flower_name = flower_info.clean_string(flower_name)
        if(label_count.get(flower_name) == None):
            label_count[flower_name] = times_to_add
        else:
            label_count[flower_name] = label_count[flower_name] + times_to_add

#counts the annotations within the annotations_file and returns a map containing the counts
def count_annotations(annotations_file):
    
    labels = {}
    annotation_data = file_utils.read_json_file(annotations_file)
    if(not annotation_data):
        return []
    annotations = annotation_data["annotatedFlowers"]
    
    for flower in annotations:
        add_label_to_labelcount(flower["name"], labels)
    
    return labels

#counts the annotations within the groud_truth_file and returns a map containing the counts
def get_ground_truth(ground_truth_file):
    ground_truth = {}
    with open(ground_truth_file,encoding='utf-8-sig') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';', dialect=csv.excel)
        for row in csv_reader:
            add_label_to_labelcount(row[0],ground_truth,times_to_add=int(row[1]))
    return ground_truth


sum_ground_truth = {}
sum_annotations = {}

#loop through all folders inside the input_folders list and count the annotations
#and ground truths in each of them and add the to sum_ground_truth and sum_annotations
for folder in input_folders:
    images = file_utils.get_all_images_in_folder(folder)
    
    for image in images:
        ground_truth_file = image[:-4] + "_groundtruth.csv"
        annotation_file = image[:-4] + "_annotations.json"
        annotations = count_annotations(annotation_file)
        ground_truth = get_ground_truth(ground_truth_file)
        
        for key,value in annotations.items():
            add_label_to_labelcount(key,sum_annotations,value)
        for key,value in ground_truth.items():
            add_label_to_labelcount(key,sum_ground_truth,value)
    
     
#print the summed up statistics to the console in a format that can directly
#be imported into a latex table


all_items = sorted(sum_annotations.items(), key=lambda k: k[0]) 


for key,value in all_items:
    if key in sum_ground_truth:
        value_g = sum_ground_truth[key]
        if value_g != 0 or value != 0:
            print(key + "  &  " + str(value) + "  &  " + str(int(value_g*56.1358707695)) + "  \\\\ ")
            #print("   " + key + ": "+ str(value) + " vs. " + str(value_g))
        sum_ground_truth.pop(key)
    else:
        if not value==0:
            print("   " + key + ": "+ str(value) + " vs. 0")
        
for key,value in sum_ground_truth.items():
    if value != 0:
        print("   " + key + ": 0 vs. "+ str(value))


