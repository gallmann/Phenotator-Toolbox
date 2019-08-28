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
import math
import numpy as np
from PIL import Image
from concurrent.futures import ThreadPoolExecutor
import time

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
        
    
    def preprocess_internal(self, in_path, out_path, callback=None, tile_size = 256):
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
    
        with ThreadPoolExecutor(max_workers=10) as executor:
    
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
            
            if create_geoinfo_file:
                #GetGeoTransform() returns the upper left coordinates in the input (swiss) coordinate system (ulx,uly)
                #xres and yres denote the width and height of a pixel
                #xskew and yskew is the tilt. This should be 0
                ulx, xres, xskew, uly, yskew, yres  = ds.GetGeoTransform()                
                
                lrx = ulx + (ds.RasterXSize * xres)
                lry = uly + (ds.RasterYSize * yres)
                
                lrx,lry = pyproj.transform(swiss, wgs84, lrx, lry)
                ulx,uly = pyproj.transform(swiss, wgs84, ulx, uly)
            else:
                lrx = lry = ulx = uly = 0.0
    
            
            
            
            
            
            
            
            
            #get the size of the input image
            band = ds.GetRasterBand(1)
            xsize = band.XSize
            ysize = band.YSize
            
            print("Loading input image of size " + str(xsize) + "x" + str(ysize) + "...")
            image_array = ds.ReadAsArray().astype(np.uint8)
            image_array = np.swapaxes(image_array,0,1)
            image_array = np.swapaxes(image_array,1,2)
        
    
        
            futures_list = []
            number_of_zoom_levels = int(min(math.floor(math.log(xsize/tile_size,2)), math.floor(math.log(ysize/tile_size,2))))
            
            
            
            #creating meta data file
            metadata = {"lrx":lrx, "lry": lry, "ulx":ulx, "uly":uly}
            metadata["zoomlevels"] = number_of_zoom_levels
            metadata["imageWidth"] = xsize
            metadata["imageHeight"] = ysize
            metadata["tileSize"] = tile_size
            
            metadata_path = os.path.join(out_path,"metadata.json")
            #save metadata file
            with open(metadata_path, 'w') as outfile:
                json.dump(metadata, outfile)
    
            
            
            
            
            
            
            print("Tiling image into " + str(number_of_zoom_levels) + " zoom levels...")
            for zoom_level in (range(0,number_of_zoom_levels)):
                
                os.makedirs(os.path.join(out_path,str(zoom_level)),exist_ok=True)
                original_tilesize = tile_size*2**(zoom_level)
                #Tiling the image
                for x_start in range(0, xsize, original_tilesize):
                    for y_start in range(0, ysize, original_tilesize):
                        #define paths of image tile and the corresponding json file containing the geo information
                        out_path_image = str(out_path) + str(zoom_level) + "/tile_level" + str(zoom_level) + "_x" + str(int(x_start/original_tilesize)) + "_y" + str(int(y_start/original_tilesize)) + ".png"
                        #out_path_json = str(out_path) + str(output_filename) + "row" + str(int(j/tile_size_y)) + "_col" + str(int(i/tile_size_x)) + "_geoinfo.json"
    
                        future = executor.submit(self.crop_image,tile_size,ds, original_tilesize,image_array,y_start,x_start,out_path_image)
                        futures_list.append(future)
                        
    
                        
            for i in range(0,len(futures_list)):
                callback(i/len(futures_list))
                while not futures_list[i].done():
                    time.sleep(0.5)
                       
    
            callback(999)
                    
            '''
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
            '''



    def crop_image(self, tile_size, ds, original_tilesize,image_array,y_start,x_start,out_path_image):
        if not self.pleaseStop:
            if original_tilesize < 10000:
    
                            #crop_image(tile_size, original_tilesize,image_array,y_start,x_start,out_path_image)
                cropped_array = image_array[y_start:y_start+original_tilesize,x_start:x_start+original_tilesize,:]
    
                pad_end_x = original_tilesize - cropped_array.shape[1]
                pad_end_y = original_tilesize - cropped_array.shape[0]
                cropped_array = np.pad(cropped_array,((0,pad_end_y),(0,pad_end_x),(0,0)), mode='constant', constant_values=0)
                cropped_im = Image.fromarray(cropped_array,'RGB')
                cropped_im = cropped_im.resize((tile_size,tile_size), Image.ANTIALIAS)
                cropped_im.save(out_path_image)
            else:
                gdal.Translate(out_path_image,ds, options=gdal.TranslateOptions(width=int(tile_size),height=int(tile_size),srcWin=[x_start,y_start,original_tilesize,original_tilesize], bandList=[1,2,3], format='png'))
                if os.path.isfile(out_path_image + ".aux.xml"):
                    os.remove(out_path_image + ".aux.xml")
    
        
    
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
    
    

 