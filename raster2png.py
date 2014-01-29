#!/usr/bin/env python

import matplotlib as mpl
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import numpy as np
import netCDF4 as nc4
import sys
import os
import StringIO

from wrf_raster import make_colorbar, basemap_raster_mercator


if __name__ == "__main__":

    if len(sys.argv) != 8 and len(sys.argv) != 6:
        print('Usage: %s <wrfout-file> <varname> <esmf-time> <target-file> <coords-file> [<units> <colorbar-file>]' % sys.argv[0])
        sys.exit(1)

    # open the netCDF dataset
    d = nc4.Dataset(sys.argv[1])
    varname = sys.argv[2]
    tstr = sys.argv[3]
    outf = sys.argv[4]
    coords_file = sys.argv[5]
    if len(sys.argv) == 8:
        cb_units = sys.argv[6]
        cb_file = sys.argv[7]
    else:
        cb_units, cb_file = None, None

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

    # construct kml file
    fa_min,fa_max = np.nanmin(fa),np.nanmax(fa)

    if cb_file is not None:
        print("[raster2png] rendering colorbar and saving to %s ..." % cb_file)
        cb_png_data = make_colorbar([fa_min,fa_max],'vertical',2,mpl.cm.jet,cb_units,varname)
        with open(cb_file, 'w') as f:
            f.write(cb_png_data)

    print("[raster2png] creating raster from grid (Spherical Mercator) and saving to %s ..." % outf)
    raster_png_data,corner_coords = basemap_raster_mercator(lon,lat,fa)
    with open(outf,'w') as f:
        f.write(raster_png_data)
    with open(coords_file,'w') as f:
        for lon,lat in corner_coords:
            f.write('%f,%f\n' % (lon,lat))

    print("[raster2png] done.")

