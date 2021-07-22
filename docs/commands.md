### conda

Package list for creating same environment elsewhere\
`conda env export -n adlr > ~/Repositories/tum-adlr-ss21-08/setup/requirements.yml`

### git

Commit on computer\
`cd ~/Repositories/tum-adlr-ss21-08/rl-baselines3-zoo`\
`git <add, commit, push>`\
`cd ..`\
`git <add, commit, push>`

Update VM repos\
`cd ~/Repositories/tum-adlr-ss21-08`\
`git pull`\
`git submodule update --recursive`

`git merge <branch> --no-commit --no-ff`
### Start important scripts

`cd rl-baselines3-zoo`

Train in background process and redirect output to file\
`nohup python train.py --algo msac --env HalfCheetahBulletEnv-v0 --tensorboard-log logs/tensorboard --n-timesteps 1000000 --seed 1 > msac.out &`

`nohup python scripts/run_jobs.py > msac.out &`

Visualize trained agent\
`python enjoy.py --algo sac --env HopperBulletEnv-v0 --folder ~/Repositories/tum-adlr-ss21-08/docs/results --n-timesteps 1000`

With changed enjoy.py file to select the file directly\
`python rl-baselines3-zoo/enjoy.py --algo msac --env HalfCheetahBulletEnv-v0 --folder docs/results/msac/HalfCheetahBulletEnv-v0_1_shift_30 `

Plot training success (y-axis) w.r.t. timesteps (x-axis) with a moving window of 500 episodes\
`python scripts/plot_train.py --algo sac msac --env HopperBulletEnv-v0 --y-axis reward --x-axis steps --exp-folder ~/Repositories/tum-adlr-ss21-08/docs/results/ --episode-window 500`

Plot evaluation reward\
`python scripts/all_plots.py -a sac msac --env AntBulletEnv-v0 --print-n-trials -max 1000000 -exp state_based action_based -f /Users/Marcel/Repositories/tum-adlr-ss21-08/docs/results -l ./results`

Plot any tensorboard scalar\
`python scripts/plot_from_tensorboard.py -a sac msac --env AntBulletEnv-v0 --print-n-trials -max 1000000 -exp state_based action_based -f /Users/Marcel/Repositories/tum-adlr-ss21-08/docs/results -l ./results -t train/std`

Record video\
`python -m utils.record_video --algo sac --env AntBulletEnv-v0 -n 1000 --folder ~/Repositories/tum-adlr-ss21-08/docs/results --output-folder ~/Repositories/tum-adlr-ss21-08/docs/images/videos --exp-id 1`

Record GIF\
`python -m utils.record_training --algo msac --env Walker2DBulletEnv-v0 -n 1000 --folder ~/Repositories/tum-adlr-ss21-08/docs/results --output-folder ~/Repositories/tum-adlr-ss21-08/docs/images/videos --seed 1 --exp-id 1 --gif`
### Visualize while training

Start tensorboard on VM\
`tensorboard --host localhost --logdir logs/tensorboard`

Then reroute socket on computer to open tensorboard webpage\
`gcloud compute ssh "instance-c2" -- -NfL 6006:localhost:6006`

Start TensorBoard on server to access over web\
`nohup tensorboard --bind_all --port 8080 --logdir logs/tensorboard &`
## Setup

Use [setup/preinstall_vm.sh](./setup/preinstall_vm.sh) and [setup/install_vm.sh](./setup/install_vm.sh) on fresh VM

Copy file from computer to VM\
`gcloud compute scp --project "tum-adlr-ss21-08" ~/Repositories/tum-adlr-ss21-08/setup/install_vm.sh instance-c2:~`

Copy folder from VM to computer\
`gcloud compute scp --recurse instance-c2:~/Repositories/tum-adlr-ss21-08/rl-baselines3-zoo/logs/\{sac,msac,tensorboard\} ~/Repositories/tum-adlr-ss21-08/docs/results`
