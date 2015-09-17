#!/usr/bin/env python
"""
Created on Sat Nov 16 11:19:58 2014

@author: Hessel Winsemius and Tarasinta Perwitasari

The functions in this file dig and fill values in a space-borne 
digital elevation model following streamlines as given in a local 
drain direction file. The correction procedure ensures that a stream line
always flows down or remains horizontally. Regions where the elevation lifts
in downstream direction are "digged out"  in downstream direction, or "filled
up" in upstream direction. 

The filling and digging is necessary to remove the
effect of noise, too low resolution with respect to the channel dimensions
or effects of vegetation or islands within the river channel and to ensure
the DEM can be used in hydraulic modelling of river reaches. Typically, this
should be applied before using SRTM HydroSHEDS elevation and flow directions

The methods followed are described in:

Yamazaki, D., Baugh, C. A., Bates, P. D., Kanae, S., Alsdorf, D. E. and 
Oki, T.: Adjustment of a spaceborne DEM for use in floodplain hydrodynamic 
modeling, J. Hydrol., 436-437, 81-91, doi:10.1016/j.jhydrol.2012.02.045,
2012.

Call the function dem_fill_dig to get started.

This tool is part of the hydrotools toolbox in the openearthtools suite.

"""

import numpy as np
from osgeo import gdal
import os
import sys
import pdb
import pandas as pd
from gdal_readmap import gdal_readmap
from gdal_writemap import gdal_writemap
import matplotlib.pyplot as plt
from scipy.signal import convolve2d


def find_downstream(ldd, idx_y, idx_x, flow_dirs=np.array([[7, 8, 9], [4, 5, 6], [1, 2, 3]])):
    """
    Find the index postiion of the first downstream cell
    
    """
    flow_dir_y = np.array([-1, 0, 1])
    flow_dir_x = np.array([-1, 0, 1])
    
    flow_dir = np.where(flow_dirs==ldd[idx_y, idx_x])
    y_dir, x_dir = flow_dir_y[flow_dir[0]], flow_dir_x[flow_dir[1]]
    idx_y_new = idx_y + y_dir[0]
    idx_x_new = idx_x + x_dir[0]
    return idx_y_new, idx_x_new

def catch_boundary(ldd, pit, ldd_fill, flow_dirs=np.array([[7, 8, 9], [4, 5, 6], [1, 2, 3]])):
    """Establishes which cells on an ldd lie on a catchment boundary (i.e. do 
    not have any upstream inflow points)
    """
    upstream_cells = np.zeros(ldd.shape)
    for dir_x in range(0, 3):
        for dir_y in range(0, 3):
            if np.logical_or(dir_x != 1, dir_y != 1): # only do this if the 
                                                      # cell is not itself!
                rev_flow_dir = flow_dirs[dir_y, dir_x]  # establish reverse 
                                                        # flow direction
                conv_arr = np.zeros((3, 3)); conv_arr[dir_y, dir_x] = 1.
                upstream_cells += np.int16(convolve2d(ldd,
                                                      conv_arr,
                                                      mode='same') == rev_flow_dir)
            # find where no upstream is found
    upstream_cells[ldd == ldd_fill] = ldd_fill
    catch_bound = upstream_cells == 0
    idx = np.where(catch_bound)

    return idx, catch_bound


def stream_length(ldd, idx_upstream, pit,
                  flow_dirs=np.array([[7, 8, 9], [4, 5, 6], [1, 2, 3]]),
                  streams=None, upstream_points=None):
    """
    Calculate stream lengths by looping over all cells that lie on an upstream
    boundary.
    """
    if not(streams):
        streams = np.zeros(ldd.shape)
    if not(upstream_points):
        upstream_points = {}
        upstream_points['coordinates'] = zip(*idx_upstream)
        upstream_points['lengths'] = []
    else:
        upstream_points['coordinates'] += zip(*idx_upstream)
    for n, idx in enumerate(zip(*idx_upstream)):
        # find the positions of the downstream cells
        idx_down = [idx]
        idx_next = find_downstream(ldd, idx[0], idx[1])
        while np.logical_and(ldd[idx_next] != pit, streams[idx_next] == 0):
            idx_down.append(idx_next)
            idx_next = find_downstream(ldd, idx_next[0], idx_next[1])
            # print idx_next, ldd[idx_next]
        if streams[idx_next] > 0:
            len_next = streams[idx_next]
        else:
            len_next = 0
        # now make the length array
        stretch = len(idx_down) - np.arange(0, len(idx_down)) + len_next
        # write length array to idxs
        streams[zip(*idx_down)] = stretch
        upstream_points['lengths'].append(stretch.max())
    return streams, upstream_points

