import os
from common import stdout_redirected
import json
import time


dic = {}
## 0: --rw= argument / 1: code / 2: index / 3: number of lines read from temp.txt so far
modlist = [['read', 'SR', 0,0], ['write', 'SW', 1,0], ['randread', 'RR', 2,0], ['randwrite', 'RW', 3,0]]

repeats = 1
latencies = [[], [], [], []]


for current_iter in range(repeats):
    with open('output/temp.txt', 'w') as f: pass # empty file

    # for mode in ['read', 'write']:
    #     dic[mode] = {}
    #     for i in range(0, 4):
    #         bs = 4 * 4 ** i
    #         dic[mode][f"{bs}"] = 0
    #         os.system("sh -c \"sudo nvme format /dev/nvme0n1\"")
    #         with open('output/temp.txt', 'a') as f, stdout_redirected(f):
    #             cmd = f"sudo fio --minimal --filename=\"/dev/nvme0n1\" --direct=1 --rw={mode} --ioengine=psync --bs={bs}k --iodepth=1 --size=4G --name=fio_seq_{mode}_test"
    #             shell_cmd = f"sh -c \"{cmd}\""
    #             os.system(shell_cmd)

    #     # RR의 경우, SW를 하고 진행한다.

    for m in modlist:
        m[3] = 0 # reset the number of read lines (pertaining to that mode) in temp.txt
        dic[m[0]] = {}
        for i in range(0,4):
            os.system("sh -c \"sudo nvme format /dev/nvme0n1 -f\"")
            fio_offset = (time.time_ns() % 100) * 8 # offset is set randomly so that one region does not degrade quickly as a result of repeated writes and reads

            if m[0] == 'randread': # RR should be done after SW
                # print("doing SW before RR...")
                os.system(f"sh -c \"sudo fio --minimal --filename=/dev/nvme0n1 --direct=1 --rw=write --ioengine=psync --bs=256k"
                          f"--iodepth=1 --size=4G --name=RR_prep --offset={fio_offset}G --output=/dev/null\"")

            bs = 4 * (4**i)
            dic[m[0]][f"{bs}"] = 0

            with open('output/temp.txt', 'a') as f, stdout_redirected(f):
                cmd = f"sh -c \"sudo fio --minimal --filename=/dev/nvme0n1 --direct=1 --rw={m[0]} --ioengine=psync --bs={bs}k"
                f"--iodepth=1 --size=4G --name=fio_seq_{m[1]}_test --offset={fio_offset}G\""
                os.system(cmd)

    
    with open('output/temp.txt') as f:
        for line in f:
            linesplit = line.split(";")
            for m in modlist:
                if m[1] in linesplit[2]:
                        sn = 56 if (m[2] % 2) else 15  # m[2] % 2 != 0: write
                        if current_iter == 0:
                            latencies[m[2]].append(float(linesplit[sn]))
                        else:
                            latencies[m[2]][m[3]] += float(linesplit[sn])
                            m[3] += 1


    # latencies = [[], []]
    # with open('output/temp.txt') as f:
    #     for line in f:
    #         if 'read' in line.split(";")[2]:
    #             latencies[0].append(float(line.split(";")[15]))
    #         else:
    #             latencies[1].append(float(line.split(";")[56]))

    # print this iteration
    print (f"Iteration {current_iter}")
    for m in modlist:
            print(m[1],end=": ")
            for j in range(0,4):
                print(latencies[m[2]][j], end=", ")
            print("")
                


with open("output/real_hynix.json", 'w') as f:
    for m in modlist:
        for i in range(0, 4):
            bs = 4 * 4 ** i
            dic[m[0]][f"{bs}"] = latencies[m[2]][i] / repeats

    print(dic)
    json.dump(dic, f)

        