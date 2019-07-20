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


'''
This script trains a model. To run it define the train_dir and ensure it has the following strucure:
    
train_dir
    images
    model_inputs
    pre-trained-model
    training
    
Inside the pre-trained-model the pipeline.config file must be properly configured.
The train.py script will write all outputs to the training directory.
    
'''


from utils import constants



r"""Training executable for detection models.

This executable is used to train DetectionModels. There are two ways of
configuring the training job:

1) A single pipeline_pb2.TrainEvalPipelineConfig configuration file
can be specified by --pipeline_config_path.

Example usage:
    ./train \
        --logtostderr \
        --train_dir=path/to/train_dir \
        --pipeline_config_path=pipeline_config.pbtxt

2) Three configuration files can be provided: a model_pb2.DetectionModel
configuration file to define what type of DetectionModel is being trained, an
input_reader_pb2.InputReader file to specify what training data will be used and
a train_pb2.TrainConfig file to configure training parameters.

Example usage:
    ./train \
        --logtostderr \
        --train_dir=path/to/train_dir \
        --model_config_path=model_config.pbtxt \
        --train_config_path=train_config.pbtxt \
        --input_config_path=train_input_config.pbtxt
"""
print("Loading libraries...")
import functools
import json
import os
import tensorflow as tf
from google.protobuf import text_format
from object_detection.protos import pipeline_pb2
from shutil import copyfile

from object_detection.builders import dataset_builder
from object_detection.builders import graph_rewriter_builder
from object_detection.builders import model_builder
from object_detection.legacy import trainer
from object_detection.utils import config_util

tf.logging.set_verbosity(tf.logging.INFO)



@tf.contrib.framework.deprecated(None, 'Use object_detection/model_main.py.')
def main(train_dir,pipeline_config_path):
  task = 0
  model_config_path = ''
  train_config_path = ''
  input_config_path = ''
  num_clones = 1
  clone_on_cpu = False
  
  if task == 0: tf.gfile.MakeDirs(train_dir)
  if pipeline_config_path:
    configs = config_util.get_configs_from_pipeline_file(pipeline_config_path)
    if task == 0:
      tf.gfile.Copy(pipeline_config_path,os.path.join(train_dir, 'pipeline.config'),overwrite=True)
  else:
    configs = config_util.get_configs_from_multiple_files(
        model_config_path=model_config_path,
        train_config_path=train_config_path,
        train_input_config_path=input_config_path)
    if task == 0:
      for name, config in [('model.config', model_config_path),
                           ('train.config', train_config_path),
                           ('input.config', input_config_path)]:
        tf.gfile.Copy(config, os.path.join(train_dir, name),
                      overwrite=True)

  model_config = configs['model']
  train_config = configs['train_config']
  input_config = configs['train_input_config']

  model_fn = functools.partial(
      model_builder.build,
      model_config=model_config,
      is_training=True)

  def get_next(config):
    return dataset_builder.make_initializable_iterator(
        dataset_builder.build(config)).get_next()

  create_input_dict_fn = functools.partial(get_next, input_config)

  env = json.loads(os.environ.get('TF_CONFIG', '{}'))
  cluster_data = env.get('cluster', None)
  cluster = tf.train.ClusterSpec(cluster_data) if cluster_data else None
  task_data = env.get('task', None) or {'type': 'master', 'index': 0}
  task_info = type('TaskSpec', (object,), task_data)

  # Parameters for a single worker.
  ps_tasks = 0
  worker_replicas = 1
  worker_job_name = 'lonely_worker'
  task = 0
  is_chief = True
  master = ''

  if cluster_data and 'worker' in cluster_data:
    # Number of total worker replicas include "worker"s and the "master".
    worker_replicas = len(cluster_data['worker']) + 1
  if cluster_data and 'ps' in cluster_data:
    ps_tasks = len(cluster_data['ps'])

  if worker_replicas > 1 and ps_tasks < 1:
    raise ValueError('At least 1 ps task is needed for distributed training.')

  if worker_replicas >= 1 and ps_tasks > 0:
    # Set up distributed training.
    server = tf.train.Server(tf.train.ClusterSpec(cluster), protocol='grpc',
                             job_name=task_info.type,
                             task_index=task_info.index)
    if task_info.type == 'ps':
      server.join()
      return

    worker_job_name = '%s/task:%d' % (task_info.type, task_info.index)
    task = task_info.index
    is_chief = (task_info.type == 'master')
    master = server.target

  graph_rewriter_fn = None
  if 'graph_rewriter_config' in configs:
    graph_rewriter_fn = graph_rewriter_builder.build(
        configs['graph_rewriter_config'], is_training=True)

  trainer.train(
      create_input_dict_fn,
      model_fn,
      train_config,
      master,
      task,
      num_clones,
      worker_replicas,
      clone_on_cpu,
      ps_tasks,
      worker_job_name,
      is_chief,
      train_dir,
      graph_hook_fn=graph_rewriter_fn)

def set_num_steps_in_config_file(num_steps,project_dir):
    
    #edit config file in pre_trained_model_folder
    pipeline_config = pipeline_pb2.TrainEvalPipelineConfig()                                                                                                                                                                                                          
    with tf.gfile.GFile(project_dir + "/pre-trained-model/pipeline.config", "r") as f:                                                                                                                                                                                                                     
        proto_str = f.read()                                                                                                                                                                                                                                          
        text_format.Merge(proto_str, pipeline_config)                                                                                                                                                                                                                 

    pipeline_config.train_config.num_steps = num_steps                                                                                                                                                                                          

    config_text = text_format.MessageToString(pipeline_config)                                                                                                                                                                                                        
    with tf.gfile.Open(project_dir + "/pre-trained-model/pipeline.config", "wb") as f:                                                                                                                                                                                                                       
        f.write(config_text)   
    
    #copy file to training folder
    src = project_dir + "/pre-trained-model/pipeline.config"
    dst = project_dir + "/training/pipeline.config"
    copyfile(src, dst)
                                                                                                                                                                                                                                       

def run(project_dir,max_steps):
    set_num_steps_in_config_file(max_steps,project_dir)
    pipeline_config_path = project_dir + "/pre-trained-model/pipeline.config"
    
    tf.reset_default_graph() 
    
    training_dir = os.path.join(project_dir,"training")
    
    main(training_dir,pipeline_config_path)
    #tf.app.run(main)

if __name__ == '__main__':
    train_dir = "bla"

    run(train_dir,130000)
