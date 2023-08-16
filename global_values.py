VERBOSE = True
def printv(x):
    if VERBOSE:
        print(x)
def first_non_digit(string: str, startidx: int, endidx_: int = -1) -> int:
    # return first non-digit character in the range [startidx, endidx_)
    endidx = endidx_
    DIGITS = [str(i) for i in range(10)]
    if endidx_ < 0:
        endidx = len(string)
    retv = startidx
    while retv < endidx:
        if string[retv] in DIGITS:
            retv += 1
        else:
            break
    return retv

bslist = (4,8,16,32,64,128,256)
#bslist = (4,16,64,256)
bscount = bslist.__len__()
## 0: --rw= argument and dictionary key / 1: code for finding through 'in' / 2: index / 3: number of lines read from temp.txt so far
modlist = [['randread', 'RR', 0,0], ['randwrite', 'RW', 1,0]]
#modlist = [['read', 'SR', 0,0], ['write', 'SW', 1,0]]
#modlist = [['read', 'SR', 0,0], ['write', 'SW', 1,0], ['randread', 'RR', 2,0], ['randwrite', 'RW', 3,0]]
def bs_from_index(i):
    return bslist[i]
realdevname = "/dev/nvme0n1" # device name of actual device to measure
virtdevname = "/dev/nvme1n1" # device name of virtual device created by NVMeVirt
realfiosize = "32G" # size of fio test for real devices. should include G at the end
virtfiosize = "3G" # size of fio test for virtual devices. should include G at the end
latency_multiple_cellpos = [1, 1.5, 1.8] # multiplied factor for latency of LSB, MSB, CSB