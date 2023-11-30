import datetime
import os

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

t = datetime.datetime.utcnow() + datetime.timedelta(hours=9) # adding 9h for KST
TIME_STRING = t.strftime("%y%m%dT%H%M") # e.g. 17 Aug 2023 11:45 KST => 230817T1145
def update_time_string():
    global TIME_STRING
    t = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
    TIME_STRING = t.strftime("%y%m%dT%H%M")
    

bslist = (4,8,16,32,64,128,256)
#bslist = (4,16,64,256)
bscount = bslist.__len__()
## 0: --rw= argument and dictionary key / 1: code for finding through 'in' / 2: index / 3: number of lines read from temp.txt so far
modlist = [['randread', 'RR', 0,0], ['randwrite', 'RW', 1,0]]
#modlist = [['read', 'SR', 0,0], ['write', 'SW', 1,0]]
#modlist = [['read', 'SR', 0,0], ['write', 'SW', 1,0], ['randread', 'RR', 2,0], ['randwrite', 'RW', 3,0]]
def bs_from_index(i):
    return bslist[i]
#.
hostname = os.popen("hostname -f").read().strip()
if hostname == "star3":
    realdevname = "/dev/nvme2n1" # device name of actual device to measure
    virtdevname = "/dev/nvme7n1" # device name of virtual device created by NVMeVirt
elif hostname == "streaming":
    realdevname = None # device name of actual device to measure
    virtdevname = "/dev/nvme0n1" # device name of virtual device created by NVMeVirt
elif hostname in ("blaze51-Z790-PG-Lightning", "faduu2test"):
    realdevname = "/dev/nvme2n1" # device name of actual device to measure
    virtdevname = "/dev/nvme3n1" # device name of virtual device created by NVMeVirt
else:
    raise Exception("Unknown hostname: " + hostname)


realfiosize = "32G" # size of fio test for real devices. should include G at the end

# without time_based, fio runtime is *at most* runtime.
# add --time_based=1 to make fio *always* run for runtime.
# set to empty string to limit only by size
virt_timebased = "--runtime=30"
virt_test_size = "--size=6G" 


latency_multiple_cellpos = [1, 1, 1.2] # multiplied factor for latency of LSB, MSB, CSB

# format prints warning and waits 10 seconds from version 1.10 onwards. "-f" option skips the warning, but it results in an error for version 1.9 and below. 
def whether_to_f():
    # return "" # uncomment this line to disable -f option and see the warning for higher versions
    versionstring = os.popen("nvme version").read()
    # this gives "nvme version vmaj.vmin\n". Parsing below.
    vp = versionstring.find("version ") + len("version ") # points to the first digit of version
    dotp = versionstring.find(".", vp)
    newlinep = versionstring.find("\n", dotp)
    vmaj = int(versionstring[vp:dotp])
    vmin = int(versionstring[dotp+1:newlinep])
    if vmaj > 1:
        return "-f"
    elif vmaj == 1 and vmin >= 10:
        return "-f"
    else:
        return ""

forceformat = whether_to_f()