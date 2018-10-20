import mcts.AdaptiveStressTesting as AST
import mcts.ASTSim as ASTSim
import mcts.MCTSdpw as MCTSdpw
import mcts.AST_MCTS as AST_MCTS
import numpy as np
from mylab.rewards.ast_reward import ASTReward
from mylab.envs.ast_env import ASTEnv
from mylab.simulators.policy_simulator import PolicySimulator
from Cartpole.cartpole import CartPoleEnv
import tensorflow as tf
from rllab.misc import logger
from sandbox.rocky.tf.envs.base import TfEnv
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
parser.add_argument('--n_itr', type=int, default=1000)
parser.add_argument('--batch_size', type=int, default=4000)
parser.add_argument('--snapshot_mode', type=str, default="gap")
parser.add_argument('--snapshot_gap', type=int, default=10)
parser.add_argument('--log_dir', type=str, default='./Data/AST/MCTS_AS')
parser.add_argument('--args_data', type=str, default=None)
args = parser.parse_args()

top_k = 10
interactive = False

stress_test_num = 2
max_path_length = 30#100
ec = 100.0
n = args.n_itr
k=0.5
alpha=0.85
clear_nodes=True
top_k = 10
RNG_LENGTH = 2
SEED = 0
batch_size = 1000

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

# Create the logger
log_dir = args.log_dir+'/test'

tabular_log_file = osp.join(log_dir, 'process.csv')
text_log_file = osp.join(log_dir, 'text.txt')
params_log_file = osp.join(log_dir, 'args.txt')

logger.set_snapshot_dir(log_dir)
logger.set_snapshot_mode(args.snapshot_mode)
logger.set_snapshot_gap(args.snapshot_gap)
logger.log_parameters_lite(params_log_file, args)
logger.add_text_output(text_log_file)
logger.add_tabular_output(tabular_log_file)
logger.push_prefix("["+args.exp_name+"]")

np.random.seed(0)

SEED = 0
top_paths = BPQ.BoundedPriorityQueueInit(top_k)
ast_params = AST.ASTParams(max_path_length,args.batch_size,log_tabular=True)
ast = AST.AdaptiveStressTest(p=ast_params, env=env, top_paths=top_paths)

macts_params = MCTSdpw.DPWParams(max_path_length,ec,n,k,alpha,clear_nodes,top_k)
stress_test_num = 2
if stress_test_num == 2:
	result = AST_MCTS.stress_test2(ast,macts_params,top_paths,verbose=False, return_tree=False)
else:
	result = AST_MCTS.stress_test(ast,macts_params,top_paths,verbose=False, return_tree=False)

ast.params.log_tabular = False
for (i,action_seq) in enumerate(result.action_seqs):
	reward, _ = ASTSim.play_sequence(ast,action_seq,sleeptime=0.0)
	print("predic reward: ",result.rewards[i])
	print("actual reward: ",reward)	

