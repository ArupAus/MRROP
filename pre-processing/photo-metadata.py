import exifread 
import os 
import numpy as np 
import re 
import sys
import json
import ast
from PIL import Image 
from PIL.ExifTags import TAGS

# data_directories = ['20170607_AM_PEAK_Albany_Hwy/', '20170607_PM_Peak_Albany_Hwy/', '20170608_AM_PEAK_Orrong_Road', '20170608_AM_PEAK_Orrong_Road']
data_directories = ['20170607_AM_PEAK_Albany_Hwy/']

imageDict = {}
for directory in data_directories:
    imageDict[directory] = {}
    dirs = [directory + d + "/" for d in os.listdir(directory) if os.path.isdir(os.path.join(directory, d))]
    for dd in dirs:
        images = [dd + i for i in os.listdir(dd)] 
        if len(images) > 0:
            test_image = images[1]
        imageDict[directory][dd] = [i.split(dd)[1] for i in images]

print test_image
i = Image.open(test_image)
info = i._getexif()
for tag, value in info.items():
    decoded = TAGS.get(tag, tag)
    print decoded, value

with open("images.json", "wb") as f:
    json.dump(imageDict, f, indent=2)
        
