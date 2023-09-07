import json
import os
import math

blocksizes = []
nb = 4
while nb <= 256:
    blocksizes.append(nb)
    nb *= 2
jobs = ("randread", "randwrite")
fv = "./output/ours_hynix.json"
f = open(fv, "r")
jsondata = json.load(f)
f.close()
data_table = []
for key in jsondata.keys():
    data_table.append([int(math.floor(float(nstr))) for nstr in key.strip('[]').split(', ')]) # keys are list of parameters, stored as strings.
    data_table[-1].append(data_table[-1][-1] / 86400 + 25569 + 9/24) # unix timestamp (last element) to excel date & time format (25569 = days from 1900-01-01 to 1970-01-01). + 9/24 = UTC to KST
    data_table[-1].append(jsondata[key]["perf"]) # overall performance
    for j in jobs:
        for bs in blocksizes:
            data_table[-1].append(jsondata[key]["vals"][j][str(bs)])

f = open("./output/real_hynix.json")
jsondata = json.load(f)
f.close()

savef = open("./output/simulation_results_table.txt", "w")

# save data table
labels = ["4K LSB", "4K MSB", "4K CSB", "LSB", "MSB", "CSB", "PROG", "4K READ FW", "READ FW", "WBUF FW 0", "WBUF FW 1", "CH XFER LAT", "ERASE", "UNIX TIME", "EXCEL TIME", "OVERALL PERF"]
actualdata = [""] * len(labels)
actualdata[-1] = "ACTUAL"
for j in jobs:
    for bs in blocksizes:
        labels.append(j + "." + str(bs))
        actualdata.append(str(jsondata[j][str(bs)]))
print("\t".join(labels), file=savef)
print("\t".join(actualdata), file=savef)
for row in data_table:
    print("\t".join([str(x) for x in row]), file=savef)
savef.close()