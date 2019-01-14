import mcts.AdaptiveStressTestingBlindValue as AST_BV
import mcts.ASTSim as ASTSim
import mcts.MCTSdpw as MCTSdpw
import mcts.AST_MCTS as AST_MCTS
import numpy as np
from mylab.rewards.ast_reward import ASTReward
from mylab.envs.ast_env import ASTEnv
from mylab.simulators.policy_simulator import PolicySimulator
from Cartpole.cartpole import CartPoleEnv
import tensorflow as tf
from garage.misc import logger
from mylab.envs.tfenv import TfEnv
import math

import os
os.environ["CUDA_VISIBLE_DEVICES"]="-1"    #just use CPU

import os.path as osp
import argparse

import joblib
import mcts.BoundedPriorityQueues as BPQ
import csv

# Logger Params
parser = argparse.ArgumentParser()
parser.add_argument('--exp_name', type=str, default="cartpole")
parser.add_argument('--n_trial', type=int, default=5)
parser.add_argument('--n_itr', type=int, default=1200)
parser.add_argument('--batch_size', type=int, default=4000)
parser.add_argument('--snapshot_mode', type=str, default="gap")
parser.add_argument('--snapshot_gap', type=int, default=10)
parser.add_argument('--log_dir', type=str, default='./Data/AST/MCTS_BV')
parser.add_argument('--args_data', type=str, default=None)
args = parser.parse_args()

top_k = 10
interactive = False

stress_test_num = 2
max_path_length = 100
ec = 100.0
M = 10
n = args.n_itr
k=0.5
alpha=0.85
clear_nodes=True
top_k = 10
RNG_LENGTH = 2
SEED = 0

tf.set_random_seed(0)
sess = tf.Session()
sess.__enter__()

# Instantiate the env
env_inner = CartPoleEnv(use_seed=False)
data = joblib.load("Data/Train/itr_50.pkl")
policy_inner = data['policy']
reward_function = ASTReward()

simulator = PolicySimulator(env=env_inner,policy=policy_inner,max_path_length=max_path_length)
env = TfEnv(ASTEnv(interactive=interactive,
							 simulator=simulator,
							 sample_init_state=False,
							 s_0=[0.0, 0.0, 0.0 * math.pi / 180, 0.0],
							 reward_function=reward_function,
							 ))

with open(osp.join(args.log_dir, 'total_result.csv'), mode='w') as csv_file:
	fieldnames = ['step_count']
	for i in range(top_k):
		fieldnames.append('reward '+str(i))
	writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
	writer.writeheader()

	for trial in range(args.n_trial):
		# Create the logger
		log_dir = args.log_dir+'/'+str(trial)

		tabular_log_file = osp.join(log_dir, 'process.csv')
		text_log_file = osp.join(log_dir, 'text.txt')
		params_log_file = osp.join(log_dir, 'args.txt')

		logger.set_snapshot_dir(log_dir)
		logger.set_snapshot_mode(args.snapshot_mode)
		logger.set_snapshot_gap(args.snapshot_gap)
		logger.log_parameters_lite(params_log_file, args)
		if trial > 0:
			old_log_dir = args.log_dir+'/'+str(trial-1)
			logger.pop_prefix()
			logger.remove_text_output(osp.join(old_log_dir, 'text.txt'))
			logger.remove_tabular_output(osp.join(old_log_dir, 'process.csv'))
		logger.add_text_output(text_log_file)
		logger.add_tabular_output(tabular_log_file)
		logger.push_prefix("["+args.exp_name+'_trial '+str(trial)+"]")

		np.random.seed(trial)
		SEED = trial
		top_paths = BPQ.BoundedPriorityQueueInit(top_k)
		ast_params = AST_BV.ASTParams(max_path_length,ec,M,args.batch_size,log_tabular=True)
		ast = AST_BV.AdaptiveStressTestBV(p=ast_params, env=env, top_paths=top_paths)

		macts_params = MCTSdpw.DPWParams(max_path_length,ec,n,k,alpha,clear_nodes,top_k)
		stress_test_num = 2
		if stress_test_num == 2:
			result = AST_MCTS.stress_test2(ast,macts_params,top_paths,verbose=False, return_tree=False)
		else:
			result = AST_MCTS.stress_test(ast,macts_params,top_paths,verbose=False, return_tree=False)

		row_content = dict()
		row_content['step_count'] = ast.step_count
		for j in range(top_k):
			row_content['reward '+str(j)] = result.rewards[j]
		writer.writerow(row_content)

