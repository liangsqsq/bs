import time

import docker
import paramiko
from container.models import *
from admins.networkManage import getAvailablePort


def mount_file(user,img,node):
    username=user.username
    mount_point=img.mountPoint
    ip=node.ip
    # 使用用户名，密码建立ssh链接
    trans = paramiko.Transport((node.ip, int(node.ssh_port)))
    try:
        trans.connect(username=node.user, password=node.pwd)
    except:
        print(node.hostname + " ssh connection false")
        return False
    ssh = paramiko.SSHClient()
    ssh._transport = trans
    mount_list=mount_point.split(';',-1)
    for mount in mount_list:
        split=mount.rindex('/')
        file_name=mount[split+1:]
        dir_name=mount[0:split]
        print(file_name,dir_name)
        cmd = 'mkdir -p ' + node.home_dir +username  + dir_name +' && '+'cd '+node.home_dir +username  + dir_name+' && '+'touch '+file_name
        print('cmd :' + cmd)
        cmd1 ='cd '+node.home_dir +username  + dir_name+' && '+'touch '+file_name
        print('cmd1 :' + cmd1)
        stdin, stdout, stderr = ssh.exec_command(cmd)
        if stderr:
            print('stderr : ' + stderr.read().decode())
    trans.close()
    ssh.close()
    #

def mount_volume(user,img,node):
    username = user.username
    mount_point = img.mountPoint
    mount_list = mount_point.split(';', -1)
    ip = node.ip
    dict1={}
    string=''
    list1=[]
    base_url = 'tcp://' + node.ip + ':2375'
    C = docker.DockerClient(base_url=base_url, version='auto', timeout=10)
    count=0
    for mount in mount_list:
        #须再加当前用户容器个数
        split = mount.rindex('/')
        file_name = mount[split + 1:]
        my_docker_num = container.objects.filter(user=user).count() + 1
        count=count+1
        str1=username+'-'+file_name + str(my_docker_num)+'-'+str(count)
        vol = C.volumes.create(name=str1, driver='local', labels={"key": "value"})
        volname='var/lib/docker/volumes/'+str1
        print(str1)
        string=string+volname+';'
        list1.append(str1)
        point={'bind': mount, 'mode': 'rw'}
        dict1[str1]=point
    return dict1,string,list1

def setPort(user,img,node):
    username = user.username
    ports=img.port
    port_list=ports.split(';',-1)
    dict2={}
    ip = node.ip
    # 使用用户名，密码建立ssh链接
    trans = paramiko.Transport((node.ip, int(node.ssh_port)))
    try:
        trans.connect(username=node.user, password=node.pwd)
    except:
        print(node.hostname + " ssh connection false")
        return False
    ssh = paramiko.SSHClient()
    ssh._transport = trans
    channel = ssh.invoke_shell()
    time.sleep(0.1)
    channel.send("sudo su\n")
    buff = ''
    while not buff.endswith(': '):
        resp = channel.recv(999)
        buff += resp.decode('utf-8')
        if buff.endswith('# '):
            break
    print(buff)
    channel.send(node.pwd)
    channel.send('\n')
    buff = ''
    while not buff.endswith('# '):
        resp = channel.recv(999)
        buff += resp.decode('utf-8')
    print(buff)
    print("------end------")
    for po in port_list:
        str=po+'/tcp'
        DPORT = getAvailablePort(channel, 10000, 20000)
        dict2[str]=DPORT
    return dict2