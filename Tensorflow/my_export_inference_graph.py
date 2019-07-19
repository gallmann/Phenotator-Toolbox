"""

This script was largely adapted from the Tensorflow Object Detection repository,
Only slight adjustions were made to integrate it into the command line tool.

"""


# Copyright 2017 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================


print("Loading libraries...")
import os
from utils import file_utils
from utils import constants


r"""Tool to export an object detection model for inference.

Prepares an object detection tensorflow graph for inference using model
configuration and a trained checkpoint. Outputs inference
graph, associated checkpoint files, a frozen inference graph and a
SavedModel (https://tensorflow.github.io/serving/serving_basic.html).

The inference graph contains one of three input nodes depending on the user
specified option.
  * `image_tensor`: Accepts a uint8 4-D tensor of shape [None, None, None, 3]
  * `encoded_image_string_tensor`: Accepts a 1-D string tensor of shape [None]
    containing encoded PNG or JPEG images. Image resolutions are expected to be
    the same if more than 1 image is provided.
  * `tf_example`: Accepts a 1-D string tensor of shape [None] containing
    serialized TFExample protos. Image resolutions are expected to be the same
    if more than 1 image is provided.

and the following output nodes returned by the model.postprocess(..):
  * `num_detections`: Outputs float32 tensors of the form [batch]
      that specifies the number of valid boxes per image in the batch.
  * `detection_boxes`: Outputs float32 tensors of the form
      [batch, num_boxes, 4] containing detected boxes.
  * `detection_scores`: Outputs float32 tensors of the form
      [batch, num_boxes] containing class scores for the detections.
  * `detection_classes`: Outputs float32 tensors of the form
      [batch, num_boxes] containing classes for the detections.
  * `raw_detection_boxes`: Outputs float32 tensors of the form
      [batch, raw_num_boxes, 4] containing detection boxes without
      post-processing.
  * `raw_detection_scores`: Outputs float32 tensors of the form
      [batch, raw_num_boxes, num_classes_with_background] containing class score
      logits for raw detection boxes.
  * `detection_masks`: Outputs float32 tensors of the form
      [batch, num_boxes, mask_height, mask_width] containing predicted instance
      masks for each box if its present in the dictionary of postprocessed
      tensors returned by the model.

Notes:
 * This tool uses `use_moving_averages` from eval_config to decide which
   weights to freeze.

Example Usage:
--------------
python export_inference_graph \
    --input_type image_tensor \
    --pipeline_config_path path/to/ssd_inception_v2.config \
    --trained_checkpoint_prefix path/to/model.ckpt \
    --output_directory path/to/exported_model_directory

The expected output would be in the directory
path/to/exported_model_directory (which is created if it does not exist)
with contents:
 - inference_graph.pbtxt
 - model.ckpt.data-00000-of-00001
 - model.ckpt.info
 - model.ckpt.meta
 - frozen_inference_graph.pb
 + saved_model (a directory)

Config overrides (see the `config_override` flag) are text protobufs
(also of type pipeline_pb2.TrainEvalPipelineConfig) which are used to override
certain fields in the provided pipeline_config_path.  These are useful for
making small changes to the inference graph that differ from the training or
eval config.

Example Usage (in which we change the second stage post-processing score
threshold to be 0.5):

python export_inference_graph \
    --input_type image_tensor \
    --pipeline_config_path path/to/ssd_inception_v2.config \
    --trained_checkpoint_prefix path/to/model.ckpt \
    --output_directory path/to/exported_model_directory \
    --config_override " \
            model{ \
              faster_rcnn { \
                second_stage_post_processing { \
                  batch_non_max_suppression { \
                    score_threshold: 0.5 \
                  } \
                } \
              } \
            }"
"""
import tensorflow as tf
from google.protobuf import text_format
from object_detection import exporter
from object_detection.protos import pipeline_pb2
slim = tf.contrib.slim
from importlib import reload  # Python 3.4+ only.



