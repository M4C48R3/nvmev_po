import numpy as np
from typing import *
import get_params
# import scipy.optimize
from scipy.stats import loguniform
import copy
import random
import json
import time

#SAMPLE_INITIAL_INPUTS = np.array([[1,2,6,3,8], [7,2,5,4,3], [1,7,4,11,6]], dtype = np.float64)
SAMPLE_INITIAL_INPUTS = np.random.randint(0, 20, size=(15,14)).astype(np.float64)

class NpEncoder(json.JSONEncoder):
  def default(self, obj):
    if isinstance(obj, np.integer):
      return int(obj)
    if isinstance(obj, np.floating):
      return float(obj)
    if isinstance(obj, np.ndarray):
      return obj.tolist()
    return json.JSONEncoder.default(self, obj)

ITERATION = 2
PRINT_OPTION = False


#good = '2000-2000-2000-1500-1500-1500-100000-3000-2000-5000-500'
good = '6000-7000-8000-5000-6000-7000-60000-5000-5000-5000-1000'
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
  FULL_SIMPLEX_PROVIDED = "./output/simplex/1690358782.json" # put file to load
  RANDOMIZE = True
  STORE = False
  STOREFILENAME = f"./output/simplex/{int(time.time())}.json"

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
        add[j] *= loguniform.rvs(0.45, 2.25, size=1)[0] - 1
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


if __name__ == '__main__':
  # result = scipy.optimize.minimize(
  #     fun=get_params.get_params, 
  #     x0=np.array([3000,3000,3000,2000,2000,2000,300000,5000,3000,6000,1000]),
  #     tol=5e-3,
  #     method='Nelder-Mead')

  #configs = SAMPLE_INITIAL_INPUTS
  configs = simplex_generator(INPUT_CENTRIC)
  fs = None
  for iter in range(ITERATION):
    print("iteration", iter)
    configs, best_config, best_metric = Nelder_Mead(configs, get_params.get_params)
    print(best_metric, best_config)
    print("variance", simplex_variance(configs))

  

