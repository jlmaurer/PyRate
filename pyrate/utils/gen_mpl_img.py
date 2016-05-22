'''
generate matplotlib image from numpy array
'''

from PIL import Image
import scipy.io
import numpy as np

import matplotlib.pyplot as plt
from matplotlib import figure

from os.path import join

out_mt = scipy.io.loadmat(join('/home/gap/pr_testing/tests/lap_vs_svd/syd_g/00/', 'matlab', 'out_mt.mat'))
rate_data = out_mt['stackmap']

fig = plt.figure()
fig.set_size_inches(47, 71)
ax = plt.Axes(fig, [0., 0., 1., 1.])
ax.set_axis_off()
fig.add_axes(ax)
plt.set_cmap('hot')
ax.imshow(rate_data, aspect = 'normal')
plt.savefig('myplot.png', dpi = 10)


'''
pp.figure().set_size_inches(71, 47)
fig = pp.imshow(rate_data)
pp.axis('off')
fig.axes.get_xaxis().set_visible(False)
fig.axes.get_yaxis().set_visible(False)
#fig.set_size_inches(47, 71)
#figure = pp.gcf()
print rate_data.shape
#figure.set_size_inches(rate_data.shape[1], rate_data.shape[0])
pp.savefig("myplot.png", dpi = 10, bbox_inches = 'tight', pad_inches=0)
#pp.show()
'''