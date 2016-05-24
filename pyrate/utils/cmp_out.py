'''
* problems with getopt means won't have traditional command line "args"
* everything has to be an opt and param... if you leave out the opt. it does the default...
* options
    * directory
    * ignore
    * just
    * output file
'''

import sys
import os
from os.path import join
import time
import numpy as np
import pickle
import scipy.io     # scipy is the package. need must always import the module (io)
from decimal import Decimal

from PIL import Image
from PIL import ImageDraw

import matplotlib.pyplot as plt
from matplotlib import figure

MPL_SCALING = 10        # matplotlib scaling

# =================================================================
# MARKER DEFINITIONS...
# =================================================================
marker_tol = Image.new('RGBA', (MPL_SCALING, MPL_SCALING), (0, 0, 0, 0))      # fully transparent
marker_nan1 = Image.new('RGBA', (MPL_SCALING, MPL_SCALING), (0, 0, 0, 0))
marker_nan2 = Image.new('RGBA', (MPL_SCALING, MPL_SCALING), (0, 0, 0, 0))

drawer = ImageDraw.ImageDraw(marker_tol)
drawer.line((0, 0, 0, 9), (255, 0, 0, 255))     # fully opaque
drawer.line((0, 0, 9, 0), (255, 0, 0, 255))
drawer.line((9, 9, 9, 0), (255, 0, 0, 255))
drawer.line((9, 9, 0, 9), (255, 0, 0, 255))

