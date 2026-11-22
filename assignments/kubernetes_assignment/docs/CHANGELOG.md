Se ha creado la estructura inicial del proyecto:
1. `deployment/`: Directorio en el que estará el Dockerfile.
2. `docs/`: Aquí irá la documentación final de la práctica junto al `CHANGELOG.md` que se usará para apoyar el proceso de la documentación final.
3. `k8s`: Estarán los `.yaml` que usará kuberenetes para desplegarse.
4. `docs/`: Contendrá evidencias (imágenes, gifs, videos) para la documentación.

En cuanto al código python de la imagen del docker, se usará el directorio por encima del proyecto, `rpc_assignment` para no repetir código y por si en algún futuro sehace un cambio en la práctica 1, los cambias se aplicarán también en la práctica 2.

---
Ahora he creado el Dockerfile, el cual, como mencioné antes, usa el código del `rpc_assignment`, por lo que el comando de `docker build ...` debe de ejecutarse desde `assignment/` para que funcione. También he creado un script de bash que crea la imagen del docker desde cualquier directorio (recomiendo usar esto).

También se ha subido en [assets](../assets/docker_working.png) una imagen que demuestra que el contenedor de docker funciona correctamente.
Finalmente, en la documentación he añadido un fichero con los prompts de IA usados durante la práctica.

---

