# -*- coding: utf-8 -*-
"""
Created on Fri Jun  7 14:17:19 2019

@author: gallmanj
"""



'''MOST IMPORTANT SETTINGS'''
project_folder = "G:/Johannes/EarDetection/working_dir"
pretrained_model_link = "http://download.tensorflow.org/models/object_detection/faster_rcnn_resnet101_coco_2018_01_28.tar.gz"


'''image-preprocessing command parameters'''
input_folders = ["G:/Johannes/ObjectDetectionDemo/src_images"]

test_splits = [0.1]

validation_splits = [0.1]

split_mode = "random"
train_tile_sizes =[450]
train_overlap = 50
min_flowers = 5 #minimum amount of flower instances to include species in training
#All images will be resized to tensorflow_tile_size x tensorflow_tile_size tiles
#choose a smaller tensorflow_tile_size if your gpu is not powerful enough to handle
#900 x 900 pixel tiles
tensorflow_tile_size = 900 
data_augmentation_enabled = True

'''train command parameters'''
max_steps = 130000
with_validation = True
model_selection_criterion = "f1" #also used for export-inference-graph command

'''predict command parameters'''
images_to_predict = project_folder + "/images/test"
predictions_folder = project_folder + "/predictions"
prediction_tile_size = 1024
prediction_overlap = 50
min_confidence_score = 0.2 #also used by evaluate command
visualize_predictions = True
visualize_groundtruth = False
visualize_name = False
visualize_score = False
max_iou = 0.3


'''evaluate cmomand parameters'''
prediction_evaluation_folder = predictions_folder + "/evaluations"
iou_threshold = 0.3


'''visualization command parameters'''
visualize_bounding_boxes_with_name = True
clean_output_folder = True

'''copy-annotations command parameters'''
one_by_one = True

'''prepare-for-tablet command parameters'''
prepare_for_tablet_tile_size = 256


'''generate-heatmap command parameters'''
heatmap_width=100
max_val = None
classes = None
overlay = True
output_image_width = 1000



'''Set the radius (not diameter) of each flower species'''
flower_bounding_box_size = {
        
'Loewenzahn' : 6,
'Margarite'   : 4,
'achillea millefolium': 20,
'anthyllis vulneraria'   : 16,
'agrimonia eupatoria': 15,
'carum carvi'   : 22,
'centaurea jacea': 14,
'cerastium caespitosum'   : 7,
'crepis biennis'   : 17,
'daucus carota': 23,
'galium mollugo'   : 4,
'knautia arvensis'   : 17,
'medicago lupulina'   : 4,
'leucanthemum vulgare'   : 20,
'lotus corniculatus'   : 8,
'lychnis flos cuculi'   : 15,
'myosotis arvensis'   : 6,
'onobrychis viciifolia'   : 10,
'picris hieracioides': 13,
'plantago lanceolata'   : 8,
'plantago major'   : 11,
'prunella vulgaris': 10,
'ranunculus acris'   : 11,
'ranunculus bulbosus'   : 11,
'ranunculus friesianus'   : 11,
'ranunculus'   : 11,
'salvia pratensis'   : 15,
'tragopogon pratensis'   : 17,
'trifolium pratense'   : 10,
'veronica chamaedris'   : 4,
'vicia sativa'   : 6,
'vicia sepium'   : 4,
'dianthus carthusianorum': 11,
'lathyrus pratensis' : 8,
'leontodon hispidus' : 18,
'rhinanthus alectorolophus': 20,
'trifolium repens': 10,
'orchis sp': 20
}


flower_groups = {
        
    "ranunculus": ["ranunculus bulbosus", "ranunculus friesianus", "ranunculus acris"],
    "lotus corniculatus": ["lotus corniculatus", "lathyrus pratensis"],
    #"galium mollugo": ["galium mollugo","carum carvi", "achillea millefolium", "daucus carota"],
    "galium mollugo": ["galium mollugo","carum carvi", "achillea millefolium", "daucus carota"],
    "crepis biennis": ["crepis biennis", "leontodon hispidus", "tragopogon pratensis", "picris hieracioides"],
    "centaurea jacea": ["centaurea jacea", "lychnis flos cuculi"]   
    #"centaurea jacea": ["lychnis flos cuculi"]             
}



