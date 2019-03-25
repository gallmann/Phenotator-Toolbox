# -*- coding: utf-8 -*-
"""
Created on Mon Mar 18 11:20:35 2019

@author: johan
"""

import osr
import gdal
import pyproj # Import the pyproj module
import json
import subprocess
import threading
import os

class GeoInformation(object):
    def __init__(self):
        self.lr_lon = 0
        self.lr_lat = 0
        self.ul_lon = 0
        self.ul_lat = 0
     

class PreprocessTool(object):
    
    pleaseStop = False
    
    def stop(self):
        self.pleaseStop = True
    
    def preprocess_internal(self, in_path, out_path, progress_callback):
        
        
        output_filename = 'tile_'
        tile_size_x = 3000
        tile_size_y = 3000
        
        
        
        
        inDS = gdal.Open(in_path)
        
        inSRS_wkt = inDS.GetProjection()  # gives SRS in WKT
        inSRS_converter = osr.SpatialReference()  # makes an empty spatial ref object
        inSRS_converter.ImportFromWkt(inSRS_wkt)  # populates the spatial ref object with our WKT SRS
        inSRS_forPyProj = inSRS_converter.ExportToProj4()  # Exports an SRS ref as a Proj4 string usable by PyProj
        
        
        swiss = pyproj.Proj(inSRS_forPyProj)
        wgs84=pyproj.Proj("+init=EPSG:4326") # LatLon with WGS84 datum used by GPS units and Google Earth
        
        ulx, xres, xskew, uly, yskew, yres  = inDS.GetGeoTransform()
        lrx = ulx + (inDS.RasterXSize * xres)
        lry = uly + (inDS.RasterYSize * yres)
        
        geo_info = GeoInformation()
        
        geo_info.lr_lon,geo_info.lr_lat  = pyproj.transform(swiss, wgs84, lrx, lry)
        geo_info.ul_lon,geo_info.ul_lat = pyproj.transform(swiss, wgs84, ulx, uly)
        
        
        
        ds = gdal.Open(in_path)
        band = ds.GetRasterBand(1)
        xsize = band.XSize
        ysize = band.YSize
        
        progress_callback(0.01)
    
        for i in range(0, xsize, tile_size_x):
            processes = []
            if self.pleaseStop:
                progress_callback(999)
                return
            for j in range(0, ysize, tile_size_y):
                out_path_image = str(out_path) + str(output_filename) + "row" + str(int(j/tile_size_y)) + "_col" + str(int(i/tile_size_x)) + ".png"
                out_path_json = str(out_path) + str(output_filename) + "row" + str(int(j/tile_size_y)) + "_col" + str(int(i/tile_size_x)) + "_geoinfo.json"
        
                com_string = "gdal_translate -b 1 -b 2 -b 3 -of png -srcwin " + str(i)+ ", " + str(j) + ", " + str(tile_size_x) + ", " + str(tile_size_y) + " " + str(in_path)  + " " + out_path_image 
                process = subprocess.Popen(com_string, shell=True)
                processes.append(process)
                
                
                
                #write geoinfo file
                geo_info_curr = GeoInformation()
                pixel_step_lon = (geo_info.lr_lon - geo_info.ul_lon)/xsize
                pixel_step_lat = (geo_info.lr_lat - geo_info.ul_lat)/ysize
        
                geo_info_curr.ul_lon = geo_info.ul_lon + i* pixel_step_lon
                geo_info_curr.ul_lat = geo_info.ul_lat + j* pixel_step_lat
                geo_info_curr.lr_lon = geo_info.ul_lon + (i+tile_size_x) * pixel_step_lon
                geo_info_curr.lr_lat = geo_info.ul_lat + (j+tile_size_x) * pixel_step_lat
        
                with open(out_path_json, 'w') as outfile:
                    json.dump(geo_info_curr.__dict__, outfile)
        
        
                
            for process in processes:
                process.wait()
            
            progress = min((i+tile_size_x)/xsize,1.0)
            
            progress_callback(progress)
    
        
    
    def preprocess(self, in_path, out_path, progress_callback):
            
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
        
        #in_path = 'C:/Users/johan/Desktop/Resources/orthoJPEG.tif'
        
        #out_path = 'C:/Users/johan/Desktop/Resources/Test/'
        thr = threading.Thread(target=self.preprocess_internal, args=[in_path,out_path,progress_callback], kwargs={})
        thr.daemon = True
        thr.start() 
        
        return ""
    
    

 