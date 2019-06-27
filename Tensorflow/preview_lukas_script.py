# -*- coding: utf-8 -*-
"""
Created on Tue Jun 25 12:28:11 2019

@author: johan
"""

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib import pyplot as plt
import imageio
import geopandas as gpd
from matplotlib.collections import  PatchCollection
from matplotlib.patches import Rectangle, Polygon
from descartes import PolygonPatch


regions = gpd.read_file('C:/Users/johan/Desktop/MSc_Gallmann__DSC6187.geojson')
image = imageio.imread('C:/Users/johan/Desktop/_DSC6187.JPG')

# Create shapes
polygons = []
regions_geometries = regions.geometry
for regions_geometry in regions_geometries:
    polygons.append(PolygonPatch(regions_geometry))

pc_polygons = PatchCollection(polygons, facecolor='none', edgecolor="white", linewidth=0.3)

fig, ax = plt.subplots(1)

ax.imshow(image)
ax.add_collection(pc_polygons)

plt.show()
