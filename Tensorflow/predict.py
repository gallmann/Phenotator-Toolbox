# -*- coding: utf-8 -*-
"""
Created on Fri Apr  5 15:50:29 2019

@author: johan



This script makes predictions on images of any size.
"""



print("Loading libraries...")
from utils import constants
import os
#os.environ["CUDA_VISIBLE_DEVICES"] = '-1'
from utils import file_utils
from utils import flower_info
import numpy as np
import sys
import tensorflow as tf
from object_detection.utils import visualization_utils
import progressbar
import gdal


from distutils.version import StrictVersion
from PIL import Image
# This is needed since the notebook is stored in the object_detection folder.
sys.path.append("..")
from object_detection.utils import ops as utils_ops
if StrictVersion(tf.__version__) < StrictVersion('1.9.0'):
  raise ImportError('Please upgrade your TensorFlow installation to v1.9.* or later!')
from object_detection.utils import label_map_util


def predict(project_dir,images_to_predict,output_folder,tile_size,prediction_overlap,min_confidence_score=0.5):
  """
  Makes predictions on all images in the images_to_predict folder and saves them to the
  output_folder with the prediction bounding boxes drawn onto the images. Additionally
  for each image a json file is saved to the output folder with all the prediction results.
  The images can be of any size and of png, jpg or tif format. If the images
  in the images_to_predict folder have annotation files stored in the same folder,
  these annotation files are also copied to the output folder. This allows the 
  evaluate command to compare the predictions to the groundtruth annotations.
  
  Parameters:
      project_dir (str): path of the project directory, in which the exported
          inference graph is looked for.
      images_to_predict (str): path of the folder containing the images on which
          to run the predictions on.
      output_folder (str): path of the output folder
      tile_size (int): tile_size to use to make predictions on. Should be the same
          as it was trained on.
      prediction_overlap (int): the size of the overlap of the tiles to run the
          prediction algorithm on in pixels

  Returns:
      None
  
  """
    
  MODEL_NAME = project_dir + "/trained_inference_graphs/output_inference_graph_v1.pb"
  # Path to frozen detection graph. This is the actual model that is used for the object detection.
  PATH_TO_FROZEN_GRAPH = MODEL_NAME + '/frozen_inference_graph.pb'
  PATH_TO_LABELS = project_dir + "/model_inputs/label_map.pbtxt"

    
  detection_graph = get_detection_graph(PATH_TO_FROZEN_GRAPH)
  category_index = label_map_util.create_category_index_from_labelmap(PATH_TO_LABELS, use_display_name=True)
  print(category_index)

  with detection_graph.as_default():
   with tf.Session() as sess:
       
       
    tensor_dict = get_tensor_dict(tile_size)
    image_tensor = tf.get_default_graph().get_tensor_by_name('image_tensor:0') 
    all_images = file_utils.get_all_images_in_folder(images_to_predict)
    
    for image_path in all_images:
        
        try:
            image = Image.open(image_path)
            width, height = image.size
        except Image.DecompressionBombError:
            ds = gdal.Open(image_path)
            band = ds.GetRasterBand(1)
            width = band.XSize
            height = band.YSize
            image_array = ds.ReadAsArray().astype(np.uint8)
            image_array = np.swapaxes(image_array,0,1)
            image_array = np.swapaxes(image_array,1,2)
            print("Please note that the image is very large. The prediction algorithm will work as usual but no information will be drawn onto the bounding boxes.")
            
        print("Making Predictions for " + os.path.basename(image_path) + "...")
        
        detections = []

        #create appropriate tiles from image
        for x_start in progressbar.progressbar(range(0, width-2,tile_size-prediction_overlap)):
            for y_start in range(0,height-2,tile_size-prediction_overlap):
                
                try:
                    crop_rectangle = (x_start, y_start, x_start+tile_size, y_start + tile_size)
                    cropped_im = image.crop(crop_rectangle)
                except (Image.DecompressionBombError, UnboundLocalError):
                    #crop the image using gdal if it is too large for PIL
                    cropped_array = image_array[x_start:x_start+tile_size,y_start:y_start+tile_size,:]
                    pad_x = tile_size - cropped_array.shape[0]
                    pad_y = tile_size - cropped_array.shape[1]

                    cropped_array = np.pad(cropped_array,((0,pad_x),(0,pad_y),(0,0)), mode='constant', constant_values=0)
                    cropped_im = Image.fromarray(cropped_array)
                

                #check if image consists of only one color.
                extrema = cropped_im.convert("L").getextrema()
                if extrema[0] == extrema[1]:
                    continue

                image_np = load_image_into_numpy_array(cropped_im)
                output_dict = sess.run(tensor_dict,feed_dict={image_tensor: np.expand_dims(image_np, 0)})
                output_dict = clean_output_dict(output_dict)
                

        
                count = 0
                for i,score in enumerate(output_dict['detection_scores']):
                    center_x = (output_dict['detection_boxes'][i][3]+output_dict['detection_boxes'][i][1])/2*tile_size
                    center_y = (output_dict['detection_boxes'][i][2]+output_dict['detection_boxes'][i][0])/2*tile_size
                    if score >= min_confidence_score and center_x >= prediction_overlap and center_y >= prediction_overlap and center_x < tile_size-prediction_overlap and center_y < tile_size-prediction_overlap:
                        count += 1
                        top = round(output_dict['detection_boxes'][i][0] * tile_size + y_start)
                        left = round(output_dict['detection_boxes'][i][1] * tile_size + x_start)
                        bottom = round(output_dict['detection_boxes'][i][2] * tile_size + y_start)
                        right = round(output_dict['detection_boxes'][i][3] * tile_size + x_start)
                        detection_class = output_dict['detection_classes'][i]
                        detections.append({"bounding_box": [top,left,bottom,right], "score": float(score), "name": category_index[detection_class]["name"]})



        print(str(len(detections)) + " flowers detected")
        
        predictions_out_path = os.path.join(output_folder, os.path.basename(image_path)[:-4] + "_predictions.json")
        file_utils.save_json_file(detections,predictions_out_path)

        #copy the ground truth annotations to the output folder if there is any ground truth
        ground_truth = get_ground_truth_annotations(image_path)
        if ground_truth:
            #draw ground truth
            for detection in ground_truth:
                [top,left,bottom,right] = detection["bounding_box"]
                col = "black"
                try:
                    visualization_utils.draw_bounding_box_on_image(image,top,left,bottom,right,display_str_list=(),thickness=1, color=col, use_normalized_coordinates=False)          
                except UnboundLocalError:
                    draw_bounding_box_onto_array(image_array,top,left,bottom,right)

            ground_truth_out_path = os.path.join(output_folder, os.path.basename(image_path)[:-4] + "_ground_truth.json")
            file_utils.save_json_file(ground_truth,ground_truth_out_path)
        

        for detection in detections:
            col = flower_info.get_color_for_flower(detection["name"])
            [top,left,bottom,right] = detection["bounding_box"]
            score_string = str('{0:.2f}'.format(detection["score"]))
            try:
                visualization_utils.draw_bounding_box_on_image(image,top,left,bottom,right,display_str_list=[score_string,detection["name"]],thickness=1, color=col, use_normalized_coordinates=False)          
            except UnboundLocalError:
                col = flower_info.get_color_for_flower(detection["name"],get_rgb_value=True)[0:3]
                draw_bounding_box_onto_array(image_array,top,left,bottom,right,color=col)
        
        image_output_path = os.path.join(output_folder, os.path.basename(image_path))
        try:
            image.save(image_output_path)
        except UnboundLocalError:
            image_array = np.swapaxes(image_array,2,1)
            image_array = np.swapaxes(image_array,1,0)
            ds.GetRasterBand(1).WriteArray(image_array[0], 0, 0)
            ds.GetRasterBand(2).WriteArray(image_array[1], 0, 0)
            ds.GetRasterBand(3).WriteArray(image_array[2], 0, 0)
            gdal.Translate(image_output_path,ds, options=gdal.TranslateOptions(bandList=[1,2,3]))




