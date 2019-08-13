# -*- coding: utf-8 -*-
"""
Created on Tue Aug 13 16:12:50 2019

@author: gallmanj
"""

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import numpy as np



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



def plot(x_indices, data, errors, data_labels, x_axis_label, y_axis_label, out_path):
    
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
    plt.xticks(1/x_indices)
    ax.yaxis.set_major_formatter(FuncFormatter(y_fmt))

    top = None
    label_datapoints = True

    plt.gca().set_ylim(bottom=0, top=top)
    plt.gca().set_xlim(left=0)
    
    if label_datapoints:
        for line in data:
            for i,j in zip(1/x_indices,line):
                ax.annotate(round(j,1),xy=(i,j))
            
            
    plt.grid(linestyle='--')
    plt.savefig(out_path,dpi=300)
    plt.show()
    plt.close('all')




def plot1(x_indices, data, errors, data_labels, x_axis_label, y_axis_label, out_path):
        
    plt.plot(x_indices, data[0],"-o")
    #plt.axis(x_indices)
    plt.ylabel(y_axis_label)
    plt.xlabel(x_axis_label)
    plt.show()








x_indices = np.array([1.0,0.9,0.8,0.7,0.6,0.5,0.4,0.3,0.2,0.1,0.05])

data = np.array([[0.3,0.6,3,4,5,6,7,8,9,3,4],[1,1,1,1,1,1,1,1,1,1,1]])
errors = np.array([[0,0,0,0,0,0,0,0,0,0,0]])
data_labels = np.array(["bla"])

x_axis_label = "fff"
y_axis_label = "yyy"
out_path = "G:/Johannes/test/test.png"

plot(x_indices, data, errors, data_labels, x_axis_label, y_axis_label, out_path)












