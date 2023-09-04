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
from time import time as unixtime
def get_params(values_) -> float:
	## 0: --rw= argument and dictionary key / 1: code for finding through 'in' / 2: index / 3: number of lines read from temp.txt so far
	modlist = copy.deepcopy(gv.modlist)
	#values = copy.deepcopy(values_)

	# reduced to 7 to 9 values, given ratios of LSB/MSB/CSB latencies. FW_CH_XFER_LATENCY (values[11], ${12:-0} in make_config) and ERASE_LATENCY (values[12], ${13:-0} in make_config) are defaulted to zero if unspecified.
	if len(values_) < 7 or len(values_) > 9:
		print("ERROR! There must be 7 to 9 values.")
		return
	vcount = len(values_) + 4
	values = [0 for dummy in vcount]
	for i in range(3):
		values[i] = values_[0] * gv.latency_multiple_cellpos[i] # 4KB read latency (LSB,MSB,CSB)
		values[i+3] = values_[0] * values_[1] * gv.latency_multiple_cellpos[i] # read latency (LSB,MSB,CSB)
	for i in range(6,vcount):
		values[i] = values_[i-4]

	values = [math.floor(v) for v in values]
	for val in values:
		if val < 0:
			return 1000
	
	try:
		with open("output/ours_hynix.json") as f:
			cache = json.load(f)
	except:
		cache = {}

	# cache is a dict, and if input is the same, it will return the same output. time is added to make sure that the keys do not collide
	# cache now serves as a history of inputs and outputs, not returning the same output twice
	values.append(unixtime())
	key = tuple(values)
	print(key)
	cache[key] = {}
	values.pop() # remove time from values
	
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
				gv.printv("doing SW before RR...")
				cmd = f"sh -c \"sudo fio --minimal --filename={gv.virtdevname} --direct=1 --rw=write --ioengine=psync --bs=256k " \
				f"--iodepth=1 {gv.virt_test_size} --name=RR_prep --output=/dev/null\""
				os.system(cmd)
						  
			ours[m[0]][f"{bs}"] = 0

			with open('output/temp.txt', 'a') as f, stdout_redirected(f):
				cmd = f"sh -c \"sudo fio --minimal --filename={gv.virtdevname} --direct=1 --rw={m[0]} --ioengine=psync --bs={bs}k " \
				f"--iodepth=1 {gv.virt_test_size} --name=fio_seq_{m[1]}_test\""
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
			# log2(bs): different weights, more weight for larger block size as this does not seem to be getting large block reads right
	diff /= (modlist.__len__() * gv.bscount) # average error rate

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
	# 7 values for 4KB read latency, (read latency / 4KB read latency), prog latency, 4KB read FW, read FW, WBUF latency 0, WBUF latency 1
	# Possibly 2 more, FW_CH_XFER_LATENCY (values[11], ${12:-0} in make_config) and ERASE_LATENCY (values[12], ${13:-0} in make_config) are defaulted to zero if unspecified.
	# arr=[3e4, 1.00, 20e3, 2e3, 1e3, 1e3, 500]
	# avg read latency = 41us = 1.433 ((1 + 1.5 + 1.8) / 3) * 24e3 (ns) * 1.2 (assumed 4KB read optimization factor)
	

	arr = [24e3,1.2,950e3,1000,100,100,100]
	get_params(arr)
