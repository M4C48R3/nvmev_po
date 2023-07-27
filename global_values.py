bscount = 4
bslist = [4,16,64,256]
## 0: --rw= argument and dictionary key / 1: code for finding through 'in' / 2: index / 3: number of lines read from temp.txt so far
#modlist = [['randread', 'RR', 0,0], ['randwrite', 'RW', 1,0]]
modlist = [['read', 'SR', 0,0], ['write', 'SW', 1,0], ['randread', 'RR', 2,0], ['randwrite', 'RW', 3,0]]
def bs_from_index(i):
    return bslist[i]