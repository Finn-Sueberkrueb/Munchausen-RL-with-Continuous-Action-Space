# run on computer
# chmod +x connect_vm.sh
# ./connect_vm.sh

# gcloud compute regions list
# gcloud config set compute/region REGION
# gcloud compute zones list
# gcloud config set compute/zone ZONE
VM=mock-instance
gcloud config set compute/region europe-west3
gcloud config set compute/zone europe-west3-c
gcloud compute ssh "$VM" --project "tum-adlr-ss21-08"