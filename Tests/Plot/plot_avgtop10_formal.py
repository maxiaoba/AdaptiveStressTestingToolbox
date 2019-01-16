import csv
import os.path
import matplotlib 
matplotlib.rcParams.update({'font.size': 20})
from matplotlib import pyplot as plt
import numpy as np

n_trial = 5
top_k = 10
batch_size = 4000
max_step = 1e7#np.inf
max_reward = np.inf
min_reward = -np.inf

prepath = "../"
# exp = "CartPoleNd"
exp = "Acrobot"
policies = ["TRPO","MCTS_BV","GATRDStep1.0Fmax","PSMCTSStep1.0Ec1.414K0.5A0.5Qmax","PSMCTSTRCStep1.0Ec1.414K0.5A0.5Qmax"]
plot_name = exp
legends = ["TRPO","MCTSBV","GA","PSMCTS*","PSMCTS"]
# colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'w']

# colors = []
# for i in range(len(policies)):
#     colors.append('C'+str(i))


plts = []
# legends = []
fig = plt.figure(figsize=(10, 10))

for (policy_index,policy) in enumerate(policies):
    print(policy)
    Rewards = []
    min_array_length = np.inf
    for trial in range(n_trial):
        file_path = prepath+exp+'/Data/AST/Lexington/'+policy+'/'+str(trial)+'/process.csv'
        if os.path.exists(file_path):
            print(trial)
            steps = []
            rewards = []
            with open(file_path) as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                for (i,row) in enumerate(csv_reader):
                    if i == 0:
                        entry_dict = {}
                        for index in range(len(row)):
                            entry_dict[row[index]] = index
                    else:
                        if int(row[entry_dict["StepNum"]]) > max_step:
                            break
                        if int(row[entry_dict["StepNum"]])%batch_size == 0:
                            steps.append(int(row[entry_dict["StepNum"]]))
                            avg_top = 0.0
                            for k in range(top_k):
                                avg_top += np.clip(float(row[entry_dict["reward "+str(k)]]),min_reward,max_reward)
                            avg_top /= top_k
                            rewards.append(avg_top)
            if len(rewards) < min_array_length:
                min_array_length = len(rewards) 
            Rewards.append(rewards)
            # print(len(rewards))
            # print(steps[-1])
            # print(min_array_length)
    steps = steps[:min_array_length]
    Rewards = [rewards[:min_array_length] for rewards in Rewards]
    # plot, = plt.plot(steps,np.mean(Rewards,0),color=colors[policy_index])
    plot, = plt.plot(steps,np.mean(Rewards,0))
    plts.append(plot)
    # legends.append(policy)

plt.ticklabel_format(style='sci', axis='x', scilimits=(0,0))
plt.legend(plts,legends,loc='lower right')
plt.xlabel('Step Number')
plt.ylabel('Average Top '+str(top_k) +' Reward')        
fig.savefig(prepath+exp+'/Data/Plot/avgtop10/'+plot_name+'_avgtop10.pdf')
plt.close(fig)