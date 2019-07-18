# -*- coding: utf-8 -*-
"""
Created on Mon Mar 18 11:20:35 2019

@author: johan


This script tiles a large image that is to be annotated on the tablet. The output
of the script is a folder that can be copied onto an Android tablet and imported into 
the Annotation App.


"""

print("Loading libraries...")
import osr
import gdal
import json
import os
import pyproj
import progressbar


class GeoInformation(object):
    def __init__(self):
        self.lr_lon = 0
        self.lr_lat = 0
        self.ul_lon = 0
        self.ul_lat = 0
     
    
def preprocess_internal(in_path, out_path, tile_size = 5120):
    """
    Given an input-image (any format) and an output-folder,
    the command tiles the input-image into tiles of suitable size for an android
    tablet. If the input image is georeferenced (can be georeferenced tif or other image format with
    a imagename.imageformat.aux.xml file in the same folder(=>see gdal)), the script generates
    additional files with geo information that are read and used by the tablet app
    for displaying the user location. An additional advantage of using a georeferenced image as input
    is that after annotating on the tablet, all annotations can be copied onto other georeferenced
    images with the copy-annotations commmand.

    Parameters:
        in_path (str): path to the input image
        out_path (str): path of the output folder
        tile_size (str): the size of the tile (square shaped)
        
    Returns:
        None, a folder that can bi copied onto the android tablet.
    """

    #fixed tile size
    output_filename = 'tile_'
    tile_size_x = tile_size
    tile_size_y = tile_size
    
    #Read the input Coordinate system
    ds = gdal.Open(in_path)
    inSRS_wkt = ds.GetProjection()  # gives SRS in WKT
    inSRS_converter = osr.SpatialReference()  # makes an empty spatial ref object
    inSRS_converter.ImportFromWkt(inSRS_wkt)  # populates the spatial ref object with our WKT SRS
    inSRS_forPyProj = inSRS_converter.ExportToProj4()  # Exports an SRS ref as a Proj4 string usable by PyProj
    
    create_geoinfo_file = True
    try:
        #swiss represents the coordinate system of the georeferenced image saved at in_path
        #this should be the swiss coordinate system CH1903+ / LV95 ("+init=EPSG:2056")
        swiss = pyproj.Proj(inSRS_forPyProj) 
    except RuntimeError:
        create_geoinfo_file = False
    # LatLon with WGS84 datum used by GPS units and Google Earth
    wgs84=pyproj.Proj("+init=EPSG:4326") 
    
    #GetGeoTransform() returns the upper left coordinates in the input (swiss) coordinate system (ulx,uly)
    #xres and yres denote the width and height of a pixel
    #xskew and yskew is the tilt. This should be 0
    ulx, xres, xskew, uly, yskew, yres  = ds.GetGeoTransform()                
    
    #get the size of the input image
    band = ds.GetRasterBand(1)
    xsize = band.XSize
    ysize = band.YSize
    
    print("Tiling image...")
    #Tiling the image
    for i in progressbar.progressbar(range(0, xsize, tile_size_x)):
        for j in range(0, ysize, tile_size_y):
            
            #define paths of image tile and the corresponding json file containing the geo information
            out_path_image = str(out_path) + str(output_filename) + "row" + str(int(j/tile_size_y)) + "_col" + str(int(i/tile_size_x)) + ".png"
            out_path_json = str(out_path) + str(output_filename) + "row" + str(int(j/tile_size_y)) + "_col" + str(int(i/tile_size_x)) + "_geoinfo.json"
            
            #tile image with gdal (copy bands 1, 2 and 3)
            gdal.Translate(out_path_image,ds, options=gdal.TranslateOptions(srcWin=[i,j,tile_size_x,tile_size_y], bandList=[1,2,3], format='png'))
            

            if create_geoinfo_file:
                #calculate upper left and lower right coordinates of image tile
                geo_info_curr = GeoInformation()
                geo_info_curr.ul_lon = ulx + (i * xres)
                geo_info_curr.ul_lat = uly + j* yres
                geo_info_curr.lr_lon = ulx + (i+tile_size_x) * xres
                geo_info_curr.lr_lat = uly + (j+tile_size_x) * yres
                
                #convert them to wgs84
                geo_info_curr.lr_lon,geo_info_curr.lr_lat  = pyproj.transform(swiss, wgs84, geo_info_curr.lr_lon, geo_info_curr.lr_lat)
                geo_info_curr.ul_lon,geo_info_curr.ul_lat = pyproj.transform(swiss, wgs84, geo_info_curr.ul_lon, geo_info_curr.ul_lat)

                #save geoinfo file
                with open(out_path_json, 'w') as outfile:
                    json.dump(geo_info_curr.__dict__, outfile)
    
            if os.path.isfile(out_path_image + ".aux.xml"):
                os.remove(out_path_image + ".aux.xml")

        
    
def preprocess(in_path, out_path,tile_size=5120):
    """
    Does some sanity checks on the input parameters before passing them on to
    the preprocess_internal(...) function

    Parameters:
        in_path (str): path to the input image
        out_path (str): path of the output folder
        tile_size (str): the size of the tile (square shaped)
        
    Returns:
        None, a folder that can bi copied onto the android tablet.
    """

    #Some sanity checks
    try:
        fh = open(in_path, 'r')
    except FileNotFoundError:
        print("Input File not found!")
        return

    if not os.path.isdir(out_path):
        print("Output Directory not found!")
        return

    
    if(in_path.endswith("/") or in_path.endswith("\\")):
        in_path = in_path[:-1]
    
    if(not out_path.endswith("/") and not out_path.endswith("\\")):
        out_path = out_path + "/"
    '''
    if(not in_path.endswith(".tif")):
        print("Input File must be a .tif file!")
        return
    '''
    preprocess_internal(in_path,out_path,tile_size)
    

 