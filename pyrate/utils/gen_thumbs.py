from PIL import Image
import os
import numpy as np
import matplotlib.pyplot as plt
import sys
from osgeo import gdal
from os.path import join

import pyrate.ifgconstants as ifc

# will get below from argument
#direc = r'C:\Users\gap\grk_viz\tif'
#direc = sys.argv[1]
direc = '/home/gap/pr_testing/tests/orbitalfit/syd_g/1/python'

#print direc
#while True: pass

#lev = 0
for trav in os.walk(direc):
    #print trav
    break

#print trav
root = trav[0]
fns = trav[2]
print root
#print fns

#while True: pass

ifg_1s, ifg_2s, ts_cums, ts_vels, ts_incrs = [], [], [], [], []
'''
# this would be the better way of doing it but i'm too lazy to write tests for these metadata additions
for fn in fns:
    ds = gdal.Open(os.path.join(root,fn))
    md = ds.GetMetadata()
    if md[ifc.PR_OUT_TYPE] == 'ifg_1':
        ifg_1s.append(fn)   # hopefully this just creates a reference and not a copy. don't want string copies
    if md[ifc.PR_OUT_TYPE] == 'ts_cum':
        pass
    if md[ifc.PR_OUT_TYPE] == 'ts_vel':
        pass
    if md[ifc.PR_OUT_TYPE] == 'ts_incr':
        pass
'''
# can't actually identify ifg_1s from file name. so can't do
for fn in fns:
    if fn[-6:] == 'cr.tif':
        ifg_2s.append(fn)
    elif fn[:6] == 'tscuml':
        ts_cums.append(fn)
    elif fn[:5] == 'tsvel':
        ts_vels.append(fn)
    elif fn[:6] == 'tsincr':
        ts_incrs.append(fn)

print ifg_2s
#print ts_cums
#print ts_vels
#print ts_incrs

# create ifg_2 thumbnails...
ifg_2s.sort()
# have to assume they are of the same size...


'''
fig = plt.figure()
fig_shape = (len(ifg_2s)/5, 5)     # rows, cols

while True: pass
'''

'''
#print tif_dats
# matplotlibification
fig = pp.figure()
for it, tif_dat in enumerate(tif_dats):
    plt = fig.add_subplot(4, 5, it+1)
    pp.imshow(tif_dat)

#print dir(plt)
pp.show()
'''