def main(pipeline_config_path,trained_checkpoint_prefix,output_directory):
  """
  Main function executing the export. This is directly adapted from the Tensorflow implementation.
  """
  config_override = ''
  input_shape = None
  input_type = 'image_tensor'
  write_inference_graph_flag = False
  pipeline_config = pipeline_pb2.TrainEvalPipelineConfig()
  with tf.gfile.GFile(pipeline_config_path, 'r') as f:
    text_format.Merge(f.read(), pipeline_config)
  text_format.Merge(config_override, pipeline_config)
  if input_shape:
    input_shape = [
        int(dim) if dim != '-1' else None
        for dim in input_shape.split(',')
    ]
  else:
    input_shape = None
    reload(exporter)
  exporter.export_inference_graph(
      input_type, pipeline_config, trained_checkpoint_prefix,
      output_directory, input_shape=input_shape,
      write_inference_graph=write_inference_graph_flag)

def find_best_model(training_directory, look_in_checkpoints_dir = True, model_selection_criterion="f1"):
    """
    Finds the best model. If look_in_checkpoints_dir is set to True, the model best model is
    selected based on the score it achieved on the validation set using either the f1 score or
    mAP. 

    Parameters:
        training_directory (str): path to the training directory
        look_in_checkpoints_dir (bool): if True, it was trained with a validation set
            and the best model accordint to the model_selection_criterion is chosen
        model_selection_criterion (str): either 'f1' or 'mAP'. 
    
    Returns:
        str: path of the best model prefix
    """

    
    if not look_in_checkpoints_dir:
        largest_number = -1
        for file in os.listdir(training_directory):
            if file.endswith(".index") and file.startswith("model.ckpt-"):
                start = file.index("model.ckpt-") + len("model.ckpt-")
                end = file.index( ".index", start )
                curr_number = int(file[start:end])
                if(curr_number>largest_number):
                    largest_number = curr_number
        return os.path.join(training_directory,"model.ckpt-" + str(largest_number))
    
    
    checkpoints_dir = os.path.join(training_directory,"checkpoints")
    precision_recall_evolution_file = os.path.join(checkpoints_dir,"precision_recall_evolution.txt")
    if os.path.isdir(checkpoints_dir):
        #there is a checkpoints dir
        if os.path.isfile(precision_recall_evolution_file):
            #precision recall evolution exists
            with open(precision_recall_evolution_file) as f:
                lines = f.readlines()
            best_configuration = 0
            best_step = 0
                
            for line in lines:
                step =int(line[line.find("step ")+len("step "):line.rfind("; precision: ")])
                precision = float(line[line.find("; precision: ")+len("; precision: "):line.rfind(" recall: ")])
                recall = float(line[line.find(" recall: ")+len(" recall: "):line.rfind(" mAP: ")])
                mAP = float(line[line.rfind(" mAP: ")+len(" mAP: "):line.rfind(" f1: ")])
                f1 = 2 * (precision*recall)/(precision+recall)
                relevant_metric = f1
                if model_selection_criterion == "mAP":
                    relevant_metric = mAP
                    
                if relevant_metric > best_configuration:
                    best_configuration = relevant_metric
                    best_step = step
            checkpoint_file = os.path.join(checkpoints_dir,"model.ckpt-" + str(best_step))
            if os.path.isfile(checkpoint_file + ".index"):
                return checkpoint_file
            else:
                return find_best_model(training_directory,look_in_checkpoints_dir=False)

        
        





def run(project_dir,look_in_checkpoints_dir = True, model_selection_criterion="f1"):
    """
    Runs the export command.
    
    Parameters:
        project_dir (str): path to the project directory
        look_in_checkpoints_dir (bool): if True, it was trained with a validation set
            and the best model accordint to the model_selection_criterion is chosen
        model_selection_criterion (str): either 'f1' or 'mAP'. 
    
    Returns:
        None
    """

    train_dir = project_dir
    output_directory =  train_dir + "/trained_inference_graphs/output_inference_graph_v1.pb"
    pipeline_config_path = train_dir + "/pre-trained-model/pipeline.config"
    training_directory = os.path.join(project_dir,"training")
    trained_checkpoint_prefix = find_best_model(training_directory,look_in_checkpoints_dir,model_selection_criterion)
    print("Exporting " + trained_checkpoint_prefix)

    file_utils.delete_folder_contents(output_directory)
    
    
    
    main(pipeline_config_path,trained_checkpoint_prefix,output_directory)
    #tf.app.run(main)


if __name__ == '__main__':
    project_dir = constants.train_dir
    run(project_dir)