# =================================================================
# ARRAY CHECKING FUNCTIONS...
# these could really be made into just 1 function
# =================================================================
M1_N = 'py'  # matrix name. should be passed as a function
M2_N = 'mt'
def chk_out_mats(m1, m2):
    # checks pirate/pyrate (m1/m2) output arrays
    # will determine if 2d or 3d... can only deal with either of those two
    # returns an error string that you just plonk into the error file
    relative_tolerance=0.1      # todo: have this as function and program argument

    er_str = ''     # the error string we build up

    # check reference points here. not the right place but whatever
    global rp_mt, rp_py
    if rp_mt != rp_py:
        er_str += '\t'*4+'* REFERENCE PIXELS DO NOT MATCH...\n'
        er_str += '\t'*5+'* '+M1_N+' is '+repr(rp_py)+'\n'
        er_str += '\t'*5+'* '+M2_N+' is '+repr(rp_mt)+'\n'
        return er_str           # exit here. won't be anything meaningful

    er_array_shapes = ''
    if m1.shape != m2.shape:
        if verbosity == 1:
            er_array_shapes += '\t'*4+'* ARRAY SHAPES DO NOT MATCH. CHECKING WITH STRIPPED DATA...\n'
            er_array_shapes += '\t'*5+'* '+M1_N+' is '+repr(m1.shape)+'\n'
            er_array_shapes += '\t'*5+'* '+M2_N+' is '+repr(m2.shape)+'\n'

        # strip rows or cols to make have the same shape
        # don't worry about epochs. you'd hope they're equal...
        shape_diff = tuple(np.subtract(m1.shape, m2.shape))
        for elem in [0, 1]:
            if shape_diff[elem] > 0:
                # strip diff off m1
                if elem == 0:
                    if len(shape_diff) == 2:
                        m1 = m1[:m1.shape[elem]-shape_diff[elem],:]
                    else:
                        # must be 3d array
                        m1 = m1[:m1.shape[elem]-shape_diff[elem],:,:]
                else:
                    # must be elem == 1
                    if len(shape_diff) == 2:
                        m1 = m1[:,:m1.shape[elem]-shape_diff[elem]]
                    else:
                        m1 = m1[:,:m1.shape[elem]-shape_diff[elem],:]
            else:
                # must be negative. strip abs off m2
                if elem == 0:
                    if len(shape_diff) == 2:
                        m2 = m2[:m2.shape[elem]-abs(shape_diff[elem]),:]
                    else:
                        m2 = m2[:m2.shape[elem]-abs(shape_diff[elem]),:,:]
                else:
                    # must be elem == 1
                    if len(shape_diff) == 2:
                        m2 = m2[:,:m2.shape[elem]-abs(shape_diff[elem])]
                    else:
                        m2 = m2[:,:m2.shape[elem]-abs(shape_diff[elem]),:]

    # sanity checking
    assert m1.size == m2.size, 'array shapes do not match up even after stripping'
    '''
    print len(m1.shape)
    while True: pass
    '''
    fun_mode = len(m1.shape)              # function mode. 2d or 3d matrices. don't bother checking otherwise. assume can't happen
    if fun_mode == 2:
        n_r, n_c = m1.shape
        n_e = 1
    else:   # gauranteed to be 3. else is faster than testing for 3
        n_r, n_c, n_e = m1.shape        # number of rows, cols, epochs

    it_r, it_c, it_e = (0,0,0)      # iterators. not pythonic, but whatever
    n_nan_mis = 0   # number of nan mismatches
    n_tol_mis = 0   # number of tolerance mismatches

    # open up an image to put pixels to
    #img = Image.new('RGB', (n_r, n_c), (255, 255, 255))
    if fun_mode == 2:
        fig = plt.figure()
        fig.set_size_inches(m2.shape[1], m2.shape[0])
        ax = plt.Axes(fig, [0., 0., 1., 1.])
        ax.set_axis_off()
        fig.add_axes(ax)
        plt.set_cmap('hot')
        ax.imshow(m2, aspect = 'normal')
        plt.savefig(er_img_rate_fn, dpi=MPL_SCALING)   # pixels per data point...
        # open it up in PIL now so we can add our hit markers *pttt* *pttt* <-- mw2. MLG!
        img = Image.open(er_img_rate_fn)

        '''
        print m1.shape
        print img.size
        while True: pass
        '''

    while it_e < n_e:
        it_r = 0
        while it_r < n_r:
            it_c = 0
            while it_c < n_c:
                if fun_mode == 2:
                    it = (it_r, it_c)
                else:
                    it = (it_r, it_c, it_e)     # this can be used to index ndarray
                if (not np.isnan(m1[it])) and (not np.isnan(m2[it])):  # both floats
                    # Duncan's way of checking if floats are equal...
                    if abs(m1[it].item() - m2[it].item()) > relative_tolerance:
                        if fun_mode == 2:
                            # img.putpixel((it_c*10, it_r*10), (0, 0, 255))
                            img.paste(marker_tol, (it_c*MPL_SCALING, it_r*MPL_SCALING), marker_tol)
                        # not within tolerance...
                        n_tol_mis += 1
                        if verbosity == 1 or verbosity == 2:
                            er_str += '\t'*4+'* do not match to tolerance @ '+str(it)+'\n'
                            er_str += '\t'*5+'* '+M1_N+' = '+str(Decimal(m1[it].item()))+'\n'
                            er_str += '\t'*5+'* '+M2_N+' = '+str(Decimal(m2[it].item()))+'\n'
                    '''
                    # my original ideas about checking if floats are equal...
                    # check if match to a certain number of decimal places
                    if truncate(m1[it].item(),1) != truncate(m2[it].item(),1):
                        er_str += ' '*8+'* do not match to precision @ '+str(it)+'\n'
                        er_str += ' '*12+'* m1 = '+str(Decimal(m1[it].item()))+'\n'
                        er_str += ' '*12+'* m2 = '+str(Decimal(m2[it].item()))+'\n'
                    '''
                else:   # atleast one of py[it], m2[it] is NaN
                    if (not np.isnan(m1[it])) and (np.isnan(m2[it])):
                        if fun_mode == 2:
                            img.paste(marker_tol, (it_c*MPL_SCALING, it_r*MPL_SCALING), marker_tol)
                        n_nan_mis += 1
                        if verbosity == 1 or verbosity == 2:
                            er_str += '\t'*4+'* '+M1_N+' should be NaN (but is not) @ '+str(it)+'\n'
                    if (np.isnan(m1[it])) and (not np.isnan(m2[it])):
                        if fun_mode == 2:
                            img.paste(marker_tol, (it_c*MPL_SCALING, it_r*MPL_SCALING), marker_tol)
                        n_nan_mis += 1
                        if verbosity == 1 or verbosity == 2:
                            er_str += '\t'*4+'* '+M1_N+' should not be NaN (but is) @ '+str(it)+'\n'
                it_c += 1
            it_r += 1
        it_e += 1

    if fun_mode == 2:
        img.save(er_img_rate_fn, 'PNG')

    er_str_prep = ''
    '''
    print n_tol_mis
    print n_nan_mis
    while True: pass
    '''
    if n_tol_mis != 0 or n_nan_mis != 0:
        tot_pix = m1.shape[0]*m1.shape[1]*n_e
        tol_percent = (float(n_tol_mis)/tot_pix)*100
        nan_percent = (float(n_nan_mis)/tot_pix)*100
        tot_percent = (float(n_tol_mis+n_nan_mis)/tot_pix)*100
        er_str_prep += '\t'*4+'* tolerance errors = '+str(n_tol_mis)+'/'+str(tot_pix)+' = '+str(tol_percent)+'%\n'
        er_str_prep += '\t'*4+'* NaN errors       = '+str(n_nan_mis)+'/'+str(tot_pix)+' = '+str(nan_percent)+'%\n'
        er_str_prep += '\t'*4+'* total fail       = '+str(n_tol_mis+n_nan_mis)+'/'+str(tot_pix)+' = '+str(tot_percent)+'%\n'

    er_str = er_array_shapes+er_str_prep+er_str
    return er_str
# =================================================================
# =================================================================

