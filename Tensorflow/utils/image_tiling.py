# -*- coding: utf-8 -*-
"""
Created on Mon Apr  1 17:28:56 2019

@author: johan
"""

import Image
import sys



tile_size = 512


def tile_image(image_path, output_folder):
    
    image = Image.open(image_path)
    
    if image.size[0] % tile_width == 0 and image.size[1] % tile_height ==0 :
        currentx = 0
        currenty = 0
        while currenty < image.size[1]:
            while currentx < image.size[0]:
                print currentx,",",currenty
                tile = image.crop((currentx,currenty,currentx + tile_width,
                                      currenty + tile_height))
                tile.save("x" + str(currentx) + "y" + str(currenty
                                            ) + "z" + zoom_level + ".png","PNG")
                currentx += tile_width
                currenty += tile_height
                currentx = 0
    else:
        print ("sorry your image does not fit neatly into",
                    tile_width,"*",tile_height,"tiles")
