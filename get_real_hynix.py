import os
from common import stdout_redirected
import json

dic = {}
with open('output/temp.txt', 'w') as f, stdout_redirected(f):
    for mode in ['read', 'write']:
        dic[mode] = {}
        for i in range(0, 7):
            bs = 4 * 2 ** i
            dic[mode][f"{bs}"] = 0
            cmd = f"sudo fio --minimal --filename=\"/dev/nvme0n1p6\" --direct=1 --rw={mode} --ioengine=psync --bs={bs}k --iodepth=1 --size=1G --name=fio_seq_{mode}_test"
            shell_cmd = f"sh -c \"{cmd}\""
            os.system(shell_cmd)

latencies = [[], []]
with open('output/temp.txt') as f:
    for line in f:
        if 'read' in line.split(";")[2]:
            latencies[0].append(float(line.split(";")[15]))
        else:
            latencies[1].append(float(line.split(";")[56]))

with open("output/real_hynix.json", 'w') as f:
    for mode in ['read', 'write']:
        for i in range(0, 7): # TODO: change to 7
            bs = 4 * 2 ** i
            dic[mode][f"{bs}"] = latencies[0 if mode == 'read' else 1][i]

    print(dic)
    json.dump(dic, f)

        