import getopt
opts, args = getopt.getopt(sys.argv[1:], 'd:i:j:v:', ['od=','of='])
# usage checking
if opts == [] and args != []:
    print 'read usage'
    sys.exit(0)
# gettting command line options
root_direct = False
ign_list = []
jst_list = []
out_direct = False
out_fn = False
verbosity = 3       # default verbosity (don't tell about stripping rows)
# assiging and checking valid options
for opt in opts:
    if opt[0] == '-d':
        # check if is a valid directory and ensure ends in '/' or '\'
        root_direct = opt[1]
    if opt[0] == '-i':
        ign_list = opt[1]
    if opt[0] == '-j':
        jst_list = opt[1]
    if opt[0] == '--od':
        out_direct = opt[1]
    if opt[0] == '--of':
        out_fn = opt[1]
    if opt[0] == '-v':
        verbosity = int(opt[1])
# checking for valid output options
if out_direct != False and out_fn != False:
    print 'can only have one or the other or none of --od and --of'
    sys.exit(0)
# check verbosity options are correct
if not (verbosity in [1, 2, 3]):
    print 'verbositiy can only be 1 or 2. default is 1 (most verbose)'
    sys.exit(0)
# configuring global program variables
if root_direct == False:
    root_direct = os.getcwd()
# figuring out where to write output
if out_direct == False and out_fn == False:
    out_fn = join(os.getcwd(),'pr_testing_'+time.ctime().replace(' ','_').replace(':','_')+'.log')
elif out_direct != False:
    out_fn = join(out_direct,'pr_testing_'+time.ctime().replace(' ','_').replace(':','_')+'.log')
'''
else:
    # out_direct == False and out_fn != False
    # out_fn should be what we want
    pass
'''
print 'writing output to '+out_fn
out_fp = open(name=out_fn, mode='w')
out_fp.write('cmp_out.py log file\n')
out_fp.write('===================\n')

# these used in below loop to keep track of what indent writing to in log file
in_tst = ''
in_dat = ''
write_tst = False
write_dat = False

sorted_nums = sorted(filter(lambda x: os.path.isdir(os.path.join(root_direct, x)), os.listdir(root_direct)))
#print sorted_nums
#while True: pass
dat_fld = os.path.split(os.path.split(root_direct)[0])[1]
tst_fld = os.path.split(os.path.split(os.path.split(root_direct)[0])[0])[1]
out_fp.write('* '+tst_fld+'\n')
out_fp.write('\t'*1+'* '+dat_fld+'\n')
for cont_fld in sorted_nums:
    path = join(root_direct, cont_fld)

    pick_f = open(join(path, 'python', 'out_py.pkl'), 'r')      # todo: don't create pickle. read in tiff files (this requires changing run_pyrate.py though)
    out_py = pickle.load(pick_f)
    pick_f.close()
    out_mt = scipy.io.loadmat(join(path, 'matlab', 'out_mt.mat'))

    # load reference pixel values
    refpix_f = open(join(path, 'python', 'refpt.pkl'), 'r')
    rp_py = pickle.load(refpix_f)
    refpix_f.close()
    rp_mt = scipy.io.loadmat(join(path, 'matlab', 'refpt.mat'))
    rp_mt = rp_mt['refpt']
    rp_mt = rp_mt[0,0]
    rp_mt = (rp_mt[0].item()-1, rp_mt[1].item()-1)  # matlab reference point seems to be greater by 1 in each dimension

    # paths where write out error image file
    # overlay ontop of matlab image
    #er_img_tsincr_fn = join(path, 'er_tsincr.png')     # do it just for rate for now
    er_img_rate_fn = join(path, 'er_rate.png')

    ers = []
    if ('tsincr' in out_py) and ('tsincr' in out_mt):
        py = out_py['tsincr']   # data is double
        mt = out_mt['tsincr']   # data is single
        #py = py[:py.shape[0]-1,:,:]     # remove last row... have to check this happens for all inputs
        ers.append(('tsincr', chk_out_mats(m1=py, m2=mt)))

    if ('rate' in out_py) and ('stackmap' in out_mt):
        py = out_py['rate']   # data is double
        mt = out_mt['stackmap']   # data is single
        #py = py[:py.shape[0]-1,:]     # remove last row... have to check this happens for all inputs
        ers.append(('rate/stackmap', chk_out_mats(m1=py, m2=mt)))

    # check if actually have an error to write
    if ['', ''] != [er[1] for er in ers]:
        # write indents if need to
        #if write_tst:
        #    out_fp.write('* '+tst_fld+'\n')
        #if write_dat:
        #    out_fp.write('\t'*1+'* '+dat_fld+'\n')
        out_fp.write('\t'*2+'* '+cont_fld+'\n')
        # write errors
        for er in ers:
            if er[1] != '':
                out_fp.write('\t'*3+'* '+er[0]+'\n')
                out_fp.write(er[1])     # <-- pass an indent level parameter
#out_fp.write('test!!!!')
out_fp.close()