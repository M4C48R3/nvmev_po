"""
input: configurations (array of dim 1x9)
output: error percentage

Logs (values, 14 latencies) to a file.
"""
import os
from common import stdout_redirected
import json

def get_params(values) -> int:
    if len(values) != 9:
        print("ERROR! 9 values must be given.")
        return
    
    try:
        with open("output/ours_hynix.json") as f:
            cache = json.load(f)
    except:
        cache = {}

    key = f"{values[0]}-{values[1]}-{values[2]}-{values[3]}-{values[4]}-{values[5]}-{values[6]}-{values[7]}-{values[8]}"
    if key in cache:
        return cache[key]['perf']
    else:
        cache[key] = {}
    # make config file
    os.system("sh -c \"./make_config.sh %d %d %d %d %d %d %d %d %d \"" %
    (values[0], values[1], values[2], values[3], values[4], 
    values[5], values[6], values[7], values[8]))

    # make nvmev kernel module and install it
    os.system("sh -c \"./make_all.sh\"")

    # run fio and get params
    ours = {}
    with open('output/temp.txt', 'w') as f, stdout_redirected(f):
        for mode in ['read', 'write']:
            ours[mode] = {}
            for i in range(0, 7): # TODO: change to 7
                bs = 4 * 2 ** i
                ours[mode][f"{bs}"] = 0
                cmd = f"sudo fio --minimal --filename=\"/dev/nvme1n1\" --direct=1 --rw={mode} --ioengine=psync --bs={bs}k --iodepth=1 --size=1G --name=fio_seq_{mode}_test"
                shell_cmd = f"sh -c \"{cmd}\""
                os.system(shell_cmd)
    
    r, w = 0, 0
    with open('output/temp.txt') as f:
        for line in f:
            if 'read' in line.split(";")[2]:
                bs = 4 * 2 ** r
                mode = 'read'
                ours[mode][f"{bs}"] = float(line.split(";")[15])
                r += 1
            else:
                bs = 4 * 2 ** w
                mode = 'write'
                ours[mode][f"{bs}"] = float(line.split(";")[56])
                w += 1
    print(ours)

    diff = 0
    f = open("output/real_hynix.json")
    real = json.load(f)
    for mode in ['read', 'write']:
        for i in range(0, 7): # TODO: change to 7
            bs = f"{4 * 2 ** i}"
            diff += abs(real[mode][bs] - ours[mode][bs]) / real[mode][bs]
    diff /= 14

    with open("output/ours_hynix.json", "w") as f:
        cache[key]['perf'] = diff
        cache[key]['vals'] = ours
        json.dump(cache, f)

    return diff






if __name__ == '__main__':
    arr = [9, 8, 7, 6, 5, 4, 3, 2, 1]
    get_params(arr)