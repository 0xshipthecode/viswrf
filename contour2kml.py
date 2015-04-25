#!/usr/bin/env python

import netCDF4 as nc4
import sys
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import simplekml as kml


if __name__ == '__main__':
  
  if len(sys.argv) != 6:
    print('Usage: %s <wrfout-file> <varname> <dom-id> <esmf-time> <out-path>' % sys.argv[0])
    sys.exit(1)

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
  lon = d.variables['FXLONG'][0,:,:]
  lat = d.variables['FXLAT'][0,:,:]

  # add each polygon to the KML document
  doc = kml.Kml(name = tstr)
  style = kml.Style()
  style.linestyle.color = kml.Color.red
  style.linestyle.width = 3
  style.polystyle.outline = 1
  style.polystyle.fill = 0
  c = plt.contour(lon, lat, fa, [0]).collections[0]
  paths = c.get_paths()
  polys = []
  for path in paths:
    if len(path) > 3:
      poly = doc.newpolygon()
      poly.outerboundaryis = [(x,y) for x,y in path.to_polygons()[0]]
      poly.style = style
      polys.append(poly)

  # always store as kmz
  doc.savekmz(os.path.join(out_path, "%s-%02-%s.kmz" % (varname,dom_id,tstr)))

