#!flask/bin/python
import json

import requests
from flask import Flask, jsonify
import VMManagement
import DockerManagement
import sql
from zabbix import Zabbix

"""
功能描述：增加资源
接口名称：resource_add
参数说明：
node_name：
apply_cpu, apply_mem, apply_disk：
class_name,model_name：
"""
def resource_add(node_name, apply_cpu, apply_mem, apply_disk,class_name,model_name):
    #资源唯一名
    my_vm_num = sql.select_cmd("select count(distinct name) from vm_vm;")[0]
    my_container_num = sql.select_cmd("select count(distinct name) from container_container;")[0]
    resource_num = my_vm_num + my_container_num + 1
    vm_name = str(resource_num) + "admin"

    print(my_vm_num, my_container_num,vm_name)

    #返回值
    dic = {"resource_name":vm_name}

    # #判断所属域
    if node_name == "server1":
        VMManagement.applyVM(node_name, apply_cpu, apply_mem, apply_disk, vm_name)

    elif node_name == "ubuntu16":
        DockerManagement.applyDocker_X86(node_name, apply_cpu, apply_mem)

    else:
        DockerManagement.applyDocker_ARM(node_name, apply_cpu, apply_mem)

    # #更改数据库
    SQL = "insert into res_transfer(resource_name,classes,model) values(\"{}\",{},{});".format(vm_name, class_name,
                                                                                                 model_name)
    sql.exec_cmd(SQL)
    # 更新resource_class
    class_number = sql.select_cmd("select number from res_classes where class_name={};".format(class_name))[0] + 1
    SQL2 = "update res_classes set number={} where class_name={}".format(class_number, class_name)
    sql.exec_cmd(SQL2)
    # 更新resource_model
    model_number = sql.select_cmd("select number from res_model where model_name={};".format(model_name))[
                       0] + 1
    SQL3 = "update res_model set number={} where model_name={}".format(model_number, model_name)
    sql.exec_cmd(SQL3)
    #
    return dic




"""
功能描述：销毁资源
接口名称：resource_drop
参数说明：
resource_name：需要删除的虚拟机或容器名称
"""
def resource_drop(resource_name):

    # 判断所属域
    SQL = "select count(*) from vm_vm where name=\"{}\";".format(resource_name)
    res = sql.select_cmd(SQL)[0]

    #如果节点是服务器
    if res == 1:
        VMManagement.delVM(resource_name)
    #节点在树莓派
    else:
        DockerManagement.container_delete(resource_name)

    # 更改数据库

    #查找虚拟机/容器对应的作战资源类型
    SQL1 = "select classes from res_transfer where resource_name=\"{}\";".format(resource_name)
    class_name = sql.select_cmd(SQL1)[0]
    SQL2 = "select model from res_transfer where resource_name=\"{}\";".format(resource_name)
    model_name = sql.select_cmd(SQL2)[0]


    # 删除resouce_transfer中对应的资源转换信息
    SQL3 = "delete from res_transfer where resource_name=\"{}\";".format(resource_name)
    sql.exec_cmd(SQL3)

    # 更新resource_class
    class_number = sql.select_cmd("select number from res_classes where class_name={};".format(class_name))[0] - 1
    SQL4 = "update res_classes set number={} where class_name={}".format(class_number, class_name)
    sql.exec_cmd(SQL4)
    # 更新resource_model
    model_number = sql.select_cmd("select number from res_model where model_name={};".format(model_name))[0] - 1
    SQL5 = "update res_model set number={} where model_name={}".format(model_number, model_name)
    sql.exec_cmd(SQL5)

    # print(res, class_name,model_name,class_number,model_number)
    return 0



"""
功能描述：任务迁移
接口名称：resource_migrate
参数说明：
resource_name：需要删除的虚拟机或容器名称
node_name：在node_name进行新容器的创建
apply_cpu, apply_mem, apply_disk：分别为创建新的容器所需要的cpu,内存,硬盘详细信息
class_name,model_name：对新创建的任
"""
def resource_migrate(resource_name, node_name, apply_cpu, apply_mem, apply_disk):
    # 查找虚拟机/容器对应的作战资源类型
    SQL1 = "select classes from res_transfer where resource_name=\"{}\";".format(resource_name)
    class_name = sql.select_cmd(SQL1)[0]
    SQL2 = "select model from res_transfer where resource_name=\"{}\";".format(resource_name)
    model_name = sql.select_cmd(SQL2)[0]

    #销毁容器
    resource_drop(resource_name)

    #创建新的容器，并进行相应的资源绑定
    resource_add(node_name, apply_cpu, apply_mem, apply_disk, class_name, model_name)

    # print(class_name, model_name)

"""
功能描述：平台的加入
接口名称：palnet_join
参数说明：
host_name:给加入平台取名(node_name)

"""
def palnet_join(host_name):

    res = sql.select_cmd("select ip,user,pwd,home_dir from container_docker_node_available where host_name=\"{}\";".format(host_name))
    ip = res[0]
    user = res[1]
    pwd = res[2]
    home_dir = res[3]
    DockerManagement.platform_join(host_name, ip, user, pwd, home_dir)

    #删除container_docker_node_available数据项
    sql.exec_cmd("delete from container_docker_node_available  where host_name=\"{}\";".format(host_name))

    # print(res)
    # print(ip,user,pwd,home_dir)
