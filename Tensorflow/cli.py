# -*- coding: utf-8 -*-
"""
Created on Wed Jul 10 16:04:58 2019

@author: johan
"""

import click
from utils import constants
import os
import sys
sys.path.append("slim")


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
@click.option('--project-folder', default=constants.project_folder,type=click.Path(), help='This project directory will be filled with various subfolders used during the training or evaluation process.',show_default=True)
@click.option('--tile-size', default=constants.train_tile_sizes,type=int, multiple=True, help='Tile size to use as tensorflow input (squared tiles). Can be more than one!',show_default=True)
@click.option('--split-mode', default=constants.split_mode, help='Test set / Train set splitting technique. Deterministic mode ensures that an input directory is split the same way if this command is executed multiple times.',show_default=True,type=click.Choice(['random', 'deterministic']))
@click.option('--min-instances', default=constants.min_flowers, type=int, help='Minimum instances of one class to include it in the training', show_default=True)
@click.option('--overlap', default=constants.train_overlap, type=int, help='The image tiles are generated with an overlap to better cover flowers on the edges of the tiles. Define the overlap in pixels with this flag.', show_default=True)
@click.option('--model-link', default=constants.pretrained_model_link, type=str, help='The link from where the pretrained model can be downloaded.', show_default=True)
def image_preprocessing(input_folder,test_split,validation_split,project_folder,tile_size,split_mode,min_instances,overlap,model_link):
    """
    Running this command converts one or multiple input folders containing annotated
    images into a format that is readable for the Tensorflow library. The input folders
    must contain images (jpg, png or tif) and along with each image a json file containing the
    annotations. These json files can either be created with the widely used LabelMe Application
    or with the AnnotationApp available for Android Tablets.
    
    """
    folders_to_check = [project_folder]
    for f in input_folder:
        folders_to_check.append(f)
    if check_inputs(folders=folders_to_check):
        import image_preprocessing
        image_preprocessing.convert_annotation_folders(input_folder, test_split,validation_split, project_folder, tile_size, split_mode, min_instances, overlap,model_link)
    
    
    
@cli.command(short_help='Train a network.')
@click.option('--project-dir', default=constants.project_folder,type=click.Path(), help='Provide the project folder that was also used for the image-preprocessing command.',show_default=True)
@click.option('--max-steps', default=constants.max_steps,type=int, help='Max Training steps to carry out.',show_default=True)
@click.option('--with-validation', default=constants.with_validation,type=bool, help='If true, the training process is carried out as long as the validation error decreases. If false, the training is carried out until max-steps is reached.',show_default=True)
@click.option('--stopping-criterion', default=constants.model_selection_criterion,type=click.Choice(['mAP', 'f1']), help="If the train command was executed with the '--with-validation True' flag, the training is stopped once either the mAP or the f1 score stop improving.",show_default=True)
def train(project_dir, max_steps, with_validation,stopping_criterion):
    """
    Trains a network. Pressing CTRL+C during the training process interrupts the training.
    Running the train command again will resume the training. If you want to start training
    from the beginning, make sure that the contents of the <path to project-folder>/training folder
    are all deleted.
    """
    if check_inputs(folders=[project_dir]):
        if with_validation:
            import train_with_validation
            train_with_validation.train_with_validation(project_dir,max_steps,stopping_criterion)
        else:
            import train
            train.run(project_dir,max_steps)
        

@cli.command(short_help='Export the trained inference graph.')
@click.option('--project-dir', default=constants.project_folder,type=click.Path(), help='Provide the project folder that was also used for the training.',show_default=True)
@click.option('--model-selection-criterion', default=constants.model_selection_criterion,type=click.Choice(['mAP', 'f1']), help="If the train command was executed with the '--with-validation True' flag, the model with the best performance on the validation set is exported (in terms of either mAP or f1 score).",show_default=True)
@click.option('--checkpoint', default=None,type=int, help="",show_default=True)
def export_inference_graph(project_dir,model_selection_criterion,checkpoint):
    """
        Exports the trained network to a format that can then be used to make predictions.
    """
    if check_inputs(folders=[project_dir]):
        import my_export_inference_graph
        my_export_inference_graph.run(project_dir,True,model_selection_criterion,checkpoint)



