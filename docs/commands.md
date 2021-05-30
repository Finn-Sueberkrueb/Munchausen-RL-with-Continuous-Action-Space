### conda

Package list for creating same environment elsewhere\
`conda env export -n adlr > ~/Repositories/tum-adlr-ss21-08/setup/requirements.yml`

### Start important scripts

`cd rl-baselines3-zoo`

Train in background process and redirect output to file\
`nohup python train.py --algo msac --env AntBulletEnv-v0 --tensorboard-log logs/tensorboard --n-timesteps 1000000 --seed 1 > msac.out &`

Visualize trained agent\
`python enjoy.py --algo sac --env AntBulletEnv-v0 --verbose 1 --reward-log enjoy_reward_log --n-timesteps 1000`

### Visualize while training

Start tensorboard on VM\
`tensorboard --host localhost --logdir logs/tensorboard`

Then reroute socket on computer to open tensorboard webpage\
`gcloud compute ssh "instance-c2" -- -NfL 6006:localhost:6006`

## Setup

Use [setup/preinstall_vm.sh](./setup/preinstall_vm.sh) and [setup/install_vm.sh](./setup/install_vm.sh) on fresh VM

Was required once on computer after adding forked submodule\
`git submodule set-url rl-baselines3-zoo https://github.com/marcelbrucker/rl-baselines3-zoo.git`

Copy file from computer to VM\
`gcloud compute scp --project "tum-adlr-ss21-08" ~/Repositories/tum-adlr-ss21-08/setup/install_vm.sh instance-c2:~`

Copy folder from VM to computer\
`gcloud compute scp --recurse instance-c2:~/Repositories/tum-adlr-ss21-08/rl-baselines3-zoo/logs/\{sac,msac,tensorboard\} ~/Repositories/tum-adlr-ss21-08/docs/results`