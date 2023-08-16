import numpy as np
from typing import *
import get_params_multi as get_params
import scipy.optimize
from scipy.stats import loguniform
import copy
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
initial_variance = 0.3


if __name__ == '__main__':
	# low and high of each variable for x0
	# 7 values for: 4KB read latency, (read latency / 4KB read latency), prog latency,
	# 4KB read FW, read FW, WBUF latency 0 (constant), WBUF latency 1 (per page)
	# x0_lowhigh = [[1e4,12e4,"uniform"],[0.6, 1.65,"log-uniform"],[0,35e3,"uniform"],
	# 							[0,3e3,"uniform"],[0,3e3,"uniform"],[0,4e3,"uniform"],[0,1e3,"uniform"]]
	x0_lowhigh = [[1e3,25e4,"uniform"],[0.4, 2.5,"log-uniform"],[0,5e5,"uniform"],
								[0,8e3,"uniform"],[0,8e3,"uniform"],[0,1e4,"uniform"],[0,1.5e3,"uniform"]]
	
	#skopt_dim = [skopt.space.space.Real(x0[0], x0[1], prior=x0[2]) for x0 in x0_lowhigh]
	pbounds = np.array([[x[0], x[1]] for x in x0_lowhigh])

	optimizer = mobopt.MOBayesianOpt(target=get_params.get_params, pbounds=pbounds, NObj=x0_lowhigh.__len__, max_or_min='min',
                                  n_restarts_optimizer=10,
                                  # Filename="./output/multiple_res/opt_progress", 
                                  verbose=True, Picture=False)


	checkpoint_file = f"./output/checkpoints/checkpoint_{TIME_STRING} (SN570).pkl" # change identifier based on real_hynix
	checkpoint_saver = [skopt.callbacks.CheckpointSaver(checkpoint_file)] # set to None to disable checkpointing
	LOAD = 0 # put file to load (./output/checkpoints/checkpoint 1691380588.pkl), if not loading a previous result from a file, set to 0
	res = skopt.load(LOAD) if LOAD else None
	res = skopt.optimizer.gp_minimize(
		func=get_params.get_params, dimensions=skopt_dim,
		initial_point_generator="hammersly", n_calls=180, n_random_starts=20,
		verbose=True, callback=checkpoint_saver,
		x0=res.x_iters if LOAD else None, y0=res.func_vals if LOAD else None
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
