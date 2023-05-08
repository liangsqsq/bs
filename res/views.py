import datetime
import json
import time

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

# Create your views here.
from container.models import container, docker_node
from res.models import transfer, radar_info, arm_info, compute_info
from res.zabbix_api import Zabbix
from vm.models import vm, workstation, cascade_list
from admins.decorate import decorate_getSources, decorate_get_node_info

@decorate_getSources
def getSources(request, car_count_other=0, ship_count_other=0, aircraft_count_other=0, host_other=None, all_node_info_other=None):
    #if request.user.is_authenticated and request.user.is_superuser:
    if True:
        if request.method == "POST":

            radar_count = transfer.objects.filter(classes=2).count()
            compute_resource_count = transfer.objects.filter(classes=3).count()
            weapon_count = transfer.objects.filter(classes=1).count()

            hostdict = {}
            host = []
            vm_workstation_list = workstation.objects.filter(state=1)
            container_node_list = docker_node.objects.filter(state=1)
            tmpdict = {}
            all_node_info = []
            cascade_self = cascade_list.objects.get(is_self=True)
            for vm_workstation in vm_workstation_list:
                vm_workstation_data = get_resourceinfo(vm_workstation.host_name)
                if vm_workstation_data:
                    server = {}
                    server["menuName"] = vm_workstation.host_name + '_' + str(cascade_self.id)
                    server["open"] = True
                    server['iconSkin'] = "hostgroup"

                    vms = vm.objects.filter(belong=vm_workstation)
                    resources = []
                    resCount = 0
                    for vm_ in vms:
                        vm_transfer = transfer.objects.get(resource_name=vm_.name)
                        vm_transfer_dict = {}
                        resCount = resCount + 1
                        if vm_transfer.classes == 1:
                            vm_transfer_name = "无人机"
                            iconSkin = "wuqi"
                        elif vm_transfer.classes == 2:
                            vm_transfer_name = "无人车"
                            iconSkin = "leida"
                        else:
                            vm_transfer_name = "无人船"
                            iconSkin = "jisuan"

                        vm_transfer_dict["menuName"] = vm_transfer_name + str(vm_transfer.model)
                        vm_transfer_dict["iconSkin"] = iconSkin
                        resources.append(vm_transfer_dict)
                    server['children'] = resources
                    hostdict[vm_workstation.host_name] = server

                    vm_workstation_data["node_weapon_count"] = resCount
                    vm_workstation_dict = {}
                    vm_workstation_dict["node_name"] = vm_workstation.host_name
                    vm_workstation_dict["node_info"] = vm_workstation_data
                    tmpdict[vm_workstation.host_name] = vm_workstation_dict

            for container_node in container_node_list:
                container_node_data = get_resourceinfo(container_node.host_name)
                if container_node_data:
                    server = {}
                    server["menuName"] = container_node.host_name + '_' + str(cascade_self.id)
                    server["open"] = True
                    server['iconSkin'] = "hostgroup"

                    containers = container.objects.filter(node=container_node)
                    resources = []
                    resCount = 0
                    for container_ in containers:
                        container_transfer = transfer.objects.get(resource_name=container_.name)
                        container_transfer_dict = {}
                        resCount = resCount + 1
                        if container_transfer.classes == 1:
                            container_transfer_name = "无人机"
                            iconSkin = "wuqi"
                        elif container_transfer.classes == 2:
                            container_transfer_name = "无人车"
                            iconSkin = "leida"
                        else:
                            container_transfer_name = "无人船"
                            iconSkin = "jisuan"

                        container_transfer_dict["menuName"] = container_transfer_name + str(container_transfer.model)
                        container_transfer_dict["iconSkin"] = iconSkin
                        resources.append(container_transfer_dict)
                    print("ccccccccccccccccccc")
                    print((hostdict.get(container_node.host_name))["children"])
                    server['children'] = resources.append((hostdict.get(container_node.host_name))["children"])
                    print(server)
                    hostdict[container_node.host_name] = server

                    container_node_data["node_weapon_count"] = resCount+tmpdict.get(container_node.host_name)["node_info"]["node_weapon_count"]
                    container_node_dict = {}
                    container_node_dict["node_name"] = container_node.host_name
                    container_node_dict["node_info"] = container_node_data
                    tmpdict[container_node.host_name] = container_node_dict

            # for vm_workstation in vm_workstation_list:
            #     vm_workstation_data = get_resourceinfo(vm_workstation.host_name)
            #     now = time.localtime()
        #     now_time = time.strftime("%Y-%m-%d %H:%M:%S", now)
            #     now_hour = now_time[-7:-9:-1][::-1]
            #     now_minute = now_time[-4:-6:-1][::-1]
            #     now_second = now_time[-1:-3:-1][::-1]
            #     data_time = vm_workstation_data["time"]
            #     data_hour = data_time[-7:-9:-1][::-1]
            #     data_minute = data_time[-4:-6:-1][::-1]
            #     data_second = data_time[-1:-3:-1][::-1]
            #     dist = (int(now_hour)*60*60+int(now_minute)*60+int(now_second))-(int(data_hour)*60*60+int(data_minute)*60+int(data_second))
            #     if dist < 80:
            #         vms = vm.objects.filter(belong=vm_workstation)
            #         node_weapon_count = 0
            #         for vm_ in vms:
            #             vm_weapon_transfer = transfer.objects.get(resource_name=vm_.name)
            #             if vm_weapon_transfer.classes == 1:
            #                 node_weapon_count = node_weapon_count+1
            #         vm_workstation_data["node_weapon_count"] = node_weapon_count
            #         vm_workstation_dict = {}
            #         vm_workstation_dict["node_name"] = vm_workstation.host_name
            #         vm_workstation_dict["node_info"] = vm_workstation_data
            #         all_node_info.append(vm_workstation_dict)
            #
            # for container_node in container_node_list:
            #     container_node_data = get_resourceinfo(container_node.host_name)
            #     now = time.localtime()
            #     now_time = time.strftime("%Y-%m-%d %H:%M:%S", now)
            #     now_hour = now_time[-7:-9:-1][::-1]
            #     now_minute = now_time[-4:-6:-1][::-1]
            #     now_second = now_time[-1:-3:-1][::-1]
            #     print(container_node.host_name)
            #     print("now_time" + now_hour + now_minute + now_second)
            #     data_time = container_node_data["time"]
            #     data_hour = data_time[-7:-9:-1][::-1]
            #     data_minute = data_time[-4:-6:-1][::-1]
            #     data_second = data_time[-1:-3:-1][::-1]
            #     print("data_time" + data_hour + data_minute + data_second)
            #     dist = (int(now_hour)*60*60+int(now_minute)*60+int(now_second))-(int(data_hour)*60*60+int(data_minute)*60+int(data_second))
            #     if dist < 80:
            #         containers = container.objects.filter(node=container_node)
            #         node_weapon_count = 0
            #         for container_ in containers:
            #             containers_weapon_transfer = transfer.objects.get(resource_name=container_.name)
            #             if containers_weapon_transfer.classes == 1:
            #                 node_weapon_count = node_weapon_count + 1
            #         container_node_data["node_weapon_count"] = node_weapon_count
            #         container_node_dict = {}
            #         container_node_dict["node_name"] = container_node.host_name
            #         container_node_dict["node_info"] = container_node_data
            #         all_node_info.append(container_node_dict)
            #
            # print(all_node_info)
            if host_other:
                host += host_other

            if all_node_info_other:
                all_node_info += all_node_info_other
            
            host = list(hostdict.values())
            all_node_info = list(tmpdict.values())

            return HttpResponse(json.dumps({
                'radar_count': radar_count+car_count_other,
                'computer_resource_count': compute_resource_count+ship_count_other,
                'weapon_count': weapon_count+aircraft_count_other,
                'host': host,
                "all_node_info": all_node_info,
            }), content_type="application/json")

            #return JsonResponse({
            #    'radar_count': radar_count+radar_count_other,
            #    'computer_resource_count': compute_resource_count+compute_resource_count_other,
            #    'weapon_count': weapon_count+weapon_count_other,
            #    'host': host+host_other,
            #    "all_node_info": all_node_info+all_node_info_other,
            #})

