#!/bin/bush
sudo apt-get update
sudo apt-get upgrade

wget  https://repo.zabbix.com/zabbix/4.0/ubuntu/pool/main/z/zabbix-release/zabbix-release_4.0-3+xenial_all.deb
sudo dpkg -i zabbix-release_4.0-3+xenial_all.deb
sudo apt update

sudo apt install qemu-kvm qemu virt-manager virt-viewer libvirt-bin bridge-utils
sudo apt install libvirt-dev libguestfs-tools python-dev libguestfs-dev gcc
sudo apt install vim openssh-server
