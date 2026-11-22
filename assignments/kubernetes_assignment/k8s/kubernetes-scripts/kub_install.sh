#!/usr/bin/env bash
# Laboratorio docente. Ejecutar como ubuntu: bash ./kub_install.sh
# Kubernetes 1.35: alternativa al repositorio antiguo con firma caducada.
# Para una EC2 Ubuntu NUEVA que sera el Control Plane. No ejecutar en Workers.
set -Eeuo pipefail
trap 'echo "ERROR en la linea $LINENO. Instalacion detenida; no continuar con la clonacion." >&2' ERR

if [ "$(id -u)" -eq 0 ]; then
  echo "Ejecutar como usuario ubuntu, sin sudo delante de bash." >&2
  exit 1
fi
. /etc/os-release
if [ "${ID:-}" != ubuntu ] || [ "$(uname -m)" != x86_64 ]; then
  echo "Este instalador requiere Ubuntu Server x86_64." >&2
  exit 1
fi
sudo -n true
if sudo test -f /etc/kubernetes/admin.conf || sudo test -f /etc/kubernetes/kubelet.conf; then
  echo "Esta maquina ya tiene configuracion Kubernetes. Usar una instancia nueva." >&2
  exit 1
fi

K8S_MINOR=1.35
FLANNEL_VERSION=v0.28.9
NODE_NAME=${NODE_NAME:-k8s-control}
WORK_DIR=$(mktemp -d)
trap 'rm -rf -- "$WORK_DIR"' EXIT

echo "=== Preparar Linux ==="
sudo hostnamectl set-hostname "$NODE_NAME"
# Apartar el repositorio de un intento anterior antes de apt-get update.
# Despues se vuelve a crear con la version y clave nuevas.
if sudo test -f /etc/apt/sources.list.d/kubernetes.list; then
  sudo mv /etc/apt/sources.list.d/kubernetes.list \
    "/etc/apt/sources.list.d/kubernetes.list.backup-$(date +%Y%m%d%H%M%S)"
fi
# Kubernetes 1.35 requiere cgroup v2 en este laboratorio.
if [ "$(stat -fc %T /sys/fs/cgroup/)" != cgroup2fs ]; then
  echo "Se requiere una imagen Ubuntu con cgroup v2 habilitado." >&2
  exit 1
fi
sudo apt-get update
sudo env DEBIAN_FRONTEND=noninteractive apt-get install -y \
  ca-certificates curl gpg apt-transport-https conntrack iproute2 \
  iptables socat containerd docker.io

# Desactivar swap ahora y en los siguientes arranques.
sudo swapoff -a
sudo cp -a /etc/fstab "/etc/fstab.k8s-backup-$(date +%Y%m%d%H%M%S)"
sudo sed -i -E '/^[[:space:]]*#/! s/^([^#]*[[:space:]]swap[[:space:]].*)$/#\1/' /etc/fstab

# Cargar los modulos ahora y en los siguientes arranques.
cat <<'EOF' | sudo tee /etc/modules-load.d/kubernetes.conf >/dev/null
overlay
br_netfilter
EOF
sudo modprobe overlay
sudo modprobe br_netfilter

cat <<'EOF' | sudo tee /etc/sysctl.d/kubernetes.conf >/dev/null
net.bridge.bridge-nf-call-ip6tables = 1
net.bridge.bridge-nf-call-iptables = 1
net.ipv4.ip_forward = 1
EOF
# Aplicar los parametros ANTES de kubeadm init.
sudo sysctl --system
test "$(sysctl -n net.ipv4.ip_forward)" = 1

echo "=== Configurar containerd con cgroups systemd ==="
# Docker se mantiene para las practicas de construccion de imagenes.
# Kubernetes utilizara directamente containerd mediante CRI.
sudo systemctl enable --now docker containerd
sudo mkdir -p /etc/containerd
if sudo test -f /etc/containerd/config.toml; then
  sudo cp -a /etc/containerd/config.toml \
    "/etc/containerd/config.toml.backup-$(date +%Y%m%d%H%M%S)"
fi
# En esta maquina nueva, generar los valores de la version instalada.
containerd config default > "$WORK_DIR/containerd.toml"
sed -i 's/SystemdCgroup = false/SystemdCgroup = true/g' "$WORK_DIR/containerd.toml"
grep -Eq 'SystemdCgroup[[:space:]]*=[[:space:]]*true' "$WORK_DIR/containerd.toml"
sudo install -m 644 "$WORK_DIR/containerd.toml" /etc/containerd/config.toml
sudo systemctl restart containerd
sudo systemctl is-active --quiet containerd

