"""
input: configurations (array of dim 1x9)
output: error percentage

Logs (values, 14 latencies) to a file.
"""
import os
from common import stdout_redirected
import json
import math
import global_values as gv
import copy
def get_params(values) -> float:
    ## 0: --rw= argument and dictionary key / 1: code for finding through 'in' / 2: index / 3: number of lines read from temp.txt so far
    modlist = copy.deepcopy(gv.modlist)

    if len(values) != 11:
        print("ERROR! 11 values must be given.")
        return
    
    values = [math.floor(v) for v in values]
    for val in values:
        if val <= 0:
            return 1000
    
    try:
        with open("output/ours_hynix.json") as f:
            cache = json.load(f)
    except:
        cache = {}
    
    key = "-".join(map(str,values))
    print(key)
    if key in cache:
        return cache[key]['perf']
    else:
        cache[key] = {}

    # make config file
    cmd = "sh -c \"./make_config.sh "
    cmd += " ".join(map(str,values))
    cmd += ("\"")
    print(cmd)
    os.system(cmd)

    # make nvmev kernel module and install it
    os.system("sh -c \"./make_all.sh 1\"")

    # run fio and get params
    ours = {}
    
    with open('output/temp.txt', 'w') as f: pass # empty file

    for m in modlist:
        m[3] = 0
        ours[m[0]] = {}
        for bs in gv.bslist:
            # format before read/write
            os.system("sh -c \"./make_all.sh\"")

            # in case of RR, do SW beforehand
            if m[0] == 'randread':
                print("doing SW before RR...")
                cmd = f"sh -c \"sudo fio --minimal --filename={gv.virtdevname} --direct=1 --rw=write --ioengine=psync --bs=256k " \
                f"--iodepth=1 --size=4G --name=RR_prep --output=/dev/null\""
                os.system(cmd)
                          
            ours[m[0]][f"{bs}"] = 0

            with open('output/temp.txt', 'a') as f, stdout_redirected(f):
                cmd = f"sh -c \"sudo fio --minimal --filename={gv.virtdevname} --direct=1 --rw={m[0]} --ioengine=psync --bs={bs}k " \
                f"--iodepth=1 --size=4G --name=fio_seq_{m[1]}_test\""
                os.system(cmd)
    
    
    #r, w = 0, 0
    with open('output/temp.txt') as f:
        for line in f:
            linesplit = line.split(";")
            for m in modlist:
                if m[1] in linesplit[2]:
                    sn = 56 if (m[1] in ["RW", "SW"]) else 15 # write completion latency is in position 56, read completion latency in 15
                    bs = gv.bs_from_index(m[3])
                    m[3] += 1
                    ours[m[0]][f"{bs}"] = float(linesplit[sn])

    # print(ours)

    diff = 0
    f = open("output/real_hynix.json")
    real = json.load(f)
    for m in modlist:
        for bs in gv.bslist:
            diff += abs(real[m[0]][f"{bs}"] - ours[m[0]][f"{bs}"]) / real[m[0]][f"{bs}"]
    # diff /= 8

    with open("output/ours_hynix.json", "w") as f:
        cache[key]['perf'] = diff
        cache[key]['vals'] = ours
        json.dump(cache, f)
    print(f"{diff}")
    return diff






if __name__ == '__main__':
    #arr = [3000,3000,3000,2000,2000,2000,30000,5000,3000,6000,1000]
    # ...,1: 1344 page block
    # ...,2: 448 block plane
    # ...2,*: WRITE_UNIT_SIZE=512
    # ...1,*: WRITE_UNIT_SIZE=4096
    # True   4K   16K    64K   256K
    # SR: 23.04 29.52  47.35 118.93
    # SW: 21.44 28.07  48.56 127.32
    # RR: 70.62 82.16 111.58 193.91
    # RW: 21.58 28.48  61.99 134.47
    #arr=[1900,2100,2300,1500,1700,1900,5e4,2000,2000,3000,1000]
    arr=[6e3,7e3,8e3,5e3,6e3,7e3,60e3,5e3,5e3,5e3,1e3]
    get_params(arr)
