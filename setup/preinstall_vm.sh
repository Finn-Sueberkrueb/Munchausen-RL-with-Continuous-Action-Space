# run on computer
# chmod +x preinstall_vm.sh
# ./preinstall_vm.sh

VM=mock-instance
gcloud compute scp --project "tum-adlr-ss21-08" ~/Repositories/tum-adlr-ss21-08/setup/install_vm.sh $VM:~
gcloud compute scp --project "tum-adlr-ss21-08" ~/.ssh/id_rsa.pub ~/.ssh/id_rsa $VM:~/.ssh