import numpy as np
from typing import *
import get_params_multi as get_params
import scipy.optimize
from scipy.stats import loguniform
import copy
import global_values
import json
import datetime
import skopt
import mobopt

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


if __name__ == '__main__':
	# low and high of each variable for x0
	# 7 values for: 4KB read latency, (read latency / 4KB read latency), prog latency,
	# 4KB read FW, read FW, WBUF latency 0 (constant), WBUF latency 1 (per page)
	# x0_lowhigh = [[1e4,12e4,"uniform"],[0.6, 1.65,"log-uniform"],[0,35e3,"uniform"],
	# 							[0,3e3,"uniform"],[0,3e3,"uniform"],[0,4e3,"uniform"],[0,1e3,"uniform"]]
	x0_lowhigh = [[1e3,19e4,"uniform"],[0.45, 2.25,"log-uniform"],[0,4e5,"uniform"],
								[0,8e3,"uniform"],[0,8e3,"uniform"],[0,1e4,"uniform"],[0,1.5e3,"uniform"]]
	
	pbounds = np.array([[x[0], x[1]] for x in x0_lowhigh])

	checkpoint_file = f"./output/multiple_res/checkpoint_{TIME_STRING} (SN570).npz" # change identifier based on real_hynix
	checkpoint_saver = [skopt.callbacks.CheckpointSaver(checkpoint_file)] # set to None to disable checkpointing
	LOAD = 0 # put file to load (./output/multiple_res/checkpoint 1691380588.pkl), if not loading a previous result from a file, set to 0

	optimizer = mobopt.MOBayesianOpt(target=get_params.get_params, pbounds=pbounds,
				  NObj=(global_values.bscount * global_values.modlist.__len__()), max_or_min='min',
					n_restarts_optimizer=10,
					Filename="./output/multiple_res/opt_progress",
					verbose=True, Picture=False)
	
	if LOAD:
		optimizer.ReadSpace(filename=LOAD)
	else:
		optimizer.initialize(init_points=10)

	res = optimizer.maximize(n_iter=50, SaveInterval=5)
	
	optimizer.WriteSpace(filename=checkpoint_file)
	print(res)