@decorate_get_node_info
def get_node_info(request, data_other=None, radar_count_other=0, computer_resource_count=0, weapon_count=0):
    if data_other or data_other == []:
        return HttpResponse(json.dumps({
                'data': data_other,
                'radar_count': radar_count_other,
                'computer_resource_count': computer_resource_count_other,
                'weapon_count': weapon_count_other,
            }), content_type='application/json')
    #if request.user.is_authenticated and request.user.is_superuser:
    if True:
        if request.method == "POST":
            node_name = request.POST.get("node_name").split('_')[0]
            radar_count = 0
            computer_resource_count = 0
            weapon_count = 0
            data = get_resourceinfo(node_name)
            if data['time'] == '1970-01-01 08:00:00':
                return JsonResponse({
                    'data': data,
                    'radar_count': radar_count,
                    'computer_resource_count': computer_resource_count,
                    'weapon_count': weapon_count,
                })
            try:
                node = workstation.objects.get(host_name=node_name)
            except:
                node = docker_node.objects.get(host_name=node_name)
                containers = container.objects.filter(node=node)
                for container_ in containers:
                    container_tranfer = transfer.objects.get(resource_name=container_.name)
                    if container_tranfer.classes == 2:
                        radar_count = radar_count + 1
                    elif container_tranfer.classes == 1:
                        weapon_count = weapon_count + 1
                    else:
                        computer_resource_count = computer_resource_count + 1
            else:
                vms = vm.objects.filter(belong=node)
                for vm_ in vms:
                    vm_tranfer = transfer.objects.get(resource_name=vm_.name)
                    if vm_tranfer.classes == 2:
                        radar_count = radar_count + 1
                    elif vm_tranfer.classes == 1:
                        weapon_count = weapon_count + 1
                    else:
                        computer_resource_count = computer_resource_count + 1
            return HttpResponse(json.dumps({
                'data': data,
                'radar_count': radar_count,
                'computer_resource_count': computer_resource_count,
                'weapon_count': weapon_count,
            }), content_type='application/json')
            #return JsonResponse({
            #    'data': data,
            #    'radar_count': radar_count,
            #    'computer_resource_count': computer_resource_count,
            #    'weapon_count': weapon_count,
            #})



