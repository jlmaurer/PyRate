'''
* filter log files
* trying to use python string processing
'''

import getopt
import sys
import collections

'''
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
verbosity = 2       # default verbosity (don't tell about stripping rows)
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
'''

in_fp  = open('/nas/users/u43382/unix/pr_testing_Fri_May_20_15_55_57_2016.log', 'r')
out_fp = open('/nas/users/u43382/unix/filter.log', 'w')

p_lt = 50       # filter out everything less than this percentage...

line_buffer = collections.deque(['']*10, 10)    # buffer the last 10 lines
#print line_buffer
#while True: pass

for line in in_fp:
    if line[0] == '*' or line[4] == '*':
        print line

    if line[-2] == '%':
        #print line.split(' ')[-1]
        if float(line.split(' ')[-1][:-2]) > p_lt:
            # we wan't this line and its parents...
            #print line
            pass

    # add this line to the queue