def fill_dig_streamline(dem, ldd, init_cell_y, init_cell_x, dem_fill=-9999.,
                        ldd_fill=255, pit=-9999., weight_fill=10.,
                        weight_dig=1., z_int_start=1.,
                        flow_dirs=np.array([[7, 8, 9], [4, 5, 6], [1, 2, 3]]),
                        dem_mod=None):
    """
    Fills one streamline of a DEM starting at a user-given upstream point. 
    The result is that elevation values along the streamline are modified
    until the point where already modified values are found (in dem_mod).
    Any non-modified values must be NaN in the dem_mod variable.
    The user must call this function such, that first the longest streamline
    is modified, then the second longest, then third, etcetera
    
    The methodology followed is described by:
    Yamazaki, D., Baugh, C. A., Bates, P. D., Kanae, S., Alsdorf, D. E. and 
    Oki, T.: Adjustment of a spaceborne DEM for use in floodplain hydrodynamic 
    modeling, J. Hydrol., 436-437, 81-91, doi:10.1016/j.jhydrol.2012.02.045,
    2012.
    
    Inputs:
        dem:            2D-array (numpy) with elevation values
        ldd:            2D-array (numpy) with local drain direction values 
                        (default is the PCRaster directions)
        init_cell_x:    idx of x-coordinate of starting point of streamline
        init_cell_y:    idx of y-coordinate of starting point of streamline
        dem_fill:       fill value of missing data in dem
        ldd_fill:       fill value of missing data in ldd
        pit:            value of outflow elevation at pit (e.g. at ocean or 
                        interior basin)
        weight_fill:    weight given to filling of upstream elevation
        weight_dig:     weight given to digging of downstream elevation
        dem_mod=None:   2D-array (numpy) of modified elevation values (NaN 
                        where no modified values are found)
    outputs:
        dem_mod:        see inputs
    
    Note: as dem_mod, you can also insert a reference to an array in a NetCDF file
    This is very useful when the DEM is very large and does not fit in memory 
    at once
    
    """
    
    # if dem_mod does not exist yet, prepare it!
    if dem_mod is None:
        print('Preparing new dem')
        dem_mod = np.zeros(dem.shape)
        dem_mod[:] = np.nan
    # otherwise the DEM is already initialized and can be reused        
    idx_y, idx_x = init_cell_y, init_cell_x
    idx_list = [(idx_y, idx_x)]
    # first make a list of topologically connected cells from the ldd
    while ldd[idx_y, idx_x] != pit:
        idx_y, idx_x = find_downstream(ldd, idx_y, idx_x, flow_dirs)
        idx_list.append((idx_y, idx_x))
    # first fill in the dem_mod with the current elevation
    idx_y, idx_x = zip(*idx_list)
    # find cells that are not yet modified in dem and give these the original dem values
