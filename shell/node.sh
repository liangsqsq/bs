sudo apt-get update
sudo apt-get upgrade -y
wget https://repo.zabbix.com/zabbix/4.0/ubuntu/pool/main/z/zabbix-release/zabbix-release_4.0-2+bionic_all.deb
sudo dpkg -i zabbix-release_4.0-
sudo apt update
sudo apt install qemu-kvm qemu virt-manager virt-viewer libvirt-bin bridge-utils -y
sudo apt install libvirt-dev libguestfs-tools python-dev libguestfs-dev gcc -y
sudo apt install vim openssh-server -y
echo '安装完成，开始修改配置文件'
echo '创建资源池'
virsh pool-define-as default dir --target /var/lib/libvirt/images/
virsh pool-build default
virsh pool-start default
virsh pool-autostart default
virsh pool-refresh default
sudo apt install zabbix-agent
sudo vim /etc/zabbix/zabbix_agent.conf
Server=192.168.47.131
Hostname=Zabbix server
EnableRemoteCommands=1
systemctl restart zabbix-agent
systemctl enable zabbix-agent