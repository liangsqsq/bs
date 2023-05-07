Docker-cloud
===

hostserver need to install:
------
    0.修改base文件，注释pymysql版本问题
    1.sudo apt-get install qemu-kvm
    2.sudo apt-get install qemu
    3.sudo apt-get install virt-manager
    4.sudo apt-get install virt-viewer 
    5.sudo apt-get install libvirt-bin 
    6.sudo apt-get install bridge-utils 
    7.sudo apt-get install libvirt-dev 
    8.sudo apt-get install libguestfs-tools
    9.sudo apt-get install gcc python-dev libguestfs-dev
    10.sudo apt-get install qemu-guest-agent
    
use requirements.txt:
---

    pip freeze > requirements
    &&
    pip install -r requirements.txt
    
how to start:
---
    mysql: create database newcloud default character set utf8
    python manage.py makemigrations
    python manage.py migrate
    python manage.py createsuperuser
python manage.py runserver localhost:27777
    