@cli.command(short_help='Run Prediction.')
@click.option('--project-dir', default=constants.project_folder,type=click.Path(), help='Provide the project folder that was used for the training.',show_default=True)
@click.option('--images-to-predict', default=constants.images_to_predict,type=click.Path(), help='Path to a folder containing images on which the prediction algorithm should be run.',show_default=True)
@click.option('--predictions-folder', default=constants.predictions_folder,type=click.Path(), help='Path to a folder where the prediction results should be saved to.',show_default=True)
@click.option('--tile-size', default=constants.prediction_tile_size,type=int, help='Image Tile Size that should be used as Tensorflow input.',show_default=True)
@click.option('--prediction-overlap', default=constants.prediction_overlap,type=int, help='The image tiles are predicted with an overlap to improve the results on the tile edges. Define the overlap in pixels with this flag.',show_default=True)
@click.option('--min-score', default=constants.min_confidence_score,type=float, help='Float between 0 and 1 indicating the minimum confidence a prediction must have to be considered.',show_default=True)
@click.option('--visualize-predictions', default=constants.visualize_predictions,type=bool, help='If True, the prediction bounding boxes are painted onto copies of the input images and are saved to the predictions-folder.',show_default=True)
@click.option('--visualize-groundtruth', default=constants.visualize_groundtruth,type=bool, help='If True, the groundtruth bounding boxes are painted onto copies of the input images and are saved to the predictions-folder.',show_default=True)
@click.option('--visualize-score', default=constants.visualize_score,type=bool, help='If true, the score is printed above each bounding box.',show_default=True)
@click.option('--visualize-name', default=constants.visualize_name,type=bool, help='If true, the class name is printed above each bounding box.',show_default=True)
@click.option('--max-iou', default=constants.max_iou,type=float, help='Float between 0 and 1 indicating the maximal iou for the non maximum suppression algorithm. For all predictions with an iou greater than max-iou, only the one with the better score is kept.',show_default=True)
def predict(project_dir,images_to_predict,predictions_folder,tile_size,prediction_overlap,min_score, visualize_predictions,visualize_groundtruth,visualize_score,visualize_name,max_iou):
    """
        Runs the prediction algorithm on images (png, jpg and tif) of any size.
    """
    if check_inputs(folders=[project_dir,images_to_predict,predictions_folder]):
        import predict
        predict.predict(project_dir,images_to_predict,predictions_folder,tile_size,prediction_overlap,min_score,visualize_predictions,visualize_groundtruth,visualize_score,visualize_name,max_iou)
    


@cli.command(short_help='Evaluate Predictions.')
@click.option('--project-dir', default=constants.project_folder,type=click.Path(), help='Provide the project folder that was used for the predictions.',show_default=True)
@click.option('--predictions-folder', default=constants.predictions_folder,type=click.Path(), help='The folder where the predictions were saved to.',show_default=True)
@click.option('--evaluations-folder', default=constants.prediction_evaluation_folder,type=click.Path(), help='The folder where the evaluation results should be saved to.',show_default=True)
@click.option('--iou-threshold', default=constants.iou_threshold,type=click.FloatRange(0, 1), help='Defines what is the minimum IoU (Intersection over Union) overlap to count a prediction as a True Positive.',show_default=True)
@click.option('--generate-visualizations', default=False,type=bool, help='If True, the erroneous predictions will be printed onto the images and saved to the evaluations-folder',show_default=True)
@click.option('--print-confusion-matrix', default=False,type=bool, help='If True, the confusion matrix will be printed to the console in latex table format.',show_default=True)
@click.option('--min-score', default=constants.min_confidence_score,type=float, help='The minimum score a prediction must have to be included in the evaluation',show_default=True)
@click.option('--visualize-info', default=False,type=bool, help='If True, in addition to the bounding boxes, info about the mispredictions is painted above the boxes.',show_default=True)
def evaluate(project_dir,predictions_folder,evaluations_folder,iou_threshold,generate_visualizations,print_confusion_matrix,min_score,visualize_info):
    """
        If the images on which the predictions algorithm was run on had groundtruth information,
        this command will evaluate the performance of the prediction algorithm on these images.
        (Evaluation of Precision and Recall)
    """
    if check_inputs(folders=[predictions_folder,evaluations_folder]):
        import custom_evaluations
        custom_evaluations.evaluate(project_dir,predictions_folder, evaluations_folder, iou_threshold,generate_visualizations,print_confusion_matrix,min_score,visualize_info)
    
    
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
    if check_inputs(folders=[input_folder,output_folder,output_folder]):
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
    if check_inputs(folders=[annotated_folder,to_be_annotated_folder,output_folder]):

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
    if check_inputs(folders=[input_folder]):
        import select_region
        select_region.check_annotations(input_folder,roi_strip)
    