echo "=== Instalar Kubernetes 1.35 ==="
# Verificar las firmas del repositorio; no usar --allow-unauthenticated.
sudo install -d -m 755 /etc/apt/keyrings
curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.35/deb/Release.key \
  -o "$WORK_DIR/Release.key"
gpg --batch --dearmor --output "$WORK_DIR/kubernetes.gpg" "$WORK_DIR/Release.key"
sudo install -m 644 "$WORK_DIR/kubernetes.gpg" /etc/apt/keyrings/kubernetes.gpg
echo 'deb [signed-by=/etc/apt/keyrings/kubernetes.gpg] https://pkgs.k8s.io/core:/stable:/v1.35/deb/ /' \
  | sudo tee /etc/apt/sources.list.d/kubernetes.list >/dev/null
sudo apt-get update
# Instalar la misma revision disponible de kubeadm kubelet y kubectl.
K8S_PACKAGE_VERSION=$(apt-cache policy kubeadm | awk '/Candidate:/ {print $2}')
case "$K8S_PACKAGE_VERSION" in
  1.35.*) ;;
  *) echo "No se encuentra un candidato valido de Kubernetes 1.35." >&2; exit 1 ;;
esac
sudo env DEBIAN_FRONTEND=noninteractive apt-get install -y \
  "kubeadm=$K8S_PACKAGE_VERSION" \
  "kubelet=$K8S_PACKAGE_VERSION" \
  "kubectl=$K8S_PACKAGE_VERSION" \
  kubernetes-cni cri-tools
sudo apt-mark hold kubeadm kubelet kubectl kubernetes-cni cri-tools
sudo systemctl enable --now kubelet

# Guardar el endpoint de CRI para facilitar el diagnostico posterior.
cat <<'EOF' | sudo tee /etc/crictl.yaml >/dev/null
runtime-endpoint: unix:///run/containerd/containerd.sock
image-endpoint: unix:///run/containerd/containerd.sock
timeout: 10
debug: false
EOF
sudo crictl info > "$WORK_DIR/cri-info.json"

echo "=== Inicializar el Control Plane ==="
# Se puede indicar CONTROL_IP al ejecutar el script si hay varias interfaces.
CONTROL_IP=${CONTROL_IP:-$(hostname -I | awk '{print $1}')}
test -n "$CONTROL_IP"
echo "IP privada del Control Plane: $CONTROL_IP"
# Los rangos de Pods y Services no deben solaparse con la VPC.
sudo kubeadm init \
  --kubernetes-version="$(kubeadm version -o short)" \
  --node-name="$NODE_NAME" \
  --apiserver-advertise-address="$CONTROL_IP" \
  --pod-network-cidr=10.244.0.0/16 \
  --service-cidr=10.96.0.0/12 \
  --cri-socket=unix:///run/containerd/containerd.sock

mkdir -p "$HOME/.kube"
chmod 700 "$HOME/.kube"
sudo install -o "$(id -u)" -g "$(id -g)" -m 600 \
  /etc/kubernetes/admin.conf "$HOME/.kube/config"
export KUBECONFIG="$HOME/.kube/config"

echo "=== Instalar Flannel ==="
curl -fsSL \
  "https://raw.githubusercontent.com/flannel-io/flannel/${FLANNEL_VERSION}/Documentation/kube-flannel.yml" \
  -o "$WORK_DIR/kube-flannel.yml"
kubectl apply -f "$WORK_DIR/kube-flannel.yml"

echo "=== Esperar a que el cluster este listo ==="
kubectl -n kube-flannel rollout status daemonset/kube-flannel-ds --timeout=300s
kubectl wait --for=condition=Ready "node/$NODE_NAME" --timeout=300s
kubectl -n kube-system rollout status deployment/coredns --timeout=300s

echo "=== Comprobacion final ==="
sysctl net.ipv4.ip_forward
sudo containerd config dump | grep SystemdCgroup
kubectl get nodes -o wide
kubectl get pods -A -o wide
echo "=== Comando para incorporar Workers (ejecutarlo en los Workers) ==="
sudo kubeadm token create --print-join-command
echo "Instalacion completada. No volver a ejecutar este instalador en esta maquina."
