# -*- coding: utf-8 -*-
"""
Created on Wed Jul 10 16:04:58 2019

@author: johan
"""

import click
from utils import constants

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

@click.group(context_settings=CONTEXT_SETTINGS)
def cli():
    """
    Below there is a list of commands each with a very brief description.
    Running 'python cli.py COMMAND -h' provides more detailed information about
    this command and all possible flags that can be set.
    
    Note that for each option a default value can be set in the constants.py
    file. 
    

    """

    pass




@cli.command(short_help='Prepare a folder with annotated images for Training.')
@click.option('--input-folder','-i',default=constants.input_folders,        type=click.Path(),   multiple=True,  help='Input Folder Path (can be multiple)')
@click.option('--split', '-s',     default=constants.input_folders_splits, type=click.FloatRange(0, 1),    multiple=True,  help='Float between 0 and 1 indicating what portion should be used for the test set (must be the same number as input folders -> one number for each folder)')
@click.option('--project-folder', default=constants.train_dir,type=click.Path(), help='This project directory will be filled with various subfolders used during the training or evaluation process.',show_default=True)
@click.option('--tile-size', default=constants.tile_size,type=int, help='Tile size to use as tensorflow input (squared tiles)',show_default=True)
@click.option('--split-mode', default=constants.split_mode, help='Test set / Train set splitting technique. Deterministic mode ensures that an input directory is split the same way if this command is executed multiple times.',show_default=True,type=click.Choice(['random', 'deterministic']))
@click.option('--min-instances', default=constants.min_flowers, type=int, help='Minimum instances of one class to include it in the training', show_default=True)

def image_preprocessing(input_folder,split,project_folder,tile_size,split_mode,min_instances):
    """
    
    Running this command converts one or multiple input folders containing annotated
    images into a format that is readable for the Tensorflow library. The input folders
    must contain images (jpg, png or tif) and along with each image a json file containing the
    annotations. These json files can either be created with the widely used LabelMe Application
    or with the AnnotationApp available for Android Tablets.
    
    """
    
    import image_preprocessing
    image_preprocessing.convert_annotation_folders(input_folder, split, project_folder, tile_size, split_mode, min_instances)
    
    
    
@cli.command(short_help='Train a network.')
@click.option('--project-dir', default=constants.train_dir,type=click.Path(), help='Provide the project folder that was also used for the image-preprocessing command.',show_default=True)
def train(project_dir):
    """
    Trains a network. Pressing CTRL+C during the training process interrupts the training.
    Running the train command again will resume the training. If the contents of the <path to project-folder>/training folder
    are deleted, the training will start from the beginning.
    
    """
    import train
    train.run(project_dir)
        

@cli.command(short_help='Export the trained inference graph.')
@click.option('--project-dir', default=constants.train_dir,type=click.Path(), help='Provide the project folder that was also used for the training.',show_default=True)
def export_inference_graph(project_dir):
    """
        Exports the trained network to a format that can then be used to make predictions.
    """
    import export_inference_graph
    export_inference_graph.run(project_dir)
        


@cli.command(short_help='Run Prediction.')
@click.option('--project-dir', default=constants.train_dir,type=click.Path(), help='Provide the project folder that was used for the training.',show_default=True)
@click.option('--images-to-predict', default=constants.images_to_predict,type=click.Path(), help='Path to a folder containing images on which the prediction algorithm should be run.',show_default=True)
@click.option('--predictions-folder', default=constants.predictions_folder,type=click.Path(), help='Path to a folder where the prediction results should be saved to.',show_default=True)
@click.option('--tile-size', default=constants.tile_size,type=int, help='Image Tile Size that should be used as Tensorflow input.',show_default=True)
@click.option('--prediction-overlap', default=constants.prediction_overlap,type=int, help='The image tiles are predicted with an overlap to improve the results on the tile edges. Define the overlap in pixels with this flag.',show_default=True)
def predict(project_dir,images_to_predict,predictions_folder,tile_size,prediction_overlap):
    """
        Runs the prediction algorithm on images (png, jpg and tif) of any size.
    """
    import predict
    predict.predict(project_dir,images_to_predict,predictions_folder,tile_size,prediction_overlap)



@cli.command(short_help='Evaluate Predictions.')
@click.option('--predictions-folder', default=constants.predictions_folder,type=click.Path(), help='The folder where the predictions were saved to.',show_default=True)
@click.option('--evaluations-folder', default=constants.prediction_evaluation_folder,type=click.Path(), help='The folder where the evaluation results should be saved to.',show_default=True)
@click.option('--iou-threshold', default=constants.iou_threshold,type=click.FloatRange(0, 1), help='Defines what is the minimum IoU (Intersection over Union) overlap to count a prediction as a True Positive.',show_default=True)
def evaluate(predictions_folder,evaluations_folder,iou_threshold):
    """
        If the images on which the predictions algorithm was run on had groundtruth information,
        this command will evaluate the performance of the prediction algorithm on these images.
        (Evaluation of Precision and Recall)
    """
    import custom_evaluations
    custom_evaluations.evaluate(predictions_folder, evaluations_folder, iou_threshold)
    
    

    
if __name__ == '__main__':
    cli(prog_name='python cli.py')
