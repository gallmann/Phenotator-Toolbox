# -*- coding: utf-8 -*-
"""
Created on Tue Jul 30 23:23:33 2019

@author: gallmanj
"""

import os
from utils import file_utils
from utils import constants
from utils import flower_info


def search_for_term_in_all_files(root_dir,keyword):
    
    for root, dirs, files in os.walk(root_dir, onerror=None):  # walk the root dir
        for filename in files:  # iterate over the files in the current dir
            file_path = os.path.join(root, filename)  # build the file path
            try:
                with open(file_path, "rb") as f:  # open the file for reading
                    # read the file line by line
                    for line in f:  # use: for i, line in enumerate(f) if you need line numbers
                        try:
                            line = line.decode("utf-8")  # try to decode the contents to utf-8
                        except ValueError:  # decoding failed, skip the line
                            continue
                        if keyword in line:  # if the keyword exists on the current line...
                            print(file_path)  # print the file path
                            break  # no need to iterate over the rest of the file
            except (IOError, OSError):  # ignore read and permission errors
                pass


def count_all_annotations_in_folder(folder):
    
    counter = 0
    all_images = file_utils.get_all_images_in_folder(folder)
    for image_path in all_images:
        annotations = file_utils.get_annotations(image_path)
        for annotation in annotations:
            if annotation["name"] != "roi":
                counter+=1
    print(counter)
    return counter
        
             
def get_all_annotations_in_folders(folders):
    annotations = []
    for folder in folders:
        all_images = file_utils.get_all_images_in_folder(folder)
        for image_path in all_images:
            curr_annotations = file_utils.get_annotations(image_path)
            for annotation in curr_annotations:
                annotations.append(flower_info.clean_string(annotation["name"]))
    from collections import Counter
    return(Counter(annotations))
    
    
    
    
    
    
    
    
all_counter = get_all_annotations_in_folders(constants.input_folders)
test_counter = get_all_annotations_in_folders(["E:/025/output/images/test_full_size"])
validation_counter = get_all_annotations_in_folders(["E:/025/output/images/validation_full_size"])
all_names = sorted(all_counter)
for x in all_names:
    all_i = all_counter[x]
    test_i = test_counter[x]
    validation_i = validation_counter[x]
    
    print(x + ": ")
    print(str(all_i-test_i-validation_i) + " & ")
    #print(test_i)
    



'''
for folder in constants.input_folders:
    print(folder)
    count_all_annotations_in_folder(folder)
'''