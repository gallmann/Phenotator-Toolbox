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
    
    Note that for most options a default value can be set in the constants.py
    file. 
    
    

    """

    pass




@cli.command(short_help='Prepare a folder with annotated images for Training.')
@click.option('--input-folder','-i',default=constants.input_folders,        type=click.Path(),   multiple=True,  help='Input Folder Path (can be multiple)')
@click.option('--test-split', '-t',     default=constants.test_splits, type=click.FloatRange(0, 1),    multiple=True,  help='Float between 0 and 1 indicating what portion should be used for the test set (must be the same number as input folders -> one number for each folder)')
@click.option('--validation-split', '-v',     default=constants.validation_splits, type=click.FloatRange(0, 1),    multiple=True,  help='Float between 0 and 1 indicating what portion should be used for the validation set (must be the same number as input folders -> one number for each folder)')
@click.option('--project-folder', default=constants.train_dir,type=click.Path(), help='This project directory will be filled with various subfolders used during the training or evaluation process.',show_default=True)
@click.option('--tile-size', default=constants.tile_sizes,type=int, multiple=True, help='Tile size to use as tensorflow input (squared tiles). Can be more than one!',show_default=True)
@click.option('--split-mode', default=constants.split_mode, help='Test set / Train set splitting technique. Deterministic mode ensures that an input directory is split the same way if this command is executed multiple times.',show_default=True,type=click.Choice(['random', 'deterministic']))
@click.option('--min-instances', default=constants.min_flowers, type=int, help='Minimum instances of one class to include it in the training', show_default=True)
@click.option('--overlap', default=constants.train_overlap, type=int, help='The image tiles are generated with an overlap to better cover flowers on the edges of the tiles. Define the overlap in pixels with this flag.', show_default=True)
def image_preprocessing(input_folder,test_split,validation_split,project_folder,tile_size,split_mode,min_instances,overlap):
    """
    
    Running this command converts one or multiple input folders containing annotated
    images into a format that is readable for the Tensorflow library. The input folders
    must contain images (jpg, png or tif) and along with each image a json file containing the
    annotations. These json files can either be created with the widely used LabelMe Application
    or with the AnnotationApp available for Android Tablets.
    
    """
    
    import image_preprocessing
    image_preprocessing.convert_annotation_folders(input_folder, test_split,validation_split, project_folder, tile_size, split_mode, min_instances, overlap)
    
    
    
@cli.command(short_help='Train a network.')
@click.option('--project-dir', default=constants.train_dir,type=click.Path(), help='Provide the project folder that was also used for the image-preprocessing command.',show_default=True)
@click.option('--max-steps', default=constants.max_steps,type=int, help='Max Training steps to carry out.',show_default=True)
@click.option('--with-validation', default=constants.with_validation,type=bool, help='If true, the training process is carried out as long as the validation error decreases. If false, the training is carried out until max-steps is reached.',show_default=True)
def train(project_dir, max_steps, with_validation):
    """
    Trains a network. Pressing CTRL+C during the training process interrupts the training.
    Running the train command again will resume the training. If you want to start training
    from the beginning, make sure that the contents of the <path to project-folder>/training folder
    are all deleted.
    """
    
    if with_validation:
        import train_with_validation
        train_with_validation.train_with_validation(project_dir,max_steps)
    else:
        import train
        train.run(project_dir,max_steps)
        

@cli.command(short_help='Export the trained inference graph.')
@click.option('--project-dir', default=constants.train_dir,type=click.Path(), help='Provide the project folder that was also used for the training.',show_default=True)
def export_inference_graph(project_dir):
    """
        Exports the trained network to a format that can then be used to make predictions.
    """
    import my_export_inference_graph
    my_export_inference_graph.run(project_dir)



@cli.command(short_help='Run Prediction.')
@click.option('--project-dir', default=constants.train_dir,type=click.Path(), help='Provide the project folder that was used for the training.',show_default=True)
@click.option('--images-to-predict', default=constants.images_to_predict,type=click.Path(), help='Path to a folder containing images on which the prediction algorithm should be run.',show_default=True)
@click.option('--predictions-folder', default=constants.predictions_folder,type=click.Path(), help='Path to a folder where the prediction results should be saved to.',show_default=True)
@click.option('--tile-size', default=constants.prediction_tile_size,type=int, help='Image Tile Size that should be used as Tensorflow input.',show_default=True)
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
    
    
@cli.command(short_help='Visualize Bounding Boxes.')
@click.argument('input-folder',type=click.Path())
@click.argument('output-folder', type=click.Path())
@click.option('--with-name-info', default=constants.visualize_bounding_boxes_with_name,type=bool, help='If True, the name will be printed on top of each bounding box. If False, only the bounding boxes will be drawn.',show_default=True)
@click.option('--clean-output-folder', default=constants.clean_output_folder,type=bool, help='If True, all contents of the output folder will be deleted before the execution of the command.',show_default=True)
def visualize(input_folder,output_folder,with_name_info,clean_output_folder):
    """
        Draws the bounding boxes on each image in the input folder. The input folder therefore
        needs to contain images (png, jpg or tif) and annotation files (LabelMe json, AnnotationApp 
        json or Tensorflow xml format)
    """
    import visualization
    visualization.draw_bounding_boxes(input_folder,output_folder,with_name_info,clean_output_folder)



@cli.command(short_help='Copy Annotations to geo referenced images.')
@click.argument('annotated-folder',type=click.Path())
@click.argument('to-be-annotated-folder', type=click.Path())
@click.argument('output-folder', type=click.Path())
@click.option('--one-by-one', default=constants.one_by_one,type=bool, help="If True, the annotations will be applied to one image in the 'to-be-annotated-folder' at a time. It will be shown to the user in the LabelMe Application such that the user can check and adjust the copied annotations.",show_default=True)
def copy_annotations(annotated_folder, to_be_annotated_folder, output_folder,one_by_one):
    """
        If you have one folder with annotated images that are geo referenced, with this command you can
        copy the annotations from that folder to other images that are also georeferenced. 
        
        An image can be georeferenced in the standard geotif format in any coordinate system. Alternatively,
        it can be a normal png or jpg image with a json file called imagename_geoinfo.json in
        the same folder. The imagename_geoinfo.json file must contain the
        following information in the WGS84 coordinate system:
        {"lr_lon": a, "lr_lat": b, "ul_lon": c, "ul_lat": d}
        
        With CTRL+C the execution of the script can be interupted. In the one-by-one mode, the execution
        can later be continued.
    """
    
    import copy_annotations_to_images
    
    if one_by_one:
        copy_annotations_to_images.copy_annotations_to_images_one_by_one(annotated_folder, to_be_annotated_folder, output_folder)
    else:
        copy_annotations_to_images.copy_annotations_to_images(annotated_folder, to_be_annotated_folder, output_folder)


@cli.command(short_help='Annotate images or adjust existing annotations.')
@click.argument('input-folder', type=click.Path())
@click.option('--roi-strip', default=False,type=bool, help="",show_default=True)
def annotate(input_folder,roi_strip):
    """
        Running this command will open the LabelMe Application with which all images
        in the input-folder can be annotated. If the images in the input folder are already
        annotated, these annotations can be viewed adjusted.
        
        If the roi-strip flag is set to True, the user can select Regions of Interest (RoI)
        in the images. To do so, the user has to draw one or multiple polygons around the
        region(s) of interest and label them 'roi'. After the user has labelled all images
        accordingly, only the Regions of Interest (RoI) are
        kept in the images. The rest of the pixels are overriden with black.
        
    """
    
    import select_region
    select_region.check_annotations(input_folder,roi_strip)
    


if __name__ == '__main__':
    cli(prog_name='python cli.py')