def draw_bounding_box_onto_array(array,top,left,bottom,right,color=[0,0,0]):
    """

    Parameters:
        image_path (str): path to the image of which the annotations should be read
    
    Returns:
        list: a list containing all annotations corresponding to that image.
            Returns the None if no annotation file is present
    """

    color = np.array(color).astype(np.uint8)
    top = max(0,int(top))
    left = max(0,int(left))
    bottom = min(array.shape[1]-1,int(bottom))
    right = min(array.shape[0]-1,int(right))
    for i in range(top,bottom+1,1):
        array[left,i] = color
        array[right,i] = color
    for i in range(left,right+1):
        array[i,top] = color
        array[i,bottom] = color


        
def get_ground_truth_annotations(image_path):
    """Reads the ground_thruth information from either the tablet annotations (imagename_annotations.json),
        the LabelMe annotations (imagename.json) or tensorflow xml format annotations (imagename.xml)

    Parameters:
        image_path (str): path to the image of which the annotations should be read
    
    Returns:
        list: a list containing all annotations corresponding to that image.
            Returns the None if no annotation file is present
    """
    ground_truth = file_utils.get_annotations(image_path)
    for fl in ground_truth:
        fl["name"] = flower_info.clean_string(fl["name"])
        fl["bounding_box"] = flower_info.get_bbox(fl)
    
    if len(ground_truth) == 0:                     
        return None
    return ground_truth
        

