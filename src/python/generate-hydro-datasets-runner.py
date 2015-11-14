#!/usr/bin/python

# PCRaster crashes on second file - start every processing in a separate process

import os
import glob
import subprocess

files = glob.glob(r'./*.zip')
# files = glob.glob(r'./SRTM_30_Murray_Darling_5060088110.elevation.tif')
# files = glob.glob(r'./done/*.tif')
# files = glob.glob(r'./00.elevation.tif')
# files = glob.glob(r'./SRTM_30_Asia_Andijan_4060421200.elevation.tif')

def convert_to_tif(input_path, output_path, remove=True):
  cmd = u'gdal_translate -co COMPRESS=DEFLATE -co PREDICTOR=2 -co ZLEVEL=6 -of GTiff ' + input_path + ' ' + output_path
  subprocess.check_call(cmd, shell=True)

  if remove:
    os.remove(input_path)

def copy_crs(input_path, output_path):
  print('Copying CRS from ' + input_path + ' to ' + output_path)
  cmd = u'python ' + src + '/gdalcopyprj.py ' + input_path + ' ' + output_path
  subprocess.check_call(cmd, shell=True)

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description = 'Computes HAND.')
    
    parser.add_argument('--script_home', nargs = '?', help = 'home directory of a script used to generate HAND', required = True)
    parser.add_argument('--output', nargs = '?', help = 'output directory', required = True)

    args = parser.parse_args()

    src = args.script_home
    output = args.output

    cmd = u'mkdir -p ' + output
    subprocess.check_call(cmd, shell=True)

    for fzip in files:
      cmd = u'unzip ' + fzip
      subprocess.check_call(cmd, shell=True)

      f = './' + os.path.splitext(os.path.basename(fzip))[0] + '.elevation.tif'

      cmd = u'python ' + src + '/generate-hydro-datasets.py --input=' + f + ' --output=' + output + ' --step=ldd'
      subprocess.check_call(cmd, shell=True)
    
      cmd = u'python ' + src + '/generate-hydro-datasets.py --input=' + f + ' --output=' + output + ' --step=ldddem'
      subprocess.check_call(cmd, shell=True)

      cmd = u'python ' + src + '/generate-hydro-datasets.py --input=' + f + ' --output=' + output + ' --step=fa'
      subprocess.check_call(cmd, shell=True)

      cmd = u'python ' + src + '/generate-hydro-datasets.py --input=' + f + ' --output=' + output + ' --step=catchments'
      subprocess.check_call(cmd, shell=True)

      cmd = u'python ' + src + '/generate-hydro-datasets.py --input=' + f + ' --output=' + output + ' --step=stream_order'
      subprocess.check_call(cmd, shell=True)

      cmd = u'python ' + src + '/generate-hydro-datasets.py --input=' + f + ' --output=' + output + ' --step=stream'
      subprocess.check_call(cmd, shell=True)
    
      cmd = u'python ' + src + '/generate-hydro-datasets.py --input=' + f + ' --output=' + output + ' --step=height_river'
      subprocess.check_call(cmd, shell=True)
    
      cmd = u'python ' + src + '/generate-hydro-datasets.py --input=' + f + ' --output=' + output + ' --step=up_elevation'
      subprocess.check_call(cmd, shell=True)
    
      cmd = u'python ' + src + '/generate-hydro-datasets.py --input=' + f + ' --output=' + output + ' --step=hand'
      subprocess.check_call(cmd, shell=True)
    
      cmd = u'python ' + src + '/generate-hydro-datasets.py --input=' + f + ' --output=' + output + ' --step=dand'
      subprocess.check_call(cmd, shell=True)
    
      cmd = u'python ' + src + '/generate-hydro-datasets.py --input=' + f + ' --output=' + output + ' --step=fa_river'
      subprocess.check_call(cmd, shell=True)
    
      cmd = u'python ' + src + '/generate-hydro-datasets.py --input=' + f + ' --output=' + output + ' --step=faand'
      subprocess.check_call(cmd, shell=True)

      file_name = os.path.splitext(os.path.basename(f))[0]
      map_path = '' + output + '/' + file_name + '.map'
      path_prefix = map_path[:-14]
    
      os.remove(map_path)
    
      print('Converting results to GeoTIFF ...')
      convert_to_tif(path_prefix + '_ldd.map', path_prefix + '_ldd.tif', True)
      convert_to_tif(path_prefix + '_dem_pits_diff.map', path_prefix + '_dem_pits_diff.tif', True)
    
      convert_to_tif(path_prefix + '_fa.map', path_prefix + '_fa.tif', True)
      convert_to_tif(path_prefix + '_faand.map', path_prefix + '_faand.tif', True)
      convert_to_tif(path_prefix + '_hand.map', path_prefix + '_hand.tif', True)
      convert_to_tif(path_prefix + '_dist.map', path_prefix + '_dist.tif', True)
      convert_to_tif(path_prefix + '_catchments.map', path_prefix + '_catchments.tif', True)

      copy_crs(f, path_prefix + '_ldd.tif')
      copy_crs(f, path_prefix + '_dem_pits_diff.tif')
    
      copy_crs(f, path_prefix + '_fa.tif')
      copy_crs(f, path_prefix + '_faand.tif')
      copy_crs(f, path_prefix + '_hand.tif')
      copy_crs(f, path_prefix + '_dist.tif')
      copy_crs(f, path_prefix + '_catchments.tif')
    
      # recompress elevation
      convert_to_tif(f, path_prefix + '.dem.tif', False)
      copy_crs(f, path_prefix + '.dem.tif')

      cmd = u'rm -f ' + map_path
      subprocess.check_call(cmd, shell=True)
    
      cmd = u'rm -f ' + f
      subprocess.check_call(cmd, shell=True)

      cmd = u'rm -f ' + path_prefix + '_fa_river.map'
      subprocess.check_call(cmd, shell=True)

      cmd = u'rm -f ' + path_prefix + '_height_river.map'
      subprocess.check_call(cmd, shell=True)

      cmd = u'rm -f ' + path_prefix + '_stream.map'
      subprocess.check_call(cmd, shell=True)

      cmd = u'rm -f ' + path_prefix + '_streamorder.map'
      subprocess.check_call(cmd, shell=True)

      cmd = u'rm -f ' + path_prefix + '_up_elevation.map'
      subprocess.check_call(cmd, shell=True)
    
      cmd = u'rm -f ' + path_prefix + '.elevation.map.aux.xml'
      subprocess.check_call(cmd, shell=True)

      cmd = u'rm -f ./' + file_name + '.elevation.tfw'
      subprocess.check_call(cmd, shell=True)
    
      cmd = u'mkdir -p ./done/'
      subprocess.check_call(cmd, shell=True)

      cmd = u'mv ' + fzip + ' ./done/'
      subprocess.check_call(cmd, shell=True)
    