@cli.command(short_help='Prepare an image for the Android Annotation App.')
@click.argument('input-image', type=click.Path())
@click.argument('output_folder', type=click.Path())
@click.option('--tile-size', default=constants.prepare_for_tablet_tile_size, type=int, help="Tile size to use for tablet. Too large tile sizes can cause the app to crash.",show_default=True)
def prepare_for_tablet(input_image,output_folder,tile_size):
    """
        Given an input-image (any format) and an output-folder,
        the command tiles the input-image into tiles of suitable size for an android
        tablet. If the input image is georeferenced (can be georeferenced tif or other image format with
        a imagename.imageformat.aux.xml file in the same folder(=>see gdal)), the script generates
        additional files with geo information that are read and used by the tablet app
        for displaying the user location. An additional advantage of using a georeferenced image as input
        is that after annotating on the tablet, all annotations can be copied onto other georeferenced
        images with the copy-annotations commmand.
    """
    if check_inputs(folders=[output_folder],files=[input_image]):
        import prepare_for_tablet
        prepare_for_tablet.preprocess(input_image,output_folder,tile_size)


@cli.command(short_help='Export annotations to shape files.')
@click.argument('annotation-folder', type=click.Path())
@click.argument('output-folder', type=click.Path())
def export_annotations(annotation_folder,output_folder):
    """
        Exports all annotations within a folder to shape files.
    """
    if check_inputs(folders=[annotation_folder,output_folder]):
        import export_as_shape_files
        export_as_shape_files.make_shape_files(annotation_folder, output_folder)
    
    
    
    
    
    
@cli.command(short_help='Generate heatmaps from predictions.')
@click.argument('predictions-folder', type=click.Path())
@click.argument('output-folder', type=click.Path())
@click.option('--heatmap-width', default=constants.heatmap_width,type=int, help='Defines the the number of pixels the heatmap will have on the x axis. The height of the heatmap is chosen such that the width/height ratio is preserved. This heatmap will finally be resized to the size of the input (or background) image.',show_default=True)
@click.option('--max-val', default=constants.max_val, type=int, help='If defined, it denotes the maximum value of the heatmap, meaning that all values in the heatmap that are larger than this max_val will be painted as red.',show_default=True)
@click.option('--flower', default=constants.classes, multiple=True, type=str, help='For which class the heatmap should be generated. If None is provided, only the overall heatmap for all classes is generated. This flag can be defined multiple times.',show_default=True)
@click.option('--min-score', default=constants.min_confidence_score,type=float, help='The minimum score a prediction must have to be included in the heatmap.',show_default=True)
@click.option('--overlay', default=constants.overlay,type=bool, help='If True, the heatmap is drawn onto a copy of the input image. Otherwise it is drawn without any background.',show_default=True)
@click.option('--output-image-width', default=constants.output_image_width,type=int, help='The width of the output image, the height is resized such that the width/height ratio is preserved.',show_default=True)
@click.option('--generate-from-multiple', default=False,type=bool, help='If True, the script takes all predictions in the input folder and generates one heatmap from all of them. For this option, the input folder needs to contain georeferenced images and the background-image option has to be set.',show_default=True)
@click.option('--background-image', default=None,type=click.Path(), help='The path to the image that should be used as background for the heatmap. (The background can still be deactivated with the --overlay flag but it needs to be provided as a frame for the heatmap.) If generate-from-multiple is set to False, this option is ignored.',show_default=True)
@click.option('--window', default=None,type=float, help='Four float values indicating the [ulx, uly, lrx, lry] coordinates in the swiss coordinate system LV95+ of the area that should be used for the heatmap.',show_default=True,nargs=4)
def generate_heatmaps(predictions_folder, background_image, output_folder, heatmap_width, max_val ,flower , min_score, overlay, output_image_width, generate_from_multiple,window):
    """
    Creates heatmaps for all images in the predictions_folder and saves them to
    the output_folder. If the --generate-from-multiple flag is set to True and 
    the --background-image flag is defined, the script generates one heatmap from 
    all images in the predictions-folder. In this case the images have to be 
    georeferenced.
    
    """
    if window == ():
        window = None
    import create_heatmap
    if generate_from_multiple:
        if check_inputs(folders=[predictions_folder,output_folder], files=[background_image]):
            create_heatmap.create_heatmap_from_multiple(predictions_folder, background_image, output_folder, heatmap_width, max_val ,flower, min_score, overlay, output_image_width,window)
    else:
        if check_inputs(folders=[predictions_folder,output_folder]):
            create_heatmap.create_heatmap(predictions_folder, output_folder, heatmap_width, max_val ,flower, min_score, overlay, output_image_width,window)
        
        
        
def check_inputs(folders=[],files=[]):
    """Checks for all folders and files if they exist.

    Parameters:
        folders (list): list of strings representing folder paths
        files (list): list of strings representing file paths
    
    Returns:
        bool: True if all folders and files exist, False otherwise.
    """

    for folder in folders:
        if not os.path.isdir(folder):
            print(str(folder) + " is not a valid folder. Please check the spelling!")
            return False
    for file in files:
        if not os.path.isfile(file):
            print(str(file) + " is not a valid file. Please check the spelling!")
            return False
    return True

    
    

if __name__ == '__main__':
    cli(prog_name='python cli.py')
