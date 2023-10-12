import numpy as np
from typing import *
import get_params
import scipy.optimize
from scipy.stats import loguniform
import copy
import json
import datetime
import skopt

#SAMPLE_INITIAL_INPUTS = np.array([[1,2,6,3,8], [7,2,5,4,3], [1,7,4,11,6]], dtype = np.float64)
SAMPLE_INITIAL_INPUTS = np.random.randint(0, 20, size=(15,14)).astype(np.float64)
t = datetime.datetime.utcnow() + datetime.timedelta(hours=9) # adding 9h for KST
TIME_STRING = t.strftime("%y%m%dT%H%M")
class NpEncoder(json.JSONEncoder):
	def default(self, obj):
		if isinstance(obj, np.integer):
			return int(obj)
		if isinstance(obj, np.floating):
			return float(obj)
		if isinstance(obj, np.ndarray):
			return obj.tolist()
		return json.JSONEncoder.default(self, obj)

ITERATION = 80
PRINT_OPTION = False


#good = '2000-2000-2000-1500-1500-1500-100000-3000-2000-5000-500'
good = '60000-60000-60000-50000-50000-50000-10000-1500-1500-2000-500'
INPUT_CENTRIC = list(map(int, good.split('-')))
# INPUT_CENTRIC = [73000, 73000, 73000, 73000, 695000, 21500, 30490, 4000, 460]
initial_variance = 0.3

alpha = 1
gamma = 3
rho = 1/2
sigma = 1/2



def Nelder_Mead(inputs:np.ndarray, fn):
	assert(inputs.shape[0] >= 3) # 3 or more inputs required

	#Ordering
	is_deg, rec = check_degeneracy(inputs)
	if not is_deg:
		for i in range(inputs.shape[0]):
			if rec[tuple(inputs[i,:].tolist())] > 1:                   
				inputs[i,:] += np.random.randint(-1, 1, size=inputs.shape[1]).astype(np.float64)
				inputs[i, inputs[i,:] < 0] = 0
	fs = np.array([round_and_execute(input_single, fn) for input_single in inputs], dtype = np.float64)
	sorted_index = fs.argsort()
	inputs =inputs[sorted_index]
	fs=fs[sorted_index]
	
	#Centroid
	x_0 = np.mean(inputs[:-1,:].astype(np.float64), axis = 0)

	#Reflection
	x_r = x_0 + alpha*(x_0 - inputs[-1,:])
	x_r[x_r < 0] = 0
	f_r = round_and_execute(x_r, fn)

	if (fs[0] <= f_r) and (f_r < fs[-2]):
		inputs[-1,:] = np.round(x_r)
		fs[-1] = f_r

		if PRINT_OPTION: print("Reflection")
	
	elif f_r < fs[0]:
		#Expansion
		x_e = x_0 + gamma*(x_r - x_0)
		x_e[x_e<0] = 0
		f_e = round_and_execute(x_e, fn)

		if f_e < f_r:
			inputs[-1,:] = np.round(x_e)
			fs[-1] = f_e
		else:
			inputs[-1,:] = np.round(x_r)
			fs[-1] = f_r

		if PRINT_OPTION: print("Expansion")

	else: #f[-2] < f_r
		#Contraction
		bool_shrink = False
		if f_r < fs[-1]:
			x_c = x_0 + rho*(x_r - x_0)
			x_c[x_c<0] = 0
			f_c = round_and_execute(x_c, fn)
			
			if f_c < f_r:
				inputs[-1,:] = np.round(x_c)
				fs[-1] = f_c
			else:
				bool_shrink = True
			
		else:
			x_c = x_0 + rho*(inputs[-1,:] - x_0)
			x_c[x_c<0] = 0
			f_c = round_and_execute(x_c, fn)

			if f_c < fs[-1]:
				inputs[-1,:] = np.round(x_c)
				fs[-1] = f_c
			else:
				bool_shrink = True
		
		if bool_shrink:
			#Shrink
			inputs[:] = inputs[0,:] + sigma*(inputs[:] - inputs[0,:])
			inputs[inputs<0] = 0
			inputs = np.round(inputs)
			fs = np.array([round_and_execute(input_single, fn) for input_single in inputs], dtype = np.float64)

			if PRINT_OPTION: print("Shrink")

		else:

			if PRINT_OPTION: print("Contraction")
	
	#find best current best config
	best_config_ind = np.argmin(fs)

	return inputs, inputs[best_config_ind], fs[best_config_ind]

def round_and_execute(input_single: np.ndarray, fn):
	
	return fn(np.round(input_single).astype(int))

def sample_fn(input_single: np.ndarray):
	return np.sum(input_single**2)

def sample_fn_2(input_single: np.ndarray):
	return np.sum((input_single - np.array(INPUT_CENTRIC))**2)

