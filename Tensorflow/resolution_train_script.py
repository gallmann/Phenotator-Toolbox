# -*- coding: utf-8 -*-
"""
Created on Wed Jul 24 20:38:24 2019

@author: gallmanj
"""

import image_resizer
import image_preprocessing
from utils import constants
import train_with_validation

input_folder_suffixes = ["May_23/MaskedAnnotationData",
                 "June_06/MaskedAnnotationData",
                 "June_14/MaskedAnnotatedSquaresOnSingleImages",
                 "June_14/MaskedAnnotatedSingleOrthoPhotos",
                 "June_14/MaskedAnnotatedAdditionalRegions",
                 "June_14/MaskedAnnotationData",
                 "June_29/MaskedAnnotationData",
                 "July_03/MaskedAnnotatedSingleOrthoPhotos",
                 "July_03/MaskedAnnotationData"
                 ]

resolutions = [0.8,0.5,0.3,0.2,0.1,0.05]
folders = [30,31,32,33,34,35]

for i in range(len(resolutions)):
    resolution = resolutions[i]
    folder_prefix = "G:/Johannes/Experiments/0" + str(folders[i]) + "/inputs/"
    project_folder = "G:/Johannes/Experiments/0" + str(folders[i]) + "/output/"
    
    input_folders = []
    
    for folder_suffix in input_folder_suffixes:
        full_folder = folder_prefix + folder_suffix
        input_folders.append(full_folder)
    for input_folder in input_folders:
        image_resizer.change_resolution(input_folder,input_folder,resolution,keep_image_size=True)
    
    image_preprocessing.convert_annotation_folders(input_folders, constants.test_splits,constants.validation_splits, project_folder, constants.train_tile_sizes, "deterministic", constants.min_flowers, constants.train_overlap,constants.pretrained_model_link)
    train_with_validation.train_with_validation(project_folder,constants.max_steps,constants.model_selection_criterion)