def get_resourceinfo(node_name):
    ''' 通过zabbix接口获取节点的信息 '''
    url = 'http://127.0.0.1/zabbix/api_jsonrpc.php'
    za = Zabbix(url, 'Admin', 'zabbix')

    # cpu
    try:
        # cpu_idle = za.historys_get(node_name, "system.cpu.util[,idle]", 0, 1)[0]["value"]
        cpu_user = za.historys_get(node_name, "system.cpu.util[,user]", 0, 1)[0]["value"]
        cpu_system = za.historys_get(node_name, "system.cpu.util[,system]", 0, 1)[0]["value"]
    except:
        cpu = 0
    else:
        if cpu_user != -1:
            cpu = round(float(cpu_system) + float(cpu_user), 2)
        else:
            return None

    # mem
    try:
        mem_available = za.historys_get(node_name, "vm.memory.size[available]", 3, 1)[0]["value"]
        men_total = za.historys_get(node_name, "vm.memory.size[total]", 3, 1)[0]["value"]
        clock = za.historys_get(node_name, "vm.memory.size[available]", 3, 1)[0]["clock"]
    except:
        mem = 0
        clock = 0
    else:
        mem = round((1 - (float(mem_available) / float(men_total))) * 100, 2)

    # disk
    try:
        disk_total = za.historys_get(node_name, "vfs.fs.size[/,total]", 3, 1)[0]["value"]
        disk_free = za.historys_get(node_name, "vfs.fs.size[/,free]", 3, 1)[0]["value"]
        clock = za.historys_get(node_name, "vfs.fs.size[/,free]", 3, 1)[0]["clock"]
    except:
        disk = 0
    else:
        disk = round((1 - (float(disk_free) / float(disk_total))) * 100, 2)

    timeArray = time.localtime(int(clock))
    now_time = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)

    info = {
        "cpu": cpu,
        "mem": mem,
        "disk": disk,
        "time": now_time,
    }
    return info

