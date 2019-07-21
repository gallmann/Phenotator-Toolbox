# -*- coding: utf-8 -*-
"""
Created on Sun Jul 14 20:42:09 2019

@author: johan
"""


from shutil import copyfile
import train
import my_export_inference_graph
import custom_evaluations
import predict
import os
from utils import constants



def train_with_validation(project_dir,max_steps,stopping_criterion="f1"):
    """
    Trains a network using a validation set to decide when to stop training. 
    The prediction and evaluation algorithms are run on the validation set every
    2500 steps.

    Parameters:
        project_dir (str): The project directory used during the image-preprocessing
            command.
        max_steps (int): Should the stopping_criterion not trigger earlier, the network
            is trainied at most max_steps steps.
        stopping_criterion (str): Either 'f1' or 'mAP'. The network is trained as long the
            respective score improves. The training is not stopped immediately but only after
            10000 additional steps to check if the decrease in score was just local.
    
    Returns:
        None
    """

    images_folder = os.path.join(project_dir,"images")
    validation_images_folder = os.path.join(images_folder,"validation_full_size")
    validation_folder = os.path.join(project_dir,"validation")
    evaluation_folder = os.path.join(validation_folder,"evaluation")
    training_folder = os.path.join(project_dir,"training")
    checkpoints_folder = os.path.join(training_folder,"checkpoints")
    os.makedirs(checkpoints_folder,exist_ok=True)
    precision_recall_file = os.path.join(checkpoints_folder,"precision_recall_evolution.txt")
    
    precision_recall_list = get_precision_recall_list_from_file(precision_recall_file)
    (best_index,best_configuration) = get_best_configuration_from_precision_recall_list(precision_recall_list,stopping_criterion)
    
    current_step = get_max_checkpoint(checkpoints_folder)
    
    for num_steps in range(max(2500,current_step+2500),max_steps,2500):
        try:
            print("Train 2500 steps...")
            train.run(project_dir,num_steps)
        except:
            print("An exception occured in the train script. Continue anyways")
        
        print("Export inference graph...")
        
        copy_checkpoint_to_folder(num_steps,training_folder, checkpoints_folder)

        my_export_inference_graph.run(project_dir,look_in_checkpoints_dir=False)
        
        predict.predict(project_dir,validation_images_folder,validation_folder,constants.prediction_tile_size,constants.prediction_overlap)
        
        stats = custom_evaluations.evaluate(project_dir, validation_folder, evaluation_folder)
        (precision,recall,mAP,f1) = get_precision_and_recall_from_stat(stats)
        precision_recall_list.append((precision,recall,mAP,f1))
        
        with open(precision_recall_file, "a") as text_file:
            text_file.write("step " + str(num_steps) + "; precision: " + str(precision) + " recall: " + str(recall) + " mAP: " + str(mAP) + " f1: " + str(f1) + "\n")
        
        relevant_metric = f1
        if stopping_criterion == "mAP":
            relevant_metric = mAP
            
        if relevant_metric > best_configuration:
            best_configuration = relevant_metric
            best_index = len(precision_recall_list)-1
        else:
            if len(precision_recall_list)-1-best_index >=20:
                break
   
    

    

def get_best_configuration_from_precision_recall_list(precision_recall_list, metric_to_use="f1"):
    """
    Helper function returning the index and the score of the best configuration
    from a list with precision/recall/mAP/f1 scores.
    
    Parameters:
        precision_recall_list (list): List of tuples of the format (precision,recall,mAP,f1).
        metric_to_use (str): Either 'f1' or 'mAP'.
    Returns:
        tuple: (best_index,score_of_best_configuration)
    """

    best_configuration = 0
    best_index = 0
        
    for index,(precision,recall,mAP,f1) in enumerate(precision_recall_list):
        relevant_metric = f1
        if metric_to_use == "mAP":
            relevant_metric = mAP
        if relevant_metric > best_configuration:
            best_configuration = relevant_metric
            best_index = index
    return (best_index,best_configuration)


def get_precision_recall_list_from_file(file_path):
    """
    During the training the precision/recall/mAP/f1 scores are saved to a file every
    2500 steps. Should the user stop training. This function reads the values once the 
    user wants to resume the training.
    
    Parameters:
        file_path (str): path to the file containing the score information
    Returns:
        list: list of all scores of each configuration
    """

    precision_recall_list = []
    
    
    if os.path.isfile(file_path):
        #precision recall evolution exists
        with open(file_path) as f:
            lines = f.readlines()
            
        for line in lines:
            precision = float(line[line.find("; precision: ")+len("; precision: "):line.rfind(" recall: ")])
            recall = float(line[line.find(" recall: ")+len(" recall: "):line.rfind(" mAP: ")])
            mAP = float(line[line.rfind(" mAP: ")+len(" mAP: "):line.rfind(" f1: ")])
            f1 = 2 * (precision*recall)/(precision+recall)
            precision_recall_list.append((precision,recall,mAP,f1))
        
    return precision_recall_list
        
def get_max_checkpoint(checkpoints_folder):
    """
    Finds the most advanced training checkpoint saved by tensorflow within a folder
    
    Parameters:
        checkpoints_folder (str): path to the folder containing the checkpoints
    Returns:
        int: the unique identifier number of the checkpoint file
    """

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
    """
    Copies the checkpoint files from one folder to another
    
    Parameters:
        checkpoint (int): unique identifier number for the checkpoint
        src_dir (str): source folder containing the checkpoint files
        dst_dir (str): destination folder where the checkpoint files should be copied to
        
    Returns:
        None
    """

    for file in os.listdir(src_dir):
        if "model.ckpt-" + str(checkpoint) in file:
            copyfile(os.path.join(src_dir, file), os.path.join(dst_dir,file))


def get_precision_and_recall_from_stat(stat):
    """
    Extracts the precision/recall/mAP/f1 scores from the stat dict that is returned
    by the evaluation script.
    
    Parameters:
        stat (dict): dict returned by the evaluation script
        
    Returns:
        tuple: (precision,recall,mAP,f1)
    """

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
    
    f1 = 0
    if recall != "0" and precision != "0" and ((recall >0) or (precision > 0)):
        f1 = 2 * (precision*recall)/(precision+recall)

    return (float(precision),float(recall),stat["mAP"],f1)


if __name__ == '__main__':
    project_dir = "C:/Users/johan/Desktop/output"
    train_with_validation(project_dir,constants.max_steps)
