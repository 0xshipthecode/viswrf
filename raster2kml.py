#!/usr/bin/env python

import scipy.io as sio
import matplotlib as mpl
import matplotlib.pyplot as plt
import simplekml as kml
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import numpy as np
import netCDF4 as nc4
import sys
import os
import StringIO


def make_colorbar(rng,orientation,size_in,cmap,cb_label,cb_title,dpi=200):
    """
    rng - [min max]
    orientation - 'vertical' or 'horizontal'
    size_in - larger dimension (height for vertical orientation, width for horizontal)
    cmap - the colormap in use
    units - the colorbar label
    dpi - dots per inch

    See: http://matplotlib.org/examples/api/colorbar_only.html for more examples
    """
    kwargs = { 'norm':mpl.colors.Normalize(rng[0],rng[1]),
               'orientation':orientation,
               'spacing':'proportional',
               'cmap':cmap}

    # build figure according to requested orientation
    hsize, wsize = (size_in,size_in*0.5) if orientation == 'vertical' else (size_in*0.5,size_in)
    fig = plt.figure(figsize=(wsize,hsize))

    # proportions that work with axis title (horizontal not tested)
    ax = fig.add_axes([.5,.03,.12,.8]) if orientation=='vertical' else fig.add_axes([0.03,.4,.8,.12])

    # construct the colorbar and modify properties
    cb = mpl.colorbar.ColorbarBase(ax,**kwargs)
    ax.set_title(cb_title,color='1',fontsize=10)
    cb.set_label(cb_label,color='1',fontsize=8,labelpad=-40)

    # move ticks to left side
    ax.yaxis.set_ticks_position('left')
    for tick_lbl in ax.get_yticklabels():
      tick_lbl.set_color('1')
      tick_lbl.set_fontsize(8)

    # save png to a StringIO
    str_io = StringIO.StringIO()
    fig.savefig(str_io,dpi=dpi,format='png',transparent=True)

    return str_io.getvalue()


def basemap_raster_mercator(lon, lat, grid):
  # longitude/latitude extent
  lons = (np.amin(lon), np.amax(lon))
  lats = (np.amin(lat), np.amax(lat))

  # construct spherical mercator projection for region of interest
  m = Basemap(projection='merc',llcrnrlat=lats[0], urcrnrlat=lats[1],
              llcrnrlon=lons[0],urcrnrlon=lons[1],lat_ts=48)

  vmin,vmax = np.nanmin(grid),np.nanmax(grid)
  masked_grid = np.ma.array(grid,mask=np.isnan(grid))
  fig = plt.figure(frameon=False)
  plt.axis('off')
  cmap = mpl.cm.jet
  cmap.set_bad('w', 1.0)
  m.pcolormesh(lon,lat,masked_grid,latlon=True,cmap=cmap,vmin=vmin,vmax=vmax)

  str_io = StringIO.StringIO()
  plt.savefig(str_io,bbox_inches='tight',format='png',pad_inches=0,transparent=True)
  kml_bounds = [ (lons[0],lats[0]),(lons[1],lats[0]),(lons[1],lats[1]),(lons[0],lats[1]) ]

  return str_io.getvalue(), kml_bounds



if __name__ == "__main__":

    if len(sys.argv) != 6:
        print('Usage: %s <wrfout-file> <varname> <units> <esmf-time> <target-file>' % sys.argv[0])
        sys.exit(1)

    # open the netCDF dataset
    d = nc4.Dataset(sys.argv[1])
    varname = sys.argv[2]
    cb_units = sys.argv[3]
    tstr = sys.argv[4]
    outf = sys.argv[5]

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
    doc = kml.Kml(name = varname)
    fa_min,fa_max = np.nanmin(fa),np.nanmax(fa)

    print("Constructing and adding colorbar as a screen overlay ...")
    cb_png_data = make_colorbar([fa_min,fa_max],'vertical',2,mpl.cm.jet,cb_units,varname)
    with open('colorbar.png', 'w') as f:
        f.write(cb_png_data)
    doc.addfile('colorbar.png')

    cbo = doc.newscreenoverlay(name='colorbar')
    cbo.overlayxy = kml.OverlayXY(x=0,y=1,xunits=kml.Units.fraction,yunits=kml.Units.fraction)
    cbo.screenxy = kml.ScreenXY(x=0.02,y=0.98,xunits=kml.Units.fraction,yunits=kml.Units.fraction)
    cbo.size = kml.Size(x=0,y=0,xunits=kml.Units.fraction,yunits=kml.Units.fraction)
    cbo.color = kml.Color.rgb(255,255,255,a=150)
    cbo.visibility = 1
    cbo.icon.href="colorbar.png"

    print("Creating raster from grid (Mercator projection) [field min=%g max=%g] ..." % (fa_min,fa_max))
    ground = doc.newgroundoverlay(name=varname,color="80ffffff")
    raster_png_data,corner_coords = basemap_raster_mercator(lon,lat,fa)
    with open('raster.png','w') as f:
      f.write(raster_png_data)
    doc.addfile('raster.png')
    ground.icon.href="raster.png"
    ground.gxlatlonquad.coords = corner_coords

    doc.savekmz(outf)

    # cleanup
    os.remove('colorbar.png')
    os.remove('raster.png')

    print("Done.")

