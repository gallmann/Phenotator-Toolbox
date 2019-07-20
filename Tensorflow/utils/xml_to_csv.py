# -*- coding: utf-8 -*-
"""
Created on Mon Apr  1 15:47:15 2019

@author: johan


This script converts the xml annotations created by the image-preprocessing
script into csv annotations which can then be converted into tf record files
by the generate_tfrecord script.
"""

import glob
import pandas as pd
import xml.etree.ElementTree as ET


def xml_to_csv(input_folder, output_path, flowers_to_use=None):
    """Iterates through all .xml files in the input_folder and combines them in a single Pandas datagrame.

    Parameters:
        input_folder (str): path to the input folder containing all images and
            xml annotation files
        output_path (str): path to the output csv file.
        flowers_to_use (list): a list of strings containing flower names. Only
            the annotations with flowernames present in the flowers_to_use list
            are copied to the output csv file. If flowers_tu_use is None, all
            annotations are used.
    
    Returns:
        Pandas datagrame of the csv list.
    
    """

    xml_list = []
    for xml_file in glob.glob(input_folder + '/*.xml'):
        tree = ET.parse(xml_file)
        root = tree.getroot()
        for member in root.findall('object'):
            if flowers_to_use == None or member[0].text in flowers_to_use:
                value = (root.find('filename').text,
                        int(root.find('size')[0].text),
                        int(root.find('size')[1].text),
                        member[0].text,
                        int(member[4][0].text),
                        int(member[4][1].text),
                        int(member[4][2].text),
                        int(member[4][3].text)
                        )
                xml_list.append(value)
    column_name = ['filename', 'width', 'height',
                'class', 'xmin', 'ymin', 'xmax', 'ymax']
    xml_df = pd.DataFrame(xml_list, columns=column_name)
    xml_df.to_csv(output_path, index=None)
    return xml_df




if __name__ == '__main__':
    print("Please use the command line interface and run the image-preprocessing command.")
