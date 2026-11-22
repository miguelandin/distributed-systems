sudo kubeadm reset
sudo apt-get purge -y kubelet kubectl kubeadm kubernetes-cni cri-tools
sudo apt-get purge docker.io containerd
sudo rm -r /etc/kubernetes/
sudo rm -r /var/lib/etcd/
sudo rm -r /opt/cni
sudo rm -r /etc/cni
sudo rm -r /etc/containerd/
sudo rm -r /etc/apt/sources.list.d/kubernetes.list

rm -r ~/.kube
