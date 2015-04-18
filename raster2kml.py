#!/usr/bin/env python

import matplotlib as mpl
mpl.use('AGG')
import matplotlib.pyplot as plt
import simplekml as kml
from mpl_toolkits.basemap import Basemap
import numpy as np
import netCDF4 as nc4
import sys
import os
import StringIO
from var_wisdom import convert_value, get_wisdom

from wrf_raster import make_colorbar, basemap_raster_mercator


if __name__ == "__main__":

    if len(sys.argv) != 5:
        print('Usage: %s <wrfout-file> <varname> <esmf-time> <target-file>' % sys.argv[0])
        sys.exit(1)

    # open the netCDF dataset
    d = nc4.Dataset(sys.argv[1])
    varname = sys.argv[2]
    tstr = sys.argv[3]
    outf = sys.argv[4]

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

    # construct kml file
    doc = kml.Kml(name = varname)
    fa_min,fa_max = np.nanmin(fa),np.nanmax(fa)

    # render first colorbar required by wisdom
    wisdom = get_wisdom(var_name)
    native_unit = wisdom['native_unit']
    cb_unit = wisdom['colorbar_units'][0]
    print('[raster2kml] wisdom for var %s: native_unit %s main colobar unit %s' % (var_name, native_unit, cb_unit))

    cmap_name = wisdom['colormap']
    print('[raster2kml] rendering colorbar with unit %s and colormap %s...' % (cb_unit, cmap_name))
    cbu_min, cbu_max = convert_value(native_unit, cb_unit, fa_min), convert_value(native_unit, cb_unit, fa_max)
    cb_png_data = make_colorbar([cbu_min, cbu_max],'vertical',2,mpl.get_cmap(cmap_name),cb_unit,varname)
    suffix = var_name + '-' + tstr
    cb_name = 'colorbar-' + suffix + '.png'
    with open(cb_name, 'w') as f:
        f.write(cb_png_data)
    doc.addfile(cb_name)

    cbo = doc.newscreenoverlay(name='colorbar')
    cbo.overlayxy = kml.OverlayXY(x=0,y=1,xunits=kml.Units.fraction,yunits=kml.Units.fraction)
    cbo.screenxy = kml.ScreenXY(x=0.02,y=0.98,xunits=kml.Units.fraction,yunits=kml.Units.fraction)
    cbo.size = kml.Size(x=0,y=0,xunits=kml.Units.fraction,yunits=kml.Units.fraction)
    cbo.color = kml.Color.rgb(255,255,255,a=150)
    cbo.visibility = 1
    cbo.icon.href=cb_name

    print('[raster2kml] raster range [%g, %g], mean %g' % (np.amin(fa),np.amax(fa),np.mean(fa)))
    print('[raster2kml] rendering raster from variable %s (Mercator projection) ...' % varname)
    ground = doc.newgroundoverlay(name=varname,color='80ffffff')
    raster_png_data,corner_coords = basemap_raster_mercator(lon,lat,fa)
    raster_name = 'raster-' + suffix + '.png'
    with open(raster_name,'w') as f:
      f.write(raster_png_data)
    doc.addfile(raster_name)
    ground.icon.href = raster_name
    ground.gxlatlonquad.coords = corner_coords

    doc.savekmz(outf)

    # cleanup
    print("[raster2kml] cleaning up temp files ...")
    os.remove(cb_name)
    os.remove(raster_name)

    print("[raster2kml] done.")