Ahora toca subir la imagen creada a mi [cuenta de docker](https://hub.docker.com/repositories/miguelandin). Para hacemos lo siguiente:
1. **Login**
```bash
sudo docker login
```
Es importante hacerlo con sudo porque sino las credenciales estarán en otra ubicación.

2. **Commit**
```bash
sudo docker tag rpc-server:1.0 miguelandin/rpc-server:1.0
```
El primer nombre es la imagen local que tenemos mientras que la otra es el nombre en el repositorio remoto. Lo que va después de los `:` es la versión. Si no pones nada, pondrá `latest`.

Si el nombre del repositorio remoto no existe, se creara un repositorio público con ese mismo nombre.

3. **Push**
```bash
sudo docker push miguelandin/rpc-server:1.0
```

Tras hacer esto se ha logrado subir con éxito la imagen en  [este repositorio](https://hub.docker.com/r/miguelandin/rpc-server) como se puede ver en la la captura en [assets](../assets/succesfull_docker_push.png).

También se puede comprobar rápidamente que funciona con este comando:
```bash
sudo docker run -d --name rpc-server -p 5000:5000 miguelandin/rpc-server:1.0
```

---
Ahora vamos con montar las máquinas en _AWS_ para hacer el clúster con kubernetes:

**Primero**, creamos un security group que permita el puerto ssh y el 30007 para todas las ips para poder comunicarnos con las máquinas. También, para que los nodos puedan comunicarse entre ellos vamos a permitir todo el tráfico a las máquinas que estén dentro del mismo security group. Debería de quedar algo [así](../assets/security_group_conf.png).

**Segundo**, creamos el EC2 original el cual será el `k8s-control` y la imagen con la que se clonarán los demás workers. Este tendrán los siguientes parámetros: `Ubuntu Server 26.04`, `t3.medium`, par de claves, el grupo de seguridad creado en el paso anterior y 28GB de almacenamiento.

El script de la instancia sería algo así:
```bash
aws ec2 run-instances --image-id 'ami-0aacbf72109c53c0c' --instance-type 't3.medium' --key-name 'passphrase' --ebs-optimized --block-device-mappings '{"DeviceName":"/dev/xvda","Ebs":{"Encrypted":false,"DeleteOnTermination":true,"Iops":3000,"SnapshotId":"snap-05d6088954edf1680","VolumeSize":28,"VolumeType":"gp3","Throughput":125}}' --network-interfaces '{"AssociatePublicIpAddress":true,"DeviceIndex":0,"Groups":["sg-04b7c96ff88b99fec"]}' --credit-specification '{"CpuCredits":"unlimited"}' --metadata-options '{"HttpEndpoint":"enabled","HttpPutResponseHopLimit":2,"HttpTokens":"required"}' --private-dns-name-options '{"HostnameType":"ip-name","EnableResourceNameDnsARecord":true,"EnableResourceNameDnsAAAARecord":false}' --count '1' 
```

**Tercero**, nos conectamos por ssh a la instancia EC2 creada, yo recomiendo editar el archivo `.ssh/confi` para que sea más cómodo.

```ssh
Host control
    Hostname <ip>
    User ubuntu 
    IdentityFile ~/.ssh/cluster.pem
```

Ahora que nos podemos conectar a la máquina, pasamos los scripts de la [carpeta de scripts de kubernetes](../k8s/kubernetes-scripts/) a la máquina remote mediante scp:
```bash
scp -r k8s/kubernetes-scripts control:
```

Y para terminar este paso ejecutamos el script de instalación de kubernetes desde la máquina remota:
```bash
bash ./kubernetes-scripts/kub_install.sh 
```

Si la instalación ha salido bien, debería de aparecer algo como [esto](../assets/kubernetes_installed.png).

**Cuarto**, paramos la instancia y copiamos su imagen para crear varias instancias que serán workers. Para ello, una vez parado vamos a Acciones->Imágenes->Crear Imagen. En mi caso lo voy a llamar `cluster-template`.

Una vez creado la AMI vamos a crear dos workers a partir de ella. Es importante que estén en el mismo security group que el control.

El script de creación sería algo así:
```bash
aws ec2 run-instances --image-id 'ami-027dc2e31c9a1410d' --instance-type 't3.medium' --key-name 'cluster' --ebs-optimized --network-interfaces '{"AssociatePublicIpAddress":true,"DeviceIndex":0,"Groups":["sg-04b7c96ff88b99fec"]}' --credit-specification '{"CpuCredits":"unlimited"}' --tag-specifications '{"ResourceType":"instance","Tags":[{"Key":"Name","Value":"k8s-worker1"}]}' --private-dns-name-options '{"HostnameType":"ip-name","EnableResourceNameDnsARecord":true,"EnableResourceNameDnsAAAARecord":false}' --count '1'  
```

**Quinto**, nos conectamos a cada worker creado mediante su archivo de `.shh/config` previamente escrito y le cambiamos el `hostname` de cada máquina y reiniciamos sus credenciales de admin. Con el siguiente comando:
```bash
sudo hostnamectl set-hostname k8s-worker
sudo kubeadm reset
rm -f /home/ubuntu/.kube/config
```

**Sexto**, vinculamos los nodos con el control generando primero el comando de unión desde el control:
```bash
sudo kubeadm token create --print-join-command
```

 Con el siguiente comando de salida, lo ejecutamos en cada nodo para vincularlos:
```bash
sudo kubeadm join 172.31.16.211:6443 --token gmsms5.9y03ofh2jk16ozr7 --discovery-token-ca-cert-hash sha256:907fc6f44240e7ce1d217a18a920f13abc4950a373915d15c823b939227e4dd4
```

Si ha salido bien debería de salir algo como [esta imagen](../assets/node_joined.png). Y en el control esto:
```bash
ubuntu@k8s-control:~$ kubectl get nodes -o wide
NAME          STATUS   ROLES           AGE     VERSION    INTERNAL-IP     EXTERNAL-IP   OS-IMAGE             KERNEL-VERSION   CONTAINER-RUNTIME
k8s-control   Ready    control-plane   48m     v1.35.10   172.31.16.211   <none>        Ubuntu 26.04.1 LTS   7.0.0-1018-aws   containerd://2.2.2
k8s-worker1   Ready    <none>          2m58s   v1.35.10   172.31.20.82    <none>        Ubuntu 26.04.1 LTS   7.0.0-1018-aws   containerd://2.2.2
k8s-worker2   Ready    <none>          44s     v1.35.10   172.31.31.30    <none>        Ubuntu 26.04.1 LTS   7.0.0-1018-aws   containerd://2.2.2
```
(Convertir esta salida en una tabla)


