# run on VM
# chmod +x install_vm.sh
# ./install_vm.sh

# preparation
sudo apt update && sudo apt upgrade
sudo apt install build-essential
sudo apt install nano
sudo apt install git-all

# install anaconda
cd /tmp
sudo apt install curl
curl -O https://repo.anaconda.com/archive/Anaconda3-2021.05-Linux-x86_64.sh
bash Anaconda3-2021.05-Linux-x86_64.sh
source ~/.bashrc

# git repo
mkdir ~/Repositories
cd ~/Repositories
git clone git@github.com:Finn-Sueberkrueb/tum-adlr-ss21-08.git
cd ~/Repositories/tum-adlr-ss21-08
git checkout dev/marcel

# create conda environment
# conda env create -f ~/Repositories/tum-adlr-ss21-08/setup/requirements.yml
conda config --append channels conda-forge
conda create -n adlr python=3.7
conda activate adlr
pip install stable-baselines3[extra]
cd ~/Repositories
git clone https://github.com/benelot/pybullet-gym.git
cd pybullet-gym
pip install -e .

# install cuda
# sudo apt install linux-headers-$(uname -r)
# wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/cuda-ubuntu2004.pin
# sudo mv cuda-ubuntu2004.pin /etc/apt/preferences.d/cuda-repository-pin-600
# sudo apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/7fa2af80.pub
# sudo add-apt-repository "deb https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/ /"
# sudo apt-get update
# sudo apt-get -y install cuda