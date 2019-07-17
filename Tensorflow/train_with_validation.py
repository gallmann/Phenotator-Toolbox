# -*- coding: utf-8 -*-
"""
Created on Sun Jul 14 20:42:09 2019

@author: johan
"""


print("Loading libraries...")
from shutil import copyfile
import train
import my_export_inference_graph
import custom_evaluations
import predict
import os
from utils import constants



def train_with_validation(project_dir,max_steps):
    images_folder = os.path.join(project_dir,"images")
    validation_images_folder = os.path.join(images_folder,"validation_full_size")
    validation_folder = os.path.join(project_dir,"validation")
    evaluation_folder = os.path.join(validation_folder,"evaluation")
    training_folder = os.path.join(project_dir,"training")
    checkpoints_folder = os.path.join(training_folder,"checkpoints")
    os.makedirs(checkpoints_folder,exist_ok=True)
    precision_recall_file = os.path.join(checkpoints_folder,"precision_recall_evolution.txt")
    
    precision_recall_list = get_precision_recall_list_from_file(precision_recall_file)
    (best_index,best_configuration) = get_best_configuration_from_precision_recall_list(precision_recall_list)
    
    current_step = get_max_checkpoint(checkpoints_folder)
    
    for num_steps in range(max(2500,current_step+2500),max_steps,2500):
        try:
            print("Train 5000 steps...")
            train.run(project_dir,num_steps)
        except:
            print("An exception occured in the train script. Continue anyways")
        
        print("Export inference graph...")
        
        copy_checkpoint_to_folder(num_steps,training_folder, checkpoints_folder)

        my_export_inference_graph.run(project_dir,look_in_checkpoints_dir=False)
        
        predict.predict(project_dir,validation_images_folder,validation_folder,constants.tile_size,constants.prediction_overlap)
        
        stats = custom_evaluations.evaluate(validation_folder, evaluation_folder)
        (precision,recall,mAP) = get_precision_and_recall_from_stat(stats)
        precision_recall_list.append((precision,recall,mAP))
        
        with open(precision_recall_file, "a") as text_file:
            text_file.write("step " + str(num_steps) + ": " + str((precision,recall,mAP)) + "\n")
            
        if precision+recall-abs(precision-recall) > best_configuration:
            best_configuration = precision+recall-abs(precision-recall)
            best_index = len(precision_recall_list)-1
        else:
            if len(precision_recall_list)-1-best_index >=4:
                break
   
    

    

def get_best_configuration_from_precision_recall_list(precision_recall_list):
    best_configuration = 0
    best_index = 0
        
    for index,(precision,recall,mAP) in enumerate(precision_recall_list):
        if(precision+recall-abs(precision-recall) > best_configuration):
            best_configuration = precision+recall-abs(precision-recall)
            best_index = index
    return (best_index,best_configuration)


def get_precision_recall_list_from_file(file_path):
    
    precision_recall_list = [(0,0,0),(0,0,0),(0,0,0)]
    
    
    if os.path.isfile(file_path):
        #precision recall evolution exists
        with open(file_path) as f:
            lines = f.readlines()
            
        for line in lines:
            precision = float(line[line.find(": (")+len(": ("):line.find(",")])
            recall = float(line[line.find(",")+len(","):line.rfind(",")])
            mAP = float(line[line.rfind(",")+len(","):line.rfind(")")])
            precision_recall_list.append((precision,recall,mAP))
        
    return precision_recall_list
        
def get_max_checkpoint(checkpoints_folder):
    largest_number = -1                        
    for file in os.listdir(checkpoints_folder):
        if file.endswith(".index") and file.startswith("model.ckpt-"):
            start = file.index("model.ckpt-") + len("model.ckpt-")
            end = file.index( ".index", start )
            curr_number = int(file[start:end])
            if(curr_number>largest_number):
                largest_number = curr_number
    return largest_number


def copy_checkpoint_to_folder(checkpoint,src_dir,dst_dir):
    for file in os.listdir(src_dir):
        if "model.ckpt-" + str(checkpoint) in file:
            copyfile(os.path.join(src_dir, file), os.path.join(dst_dir,file))


def get_precision_and_recall_from_stat(stat):
    print("Evaluation_stats:")
    n = stat["tp"] + stat["fn"]
    print("Overall" + " (n=" + str(n) + "):")
    if float(stat["fp"]+stat["tp"]) == 0:
        precision = "0"
    else:
        precision = float(stat["tp"]) / float(stat["fp"]+stat["tp"])
    if float(stat["tp"] + stat["fn"]) == 0:
        recall = "0"
    else:
        recall = float(stat["tp"]) / float(stat["tp"] + stat["fn"])

    print("   precision: " + str(precision))
    print("   recall: " + str(recall))
    print("   TP: " + str(stat["tp"]) + " FP: " + str(stat["fp"]) + " FN: " + str(stat["fn"]))
    
    return (float(precision),float(recall))


if __name__ == '__main__':
    project_dir = "C:/Users/johan/Desktop/output"
    train_with_validation(project_dir,constants.max_steps)
