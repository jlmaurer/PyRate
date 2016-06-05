'''
see how long it takes to hash a large file
'''

import hashlib

def hash_win_iso():
    BLOCKSIZE = 65536
    hasher = hashlib.sha1()
    with open('/home/gap/Desktop/Windows.iso', 'rb') as afile:
        buf = afile.read(BLOCKSIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = afile.read(BLOCKSIZE)
    print 'win hash = ' + hasher.hexdigest()

def hash_matlab_iso():
    BLOCKSIZE = 65536
    hasher = hashlib.sha1()
    with open('/home/gap/Desktop/Mathworks_Matlab_R2015a_Linux/R2015a-glnxa64.iso', 'rb') as afile:
        buf = afile.read(BLOCKSIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = afile.read(BLOCKSIZE)
    print 'mat hash = ' + hasher.hexdigest()

import timeit
n_times = 1
print timeit.timeit(hash_matlab_iso, number=n_times)
