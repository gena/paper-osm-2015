import glob
import os
import subprocess

import numpy.ma as ma
import pcraster as pcr

def generate_hydro_datasets(path, output_dir, step):
  print(path)

  file_name = os.path.splitext(os.path.basename(path))[0]
  map_path = output_dir + '/' + file_name + '.map'
  path_prefix = map_path[:-14]

  if step == 'ldd':
    cmd = u'gdal_translate -a_nodata 0 -of PCRaster -ot Float32 ' + path + ' ' + map_path
    print(cmd)
    subprocess.call(cmd, shell=True)

  # slope = pcr.slope(dem)
  # pcr.report(slope, path_prefix + '_slope.map')

  # pcr.setglobaloption("lddin")

  if step == 'ldd':
    dem = pcr.readmap(map_path)

    print("Computing LDD ...")
    # enable pit filling
    ldd = pcr.lddcreate(dem, 9999999, 9999999, 9999999, 9999999)
    pcr.report(ldd, path_prefix + '_ldd.map')

    return
  elif step == 'ldddem':
    dem = pcr.readmap(map_path)

    print("Computing LDD DEM ...")
    dem_pitfilled = pcr.lddcreatedem(dem, 9999999, 9999999, 9999999, 9999999)
    dem_diff = dem_pitfilled - dem
    pcr.report(dem_diff, path_prefix + '_dem_pits_diff.map')

    return

  # print("Computing LDD without pit filling ...")
  # ldd_pits = pcr.lddcreate(dem, 0, 0, 0, 0)
  # pcr.report(ldd_pits, path_prefix + '_ldd_with_pits.map')

  # print("Computing pits ...")
  # pits = pcr.pit(ldd_pits)

  # pcr.report(pits, path_prefix + '_pits.map')

  if step == 'fa':
    ldd = pcr.readmap(path_prefix + '_ldd.map')

    print("Computing flow accumulation ...")
    fa = pcr.accuflux(ldd, 1)
    pcr.report(fa, path_prefix + '_fa.map')

    return

  if step == 'catchments':
    ldd = pcr.readmap(path_prefix + '_ldd.map')

    print("Delineating catchments ...")
    catchments = pcr.catchment(ldd, pcr.pit(ldd))
    pcr.report(catchments, path_prefix + '_catchments.map')

    return

  if step == 'stream_order':
    ldd = pcr.readmap(path_prefix + '_ldd.map')

    print("Computing stream order ...")
    stream_order = pcr.streamorder(ldd)
    pcr.report(stream_order, path_prefix + '_streamorder.map')
  
    return

  if step == 'stream':
    ldd = pcr.readmap(path_prefix + '_ldd.map')
    accuThreshold = 10000
    print("Computing stream ...")
    stream = pcr.ifthenelse(pcr.accuflux(ldd, 1) >= accuThreshold, pcr.boolean(1), pcr.boolean(0))
    pcr.report(stream, path_prefix + '_stream.map')
    return

  if step == 'height_river':
    print("Computing heigh_river ...")

    stream = pcr.readmap(path_prefix + '_stream.map')
    dem = pcr.readmap(map_path)
    height_river = pcr.ifthenelse(stream, pcr.ordinal(dem), 0)
    pcr.report(height_river, path_prefix + '_height_river.map')
    return

  if step == 'up_elevation':
    print("Computing up_elevation ...")

    height_river = pcr.readmap(path_prefix + '_height_river.map')
    ldd = pcr.readmap(path_prefix + '_ldd.map')
    up_elevation = pcr.scalar(pcr.subcatchment(ldd, height_river))
    pcr.report(up_elevation, path_prefix + '_up_elevation.map')
    return

  if step == 'hand':
    print("Computing HAND ...")
    dem = pcr.readmap(map_path)
    up_elevation = pcr.readmap(path_prefix + '_up_elevation.map')
    hand = pcr.max(dem-up_elevation, 0)
    pcr.report(hand, path_prefix + '_hand.map')
    return

  if step == 'dand':
    print("Computing DAND ...")
    ldd = pcr.readmap(path_prefix + '_ldd.map')
    stream = pcr.readmap(path_prefix + '_stream.map')
    dist = pcr.ldddist(ldd, stream, 1)
    pcr.report(dist, path_prefix + '_dist.map')
    return
 
  if step == 'fa_river':
    print("Computing FA river ...")
    fa = pcr.readmap(path_prefix + '_fa.map') 
    stream = pcr.readmap(path_prefix + '_stream.map')
    fa_river = pcr.ifthenelse(stream, pcr.ordinal(fa), 0)
    pcr.report(fa_river, path_prefix + '_fa_river.map')
    return

  if step == 'faand':
    print("Computing FAAND ...")
    fa_river = pcr.readmap(path_prefix + '_fa_river.map')
    ldd = pcr.readmap(path_prefix + '_ldd.map')
    up_fa = pcr.scalar(pcr.subcatchment(ldd, fa_river))
    pcr.report(up_fa, path_prefix + '_faand.map')
    return

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description = 'Generates hydrological datasets given DEM file.')

    parser.add_argument('--input', nargs = '?', help = 'input DEM file', required = True)
    parser.add_argument('--output', nargs = '?', help = 'output directory', required = True)
    parser.add_argument("--step", type=str, choices=['ldd', 'ldddem', 'fa', 'catchments', 'stream_order', 'faand', 'fa_river', 'dand', 'height_river', 'up_elevation', 'hand','stream'], required = True)

    args = parser.parse_args()

    generate_hydro_datasets(args.input, args.output, args.step)

