# -*- coding: utf-8 -*-
"""
Created on Mon Apr  1 16:13:06 2019

@author: johan

This script converts csv input annotations to tfrecord files that are used by 
Tensorflow for the training.

"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import os
import io
import pandas as pd
import tensorflow as tf
import sys
sys.path.append("../../models/research")

from PIL import Image
from object_detection.utils import dataset_util
from collections import namedtuple


def class_text_to_int(row_label, labels):
    index = list(labels.keys()).index(row_label) + 1
    return index

def class_text_to_weight(row_label, labels):
    """
    Calculates the weight of a class label.
    
    Parameters:
        row_label (str): label of the class
        labels (map): the labels map mapping from each class label to an int
            describing how many instances of that class the training data contains
    
    Returns:
        float: The class weight used to write to the tfrecord file
    """
    if(len(labels) == 1):
        return 1
    
    total_flower_count = 0
    for key, value in labels.items():
        total_flower_count += value
    weight = 1 - labels[row_label]/total_flower_count
    #weight = 1
    return weight


def split(df, group):
    data = namedtuple('data', ['filename', 'object'])
    gb = df.groupby(group)
    return [data(filename, gb.get_group(x)) for filename, x in zip(gb.groups.keys(), gb.groups)]


def create_tf_example(group, path, labels):
    """
    Creates the tfrecord file. This function is largely adapted from the Tesorflow
    utilities.
    """
    with tf.gfile.GFile(os.path.join(path, '{}'.format(group.filename)), 'rb') as fid:
        encoded_jpg = fid.read()
    encoded_jpg_io = io.BytesIO(encoded_jpg)
    image = Image.open(encoded_jpg_io)
    width, height = image.size

    filename = group.filename.encode('utf8')
    image_format = b'png'
    # check if the image format is matching with your images.
    xmins = []
    xmaxs = []
    ymins = []
    ymaxs = []
    classes_text = []
    classes = []
    weights = []


    for index, row in group.object.iterrows():
        xmins.append(row['xmin'] / width)
        xmaxs.append(row['xmax'] / width)
        ymins.append(row['ymin'] / height)
        ymaxs.append(row['ymax'] / height)
        classes_text.append(row['class'].encode('utf8'))
        classes.append(class_text_to_int(row['class'],labels))
        weights.append(class_text_to_weight(row['class'],labels))


    tf_example = tf.train.Example(features=tf.train.Features(feature={
        'image/height': dataset_util.int64_feature(height),
        'image/width': dataset_util.int64_feature(width),
        'image/filename': dataset_util.bytes_feature(filename),
        'image/source_id': dataset_util.bytes_feature(filename),
        'image/encoded': dataset_util.bytes_feature(encoded_jpg),
        'image/format': dataset_util.bytes_feature(image_format),
        'image/object/bbox/xmin': dataset_util.float_list_feature(xmins),
        'image/object/bbox/xmax': dataset_util.float_list_feature(xmaxs),
        'image/object/bbox/ymin': dataset_util.float_list_feature(ymins),
        'image/object/bbox/ymax': dataset_util.float_list_feature(ymaxs),
        'image/object/class/text': dataset_util.bytes_list_feature(classes_text),
        'image/object/class/label': dataset_util.int64_list_feature(classes),
        'image/object/weight': dataset_util.float_list_feature(weights),

    }))
    return tf_example


def make_tfrecords(input_csv, output_tf_record, images_folder, labels):
    """
    This is the main command of the script that converts the input csv to a
    tf record file.
    
    Parameters:
        input_csv (str): path to the input csv file
        output_tf_record (str): path to the output tf record file
        images_folder (str): the folder containing the training images
        labels (map): A map containing for each class name an integer that
            defines how many instances of that class are in the training data.
            This is used to weigh the classes according to the number of instances
            there are.
    
    Returns:
        None
    
    """
    writer = tf.python_io.TFRecordWriter(output_tf_record)
    examples = pd.read_csv(input_csv)
    grouped = split(examples, 'filename')
    for group in grouped:
        tf_example = create_tf_example(group, images_folder, labels)
        writer.write(tf_example.SerializeToString())
    writer.close()


    
