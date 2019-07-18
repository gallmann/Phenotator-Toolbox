# -*- coding: utf-8 -*-
"""
Created on Mon Mar 18 11:20:35 2019

@author: johan
"""

import osr
import gdal
import json
import threading
import os
import pyproj


class GeoInformation(object):
    def __init__(self):
        self.lr_lon = 0
        self.lr_lat = 0
        self.ul_lon = 0
        self.ul_lat = 0
     

class PreprocessTool(object):
    
    pleaseStop = False
    
    #Method called when the user pressed the cancel button to stop the translation process
    def stop(self):
        self.pleaseStop = True
        
    
    def preprocess_internal(self, in_path, out_path, progress_callback):
        
        #fixed tile size
        output_filename = 'tile_'
        tile_size_x = 5120
        tile_size_y = 5120
        
        #Read the input Coordinate system
        ds = gdal.Open(in_path)
        inSRS_wkt = ds.GetProjection()  # gives SRS in WKT
        inSRS_converter = osr.SpatialReference()  # makes an empty spatial ref object
        inSRS_converter.ImportFromWkt(inSRS_wkt)  # populates the spatial ref object with our WKT SRS
        inSRS_forPyProj = inSRS_converter.ExportToProj4()  # Exports an SRS ref as a Proj4 string usable by PyProj
        
        print("coord_system: " + str(inSRS_forPyProj))
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
        
        #indicate to UI that the process of tiling has started (progress of 1%)
        progress_callback(0.01)
    
        #Tiling the image
        for i in range(0, xsize, tile_size_x):
            for j in range(0, ysize, tile_size_y):
                #check if user pressed stop button
                if self.pleaseStop:
                    progress_callback(999)
                    return
                
                #define paths of image tile and the corresponding json file containing the geo information
                out_path_image = str(out_path) + str(output_filename) + "row" + str(int(j/tile_size_y)) + "_col" + str(int(i/tile_size_x)) + ".png"
                out_path_json = str(out_path) + str(output_filename) + "row" + str(int(j/tile_size_y)) + "_col" + str(int(i/tile_size_x)) + "_geoinfo.json"
                
                #tile image with gdal (copy bands 1, 2 and 3)
                gdal.Translate(out_path_image,ds, options=gdal.TranslateOptions(srcWin=[i,j,tile_size_x,tile_size_y], bandList=[1,2,3], format='png'))
                
                #update UI progressbar
                y_progress = min((j+tile_size_y)/ysize,1.0)
                progress = min((i+ y_progress*tile_size_x)/xsize,0.99)
                progress_callback(progress)

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

            #update UI progressbar
            progress = min((i+tile_size_x)/xsize,1.0)
            progress_callback(progress)
    
        
    
    def preprocess(self, in_path, out_path, progress_callback):
            
        #Some sanity checks
        try:
            fh = open(in_path, 'r')
        except FileNotFoundError:
            return "Input File not found!"
    
        if not os.path.isdir(out_path):
            return "Output Directory not found!"
    
        
        if(in_path.endswith("/") or in_path.endswith("\\")):
            in_path = in_path[:-1]
        
        if(not out_path.endswith("/") and not out_path.endswith("\\")):
            out_path = out_path + "/"
    
        if(not in_path.endswith(".tif")):
            return "Input File must be a .tif file!"
        
        #start a new thread with the tiling process
        thr = threading.Thread(target=self.preprocess_internal, args=[in_path,out_path,progress_callback], kwargs={})
        thr.daemon = True
        thr.start() 
        
        return ""
    
    

 