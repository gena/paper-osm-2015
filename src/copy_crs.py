#!/usr/bin/python

# PCRaster crashes on second file - start every processing in a separate process

import os
import glob
import subprocess

files = glob.glob(r'./output/*.tif')

def set_crs(input_path, output_path):
  print('Assigning CRS to ' + input_path)
  cmd = u'gdalwarp -co COMPRESS=DEFLATE -co PREDICTOR=2 -co ZLEVEL=6 ' + input_path + ' ' + output_path + ' -t_srs "+proj=longlat +ellps=WGS84"'
  subprocess.check_call(cmd, shell=True)

for f in files:
  file_name = os.path.splitext(os.path.basename(f))[0]
  
  set_crs(f, './output_reproject/' + file_name + '.tif')
