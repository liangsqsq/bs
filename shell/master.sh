#!/bin/bash
sudo apt-get update 
sudo apt-get upgrade -y
sudo apt-get install git -y
git clone https://github.com/pyenv/pyenv.git ~/.pyenv
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc
source .bashrc
echo 'pyenv安装完成，开始安装 python...'

sudo apt-get install qemu-kvm -y
sudo apt-get install qemu -y
sudo apt-get install virt-manager -y
sudo apt-get install virt-viewer -y
sudo apt-get install libvirt-bin -y
sudo apt-get install bridge-utils -y
sudo apt-get install libvirt-dev -y
sudo apt-get install libguestfs-tools -y
sudo apt-get install gcc python-dev libguestfs-dev -y
sudo apt-get install qemu-guest-agent -y
sudo apt install \
    build-essential \
    curl \
    libbz2-dev \
    libffi-dev \
    liblzma-dev \
    libncursesw5-dev \
    libreadline-dev \
    libsqlite3-dev \
    libssl-dev \
    libxml2-dev \
    libxmlsec1-dev \
    llvm \
    make \
    tk-dev \
    wget \
    xz-utils \
    zlib1g-dev

pyenv global 3.6.8
pip install virtualenv -i https://pypi.python.org/simple/
virtualenv -p ~/.pyenv/versions/3.6.8/bin/python venv/
wget https://repo.zabbix.com/zabbix/5.0/ubuntu/pool/main/z/zabbix-release/zabbix-release_5.0-1+bionic_all.deb
dpkg -i z
sudo apt update
sudo apt install apache2
sudo apt install php
sudo apt install  zabbix-server-mysql zabbix-frontend-php zabbix-agent zabbix-get 