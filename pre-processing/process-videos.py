import cv2
import os
import glob
import sys

def main(dirname):
  ## im just going to change this to use os
  video_dir = dirname
  files = [x for x in os.listdir(dirname) if '.MP4' in x]
  for i, filename in enumerate(files): 
    vidcap = cv2.VideoCapture(video_dir+filename)
    capLength = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
    if capLength==0:
      continue
    success,image = vidcap.read()
    success = True
    foldername = filename.split(".")[0]
    path=dirname+foldername
    if os.path.exists(path):
      continue
    else:
      os.makedirs(path, 755)
    count=0
    while success:
      success,image = vidcap.read()
      sys.stdout.write("Processing Video %d of %d: %.2f%% Completed       \r" % (i+1, len(files), float(count+1) * 100 / capLength))
      sys.stdout.flush()
      if count % (3*59) is 1:    
        img_path = path+"/frame%d.jpg" % count
        if not os.path.exists(img_path):
          cv2.imwrite(img_path, image)    
      count += 1
    sys.stdout.write('Video Processed                                           \n')

if __name__ == "__main__":
    data_directories = ['20170607_PM_Peak_Albany_Hwy/', '20170608_AM_PEAK_Orrong_Road/', '20170608_AM_PEAK_Orrong_Road/']
    for j, directory in enumerate(data_directories):
      sys.stdout.write("Getting Files for Directory %d of %d: %s                      \n" % (j+1, len(data_directories), directory))
      main(directory)