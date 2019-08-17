# -*- coding: utf-8 -*-
"""
Created on Tue Aug 13 16:12:50 2019

@author: gallmanj
"""

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import numpy as np
import custom_evaluations
from utils import constants


def y_fmt(y, pos):
    decades = [1e9, 1e6, 1e3, 1e0, 1e-3, 1e-6, 1e-9 ]
    suffix  = ["G", "M", "k", "" , "m" , "u", "n"  ]
    if y == 0:
        return str(0)
    for i, d in enumerate(decades):
        if np.abs(y) >=d:
            val = y/float(d)
            signf = len(str(val).split(".")[1])
            if signf == 0:
                return '{val:d} {suffix}'.format(val=int(val), suffix=suffix[i])
            else:
                if signf == 1:
                    if str(val).split(".")[1] == "0":
                        return '{val:d} {suffix}'.format(val=int(round(val)), suffix=suffix[i]) 
                tx = "{"+"val:.{signf}f".format(signf = signf) +"} {suffix}"
                return tx.format(val=val, suffix=suffix[i])

                #return y
    return y



def plot(x_indices, data, data_labels, x_axis_label, y_axis_label, out_path):
    
    #plt.figure(graph_no)

    fig = plt.figure()
    ax = fig.add_subplot(111)
    plt.xlabel(x_axis_label)
    plt.ylabel(y_axis_label)  
    for i in range(data.shape[0]):
        #ax.plot(x_indices,data[i])
        ax.errorbar(1/x_indices, data[i], yerr = None,fmt="-o", capsize=2)
    
    #plt.plot(x_indices,data, "-o") #,"b-o"
    plt.legend(data_labels)
    #plt.xticks(1/x_indices)
    #ax.yaxis.set_major_formatter(FuncFormatter(y_fmt))

    top = 1.0
    label_datapoints = False

    plt.gca().set_ylim(bottom=0, top=top)
    plt.gca().set_xlim(left=1)
    
    if label_datapoints:
        for line in data:
            for i,j in zip(1/x_indices,line):
                ax.annotate(round(j,1),xy=(i,j))
            
            
    plt.grid(linestyle='--')
    plt.savefig(out_path,dpi=300)
    #plt.show()
    plt.close('all')


def get_metrics(stat):
    stat["f1"] = 0
    stat["precision"] = 0
    stat["recall"] = 0

    n = stat["tp"] + stat["fn"]
    if float(stat["fp"]+stat["tp"]) == 0:
        precision = "-"
    else:
        precision = float(stat["tp"]) / float(stat["fp"]+stat["tp"])
        stat["precision"] = precision
    if float(stat["tp"] + stat["fn"]) == 0:
        recall = "-"
    else:
        recall = float(stat["tp"]) / float(stat["tp"] + stat["fn"])
        stat["recall"] = precision
    f1 = "-"
    if recall != "-" and precision != "-" and ((recall >0) or (precision > 0)):
        f1 = 2 * (precision*recall)/(precision+recall)
        stat["f1"] = f1
    return stat


def make_plot_with_data_from_experiments():
    
    flowers_of_interest = ["overall", "knautia arvensis", "leucanthemum vulgare", "lotus corniculatus"]
    
    x_indices = np.array([1.0,0.8,0.5,0.3,0.2,0.1,0.05])
    data = np.zeros((len(flowers_of_interest),len(x_indices)))
    data_labels = flowers_of_interest
    x_axis_label = "Ground Resolution (mm/pixel)"
    y_axis_label = "mAP"
    out_path = "G:/Johannes/test/test.png"

    folders = ["25_1",27,30,32,33,34,35]
    for experiment_index in range(len(folders)):
        experiment_number = folders[experiment_index]
        project_folder = "G:/Johannes/Experiments/0" + str(experiment_number) + "/output/"
        predictions_folder = project_folder + "predictions_model25"
        stats = custom_evaluations.evaluate(project_folder, predictions_folder, "" ,iou_threshold=constants.iou_threshold,generate_visualizations=False,should_print_confusion_matrix=False,min_score=0.2)
        for i in range(len(flowers_of_interest)):
            flower_of_interest = flowers_of_interest[i]
            stat = get_metrics(stats[flower_of_interest])
            data[i][experiment_index] = stat["mAP"]
        
    print(data)
    plot(x_indices, data, data_labels, x_axis_label, y_axis_label, out_path)


make_plot_with_data_from_experiments()
    
'''
from utils import file_utils

count = file_utils.get_annotation_count_in_folder("G:/Johannes/Data/June_29/flight2/MaskedAnnotationData")
print(count)
'''










