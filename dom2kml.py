#!/usr/bin/env python

import netCDF4 as nc4
import simplekml as kml
import numpy as np
import sys


if __name__ == '__main__':

  if len(sys.argv) < 4:
    print('Usage: %s <kml_name> <out_file> <geo_em_file> [<geo_em_file>*]' % sys.argv[0])
    sys.exit(1)

  # read in input names
  kmlname = sys.argv[1]
  tgtfile = sys.argv[2]
  geonames = sys.argv[3:]

  # construct kml document with grid point markers
  doc = kml.Kml(name = kmlname)

  # the generic poly style
  style = kml.Style()
  style.linestyle.color = kml.Color.red
  style.linestyle.width = 3
  style.polystyle.outline = 1
  style.polystyle.fill = 0

  for geoname in geonames:
    # open netCDF data 
    d = nc4.Dataset(geoname)

    # read in CLONG & CLAT
    lon = d.variables['CLONG'][0,:,:]
    lat = d.variables['CLAT'][0,:,:]
    shape = lon.shape

    # construct a poly that shows the domain
    dom = doc.newpolygon(name = geoname)

    bdry = []
    bdry.extend([(lon[0,i], lat[0,i]) for i in range(shape[1])])
    bdry.extend([(lon[j,-1], lat[j,-1]) for j in range(shape[0])])
    bdry.extend([(lon[-1,i], lat[-1,i]) for i in range(shape[1]-1,-1,-1)])
    bdry.extend([(lon[j,0], lat[j,0]) for j in range(shape[0]-1,-1,-1)])

    dom.outerboundaryis = bdry
    dom.style = style

  if tgtfile.endswith('kmz'):
    doc.savekmz(tgtfile)
  else:
    doc.save(tgtfile)

  print('Success.')


