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

    if len(sys.argv) != 6:
        print('Usage: %s <wrfout-file> <varname> <dom-id> <esmf-time> <out-path>' % sys.argv[0])
        sys.exit(1)

    # open the netCDF dataset
    d = nc4.Dataset(sys.argv[1])
    varname = sys.argv[2]
    dom_id = int(sys.argv[3])
    tstr = sys.argv[4]
    out_path = sys.argv[5]
    base_name = varname + ('-%02d-' % dom_id) + tstr

    vw = get_wisdom(varname)

    # extract ESMF string times
    times = [''.join(x) for x in d.variables['Times'][:]]
    if tstr not in times:
        print('Error: invalid timestamp %s' % tstr)
        sys.exit(2)

    # extract variables
    tndx = times.index(tstr)
    fa = vw['retrieve_as'](d,tndx) # this calls a lambda defined to read the required 2d field
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

    # gather wisdom about the variable
    wisdom = get_wisdom(varname)
    native_unit = wisdom['native_unit']
    cmap_name = wisdom['colormap']
    cmap = mpl.cm.get_cmap(cmap_name)
    cb_unit = wisdom['colorbar_units'][0]

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

    cbu_min,cbu_max = convert_value(native_unit, cb_unit, fa_min), convert_value(native_unit, cb_unit, fa_max)

    # 
    print('[raster2kml] rendering colorbar with unit %s and colormap %s...' % (cb_unit, cmap_name))
    cb_png_data = make_colorbar([cbu_min, cbu_max],'vertical',2,cmap,vw['name'] + ' ' + cb_unit,varname)
    cb_name = 'colorbar-' + base_name + '.png'
    with open(cb_name, 'w') as f:
        f.write(cb_png_data)
    doc.addfile(cb_name)

    cbo = doc.newscreenoverlay(name='colorbar')
    cbo.overlayxy = kml.OverlayXY(x=0,y=1,xunits=kml.Units.fraction,yunits=kml.Units.fraction)
    cbo.screenxy = kml.ScreenXY(x=0.02,y=0.95,xunits=kml.Units.fraction,yunits=kml.Units.fraction)
    cbo.size = kml.Size(x=150,y=300,xunits=kml.Units.pixel,yunits=kml.Units.pixel)
    cbo.color = kml.Color.rgb(255,255,255,a=150)
    cbo.visibility = 1
    cbo.icon.href=cb_name

    print('[raster2kml] rendering raster from variable %s (Mercator projection) ...' % varname)
    ground = doc.newgroundoverlay(name=varname,color='80ffffff')
    raster_png_data,corner_coords = basemap_raster_mercator(lon,lat,fa,fa_min,fa_max,cmap)
    raster_name = 'raster-' + base_name + '.png'
    with open(raster_name,'w') as f:
      f.write(raster_png_data)
    doc.addfile(raster_name)
    ground.icon.href = raster_name
    ground.gxlatlonquad.coords = corner_coords

    doc.savekmz(os.path.join(out_path, base_name + ".kmz"))

    # cleanup
    print("[raster2kml] cleaning up temp files ...")
    os.remove(cb_name)
    os.remove(raster_name)

    print("[raster2kml] done.")