def check_degeneracy(inputs: np.ndarray):
	temp_record = {}
	for input in inputs:
		input = tuple(input.tolist())
		if input not in temp_record:
			temp_record[input] = 1
		else:
			temp_record[input] += 1
	for record in temp_record.keys():
		if temp_record[record] > 1: return False, temp_record
	return True, {}

def simplex_variance(inputs: np.ndarray):
	return np.var(inputs, axis = 0)

'''
def simplex_generator(input_centric):
	n = len(input_centric)
	L = [1 if i < (n+1)/2 else 0 for i in range(n)]
	Mapper = [0 for i in range(n)]
	for i in range(n):
		Mapper += L
		L = [L[-1]] + L[:-1]
	Mapper = np.array(Mapper).reshape(n+1,n).astype(np.float64)
	variance = np.array(input_centric)*initial_variance
	initial_input = np.zeros((n+1,n), dtype = np.float64)
	initial_input += np.array(input_centric)
	initial_input -= variance
	initial_input += 2 * np.multiply(Mapper, variance)
	return np.round(initial_input)
'''

#generates initial simplex and keeps write variables fixed
def simplex_generator(input_centric):
	FULL_SIMPLEX_PROVIDED = "./output/simplex/1690789123 copy.json" # put file to load (./output/simplex/1690358782.json), if not, set to 0
	RANDOMIZE = True
	STORE = True
	STOREFILENAME = f"./output/simplex/{TIME_STRING}.json"

	if FULL_SIMPLEX_PROVIDED:
		f = open(FULL_SIMPLEX_PROVIDED, "r")
		simplex = np.array(json.load(f), dtype=np.float64)
		f.close()
		return simplex

	input_centric = np.array(input_centric, dtype = np.float64)
	simplex = []
	simplex.append(input_centric)
	insize = len(input_centric)
	print(input_centric)
	for i in range(insize):
		add = copy.deepcopy(input_centric)
		if RANDOMIZE:
			for j in range(insize):
				add[j] *= loguniform.rvs(0.25, 4, size=1)[0] - 1
		else:
			for j in range(insize):
				if i == j:
					add[j] *= -0.5
				else:
					add[j] *= 0.5
		simplex.append(input_centric + add)
	
	simplex = np.array(simplex, dtype = np.float64)
	print(simplex[0])
	if STORE:
		f = open(STOREFILENAME, "w")
		json.dump(simplex.tolist(), f)
		f.close()
	return simplex

def make_array_then_gp(inputs:np.ndarray):
	inputs_modif = []
	for i in inputs:
		inputs_modif.append(i)
	if inputs_modif[2] < inputs_modif[1]: # if there are fewer channels than FTLs, set FTLs to channels
		inputs_modif[1] = inputs_modif[2]
	# MDTS = maximum data transfer size, unit 4KB, log2
	# GLOBAL_WB_SIZE is set at NAND_CHANNELS * LUNS_PER_NAND_CH * ONESHOT_PAGE_SIZE
	# or inputs[2] + [3] + [4]
	# MDTS must be smaller than GLOBAL_WB_SIZE
	mdts = -3
	for i in (2,3,4,5):
		mdts += inputs_modif[i]
	if mdts > 6:
		mdts = 6
	inputs_modif.append(mdts)
	for i in (1,2,3,4,5): # these values are stored as log2(x), should be transformed 1 -> 2, 2 -> 4, 3 -> 8, 4 -> 16
		inputs_modif[i] = 2 ** inputs_modif[i]
	inputs_modif[10] *= inputs_modif[9] # (read latency / 4KB read latency) * 4KB read latency = read latency
	inputs_modif[10] = int(inputs_modif[10])
	inputs_modif[9] = int(inputs_modif[9])
	return get_params.get_params(inputs_modif)

def remove_outofbound_points(loaded_cp, skopt_dim):
	x0_fit = []
	y0_fit = []
	ecount = len(loaded_cp.x_iters)
	xsize = len(skopt_dim)
	i = 0
	while i < ecount: # for each point
		j = 0
		toadd = True
		while j < xsize: # for each coordinate dimension
			if loaded_cp.x_iters[i][j] < skopt_dim[j].low or loaded_cp.x_iters[i][j] > skopt_dim[j].high:
				toadd = False 
				j = xsize
			j += 1
		if toadd:
			x0_fit.append(loaded_cp.x_iters[i])
			y0_fit.append(loaded_cp.func_vals[i])
		i += 1

	return x0_fit, y0_fit