def get_res_info(request):
    if request.user.is_authenticated and request.user.is_superuser:
        if request.method == "POST":
            res = request.POST.get("res")
            res_name = int(res[-1:-4:-1][::-1])
            res_type = res[-4::-1][::-1]
            print(res_name, res_type)

            # 获取资源信息
            if res_type == "虚拟机":
                radar_object = radar_info.objects.get(rsname=res_name)
                return JsonResponse({"dataInfo":{
                    "rsid":radar_object.id,
                    "rsname": radar_object.rsname,
                    "rtype": radar_object.rtype,
                    "rop_band": radar_object.rop_band,
                    "rpulse_width": radar_object.rpulse_width,
                    "rantenna_gain": radar_object.rantenna_gain,
                    "rpulse_freq": radar_object.rpulse_freq,
                    "rtrans_power": radar_object.rtrans_power,
                    "rradius_max": radar_object.rradius_max,
                    "rdist_max": radar_object.rdist_max
                }})
            elif res_type == "":
                weapon_object = arm_info.objects.get(asname=res_name)
                return JsonResponse({"dataInfo":{
                    "asid": weapon_object.id,
                    "asname": weapon_object.asname,
                    "atype": weapon_object.atype,
                    "aspeed": weapon_object.aspeed,
                    "akill_radius": weapon_object.akill_radius,
                    "ahit_rate": weapon_object.ahit_rate,
                    "aguide_accuracy": weapon_object.aguide_accuracy,
                    "ahit_accuracy": weapon_object.ahit_accuracy,
                    "aattack_distmax": weapon_object.aattack_distmax
                }})
            else:
                compute_object = compute_info.objects.get(csname=res_name)
                return JsonResponse({"dataInfo":{
                    'csid': compute_object.id,
                    "csname": compute_object.csname,
                    "ctype": compute_object.ctype,
                    "caccuracy": compute_object.caccuracy
                }
                })

            # if res_type == "雷达":
            #     radar_object = radar_info.objects.get(rsname=res_name)
            #     return JsonResponse({"dataInfo":{
            #         "rsid":radar_object.id,
            #         "rsname": radar_object.rsname,
            #         "rtype": radar_object.rtype,
            #         "rop_band": radar_object.rop_band,
            #         "rpulse_width": radar_object.rpulse_width,
            #         "rantenna_gain": radar_object.rantenna_gain,
            #         "rpulse_freq": radar_object.rpulse_freq,
            #         "rtrans_power": radar_object.rtrans_power,
            #         "rradius_max": radar_object.rradius_max,
            #         "rdist_max": radar_object.rdist_max
            #     }})
            # elif res_type == "武器":
            #     weapon_object = arm_info.objects.get(asname=res_name)
            #     return JsonResponse({"dataInfo":{
            #         "asid": weapon_object.id,
            #         "asname": weapon_object.asname,
            #         "atype": weapon_object.atype,
            #         "aspeed": weapon_object.aspeed,
            #         "akill_radius": weapon_object.akill_radius,
            #         "ahit_rate": weapon_object.ahit_rate,
            #         "aguide_accuracy": weapon_object.aguide_accuracy,
            #         "ahit_accuracy": weapon_object.ahit_accuracy,
            #         "aattack_distmax": weapon_object.aattack_distmax
            #     }})
            # else:
            #     compute_object = compute_info.objects.get(csname=res_name)
            #     return JsonResponse({"dataInfo":{
            #         'csid': compute_object.id,
            #         "csname": compute_object.csname,
            #         "ctype": compute_object.ctype,
            #         "caccuracy": compute_object.caccuracy
            #     }
            #     })

