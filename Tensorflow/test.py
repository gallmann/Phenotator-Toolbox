# -*- coding: utf-8 -*-
"""
Created on Wed Aug 21 12:38:25 2019

@author: johan
"""



#https://matplotlib.org/3.1.0/api/_as_gen/matplotlib.pyplot.colorbar.html
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.image as mpimg
import numpy as np

color_ramp = [
   [255,255,255,0],
   [0,128,255,100],	#0080FF
   [63,159,191,100],	#3F9FBF
   [127,191,127,100],	#7FBF7F
   [191,223,63,100],	#BFDF3F
   [255,255,0,100],	#FFFF00
   [255,191,0,100],	#FFBF00
   [255,127,0,100],	#FF7F00
   [255,63,0,100], #FF3F00
   [255,0,0,100]
]

color_ramp = np.array(color_ramp)/255

cmap = mpl.colors.ListedColormap(color_ramp,N=len(color_ramp)-1)
cmap.set_over('red',100/255)



fig, axs = plt.subplots()

img = mpimg.imread("E:/heatmaps/ortho_tif_july_03_heatmap_overall.png")
imgplot = plt.imshow(img)
plt.axis('off')

imgplot.set_cmap(cmap)
imgplot.set_clim(0,10)

plt.colorbar(extend='max')

plt.savefig("E:/test.png",dpi=1000)