if __name__ == '__main__':

	# parameter description [index in python] (index in make_config.sh, there argument 0 is the name of the script)
	skopt_dim = [skopt.space.space.Integer(2,3), # Cell type (1: SLC, 2: MLC, 3: TLC) - [0] A1
			  skopt.space.space.Integer(0,2), # SSD Partitions (FTL Instances), log2 (0->1, 1->2, 2->4, 3->8) - [1] A2
			  skopt.space.space.Integer(1,5), # NAND Channels, log2 - [2] A3. SSD with only one channel is unlikely
			  skopt.space.space.Integer(0,3), # NAND Dies per Channel, log2 - [3] A4
			  skopt.space.space.Integer(2,7), # NAND page size in KB, log2 - [4] A5
			  skopt.space.space.Integer(1,3), # Global WB size, log2 - [5] A6
			  skopt.space.space.Real(2048, 262144, prior="log-uniform"), # line size in KB - [6] A7
			  skopt.space.space.Integer(400, 4000), # channel bandwidth in MB/s - [7] A8
			  skopt.space.space.Integer(5000, 10000), # PCIe bandwidth in MB/s - [8] A9
			  skopt.space.space.Integer(5000, 90000), # 4KB read latency in ns - [9] A10
			  skopt.space.space.Real(0.9, 1.4), # read latency / 4KB read latency - [10] A11 / A10
			  skopt.space.space.Real(0.2 ,1.5), # MSB, CSB multiplier for read latencies - [11] A12
			  skopt.space.space.Integer(50000, 3000000), # prog latency in ns - [12] A13
			  skopt.space.space.Integer(50000, 5000000), # erase latency in ns - [13] A14
			  skopt.space.space.Integer(0,2000), # 4KB read FW - [14] A15
			  skopt.space.space.Integer(0,7000), # read FW - [15] A16
			  skopt.space.space.Integer(0,3000), # WBUF FW 0 (constant) - [16] A17
			  skopt.space.space.Integer(0,400), # WBUF FW 1 (per page) - [17] A18
			  skopt.space.space.Integer(0,800), # channel transfer latency - [18] A19
			  skopt.space.space.Real(0.01, 0.15) # overprovisioning - [19] A20
			  # A21, MDTS, is calculated in make_array_then_gp
			  ]

	checkpoint_file = f"./output/checkpoints/checkpoint_{TIME_STRING} (FADU_FULL_20param).pkl" # change identifier based on real_hynix
	checkpoint_saver = [skopt.callbacks.CheckpointSaver(checkpoint_file)] # set to None to disable checkpointing
	LOAD = "output/checkpoints/checkpoint_231011T1600 (FADU).pkl" # put file to load (./output/checkpoints/checkpoint 1691380588.pkl), if not loading a previous result from a file, set to 0
	# load checkpoint
	loaded_cp = skopt.load(LOAD) if LOAD else None
	loaded_x0, loadeD_y0 = None, None
	if LOAD:
		loaded_x0, loaded_y0 = remove_outofbound_points(loaded_cp, skopt_dim)
	res = skopt.optimizer.gp_minimize(
		func=make_array_then_gp, dimensions=skopt_dim,
		initial_point_generator="hammersly", n_calls=100, n_random_starts=15,
		verbose=True, callback=checkpoint_saver,
		x0=loaded_x0, y0=loaded_y0
	)
	print(res)

#   #configs = SAMPLE_INITIAL_INPUTS
#   configs = simplex_generator(INPUT_CENTRIC)
#   fs = None
#   for iter in range(ITERATION):
#     print("iteration", iter)
#     configs, best_config, best_metric = Nelder_Mead(configs, get_params.get_params)
#     print(best_metric, best_config)
#     print("variance", simplex_variance(configs))

	# # low and high of each variable for x0
	# # 9 values for: 4KB read latency, (read latency / 4KB read latency), prog latency,
	# # 4KB read FW, read FW, WBUF latency 0 (constant), WBUF latency 1 (per page),
	# # channel transfer latency, erase latency
	# x0_lowhigh = [[8e3,35e3,"uniform"],[0.9, 1.4,"uniform"],[6e4,1e6,"uniform"],
	# 							[0,15e3,"uniform"],[0,15e3,"uniform"],[0,2e3,"uniform"],[0,600,"uniform"],[0,7e3,"uniform"],[6e4,2e6,"uniform"]]
	# skopt_dim = [skopt.space.space.Real(x0[0], x0[1], prior=x0[2]) for x0 in x0_lowhigh]

	# checkpoint_file = f"./output/checkpoints/checkpoint_{TIME_STRING} (FADU).pkl" # change identifier based on real_hynix
	# checkpoint_saver = [skopt.callbacks.CheckpointSaver(checkpoint_file)] # set to None to disable checkpointing
	# LOAD = 0 # put file to load (./output/checkpoints/checkpoint 1691380588.pkl), if not loading a previous result from a file, set to 0
	# res = skopt.load(LOAD) if LOAD else None
	# res = skopt.optimizer.gp_minimize(
	# 	func=get_params.get_params, dimensions=skopt_dim,
	# 	initial_point_generator="hammersly", n_calls=60, n_random_starts=10,
	# 	verbose=True, callback=checkpoint_saver,
	# 	x0=res.x_iters if LOAD else None, y0=res.func_vals if LOAD else None
	# )
	# print(res)