def get_detection_graph(PATH_TO_FROZEN_GRAPH):
    """
    Reads the frozen detection graph into memory.
    
    Parameters:
        PATH_TO_FROZEN_GRAPH (str): path to the directory containing the frozen
            graph files.
    
    Returns:
        A tensorflow graph instance with which the prediction algorithm can be run.
    """
    detection_graph = tf.Graph()
    with detection_graph.as_default():
      od_graph_def = tf.GraphDef()
      with tf.gfile.GFile(PATH_TO_FROZEN_GRAPH, 'rb') as fid:
        serialized_graph = fid.read()
        od_graph_def.ParseFromString(serialized_graph)
        tf.import_graph_def(od_graph_def, name='')
    return detection_graph

def load_image_into_numpy_array(image):
  """
  Helper function that loads an image into a numpy array.
  
  Parameters:
      image (PIL image): a PIL image
      
  Returns:
      np.array: a numpy array representing the image
  """
  (im_width, im_height) = image.size
  return np.array(image.getdata()).reshape(
      (im_height, im_width, 3)).astype(np.uint8)

def clean_output_dict(output_dict):
    # all outputs are float32 numpy arrays, so convert types as appropriate
    output_dict['num_detections'] = int(output_dict['num_detections'][0])
    output_dict['detection_classes'] = output_dict['detection_classes'][0].astype(np.uint8)
    output_dict['detection_boxes'] = output_dict['detection_boxes'][0]
    output_dict['detection_scores'] = output_dict['detection_scores'][0]
    if 'detection_masks' in output_dict:
        output_dict['detection_masks'] = output_dict['detection_masks'][0]
    return output_dict

def get_tensor_dict(tile_size):
  """
  Helper function that returns a tensor_dict dictionary that is needed for the 
  prediction algorithm.
  
  Parameters:
      tile_size (int): The size of the tiles on which the prediction algorithm is
          run on.

  Returns:
      dict: The tensor dictionary
  
  """
      # Get handles to input and output tensors
  ops = tf.get_default_graph().get_operations()
  all_tensor_names = {output.name for op in ops for output in op.outputs}
  tensor_dict = {}
  for key in ['num_detections', 'detection_boxes', 'detection_scores','detection_classes', 'detection_masks']:
    tensor_name = key + ':0'
    if tensor_name in all_tensor_names:
      tensor_dict[key] = tf.get_default_graph().get_tensor_by_name(tensor_name)
  if 'detection_masks' in tensor_dict:
    # The following processing is only for single image
    detection_boxes = tf.squeeze(tensor_dict['detection_boxes'], [0])
    detection_masks = tf.squeeze(tensor_dict['detection_masks'], [0])
    # Reframe is required to translate mask from box coordinates to image coordinates and fit the image size.
    real_num_detection = tf.cast(tensor_dict['num_detections'][0], tf.int32)
    detection_boxes = tf.slice(detection_boxes, [0, 0], [real_num_detection, -1])
    detection_masks = tf.slice(detection_masks, [0, 0, 0], [real_num_detection, -1, -1])
    detection_masks_reframed = utils_ops.reframe_box_masks_to_image_masks(
        detection_masks, detection_boxes, tile_size, tile_size)
    detection_masks_reframed = tf.cast(
        tf.greater(detection_masks_reframed, 0.5), tf.uint8)
    # Follow the convention by adding back the batch dimension
    tensor_dict['detection_masks'] = tf.expand_dims(
        detection_masks_reframed, 0)
    
  return tensor_dict



if __name__ == '__main__':
    
    train_dir = constants.train_dir

    images_to_predict = constants.images_to_predict
    
    output_folder = constants.predictions_folder
    
    
    #size of tiles to feed into prediction network
    tile_size = constants.tile_size
    #minimum distance from edge of tile for prediction to be considered
    prediction_overlap = constants.prediction_overlap

    predict(train_dir,images_to_predict,output_folder,tile_size,prediction_overlap)

    