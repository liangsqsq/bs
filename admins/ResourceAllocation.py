from container.models import container, docker_node
import libvirt
import sys
from res.views import get_resourceinfo

from vm.models import workstation

import docker

def GetAvaliableNode(node_list):
    avaliable_node_list = []
    for node in node_list:
        node_date = get_resourceinfo(node.host_name)
        max_value = max(node_date["cpu"], node_date["mem"], node_date["disk"])
        if max_value < 85:
            avaliable_node_date = {
                "node": node,
                "date": node_date,
                "load": max_value,
            }
            len_anl = len(avaliable_node_date)
            for index, al in avaliable_node_list:
                if al["load"] < max_value:
                    avaliable_node_list.insert(index, avaliable_node_date)
            if len_anl == len(avaliable_node_date):
                avaliable_node_list.append(avaliable_node_date)
    return avaliable_node_list


def ResourceAllocation(domain, vcpu, mem, disk):
    print('-------------------Resource Allocaiton-------------------')
    workstation_list = workstation.objects.filter(belong=domain,state=1)
    print(mem,disk)
    isGetServer = False
    w_avaliable_list = GetAvaliableNode(workstation_list)
    for server in w_avaliable_list:
        conn = libvirt.open("qemu+ssh://" + server.user + "@" + server.ip + ":" + str(server.ssh_port) + "/system")
        if conn == None:
            print('Failed to open connection to' + server.host_name, file=sys.stderr)
        pool = conn.storagePoolLookupByName('default')

        # CPU is Available
        # current_vcpu = 0
        # vms = conn.listAllDomains(0)
        # for vm in vms:
        #     if vm.isActive() == True:
        #         current_vcpu += vm.maxVcpus()
        #     else:
        #         pass
        # MaxVcpus = conn.getMaxVcpus(None)
        # available_vcpu = MaxVcpus - current_vcpu

        FreeMem = conn.getFreeMemory() / 1024 / 1024 / 1024
        FreePoolDisk = pool.info()[3] / 1024 / 1024 / 1024
        print(str(FreeMem),str(FreePoolDisk))

        if (FreeMem > mem):
            print("The server " + server.host_name + " can define this vm")
            isGetServer = True
            break

        print("The server " + server.host_name + " can't define this vm")

    if isGetServer == False:
        print("No resource")
        return None
        # return server
    else:
        return server


def DynamicDockerAllocation():
    global docker_lock
    docker_lock.acquire()
    # 获取容器列表，并调用api检查状态
    containers = container.objects.filter(state=1)
    for container in containers:
        node_info = docker_node.objects.get(id=container.node_id)
        c = GetContainer(node_info.ip, container.id)
        d_statis = c.attrs['State']['Status']
        if d_statis != "running":
            # 判断是否为节点资源不足
            node_res_info = get_resourceinfo(node_info.ip)
            max_value = max(node_res_info["cpu"], node_res_info["mem"], node_res_info["disk"])
            # 资源不足，分配到其他节点上
            if max_value > 95:
                node_list = docker_node.objects.filter(belong_id=node_info.belong_id)
                avaliable_node_list= GetAvaliableNode(node_list)
                if len(avaliable_node_list) == 0:
                    print("no avaliable node")
                    return
                # 先创造新的再删除
                c1 = RunContainer(node_info.ip, container.im)
                log = DeleteContainer(node_info.ip, container.id)
                # 修改数据库信息
            else:
                RestartContainer(node_info.ip, container.id)
                


def GetContainer(ip, id):
    base_url = 'tcp://' + ip + ':2375'
    client = docker.DockerClient(base_url=base_url, version='auto', timeout=10)
    container = client.containers.get(container.id)
    return container

# TODO
def RunContainer(ip, images, name, command, volumes, mountPoint):
    base_url = 'tcp://' + ip + ':2375'
    client = docker.DockerClient(base_url=base_url, version='auto', timeout=10)
    container = client.containers.run(images, detach=True, tty=True, stdin_open=True, name=name,
                              command=command, volumes={"/home/jinx": {"bind": "/home/jinx", "mode": "rw"}})
    return container

def DeleteContainer(ip, id):
    base_url = 'tcp://' + ip + ':2375'
    client = docker.DockerClient(base_url=base_url, version='auto', timeout=10)
    log = client.containers.get(container.id).kill(signal=None)
    return log

def RestartContainer(ip, id):
    base_url = 'tcp://' + ip + ':2375'
    client = docker.DockerClient(base_url=base_url, version='auto', timeout=10)
    client.containers.get(container.id).restart()