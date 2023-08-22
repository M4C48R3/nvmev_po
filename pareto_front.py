import numpy as np
import get_params

# keys: 'Front' (128,14) 'Pop' (128,7) 'PF' (??, 14) 'PS' (??, 7)
array = np.load("/home/csl/nvrel/nvmev_po/output/multiple_res/FF_D07_I0045_NI60_P0.10_Q0.50opt_progress_230817T1524.npz", allow_pickle=True)

K = 0.1
obj_func_sums = np.average(array['Front'], axis=1)
# indexes with value below K
for idx in np.where(obj_func_sums < K)[0]:
	print(f"*** {idx} START ***")
	print(array['Pop'][idx])
	print(array['Front'][idx])
	print(get_params.get_params( array['Pop'][idx] ))
	print(f"*** {idx} END ***")