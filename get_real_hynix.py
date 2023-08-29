import os
from common import stdout_redirected
import json
import global_values as gv
import copy

dic = {}
## 0: --rw= argument / 1: code / 2: index / 3: number of lines read from temp.txt so far
modlist = copy.deepcopy(gv.modlist)
def printv(x):
	gv.printv(x)
repeats = 4
latencies = [[] for dummy in modlist]


for current_iter in range(repeats):
	# add time_string and current_iter to retain all data without overwriting
	fname = f"output/realdata/{gv.TIME_STRING}_{current_iter}.txt"
	print(fname)

	with open(fname, 'w') as f: pass # empty file

	for m in modlist:
		m[3] = 0 # reset the number of read lines (pertaining to that mode) in temp.txt
		dic[m[0]] = {}
		for bs in gv.bslist:
			os.system(f"sh -c \"sudo nvme format {gv.realdevname} {gv.forceformat} >/dev/null\"")
			# offset is set randomly so that one region does not degrade quickly as a result of repeated writes and reads
			# fio_offset = (time.time_ns() % 100) * 8

			if m[0] == 'randread': # RR should be done after SW
				printv("doing SW before RR...")
				cmd = f"sh -c \"sudo fio --minimal --filename={gv.realdevname} --direct=1 --rw=write --ioengine=psync --bs=256k " \
				f"--iodepth=1 --size={gv.realfiosize} --name=RR_prep --output=/dev/null\""
				os.system(cmd)

			dic[m[0]][f"{bs}"] = 0

			printv(f"Doing {m[0]} with bs = {bs}KB...")
			with open(fname, 'a') as f, stdout_redirected(f):
				cmd = f"sh -c \"sudo fio --minimal --filename={gv.realdevname} --direct=1 --rw={m[0]} --ioengine=psync --bs={bs}k " \
				f"--iodepth=1 --size={gv.realfiosize} --name=fio_seq_{m[1]}_test\""
				os.system(cmd)

	
	with open(fname) as f:
		for line in f:
			linesplit = line.split(";")
			for m in modlist:
				if m[1] in linesplit[2]:
						sn = 56 if (m[1] in ["RW", "SW"]) else 15 # write completion latency is in position 56, read completion latency in 15
						if current_iter == 0:
							latencies[m[2]].append(float(linesplit[sn])) # first write: list is empty
						else:
							latencies[m[2]][m[3]] += float(linesplit[sn]) # list is not empty, add value and move position
							m[3] += 1 # position to write next value


	# latencies = [[], []]
	# with open(fname) as f:
	#     for line in f:
	#         if 'read' in line.split(";")[2]:
	#             latencies[0].append(float(line.split(";")[15]))
	#         else:
	#             latencies[1].append(float(line.split(";")[56]))

	# print this iteration
	print (f"Iteration {current_iter} (Average so far)")
	print ("BS: ", end="")
	for bs in gv.bslist:
		print(bs, end=", ")
	print("")
	for m in modlist:
			print(m[1],end=": ")
			for j in range(gv.bscount):
				print(latencies[m[2]][j] / (current_iter + 1), end=", ")
			print("")
				


with open("output/real_hynix.json", 'w') as f:
	for m in modlist:
		for i in range(gv.bscount):
			bs = gv.bs_from_index(i)
			dic[m[0]][f"{bs}"] = latencies[m[2]][i] / repeats

	print(dic)
	json.dump(dic, f)