"""
功能描述：平台的加入
接口名称：palnet_quit
参数说明：
node_name：需要退出的平台名称
问题：需要查询平台上还剩余的所有资源信息，并删除掉吗
"""
def palnet_quit(node_name):
    #从container_docker_node查询数据添加到container_docker_node_available
    res = sql.select_cmd("select host_name,ip,user,pwd,home_dir from container_docker_node where host_name=\"{}\";".format(node_name))
    host_name = res[0]
    ip = res[1]
    user = res[2]
    pwd = res[3]
    home_dir = res[4]
    # ssh_port = 22
    sql.exec_cmd("insert into container_docker_node_available(host_name,ip,ssh_port,user,pwd, home_dir) "
                 "value(\"{}\",\"{}\",22,\"{}\",\"{}\",\"{}\");".format(host_name,ip,user,pwd,home_dir))

    #从container_docker_node删除数据项
    sql.exec_cmd("delete from container_docker_node where host_name=\"{}\";".format(node_name))

#返回作战资源类型
def class_get():
    #查询class表所有数据项
    res = sql.select_all_cmd("select class_name from res_classes;")
    res_len = len(res)
    #json封装
    dic = {"length":res_len,"class":res}
    # return jsonify(dic)
    # print(dic)
    return dic

#返回型号信息
def model_get(class_name):
    #查询class表所有数据项
    res = sql.select_all_cmd("select model_name from res_model where class_name=\"{}\";".format(class_name))
    res_len = len(res)
    #json封装
    dic = {"length":res_len,
           "class":res
    }
    # return jsonify(dic)
    # print(dic)
    return dic


"""
功能描述：获取可用平台信息
接口名称：get_available_platform
参数：无
返回值：
    length:hosts长度
    hosts:可用平台的主机名列表
"""
def get_available_platform():
    res = sql.select_all_cmd("select host_name from container_docker_node_available;")
    res_len = len(res)
    dic = {
        "length":res_len,
        "hosts":res
    }
    # print(dic)

"""
功能描述：批量增加平台
接口参数：json格式的string，包括平台列表长度length和平台host_name列表hosts
"""
def add_platforms(platforms):
    jsonData = json.loads(json.dumps(eval(platforms)))
    len = jsonData["length"]
    hosts = jsonData["hosts"]
    # print(len, hosts)
    for i in hosts:
        palnet_join(i)


"""
功能描述：批量退出平台
接口参数：json格式，包括平台列表长度length和平台host_name列表hosts
"""
def del_platforms(platforms):
    jsonData = json.loads(json.dumps(eval(platforms)))
    len = jsonData["length"]
    hosts = jsonData["hosts"]
    print(len, hosts)
    for i in hosts:
        palnet_quit(i)

"""
功能描述：修改运行中的虚拟机/容器的CPU、内存、硬盘设置
接口参数：json格式，包括平台列表长度length和平台host_name列表hosts
"""
def update_resource(resource_name,apply_cpu, apply_mem, apply_disk):
    #由resource_name查询所在资源的node_name
    res = sql.select_cmd("select node_id from container_container where name=\"{}\";".format(resource_name))
    if res!=None:
        node_Name = sql.select_cmd("select host_name from container_docker_node where id={};".format(res[0]))
    else:
        res = sql.select_cmd("select belong_id from vm_vm where name=\"{}\";".format(resource_name))
        node_Name = sql.select_cmd("select host_name from vm_workstation where id={};".format(res[0]))

    # 查找虚拟机/容器对应的作战资源类型
    SQL1 = "select classes from res_transfer where resource_name=\"{}\";".format(resource_name)
    class_name = sql.select_cmd(SQL1)[0]
    SQL2 = "select model from res_transfer where resource_name=\"{}\";".format(resource_name)
    model_name = sql.select_cmd(SQL2)[0]

    print(node_Name,class_name,model_name)

    #销毁容器
    resource_drop(resource_name)

    #创建新的容器，并进行相应的资源绑定
    resource_add(node_Name, apply_cpu, apply_mem, apply_disk, class_name, model_name)

def get_resourceinfo():
    za = Zabbix('Admin', 'zabbix')
    #从hosts_namec从数据表container_docker_node和vm_workstation查询得到
    pi_node_name = sql.select_all_cmd("select host_name from container_docker_node")
    server_node_name = sql.select_all_cmd("select host_name from vm_workstation")
    node_name = []
    for i in pi_node_name:
        node_name.append(i[0])
    for i in server_node_name:
        node_name.append(i[0])
    print(node_name)

    hosts_length = len(node_name)
    dic2 = {}
    for i in node_name:
        # cpu
        cpu_idle = za.historys_get(i, "system.cpu.util[,idle]", 0, 1)[0]["value"]
        # print("cpu idlo:"+ cpu_idle)
        cpu_user = za.historys_get(i, "system.cpu.util[,user]", 0, 1)[0]["value"]
        cpu_system = za.historys_get(i, "system.cpu.util[,system]", 0, 1)[0]["value"]

        # mem
        mem_available = za.historys_get(i, "vm.memory.size[available]", 3, 1)[0]["value"]
        men_total = za.historys_get(i, "vm.memory.size[total]", 3, 1)[0]["value"]

        # disk
        disk_total = za.historys_get(i, "vfs.fs.size[/,total]", 3, 1)[0]["value"]
        disk_free = za.historys_get(i, "vfs.fs.size[/,free]", 3, 1)[0]["value"]

        #net
        # net_out = float(za.historys_get('Zabbix server', "net.if.out[br0]", 3, 1)[0]["value"]) / 1024
        # net_in = float(za.historys_get('Zabbix server', "net.if.in[br0]", 3, 1)[0]["value"]) / 1024


        dic1 = {
            "cpu_idle": cpu_idle,
            "cpu_user": cpu_user,
            "cpu_system": cpu_system,
            "mem_available": mem_available,
            "men_total": men_total,
            "disk_total": disk_total,
            "disk_free": disk_free,
            # "net_out": net_out,
            # "net_in": net_in
        }
        dic2[i]=dic1

    dic2["host_number"] = hosts_length
    return dic2
