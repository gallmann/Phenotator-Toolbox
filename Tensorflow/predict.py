# -*- coding: utf-8 -*-
"""
Created on Fri Apr  5 15:50:29 2019

@author: johan
"""




#train_dir = "G:/Johannes/output"

#output_folder = "C:/Users/gallmanj.KP31-21-161/Desktop/vis_im"


from utils import constants

train_dir = constants.train_dir

images_to_predict = constants.images_to_predict

output_folder = constants.predictions


#size of tiles to feed into prediction network
tile_size = constants.tile_size
#minimum distance from edge of tile for prediction to be considered
padding = 50


PATH_TO_TEST_IMAGES_DIR = train_dir + "/images/test"
MODEL_NAME = train_dir + "/trained_inference_graphs/output_inference_graph_v1.pb"
# Path to frozen detection graph. This is the actual model that is used for the object detection.
PATH_TO_FROZEN_GRAPH = MODEL_NAME + '/frozen_inference_graph.pb'
PATH_TO_LABELS = train_dir + "/model_inputs/label_map.pbtxt"


import os
#os.environ["CUDA_VISIBLE_DEVICES"] = '-1'
from utils import file_utils
from utils import flower_info
import numpy as np
import sys
import tensorflow as tf
from object_detection.utils import visualization_utils
import progressbar


from distutils.version import StrictVersion
from PIL import Image
import matplotlib
# This is needed since the notebook is stored in the object_detection folder.
sys.path.append("..")
from object_detection.utils import ops as utils_ops
if StrictVersion(tf.__version__) < StrictVersion('1.9.0'):
  raise ImportError('Please upgrade your TensorFlow installation to v1.9.* or later!')
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util


def predict():
  detection_graph = get_detection_graph()
  category_index = label_map_util.create_category_index_from_labelmap(PATH_TO_LABELS, use_display_name=True)
  print(category_index)

  with detection_graph.as_default():
   with tf.Session() as sess:
       
       
    tensor_dict = get_tensor_dict(tile_size)
    image_tensor = tf.get_default_graph().get_tensor_by_name('image_tensor:0') 
    all_images = file_utils.get_all_tifs_in_folder(images_to_predict)
    all_images.extend(file_utils.get_all_images_in_folder(images_to_predict))
    
    for image_path in all_images:
        image = Image.open(image_path)
        width, height = image.size
                
        print("Making Predictions for " + os.path.basename(image_path))
        
        detections = []
        
        #create appropriate tiles from image
        for x_start in progressbar.progressbar(range(-padding, width-1,tile_size-2*padding)):
            for y_start in range(-padding,height-1,tile_size-2*padding):
                crop_rectangle = (x_start, y_start, x_start+tile_size, y_start + tile_size)
                cropped_im = image.crop(crop_rectangle)
                
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
                    if score > 0.5 and center_x >= padding and center_y >= padding and center_x < tile_size-padding and center_y < tile_size-padding:
                        count += 1
                        top = round(output_dict['detection_boxes'][i][0] * tile_size + y_start)
                        left = round(output_dict['detection_boxes'][i][1] * tile_size + x_start)
                        bottom = round(output_dict['detection_boxes'][i][2] * tile_size + y_start)
                        right = round(output_dict['detection_boxes'][i][3] * tile_size + x_start)
                        detection_class = output_dict['detection_classes'][i]
                        detections.append({"bounding_box": [top,left,bottom,right], "score": float(score), "name": category_index[detection_class]["name"]})

        

        print(str(len(detections)) + " flowers detected")
        
        #copy the ground truth annotations to the output folder if there is any ground truth
        ground_truth = get_ground_truth_annotations(image_path)
        if ground_truth:
            #draw ground truth
            for detection in ground_truth:
                [top,left,bottom,right] = detection["bounding_box"]
                col = "black"
                visualization_utils.draw_bounding_box_on_image(image,top,left,bottom,right,display_str_list=(),thickness=1, color=col, use_normalized_coordinates=False)          
            ground_truth_out_path = os.path.join(output_folder, os.path.basename(image_path)[:-4] + "_ground_truth.json")
            file_utils.save_json_file(ground_truth,ground_truth_out_path)
        
        
        for detection in detections:
            col = get_color_for_name(detection["name"], category_index)
            [top,left,bottom,right] = detection["bounding_box"]
            score_string = str('{0:.2f}'.format(detection["score"]))
            visualization_utils.draw_bounding_box_on_image(image,top,left,bottom,right,display_str_list=[score_string,detection["name"]],thickness=1, color=col, use_normalized_coordinates=False)          
        predictions_out_path = os.path.join(output_folder, os.path.basename(image_path)[:-4] + "_predictions.json")
        file_utils.save_json_file(detections,predictions_out_path)
        
        
        image_output_path = os.path.join(output_folder, os.path.basename(image_path))
        image.save(image_output_path)
        
        
def get_ground_truth_annotations(image_path):
    ground_truth = None
    ground_truth_in_path_xml = image_path[:-4] + ".xml"
    if ground_truth_in_path_xml and os.path.isfile(ground_truth_in_path_xml):
        ground_truth = file_utils.get_annotations_from_xml(ground_truth_in_path_xml)
    ground_truth_in_path_json = image_path[:-4] + "_annotations.json"
    if ground_truth_in_path_json and os.path.isfile(ground_truth_in_path_json):
        annotated_flowers = file_utils.read_json_file(ground_truth_in_path_json)["annotatedFlowers"]
        ground_truth = []
        for fl in annotated_flowers:
            flower = {}
            flower["name"] = flower_info.clean_string(fl["name"])
            flower["bounding_box"] = flower_info.get_bbox(fl)
            ground_truth.append(flower)
                        
    return ground_truth
        

def get_detection_graph():
    detection_graph = tf.Graph()
    with detection_graph.as_default():
      od_graph_def = tf.GraphDef()
      with tf.gfile.GFile(PATH_TO_FROZEN_GRAPH, 'rb') as fid:
        serialized_graph = fid.read()
        od_graph_def.ParseFromString(serialized_graph)
        tf.import_graph_def(od_graph_def, name='')
    return detection_graph

def get_color_for_name(name,category_index):
    for i in category_index:
        if category_index[i]["name"] == name:
            label = list(matplotlib.colors.cnames.keys())[category_index[i]["id"]]
            return label
    
def get_color_for_index(index):
    label = list(matplotlib.colors.cnames.keys())[index]
    return label


def load_image_into_numpy_array(image):
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


predict()

    