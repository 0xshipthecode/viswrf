#!/usr/bin/env python

import matplotlib as mpl
mpl.use('AGG')
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import numpy as np
import netCDF4 as nc4
import sys
import os
import StringIO

from wrf_raster import make_colorbar, basemap_raster_mercator
from var_wisdom import convert_value, get_wisdom

if __name__ == "__main__":

    if len(sys.argv) != 6:
        print('Usage: %s <wrfout-file> <varname> <dom-id> <esmf-time> <out-path>' % sys.argv[0])
        sys.exit(1)

    # open the netCDF dataset
    d = nc4.Dataset(sys.argv[1])
    varname = sys.argv[2]
    dom_id = int(sys.argv[3])
    tstr = sys.argv[4]
    out_path = sys.argv[5]

    # extract ESMF string times
    times = [''.join(x) for x in d.variables['Times'][:]]
    if tstr not in times:
        print('Error: invalid timestamp %s' % tstr)
        sys.exit(2)

    # extract variables
    tndx = times.index(tstr)
    fa = d.variables[varname][tndx,:,:]
    lon = d.variables['XLONG'][0,:,:]
    lat = d.variables['XLAT'][0,:,:]
    if lat.shape != fa.shape:
        print('[raster2kml] regular grid does not fit the variable %s, trying the fire grid ...' % varname)
        lon = d.variables['FXLONG'][0,:,:]
        lat = d.variables['FXLAT'][0,:,:]

    if lat.shape != fa.shape:
        print('Error: cannot find lon/lat grid for the variable %s' % varname)
        sys.exit(3)

    # gather wisdom about the variable
    wisdom = get_wisdom(varname)
    native_unit = wisdom['native_unit']
    cmap_name = wisdom['colormap']
    cmap = mpl.cm.get_cmap(cmap_name)
    cb_units = wisdom['colorbar_units']

    # look at mins and maxes
    fa_min,fa_max = np.nanmin(fa),np.nanmax(fa)
    print('[raster2kml] variable range [%g, %g], mean %g in %s' % (fa_min, fa_max, np.nanmean(fa), native_unit))

    # determine if we will use the range in the variable or a fixed range
    scale = wisdom['scale']
    if scale == 'original':
        print('[raster2kml] using original range [%g - %g] %s' % (fa_min, fa_max, native_unit))
    else:
        fa_min, fa_max = scale[0], scale[1]
        fa[fa < fa_min] = fa_min
        fa[fa > fa_max] = fa_max
        print('[raster2kml] enforcing range as [%g - %g] %s' % (fa_min, fa_max, native_unit))

    # render all requested colorbars
    for cb_unit in cb_units:
        cb_path = os.path.join(out_path, ('%s-%02d-%s-' % (varname,dom_id,tstr)) + cb_unit.replace('/','_') + "-cb.png")
        print("[raster2png] rendering colorbar for unit %s as [%s] ..." % (cb_unit, cb_path))
        cbu_min, cbu_max = convert_value(native_unit, cb_unit, fa_min), convert_value(native_unit, cb_unit, fa_max)
        cb_png_data = make_colorbar([cbu_min,cbu_max],'vertical',2,cmap,vw['name'] + ' ' + cb_unit,varname)
        with open(cb_path, 'w') as f:
            f.write(cb_png_data)

    raster_path_pfix = os.path.join(out_path, '%s-%02d-%s' % (varname,dom_id,tstr))
    print("[raster2png] creating raster from grid (Spherical Mercator) and saving to %s.png ..." % raster_path_pfix)
    raster_png_data,corner_coords = basemap_raster_mercator(lon,lat,fa,fa_min,fa_max,cmap)
    with open(raster_path_pfix + '.png','w') as f:
        f.write(raster_png_data)
    with open(raster_path_pfix + '.coords','w') as f:
        for lon,lat in corner_coords:
            f.write('%f,%f\n' % (lon,lat))

    print("[raster2png] done.")

