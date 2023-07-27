bslist = [4, 8, 16, 32, 64, 128, 256]
bscount = bslist.__len__()
## 0: --rw= argument and dictionary key / 1: code for finding through 'in' / 2: index / 3: number of lines read from temp.txt so far
modlist = [['randread', 'RR', 0,0], ['randwrite', 'RW', 1,0]]
#modlist = [['read', 'SR', 0,0], ['write', 'SW', 1,0], ['randread', 'RR', 2,0], ['randwrite', 'RW', 3,0]]
def bs_from_index(i):
    return bslist[i]
realdevname = "/dev/nvme0n1" # device name of actual device to measure
virtdevname = "/dev/nvme1n1" # device name of virtual device created by NVMeVirt
VERBOSE = True
def printv(x):
    if VERBOSE:
        print(x)