#!/usr/bin/python

# PCRaster crashes on second file - start every processing in a separate process

import os
import glob
import subprocess

# files = glob.glob(r'./*.tif')
# files = glob.glob(r'./SRTM_30_Murray_Darling_5060088110.elevation.tif')
# files = glob.glob(r'./done/*.tif')
# files = glob.glob(r'./00.elevation.tif')
files = glob.glob(r'./SRTM_30_Asia_Andijan_4060421200.elevation.tif')

def convert_to_tif(input_path, output_path):
  cmd = u'gdal_translate -co COMPRESS=DEFLATE -co PREDICTOR=2 -co ZLEVEL=6 -of GTiff ' + input_path + ' ' + output_path
  subprocess.check_call(cmd, shell=True)

  # cmd = u'python ../src/flip_y.py ' + output_path
  # subprocess.check_call(cmd, shell=True)

  os.remove(input_path)

def copy_crs(input_path, output_path):
  print('Copying CRS from ' + input_path + ' to ' + output_path)
  cmd = u'python ../src/gdalcopyprj.py ' + input_path + ' ' + output_path
  subprocess.check_call(cmd, shell=True)

for f in files:
  cmd = u'python ../src/generate-hydro-datasets.py --input=' + f + ' --output=../output --step=ldd'
  subprocess.check_call(cmd, shell=True)

  cmd = u'python ../src/generate-hydro-datasets.py --input=' + f + ' --output=../output --step=ldddem'
  subprocess.check_call(cmd, shell=True)

  cmd = u'python ../src/generate-hydro-datasets.py --input=' + f + ' --output=../output --step=fa'
  subprocess.check_call(cmd, shell=True)

  cmd = u'python ../src/generate-hydro-datasets.py --input=' + f + ' --output=../output --step=catchments'
  subprocess.check_call(cmd, shell=True)

  cmd = u'python ../src/generate-hydro-datasets.py --input=' + f + ' --output=../output --step=stream_order'
  subprocess.check_call(cmd, shell=True)

  cmd = u'python ../src/generate-hydro-datasets.py --input=' + f + ' --output=../output --step=stream'
  subprocess.check_call(cmd, shell=True)

  cmd = u'python ../src/generate-hydro-datasets.py --input=' + f + ' --output=../output --step=height_river'
  subprocess.check_call(cmd, shell=True)

  cmd = u'python ../src/generate-hydro-datasets.py --input=' + f + ' --output=../output --step=up_elevation'
  subprocess.check_call(cmd, shell=True)

  cmd = u'python ../src/generate-hydro-datasets.py --input=' + f + ' --output=../output --step=hand'
  subprocess.check_call(cmd, shell=True)

  cmd = u'python ../src/generate-hydro-datasets.py --input=' + f + ' --output=../output --step=dand'
  subprocess.check_call(cmd, shell=True)

  cmd = u'python ../src/generate-hydro-datasets.py --input=' + f + ' --output=../output --step=fa_river'
  subprocess.check_call(cmd, shell=True)

  cmd = u'python ../src/generate-hydro-datasets.py --input=' + f + ' --output=../output --step=faand'
  subprocess.check_call(cmd, shell=True)

  file_name = os.path.splitext(os.path.basename(f))[0]
  map_path = '../output/' + file_name + '.map'
  path_prefix = map_path[:-14]

  os.remove(map_path)

  print('Converting results to GeoTIFF ...')
  convert_to_tif(path_prefix + '_ldd.map', path_prefix + '_ldd.tif')
  convert_to_tif(path_prefix + '_dem_pits_diff.map', path_prefix + '_dem_pits_diff.tif')

  convert_to_tif(path_prefix + '_fa.map', path_prefix + '_fa.tif')
  convert_to_tif(path_prefix + '_faand.map', path_prefix + '_faand.tif')
  convert_to_tif(path_prefix + '_hand.map', path_prefix + '_hand.tif')
  convert_to_tif(path_prefix + '_dist.map', path_prefix + '_dist.tif')
  convert_to_tif(path_prefix + '_catchments.map', path_prefix + '_catchments.tif')

  copy_crs(f, path_prefix + '_ldd.tif')
  copy_crs(f, path_prefix + '_dem_pits_diff.tif')

  copy_crs(f, path_prefix + '_fa.tif')
  copy_crs(f, path_prefix + '_faand.tif')
  copy_crs(f, path_prefix + '_hand.tif')
  copy_crs(f, path_prefix + '_dist.tif')
  copy_crs(f, path_prefix + '_catchments.tif')

  cmd = u'mv ./' + file_name + '.* ./done/'
  subprocess.check_call(cmd, shell=True)

  cmd = u'rm ../output/*.map'
  subprocess.check_call(cmd, shell=True)
 