#    print np.where(np.isnan(dem_mod[idx_y, idx_x]))[0]
    idx_y_select = np.array(idx_y)[np.isnan(dem_mod[idx_y, idx_x])]
    idx_x_select = np.array(idx_x)[np.isnan(dem_mod[idx_y, idx_x])]
    dem_mod[idx_y_select, idx_x_select] = dem[idx_y_select, idx_x_select]
    #return idx_list
    
    # loop through all cells in the streamline        
    for i, (idx_y, idx_x) in enumerate(idx_list[:-1]):
        # first find index of downstream cell
        # idx_y_down, idx_x_down = find_downstream(ldd, idx_y, idx_x, flow_dirs)
        z_min = dem_mod[idx_y, idx_x]
        z_max = dem_mod[idx_list[i+1]]
        # If there are no errors, do nothing and continue ...
        if z_max <= z_min:
            dem_mod[idx_y, idx_x] = z_min
        else:
            z_var = np.arange(z_min, z_max + z_int_start, z_int_start)
            z_var = z_var[z_var <= z_max]
            err_min = 1e12  # make error start value very large
            
            for step, z_mod in enumerate(z_var):
                err = 0.
                down_count = 1  # amount of cells further downstream
                z_down = dem_mod[idx_list[i + down_count]]  # initiate with a very large number
                # loop until lower downstream value is found
                # stop the loop if the error with current elevation modification 
                # is larger than the smallest error found so far
                # or if the downstream elevation is smaller than modified elevation
                while np.logical_and(z_down > z_mod, err < err_min):
                    err += np.maximum(z_mod - z_down, 0)*weight_fill + np.maximum(z_down - z_mod, 0)*weight_dig
                    # np.abs(z_down - z_mod)*weight_down  # add difference between current and down
                    down_count += 1
                    if i + down_count >= len(idx_list):
                        break  # no more downstream cell values available in stream line
                    z_down = dem_mod[idx_list[i + down_count]]
                # now fill cell itself and upstream cells
                up_count = 0
                z_up = dem_mod[idx_list[i + up_count]]
                while np.logical_and(z_up < z_mod, err < err_min):
                    err += np.maximum(z_mod - z_up, 0)*weight_fill + np.maximum(z_up - z_mod, 0)*weight_dig
                    #err += np.abs(z_mod - z_up)*weight_up  # add difference between current and down
                    up_count -= 1
                    if i + up_count < 0:
                        break  # no more upstream cell values available in stream line
                    z_up = dem_mod[idx_list[i + up_count]]
                if err < err_min:
                    err_min = err
                    z_mod_select = z_mod
                # print 'z_down: ', z_down, 'z_mod: ', z_mod, 'error: ', err, 'err_min: ', err_min
            
            # z_mod_select is now optimized. Now perform correction
            # downstream
            down_count = 1
            
            while dem_mod[idx_list[i + down_count]] > z_mod_select:
                # print i + down_count, len(idx_list)
                dem_mod[idx_list[i + down_count]] = z_mod_select
                down_count += 1
                if len(idx_list) <= i + down_count:
                    # we've reached the downstream end
                    break
            # upstream
            up_count = 0
            while dem_mod[idx_list[i + up_count]] < z_mod_select:
                dem_mod[idx_list[i + up_count]] = z_mod_select
                up_count -= 1
#
    return idx_list, dem_mod

def dem_fill_dig(dem, ldd, dem_fill, ldd_fill, pit, weight_fill=1.,
                 weight_dig=10., z_int=1.,
                 flow_dirs=np.array([[7, 8, 9], [4, 5, 6], [1, 2, 3]])):
    """
    This function will modify a given elevation model along the streamlines of
    a local drainage direction map, derived from this elevation model.
    
    The methodology followed is described by:
    Yamazaki, D., Baugh, C. A., Bates, P. D., Kanae, S., Alsdorf, D. E. and 
    Oki, T.: Adjustment of a spaceborne DEM for use in floodplain hydrodynamic 
    modeling, J. Hydrol., 436-437, 81-91, doi:10.1016/j.jhydrol.2012.02.045,
    2012.
    
    Inputs:
        dem:            2D-array (numpy) with elevation values
        ldd:            2D-array (numpy) with local drain direction values 
                        (default is the PCRaster directions)
        dem_fill:       fill value of missing data in dem
        ldd_fill:       fill value of missing data in ldd
        pit:            value of outflow elevation at pit (e.g. at ocean or 
                        interior basin)
        weight_fill:    weight given to filling of upstream elevation
        weight_dig:     weight given to digging of downstream elevation
        z_int:          stepwise interval of modification to elevation
        flow_dirs:      2D-array (3x3 numpy) of the flow directions used in ldd
                        default is the PCRaster directions 
                        [[7, 8, 9], [4, 5, 6], [1, 2, 3]]
    outputs:
        dem_mod:        2D-array (numpy) with modified elevation

    """
    idx, catch_bound = catch_boundary(ldd, 5, ldd_fill, flow_dirs=flow_dirs)
    streams, upstream_points = stream_length(ldd, idx, 5)
    # sort the list of upstream point lengths
    lengths_sorted = pd.DataFrame(upstream_points).sort(columns=['lengths'],
                                                        ascending=False)
    # correct the DEM according to the sorted lengths, starting with the longest
    dem_mod = None
    for n, (init_cell_y, init_cell_x) in enumerate(lengths_sorted['coordinates']):
        #print('treating stream {:d} of {:d}').format(n + 1, len(lengths_sorted['coordinates']))
        idx_list, dem_mod = fill_dig_streamline(dem, ldd, init_cell_y,
                            init_cell_x, dem_fill=dem_fill,
                            ldd_fill=ldd_fill, pit=5, weight_fill=10.,
                            weight_dig=1., z_int_start=0.05,
                            dem_mod=dem_mod)
    dem_mod[np.isnan(dem_mod)] = dem_fill
    #gdal_writemap(r'D:\hoch\Desktop\PhD\Yamazaki DEM modification/dem_mod.map', 'PCRaster', x, y, dem_mod, dem_fill)
    return dem_mod


