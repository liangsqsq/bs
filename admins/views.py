import socket
import threading
from time import sleep

from django.core import serializers
from django.db.models import Count
from django.shortcuts import render, redirect
import json
import sys

from res.models import transfer, model, classes
from utils.email_send import send_sucess_email
from . import zabbix_api
from django.http import HttpResponse, JsonResponse
from configobj import ConfigObj
from django.contrib.auth.models import Group
from users.models import UserProfile, group
from vm.models import *
from container.models import *
from admins.ResourceAllocation import DynamicDockerAllocation, ResourceAllocation
from admins.sshConnection import *
from admins.getVMInfo import getVMInfo
from admins.customVM import *
from admins.networkManage import *
from django.core.paginator import Paginator

from .decorate import decorate_request_pindex, decorate_request, decorate_vm_recv, decorate_existing_workstation, \
    decorate_add_domain, decorate_add_workstation, decorate_get_domain_by_ip, decorate_get_node_by_name, decorate_node_apply
from .decorate import decorate_agree_zabbix_node
from .zabbix_api import Zabbix

config = ConfigObj("config.ini", encoding='UTF8')

FLAG_RESOURCE_NOT_ENOUGH = -1

@decorate_add_domain
def add_domain(request, server_list=None, message=None):
    if request.user.is_superuser == 1:
        if message:
            return render(request, "admins/add_domain.html", {
                'message': message,
                'communication_list': server_list,
            })
        if request.method == "POST":
            new_domain = request.POST.get("exampleInputDomain")
            new_location = request.POST.get("exampleInputLocation")
            new_gw_ip = request.POST.get("exampleInputGw-ip")
            new_port = request.POST.get("exampleInputPort")
            new_user = request.POST.get("exampleInputUser", None)
            new_pwd = request.POST.get("exampleInputPassword", None)
            homeDir = request.POST.get("home")

            if ssh_Auth(new_gw_ip, new_port, new_user, new_pwd, homeDir) == True:
                domain.objects.create(domain=new_domain, location=new_location, gw_ip=new_gw_ip, port=int(new_port),
                                      user=new_user, pwd=new_pwd, home_dir=homeDir)
                message = "添加成功"
            else:
                message = "添加失败，请确认相关信息"
            return render(request, "admins/add_domain.html", {
                "message": message,
                'communication_list': server_list,
            })
        else:
            return render(request, "admins/add_domain.html", {
                'communication_list': server_list,
            })

def add_domain_request(request):
    new_domain = request.POST.get("exampleInputDomain")
    new_location = request.POST.get("exampleInputLocation")
    new_gw_ip = request.POST.get("exampleInputGw-ip")
    new_port = request.POST.get("exampleInputPort")
    new_user = request.POST.get("exampleInputUser", None)
    new_pwd = request.POST.get("exampleInputPassword", None)
    homeDir = request.POST.get("home")

    if ssh_Auth(new_gw_ip, new_port, new_user, new_pwd, homeDir) == True:
        domain.objects.create(domain=new_domain, location=new_location, gw_ip=new_gw_ip, port=int(new_port),
                              user=new_user, pwd=new_pwd, home_dir=homeDir)
        message = "添加成功"
    else:
        message = "添加失败，请确认相关信息"
    return HttpResponse(message)

@decorate_add_workstation
def add_workstation(request, server_list=None, domain_list=None, message=None):
    if message:
        return render(request, "admins/add_workstation.html", {
            "message": message,
            'communication_list': server_list,
            "domain_list": domain_list,
        })
    if request.user.is_superuser == 1:
        if request.method == "POST":
            hostname = request.POST.get("hostname")
            IP = request.POST.get("IP")
            SSH_port = request.POST.get("SSH")
            username = request.POST.get("username", None)
            password = request.POST.get("password", None)
            domainID = request.POST.get("domain")
            homeDir = request.POST.get("home")
            is_zabbix = request.POST.get("is_zabbix")

            if ssh_Auth(IP, SSH_port, username, password, homeDir) == True:
                if is_zabbix == "on":
                    set_zabbix = True
                    if hostname != 'Zabbix server':
                        url = 'http://127.0.0.1/zabbix/api_jsonrpc.php'
                        try:
                            za = Zabbix(url, 'Admin', 'zabbix')
                            host = za.hostid_get(IP)
                            if host:
                                hostid = host[0]['hostid']
                                za.make_host_available(hostid)
                            else:
                                za.create_host(IP, IP)
                        except:
                            message = "zabbix添加失败，请确认相关信息"
                            ret = domain.objects.all()
                            return render(request, "admins/add_workstation.html", {
                                "message": message,
                                'communication_list': server_list,
                                "domain_list": domain_list,})
                else:
                    set_zabbix = False
                workstation.objects.create(host_name=hostname, ip=IP, ssh_port=SSH_port,
                                                                user=username, pwd=password,
                                                                home_dir=homeDir, belong_id=domainID, is_zabbix=set_zabbix)
                message = "节点添加成功"
            else:
                message = "添加失败，请确认相关信息"
            return render(request, "admins/add_workstation.html", {
                "message": message,
                'communication_list': server_list,
                "domain_list": domain_list,
            })
        # 取到所有的domain get请求中
        return render(request, "admins/add_workstation.html", {
            'communication_list': server_list,
            "domain_list": domain_list,
        })

def add_workstation_request(request):
    hostname = request.POST.get("hostname")
    IP = request.POST.get("IP")
    SSH_port = request.POST.get("SSH")
    username = request.POST.get("username", None)
    password = request.POST.get("password", None)
    domainID = request.POST.get("domain")
    homeDir = request.POST.get("home")
    is_zabbix = request.POST.get("is_zabbix")

    if ssh_Auth(IP, SSH_port, username, password, homeDir) == True:
        if is_zabbix == "on":
            set_zabbix = True
            if hostname != 'Zabbix server':
                url = 'http://127.0.0.1/zabbix/api_jsonrpc.php'
                try:
                    za = Zabbix(url, 'Admin', 'zabbix')
                    host = za.hostid_get(IP)
                    if host:
                        hostid = host[0]['hostid']
                        za.make_host_available(hostid)
                    else:
                        za.create_host(IP, IP)
                except:
                    message = "zabbix添加失败，请确认相关信息"
                    ret = domain.objects.all()
                    return HttpResponse(message)
        else:
            set_zabbix = True
        workstation.objects.create(host_name=hostname, ip=IP, ssh_port=SSH_port,
                                   user=username, pwd=password,
                                   home_dir=homeDir, belong_id=domainID, is_zabbix=set_zabbix)
        message = "节点添加成功"
    else:
        message = "添加失败，请确认相关信息"
    return HttpResponse(message)

@decorate_request
def existing_domain(request, data=None):
    if request.user.is_superuser == 1:
        domains = domain.objects.filter(state=1)
        res_list = []
        for domain_ in domains:
            res_dist = {}
            res_dist['domain'] = domain_.domain
            res_dist['location'] = domain_.location
            res_dist['gw_ip'] = domain_.gw_ip
            res_dist['port'] = domain_.port
            res_dist['user'] = domain_.user
            res_dist['pwd'] = domain_.pwd
            res_dist['deploy_time'] = domain_.deploy_time.strftime('%Y-%m-%d %H:%M:%S')
            if domain_.sync_time:
                res_dist['sync_time'] = domain_.sync_time.strftime('%Y-%m-%d %H:%M:%S')
            else:
                res_dist['sync_time'] = None
            res_dist['vt_type'] = domain_.vt_type
            res_dist['state'] = domain_.state
            res_list.append(res_dist)
        if data:
            res_list += data
    return render(request, 'admins/existing_domain.html', {'data': res_list})

def existing_domain_request(request):
    domains = domain.objects.filter(state=1)
    res_list = []
    for domain_ in domains:
        res_dist = {}
        res_dist['domain'] = domain_.domain
        res_dist['location'] = domain_.location
        res_dist['gw_ip'] = domain_.gw_ip
        res_dist['port'] = domain_.port
        res_dist['user'] = domain_.user
        res_dist['pwd'] = domain_.pwd
        res_dist['deploy_time'] = domain_.deploy_time.strftime('%Y-%m-%d %H:%M:%S')
        if domain_.sync_time:
            res_dist['sync_time'] = domain_.sync_time.strftime('%Y-%m-%d %H:%M:%S')
        else:
            res_dist['sync_time'] = None
        res_dist['vt_type'] = domain_.vt_type
        res_dist['state'] = domain_.state
        res_list.append(res_dist)

    return HttpResponse(str(res_list))

# def existing_workstation(request):
#     global domain_name_name
#     print(request.method)
#     if request.method == "POST":
#         domain_name = request.POST.get("domain_name")
#         domain_name_name = domain_name
#         ws_domain = domain.objects.get(domain=domain_name)
#         workstations = workstation.objects.filter(belong=ws_domain)
#         return render(request, 'admins/existing_workstations.html', {'data': workstations})
#     else:
#         ws_domain = domain.objects.get(domain=domain_name_name)
#         workstations = workstation.objects.filter(belong=ws_domain)
#         return render(request, 'admins/existing_workstations.html', {'data': workstations})

@decorate_existing_workstation
def existing_workstation(request, data=None):
    if data or data == []:
        return render(request, 'admins/existing_workstations.html', {'data': data})
    else:
        domain_name = request.POST.get('domain_name')
        ws_domain = domain.objects.get(domain=domain_name)
        workstations = workstation.objects.filter(belong=ws_domain)
        res_list = []
        for workstation_ in workstations:
            res_dict = {}
            res_dict['host_name'] = workstation_.host_name
            res_dict['domain_ip'] = ws_domain.gw_ip
            res_dict['ssh_port'] = workstation_.ssh_port
            res_dict['ip'] = workstation_.ip
            res_dict['user'] = workstation_.user
            res_dict['pwd'] = workstation_.pwd
            res_dict['deploy_time'] = workstation_.deploy_time.strftime('%Y-%m-%d %H:%M:%S')
            res_list.append(res_dict)

        return render(request, 'admins/existing_workstations.html', {'data': res_list})

def existing_workstation_request(request):
    domain_name = request.POST.get('domain_name')
    ws_domain = domain.objects.get(domain=domain_name)
    workstations = workstation.objects.filter(belong=ws_domain)
    res_list = []
    for workstation_ in workstations:
        res_dict = {}
        res_dict['host_name'] = workstation_.host_name
        res_dict['domain_ip'] = ws_domain.gw_ip
        res_dict['ssh_port'] = workstation_.ssh_port
        res_dict['ip'] = workstation_.ip
        res_dict['user'] = workstation_.user
        res_dict['pwd'] = workstation_.pwd
        res_dict['deploy_time'] = workstation_.deploy_time.strftime('%Y-%m-%d %H:%M:%S')
        res_list.append(res_dict)

    return HttpResponse(str(res_list))

@decorate_vm_recv
def sync_domain(request):
    if request.method == 'POST':
        domain_name = request.POST.get('domain_name')
        sync_domain = domain.objects.get(domain=domain_name)
        workstations = workstation.objects.filter(belong=sync_domain)
        vmos = vm_os.objects.get(os_version='unknown')
        vmuser = UserProfile.objects.get(username='unknown')

        try:
            for sync_workstation in workstations:
                user = sync_workstation.user
                gwip = sync_workstation.ip
                port = sync_workstation.ssh_port
                conn = libvirt.open("qemu+ssh://" + user + "@" + gwip + ":" + str(port) + "/system")
                if conn == None:
                    print('Failed to open connection to' + user, file=sys.stderr)
                storagePool = conn.storagePoolLookupByName('default')

                vms = conn.listAllDomains(0)
                for sync_vm in vms:
                    vmname = sync_vm.name()
                    print(vmname)

                    myvm = vm.objects.filter(name=vmname, gateway_ip=gwip, belong=sync_workstation)
                    if myvm.exists():
                        print('vm ' + vmname + ' already exists')
                        pass
                    else:
                        isActive, isPersistent, cpus, maxmem, diskSize, diskAllocation, format_type = getVMInfo(sync_vm,
                                                                                                                storagePool)
                        # print(getVMInfo(vm,storagePool))
                        if isActive == True:
                            power = 'running'
                        else:
                            power = 'shutoff'
                        myvm = vm.objects.create(name=vmname, vCPUs=cpus, memory=maxmem, diskSize=diskSize,
                                                 diskAllocation=diskAllocation, diskType=format_type, gateway_ip=gwip,
                                                 isPersistent=isPersistent, power_state=power, state=isActive,
                                                 os=vmos, belong=sync_workstation, region=sync_domain, user=vmuser)
                        myvm.save()
            st = 1
        except:
            st = 0

    return HttpResponse(json.dumps({"st": st}), content_type="application/json")

@decorate_vm_recv
def delete_domain(request):
    if request.method == "POST":
        domain_name = request.POST.get("domain_name")
        del_domain = domain.objects.get(domain=domain_name)
        try:
            del_domain.delete()
            st = 1
        except:
            st = 2

        return HttpResponse(json.dumps({"st": st}), content_type="application/json")
    else:
        return render(request, 'index.html')

@decorate_vm_recv
def delete_workstation(request):
    if request.method == "POST":
        workstation_name = request.POST.get("workstation_name")
        del_workstation = workstation.objects.get(host_name=workstation_name)
        del_workstation.delete()
        if del_workstation.host_name != 'Zabbix server':
            del_apply_node = apply_node.objects.get(ip=del_workstation.ip)
            del_apply_node.delete()

        st = 1
        return HttpResponse(json.dumps({"st": st}), content_type="application/json")
    else:
        return render(request, 'index.html')

@decorate_add_workstation
def add_img(request, server_list=None, domain_list=None, message=None):
    if message:
        return render(request, "admins/add_img.html", {
            "message": message,
            'communication_list': server_list,
            "domain_list": domain_list,
        })
    if request.user.is_superuser == 1:
        if request.method == "POST":
            OS = request.POST.get("osVersion")
            imgPath = request.POST.get("imgPath")
            isoPath = request.POST.get("isoPath")
            imgUser = request.POST.get("imgUser")
            imgPwd = request.POST.get("imgPwd")
            imgPort = request.POST.get("imgPort")
            imgDomain = request.POST.get("imgDomain")
            vm_os.objects.create(os_version=OS, iso_path=isoPath, template_path=imgPath, default_user=imgUser,
                                 default_pwd=imgPwd, default_port=imgPort)
            if True:
                message = "添加成功"
            else:
                message = "添加失败，请确认相关信息"
            ret = domain.objects.all()
            return render(request, "admins/add_img.html", {
                "message": message,
                'communication_list': server_list,
                "domain_list": domain_list,
            })
        # 取到所有的domain get请求中
        return render(request, "admins/add_img.html", {
            'communication_list': server_list,
            "domain_list": domain_list,
        })

def add_img_request(request):
    OS = request.POST.get("osVersion")
    imgPath = request.POST.get("imgPath")
    isoPath = request.POST.get("isoPath")
    imgUser = request.POST.get("imgUser")
    imgPwd = request.POST.get("imgPwd")
    imgPort = request.POST.get("imgPort")
    imgDomain = request.POST.get("imgDomain")
    vm_os.objects.create(os_version=OS, iso_path=isoPath, template_path=imgPath, default_user=imgUser,
                         default_pwd=imgPwd, default_port=imgPort)
    if True:
        message = "添加成功"
    else:
        message = "添加失败，请确认相关信息"
    return HttpResponse(message)

@decorate_request_pindex
def applyvm(request, pindex, data=None):
    if request.user.is_superuser == 1:
        badge_audit = new_vm_apply.objects.all().order_by("-apply_time")
        res_list = []
        for deploy_ in badge_audit:
            res_dict = {}
            res_dict['username'] = deploy_.user.username
            res_dict['id'] = deploy_.id
            res_dict['os_version'] = deploy_.os_version.os_version
            res_dict['memory'] = deploy_.memory
            res_dict['cpu_cores'] = deploy_.cpu_cores
            res_dict['disk'] = deploy_.disk
            res_dict['gateway_ip'] = deploy_.region.gw_ip
            res_dict['region'] = deploy_.region.domain
            res_dict['apply_time'] = deploy_.apply_time.strftime('%Y-%m-%d %H:%M:%S')
            res_dict['isPersistent'] = deploy_.isPersistent
            res_dict['installway'] = deploy_.installway
            res_dict['state'] = deploy_.state
            res_list.append(res_dict)
        if data:
            res_list += data
        paginator = Paginator(res_list,10)
        page = paginator.page(pindex)
        if paginator.num_pages <= 5:
            display_list = paginator.page_range
        else:
            if page.number <= 3:
                display_list = [1,2,3,4,5]
            elif paginator.num_pages-page.number <= 2:
                display_list = paginator.page_range[paginator.num_pages-5:paginator.num_pages+1:1]
            else:
                display_list = [page.number-2,page.number-1,page.number,page.number+1,page.number+2]
        return render(request, 'admins/vm_apply.html', {'data': page,
                                                        'dist':paginator.num_pages-page.number,
                                                        'display_list': display_list})

def applyvm_request(request):
    badge_audit = new_vm_apply.objects.all().order_by("-apply_time")
    res_list = []
    for deploy_ in badge_audit:
        res_dict = {}
        res_dict['username'] = deploy_.user.username
        res_dict['id'] = deploy_.id
        res_dict['os_version'] = deploy_.os_version.os_version
        res_dict['memory'] = deploy_.memory
        res_dict['cpu_cores'] = deploy_.cpu_cores
        res_dict['disk'] = deploy_.disk
        res_dict['gateway_ip'] = deploy_.region.gw_ip
        res_dict['region'] = deploy_.region.domain
        res_dict['apply_time'] = deploy_.apply_time.strftime('%Y-%m-%d %H:%M:%S')
        res_dict['isPersistent'] = deploy_.isPersistent
        res_dict['installway'] = deploy_.installway
        res_dict['state'] = deploy_.state
        res_list.append(res_dict)

    return HttpResponse(str(res_list))

@decorate_request_pindex
def applydeploy(request, pindex, data=None):
    if request.user.is_superuser == 1:
        deploys = deploy_apply.objects.all().order_by("-apply_time")
        res_list = []
        for deploy in deploys:
            res_dist = {}
            res_dist['id'] = deploy.id
            res_dist['username'] = deploy.vm.user.username
            res_dist['name'] = deploy.vm.name
            res_dist['os_version'] = deploy.vm.os.os_version
            res_dist['vm_ip'] = deploy.vm.ip
            res_dist['memory'] = deploy.memory
            res_dist['vCPUs'] = deploy.vCPUs
            res_dist['diskSize'] = deploy.diskSize
            res_dist['domain'] = deploy.vm.region.domain
            res_dist['apply_time'] = deploy.apply_time.strftime('%Y-%m-%d %H:%M:%S')
            res_dist['state'] = deploy.state
            res_list.append(res_dist)
        if data:
            res_list += data
        paginator = Paginator(res_list, 10)
        page = paginator.page(pindex)
        if paginator.num_pages <= 5:
            display_list = paginator.page_range
        else:
            if page.number <= 3:
                display_list = [1,2,3,4,5]
            elif paginator.num_pages-page.number <= 2:
                display_list = paginator.page_range[paginator.num_pages-5:paginator.num_pages+1:1]
            else:
                display_list = [page.number-2,page.number-1,page.number,page.number+1,page.number+2]
        return render(request, 'admins/vm_apply_setting.html', {'data': page,
                                                                'dist': paginator.num_pages-page.number,
                                                                'display_list': display_list})

def applydeploy_request(request):
    deploys = deploy_apply.objects.all().order_by("-apply_time")
    res_list = []
    for deploy in deploys:
        res_dist = {}
        res_dist['id'] = deploy.id
        res_dist['username'] = deploy.vm.user.username
        res_dist['name'] = deploy.vm.name
        res_dist['os_version'] = deploy.vm.os.os_version
        res_dist['vm_ip'] = deploy.vm.ip
        res_dist['memory'] = deploy.memory
        res_dist['vCPUs'] = deploy.vCPUs
        res_dist['diskSize'] = deploy.diskSize
        res_dist['domain'] = deploy.vm.region.domain
        res_dist['apply_time'] = deploy.apply_time.strftime('%Y-%m-%d %H:%M:%S')
        res_dist['state'] = deploy.state
        res_list.append(res_dist)

    return HttpResponse(str(res_list))

@decorate_vm_recv
def agree_deploy(request):
    # if request.user.is_superuser == 1:
    if request.method == "POST":
        applyID = request.POST.get("applyID")
        apply = deploy_apply.objects.get(id=applyID)
        vm = apply.vm
        vmname = vm.name
        server = vm.belong
        vcpus = int(apply.vCPUs)
        mem = int(apply.memory)
        diskSize = int(apply.diskSize)

        flag = setVMConfiguration(server, vmname, vcpus, mem, diskSize)
        if flag != True:
            return HttpResponse(json.dumps({"st": flag}), content_type="application/json")

        apply.state = 1
        apply.operate_time = timezone.now()
        apply.save()
        vm.vCPUs = vcpus
        vm.memory = mem
        vm.diskSize = diskSize
        vm.save()
        return HttpResponse(json.dumps({"st": flag}), content_type="application/json")

@decorate_vm_recv
def refuse_deploy(request):
    # if request.user.is_superuser == 1:
    if request.method == "POST":
        applyID = request.POST.get("applyID")
        apply = deploy_apply.objects.get(id=applyID)
        apply.state = 2
        apply.operate_time = timezone.now()
        apply.save()
        return HttpResponse(json.dumps({"st": 1}), content_type="application/json")
    # else:
    #     return render(request, 'index.html')


def applyport(request, pindex):
    if request.user.is_superuser == 1:
        portsapply = port_apply.objects.all().order_by("-apply_time")
        paginator = Paginator(portsapply, 10)
        page = paginator.page(pindex)
        if paginator.num_pages <= 5:
            display_list = paginator.page_range
        else:
            if page.number <= 3:
                display_list = [1,2,3,4,5]
            elif paginator.num_pages-page.number <= 2:
                display_list = paginator.page_range[paginator.num_pages-5:paginator.num_pages+1:1]
            else:
                display_list = [page.number-2,page.number-1,page.number,page.number+1,page.number+2]
        return render(request, 'admins/vm_apply_port.html', {'data': page,
                                                             'dist': paginator.num_pages-page.number,
                                                             'display_list': display_list})

def agree_port(request):
    if request.user.is_superuser == 1:
        if request.method == "POST":
            applyID = request.POST.get("applyID")
            apply = port_apply.objects.get(id=applyID)
            vm = apply.vm
            region = vm.region
            mapPort = buildVMNAT(region, vm.ip, apply.vmPort, flags=1)

            apply.mapPort = mapPort
            apply.operate_time = timezone.now()
            apply.state = 1
            apply.save()
            return HttpResponse(json.dumps({"st": 1}), content_type="application/json")


def refuse_port(request):
    if request.user.is_superuser == 1:
        if request.method == "POST":
            applyID = request.POST.get("applyID")
            apply = port_apply.objects.get(id=applyID)
            print(str(applyID))
            apply.state = 2
            apply.operate_time = timezone.now()
            apply.save()
            return HttpResponse(json.dumps({"st": 1}), content_type="application/json")
    else:
        return render(request, 'index.html')


def delete_port(request):
    if request.user.is_superuser == 1:
        if request.method == "POST":
            applyID = request.POST.get("applyID")
            apply = port_apply.objects.get(id=applyID)
            vm = apply.vm
            region = vm.region

            if delPort(region, vm.ip, apply.mapPort, apply.vmPort) == True:
                apply.state = 3
                apply.save()
                return HttpResponse(json.dumps({"st": 1}), content_type="application/json")


def show_domain(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            datad = {}
            return render(request, 'admins/showdomain.html')
        else:
            return render(request, 'users/login.html')
    else:
        return render(request, 'users/login.html')


def group_list(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            datad = group.objects.all()
            return render(request, 'admins/group_list.html', {'data': datad})


def add_group(request):
    if request.method == "POST":
        gname = request.POST.get("group_name")
        group.objects.create(gname=gname)
        datad = group.objects.all()
        return render(request, 'admins/group_list.html', {'data': datad})

@decorate_vm_recv
def agree_vm(request):
    if request.method == "POST":
        vm_id = request.POST.get("vm_id")
        username = request.POST.get("username")
        my_vm_apply = new_vm_apply.objects.get(id=vm_id)

        # 获取分配资源所需要的虚拟机信息
        apply_cpu = my_vm_apply.cpu_cores
        apply_mem = my_vm_apply.memory
        apply_disk = my_vm_apply.disk
        apply_domain = my_vm_apply.region

        #调用资源分配算法
        server = ResourceAllocation(apply_domain, apply_cpu, apply_mem, apply_disk)
        if server == None:
            return HttpResponse(json.dumps({"st": FLAG_RESOURCE_NOT_ENOUGH}), content_type="application/json")
        # return HttpResponse(json.dumps({"st": 1, "vm_id": vm_id, "server_id": server.id}), content_type="application/json")
        return HttpResponse(json.dumps({"st": 1, "vm_data": {
            "vm_id": vm_id,
            "server_id": server.id,
            "username": username,
        }}), content_type="application/json")

@decorate_vm_recv
def agree_install_vm(request):
    if request.method == "POST":
        vm_data = eval(request.POST.get("vm_data"))
        vm_id = vm_data["vm_id"]
        my_vm_apply = new_vm_apply.objects.get(id=vm_id)
        server_id = vm_data["server_id"]
        #生成构建虚拟机所需的信息
        server = workstation.objects.get(id=server_id)
        apply_os = my_vm_apply.os_version
        vm_num = vm.objects.all().count()
        # my_vm_num = vm.objects.filter(user=my_vm_apply.user).count() + 1
        # my_vm_name = str(my_vm_num) + my_vm_apply.user.username
        try:
            vm_ = vm.objects.latest('id')
        except:
            vm_count = 0
        else:
            vm_name = vm.objects.latest('id').name
            vm_count = int(vm_name[:len(vm_name) - 5])
        try:
            container_ = container.objects.latest('id')
        except:
            container_count = 0
        else:
            container_name = container.objects.latest('id').name
            container_count = int(container_name[:len(container_name) - 5])
        if vm_count > container_count:
            my_vm_name = str(vm_count + 1) + "admin"
        else:
            my_vm_name = str(container_count + 1) + "admin"
        noVNC_PORT = int(config['novnc']['vnc_port']) + vm_num
        image_path = config['kvm']['image_path'] + my_vm_name + '.qcow2'

        flag, vmip = installVM(my_vm_name, my_vm_apply, apply_os, server, image_path, noVNC_PORT)
        if flag != True:
            return HttpResponse(json.dumps({"st": flag}), content_type="application/json")
        print("Success to create a domain from an XML definition.")
        vm_data["my_vm_name"] = my_vm_name
        vm_data["noVNC_PORT"] = noVNC_PORT
        vm_data["vmip"] = vmip
        return HttpResponse(json.dumps({"st": 1, "vm_data": vm_data}), content_type="application/json")

@decorate_vm_recv
def agree_build_vmNAT(request):
    if request.method == "POST":
        vm_data = eval(request.POST.get("vm_data"))
        vm_id = vm_data["vm_id"]
        my_vm_apply = new_vm_apply.objects.get(id=vm_id)
        apply_region = my_vm_apply.region
        apply_os = my_vm_apply.os_version
        vmip = vm_data["vmip"]
        if vmip:
            dport = buildVMNAT(apply_region, vmip, apply_os.default_port)
        vm_data["dport"] = dport
        return HttpResponse(json.dumps({"st": 1, "vm_data": vm_data}), content_type="application/json")

@decorate_vm_recv
def agree_definit_vm(request):
    if request.method == "POST":
        vm_data = eval(request.POST.get("vm_data"))
        vm_id = vm_data["vm_id"]
        my_vm_apply = new_vm_apply.objects.get(id=vm_id)
        my_vm_name = vm_data["my_vm_name"]
        class_name = my_vm_apply.classes
        model_name = my_vm_apply.model
        apply_cpu = my_vm_apply.cpu_cores
        apply_mem = my_vm_apply.memory
        apply_disk = my_vm_apply.disk
        apply_domain = my_vm_apply.region
        apply_os = my_vm_apply.os_version
        apply_region = my_vm_apply.region
        my_vm_apply = new_vm_apply.objects.get(id=vm_id)
        vmip = vm_data["vmip"]
        my_vm_pwd = my_vm_apply.password
        server_id = vm_data["server_id"]
        server = workstation.objects.get(id=server_id)
        noVNC_PORT = vm_data["noVNC_PORT"]
        dport = vm_data["dport"]
        apply_isPersistent = my_vm_apply.isPersistent
        username = vm_data["username"]
        my_agree_vm = vm.objects.create(name=my_vm_name,
                                        vCPUs=apply_cpu, memory=apply_mem, diskSize=apply_disk,
                                        os_version=apply_os.os_version, os=apply_os,
                                        ip=vmip, password=my_vm_pwd,
                                        belong=server, noVNC_port=noVNC_PORT,
                                        gateway_ip=apply_domain.gw_ip, region=my_vm_apply.region,
                                        user=my_vm_apply.user, conn_port=dport,
                                        apply_time=my_vm_apply.apply_time, isPersistent=apply_isPersistent)
        my_agree_vm.save()
        my_vm_apply.state = 1
        my_vm_apply.save()
        my_agree_tranfer = transfer.objects.create(resource_name=my_vm_name,classes=class_name,model=model_name)
        my_agree_model = model.objects.get(model_name=model_name)
        my_agree_model.number = my_agree_model.number+1
        my_agree_model.save()
        my_agree_classes = classes.objects.get(class_name=my_agree_tranfer.classes)
        my_agree_classes.number = my_agree_classes.number+1
        my_agree_classes.save()
        my_agree_tranfer.save()
        # NOVNC
        token_config = my_vm_name + ': ' + config['host']['ip'] + ':' + str(noVNC_PORT)
        print("token : " + token_config)
        with open('TOKEN', 'a') as wf:
            wf.write(token_config)
            wf.write("\n")

        # 发送成功通知邮件
        user = UserProfile.objects.get(username=username)
        email = user.email
        try:
            send_sucess_email(email, my_agree_vm, "success")
        except:
            print("邮件发送失败")

        return HttpResponse(json.dumps({"st": 1}), content_type="application/json")


@decorate_vm_recv
def refuse_vm(request):
    if request.method == "POST":
        vm_id = request.POST.get("vm_id")
        my_vm_apply = new_vm_apply.objects.get(id=vm_id)
        my_vm_apply.state = 2
        my_vm_apply.save()

        st = 1
        return HttpResponse(json.dumps({"st": st}), content_type="application/json")
    else:
        return render(request, 'index.html')

@decorate_request_pindex
def VM_Recy(request, pindex, data=None):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            vms = vm.objects.filter(is_del=0).order_by('-start_time')
            res_list = []
            for vm_ in vms:
                res_dist = {}
                res_dist['username'] = vm_.user.username
                res_dist['name'] = vm_.name
                res_dist['os_version'] = vm_.os.os_version
                res_dist['memory'] = vm_.memory
                res_dist['vCPUs'] = vm_.vCPUs
                res_dist['diskSize'] = vm_.diskSize
                if transfer.objects.get(resource_name=vm_.name).classes == 1:
                    diskType = "无人机"
                elif transfer.objects.get(resource_name=vm_.name).classes == 2:
                    diskType = "无人车"
                else:
                    diskType = "无人船"
                res_dist['diskType'] = diskType
                res_dist['diskAllocation'] = transfer.objects.get(resource_name=vm_.name).model
                res_dist['ip'] = vm_.ip
                res_dist['gateway_ip'] = vm_.gateway_ip
                res_dist['domain'] = vm_.region.domain
                res_dist['start_time'] = vm_.start_time.strftime('%Y-%m-%d %H:%M:%S')
                res_dist['is_del'] = vm_.is_del
                res_list.append(res_dist)
            if data:
                res_list += data
            paginator = Paginator(res_list, 10)
            page = paginator.page(pindex)
            if paginator.num_pages <= 5:
                display_list = paginator.page_range
            else:
                if page.number <= 3:
                    display_list = [1,2,3,4,5]
                elif paginator.num_pages-page.number <= 2:
                    display_list = paginator.page_range[paginator.num_pages-5:paginator.num_pages+1:1]
                else:
                    display_list = [page.number-2,page.number-1,page.number,page.number+1,page.number+2]
            return render(request, 'admins/vm_recy.html', {'vms': page,
                                                           'dist': paginator.num_pages-page.number,
                                                           'display_list': display_list})

def VM_Recy_request(request):
    vms = vm.objects.filter(is_del=0).order_by('-start_time')
    res_list = []
    for vm_ in vms:
        res_dist = {}
        res_dist['username'] = vm_.user.username
        res_dist['name'] = vm_.name
        res_dist['os_version'] = vm_.os.os_version
        res_dist['memory'] = vm_.memory
        res_dist['vCPUs'] = vm_.vCPUs
        res_dist['diskSize'] = vm_.diskSize
        if transfer.objects.get(resource_name=vm_.name).classes == 1:
            diskType = "无人机"
        elif transfer.objects.get(resource_name=vm_.name).classes == 2:
            diskType = "无人车"
        else:
            diskType = "无人船"
        res_dist['diskType'] = diskType
        res_dist['diskAllocation'] = transfer.objects.get(resource_name=vm_.name).model
        res_dist['ip'] = vm_.ip
        res_dist['gateway_ip'] = vm_.gateway_ip
        res_dist['domain'] = vm_.region.domain
        res_dist['start_time'] = vm_.start_time.strftime('%Y-%m-%d %H:%M:%S')
        res_dist['is_del'] = vm_.is_del
        res_list.append(res_dist)

    return HttpResponse(str(res_list))

@decorate_vm_recv
def delete_vm(request):
    if request.method == "POST":
        vm_name = request.POST.get("vm_name")
        myvm = vm.objects.get(name=vm_name)

        server = myvm.belong
        flag = deleteVM(vm_name, server, myvm.isPersistent)
        if flag != True:
            return HttpResponse(json.dumps({"st": flag}), content_type="application/json")

        if myvm.ip:
            delPort(myvm.region, myvm.ip, myvm.conn_port, myvm.os.default_port)

        # myvm.is_del = True
        # myvm.save()
        my_tranfer = transfer.objects.get(resource_name=myvm.name)
        my_model = model.objects.get(model_name=my_tranfer.model)
        my_model.number = my_model.number-1
        my_model.save()
        my_classes = classes.objects.get(class_name=my_tranfer.classes)
        my_classes.number = my_classes.number-1
        my_classes.save()
        my_tranfer.delete()
        myvm.delete()
        noVNC_PORT = myvm.noVNC_port

        with open('TOKEN', 'r') as rf:
            lines = rf.readlines()
        with open('TOKEN', 'w') as wf:
            for l in lines:
                if str(noVNC_PORT) not in l:
                    wf.write(l)

        return HttpResponse(json.dumps({"st": flag}), content_type="application/json")
    else:
        return render(request, 'index.html')

def show_users(request, pindex):
    if request.user.is_authenticated and request.user.is_superuser:
        users = UserProfile.objects.all().order_by('-date_joined')
        paginator = Paginator(users, 10)
        page = paginator.page(pindex)
        if paginator.num_pages <= 5:
            display_list = paginator.page_range
        else:
            if page.number <= 3:
                display_list = [1,2,3,4,5]
            elif paginator.num_pages-page.number <= 2:
                display_list = paginator.page_range[paginator.num_pages-5:paginator.num_pages+1:1]
            else:
                display_list = [page.number-2,page.number-1,page.number,page.number+1,page.number+2]
        return render(request, 'admins/showusers.html', {'users':page,
                                                           'dist': paginator.num_pages-page.number,
                                                           'display_list': display_list})


def user_manage(request):
    if request.user.is_superuser and request.method == "POST":
        username = request.POST.get("username")
        action = request.POST.get("action")
        print(username, action)
        user = UserProfile.objects.get(username=username)
        if action == 'lockuser':
            user.is_active = False
            user.save()
        elif action == 'unlockuser':
            user.is_active = True
            user.save()
        return render(request, 'admins/showusers.html')
    return render(request, 'index.html')


def get_count(request):
    new_vm_apply_count = new_vm_apply.objects.filter(state=0).aggregate(Count('state'))['state__count']
    vm_deploy_apply_count = deploy_apply.objects.filter(state=0).aggregate(Count('state'))['state__count']
    vm_port_apply_count = port_apply.objects.filter(state=0).aggregate(Count('state'))['state__count']
    new_container_apply_count= new_docker_apply.objects.filter(state=0).aggregate(Count('state'))['state__count']
    return JsonResponse({'new_vm_apply_count': new_vm_apply_count,
                         'vm_deploy_apply_count': vm_deploy_apply_count,
                         'vm_port_apply_count': vm_port_apply_count,
                         'new_container_apply_count':new_container_apply_count
                         })


@decorate_vm_recv
def backup_vm(request):
    '''
    进行备份、命令行交互式的快照功能
    :param request:
    :return: 快照列表
    '''
    # if request.user.is_superuser == 1:
    if request.method == "POST":
        domName=request.POST.get("vm_name")
        username=request.POST.get("user_name")
        #获取信息
        user=UserProfile.objects.get(username=username)
        print(username)
        vmobject=vm.objects.get(name=domName)
        serverip=vmobject.belong.ip
        serverport=vmobject.belong.ssh_port
        serveruser=vmobject.belong.user
        hostname=vmobject.belong.host_name
        #链接服务器
        conn,pool=libvirtConn(hostname,str(serverip),str(serverport),serveruser)

        if conn == None:
            print('Failed to open connection to qemu:///system', file=sys.stderr)
        dom=conn.lookupByName(domName)
        if dom == None:
            print('Failed to find the domain ' + domName, file=sys.stderr)
        #获取当前镜像文件位置 多次快照
        diskpath = config['kvm']['image_path'] +domName+'.qcow2'
        # 快照命名 True没有删除
        snapshotNum=snapshot.objects.filter(vmname=vmobject,is_exist=True).count()+1
        #dom.snapshotListNames()
        snapshotname = domName +'-'+str(snapshotNum)
        #快照xml文件
        xml=getSnapshotXML(snapshotname,diskpath)
        print(xml)
        #创建快照
        newsnapshot = snapshot.objects.create(snapshotName=snapshotname, snapshotId=snapshotNum,
                                              username=user, vmname=vmobject)
        newsnapshot.save()
        try:
            info = dom.snapshotCreateXML(xml, 0)
            flag = 1
        except:
            flag = 2
            print("快照失败")

        print(info)
        conn.close()
        return HttpResponse(json.dumps({"st": flag}), content_type="application/json")



def snapshot_manage(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            snapshots=snapshot.objects.filter(is_exist=True).order_by('-start_time')
            return render(request, 'admins/snapshot_manage.html', {'snapshots': snapshots})

def snapshot_delete(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            domName=request.POST.get("vm_name")
            snapshotname=request.POST.get("snapshot_name")
            vmobject = vm.objects.get(name=domName)
            serverip = vmobject.belong.ip
            serverport = vmobject.belong.ssh_port
            serveruser = vmobject.belong.user
            hostname = vmobject.belong.host_name
            # 链接服务器
            conn, pool = libvirtConn(hostname, str(serverip), str(serverport), serveruser)
            if conn == None:
                print('Failed to open connection to qemu:///system', file=sys.stderr)
            dom = conn.lookupByName(domName)
            if dom == None:
                print('Failed to find the domain ' + domName, file=sys.stderr)
            try:
                snapshotObject=dom.snapshotLookupByName(snapshotname)
                snapshotObject.delete(0)
                s=snapshot.objects.get(snapshotName=snapshotname,is_exist=True)
                s.is_exist=False
                s.save()
                flag=1
            except:
                flag=2
                print("delete fail")
            conn.close()
            return  HttpResponse(json.dumps({"st": flag}), content_type="application/json")

def add_members(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            group_id = request.POST.get('group_id')
            user_id = request.POST.get('members_id')
            try:
                user = UserProfile.objects.get(id=user_id)
            except:
                return HttpResponse(json.dumps({
                    "st": 0
                }), content_type="application/json")
            user.group_type = group_id
            user.save()
            return HttpResponse(json.dumps({
                "st": 1
            }), content_type="application/json")

def group_users(request, pindex):
    global group_id_id
    if request.user.is_authenticated and request.user.is_superuser:
        if request.method == "POST":
            group_id = request.POST.get('group_id')
            group_id_id = group_id
            return HttpResponse(json.dumps({'st': 1}), content_type="application/json")
        else:
            users = UserProfile.objects.filter(group_type=group_id_id).order_by('-date_joined')
            print(users)
            paginator = Paginator(users, 10)
            page = paginator.page(pindex)
            if paginator.num_pages <= 5:
                display_list = paginator.page_range
            else:
                if page.number <= 3:
                    display_list = [1,2,3,4,5]
                elif paginator.num_pages-page.number <= 2:
                    display_list = paginator.page_range[paginator.num_pages-5:paginator.num_pages+1:1]
                else:
                    display_list = [page.number-2,page.number-1,page.number,page.number+1,page.number+2]
            return render(request, 'admins/group_users.html', {'users':page,
                                                            'dist': paginator.num_pages-page.number,
                                                            'display_list': display_list})

def cascade_communicate():
    '''
    test if able to communicate with the cascade server which want to cascade
    :return: null
    '''
    while True:
        other_cascade_ip = cascade_list.objects.filter(is_self=False)
        for ip_ in other_cascade_ip:
            back_info = os.system('ping -c 1 -w 1 ' + str(ip_.ip) + ' > /dev/null')
            if back_info != 0:
                ip_.is_ping = False
            else:
                ip_.is_ping = True
            ip_.save()
#        cascade_count = cascade_list.objects.filter(is_communicate=True).count()
#        if cascade_count >= 2:
#            cascade_master = cascade_list.objects.filter(is_communicate=True).first()
#            cascade_master.is_master = True
#            cascade_master.save()
#            cascade_slave = cascade_list.objects.exclude(id=cascade_master.id)
#            for cascade_slave_ in cascade_slave:
#                cascade_slave_.is_master = False
#                cascade_slave_.save()
#        else:
#            cascade_master = cascade_list.objects.filter(is_master=True)
#           for cascade_master_ in cascade_master:
#                cascade_master_.is_master = False
#                cascade_master_.save()
        sleep(1)

def cascade_communicate_thread():
    '''
    the thread of the cascade_communicate
    :return: null
    '''
    cascade_thread = threading.Thread(target=cascade_communicate)
    cascade_thread.start()

def find_vm_by_ip(request):
    ip = request.POST.get('vm_ip')
    try:
        vm.objects.get(ip=ip)
    except:
        return HttpResponse('False')
    else:
        return HttpResponse('True')

def find_vm_by_domain_ip(request):
    domain_ip = request.POST.get('domain_ip')
    find_domains = domain.objects.filter(gw_ip=domain_ip)
    if find_domains:
        return HttpResponse('True')
    else:
        return HttpResponse('False')

@decorate_get_domain_by_ip
def get_domain_by_ip(request):
    domain_list = domain.objects.all()
    os_list = vm_os.objects.all()
    docker_os = docker_img.objects.all()
    res_list_domain = []
    res_list_os = []
    res_list_docker_os = []
    for domain_ in domain_list:
        res_dict = {}
        res_dict['id'] = domain_.id
        res_dict['domain'] = domain_.domain
        res_list_domain.append(res_dict)
    for os_ in os_list:
        res_dict = {}
        res_dict['id'] = os_.id
        res_dict['os_version'] = os_.os_version
        res_list_os.append(res_dict)
    for docker_os_ in docker_os:
        res_dict = {}
        res_dict['id'] = docker_os_.id
        res_dict['img_name'] = docker_os_.img_name
        res_list_docker_os.append(res_dict)
    return HttpResponse(str({
        'domain': res_list_domain,
        'os': res_list_os,
        'docker_os': res_list_docker_os,
    }))

@decorate_get_node_by_name
def get_node_by_name(request):
    domain_name = request.POST.get('domain_name')
    find_domain = domain.objects.get(domain=domain_name)
    node_list = docker_node.objects.filter(belong=find_domain)
    res_list = []
    for node_ in node_list:
        res_dict = {}
        res_dict['host_name'] = node_.host_name
        res_dict['id'] = node_.id
        res_list.append(res_dict)
    return HttpResponse(str(res_list))

@decorate_node_apply
def node_apply(request, data=None, server_list=None, domain_list=None):
    if request.user.is_authenticated and request.user.is_superuser:
        apply_nodes = apply_node.objects.filter(state=0)
        print(domain_list)
        res_list = []
        for apply_node_ in apply_nodes:
            res_dict = {}
            res_dict['host_name'] = apply_node_.host_name
            res_dict['ip'] = apply_node_.ip
            res_dict['ssh_port'] = apply_node_.ssh_port
            res_dict['user'] = apply_node_.user
            res_dict['pwd'] = apply_node_.pwd
            res_dict['home_dir'] = apply_node_.home_dir
            res_dict['deploy_time'] = apply_node_.deploy_time.strftime('%Y-%m-%d %H:%M:%S')
            res_list.append(res_dict)
        print(res_list)
        if data:
            res_list += data
        print(res_list)
        return render(request, 'admins/node_apply.html', {
            "apply_nodes": res_list,
            "domains": domain_list,
            "server_list": server_list,
        })

def node_apply_request(request):
    apply_nodes = apply_node.objects.filter(state=0)
    res_list = []
    for apply_node_ in apply_nodes:
        res_dict = {}
        res_dict['host_name'] = apply_node_.host_name
        res_dict['ip'] = apply_node_.ip
        res_dict['ssh_port'] = apply_node_.ssh_port
        res_dict['user'] = apply_node_.user
        res_dict['pwd'] = apply_node_.pwd
        res_dict['home_dir'] = apply_node_.home_dir
        res_dict['deploy_time'] = apply_node_.deploy_time.strftime('%Y-%m-%d %H:%M:%S')
        res_list.append(res_dict)
    return HttpResponse(str(res_list))

@decorate_agree_zabbix_node
def agree_zabbix_node(request):
    #if request.user.is_authenticated and request.user.is_superuser:
    if True:
        if request.method == "POST":
            ip = request.POST.get('ip')
            ssh_port = request.POST.get('ssh')
            user = request.POST.get('user')
            pwd = request.POST.get('pwd')
            home_dir = request.POST.get('home_dir')
            domain_name = request.POST.get('domain')
            node_type = request.POST.get('node_type')
            find_domain = domain.objects.get(domain=domain_name)
            if ssh_Auth(ip, ssh_port, user, pwd, home_dir) == True:
                if node_type == "workstation":
                    workstation.objects.create(host_name=ip, ip=ip, ssh_port=ssh_port,
                                               user=user, pwd=pwd, belong=find_domain,
                                               home_dir=home_dir, is_zabbix=True)
                else:
                    docker_node.objects.create(host_name=ip, ip=ip, ssh_port=ssh_port,
                                               user=user, pwd=pwd, belong=find_domain,
                                               home_dir=home_dir, is_zabbix=True)
                apply_node_result = apply_node.objects.get(ip=ip)
                apply_node_result.state = 1
                apply_node_result.save()
                return HttpResponse(json.dumps({"st": 1}), content_type="application/json")
            else:
                return HttpResponse(json.dumps({"st": 0}), content_type="application/json")

def apply_reload(request):
    if request.user.is_authenticated and request.user.is_superuser:
        if request.method == "POST":
            node_ip = request.POST.get('node_ip')
            find_node = apply_node.objects.get(ip=node_ip)
            find_node.delete()
            return HttpResponse(json.dumps({"st": 1}), content_type="application/json")
        else:
            return HttpResponse(json.dumps({"st": 0}), content_type="application/json")

def recv_info():
    '''
    used to recv the information from the client
    :return:
    '''
    host = '192.168.47.255'
    port = 10000
    # broadcast_ip = '172.18.20.255'
    s_recv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s_recv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s_recv.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s_recv.bind((host, port))
    while True:
        sock, addr = s_recv.recvfrom(8192)
        if sock.decode().strip(b'\x00'.decode()) == 'nss send':
            s_recv.sendto('receive jinx 1'.encode(), (addr[0], 10000))
            node_join(addr[0])

def recv_thread():
    '''
    used to start the thread to run the recv_info function and the test_pi function
    :return:
    '''
    com_thread = threading.Thread(target=recv_info)
    com_thread.start()
    test_pi_thread = threading.Thread(target=test_pi)
    test_pi_thread.start()

def node_join(ip_addr):
    url = 'http://127.0.0.1/zabbix/api_jsonrpc.php'
    za = Zabbix(url, 'Admin', 'zabbix')
    host = za.hostid_get(ip_addr)
    if host:
        hostid = host[0]['hostid']
        za.make_host_available(hostid)
    else:
        za.create_host(ip_addr, ip_addr)

def ping_host(ip):
    back_info = os.system('ping -c 1 -w 1 '+ip + ' > /dev/null')
    url = 'http://127.0.0.1/zabbix/api_jsonrpc.php'
    za = Zabbix(url, 'Admin', 'zabbix')
    if back_info != 0:
        hostid = za.hostid_get(ip)[0]["hostid"]
        za.make_host_no_available(hostid)

def test_pi():
    while True:
        workstations = workstation.objects.all()
        docker_nodes = docker_node.objects.all()
        apply_nodes = apply_node.objects.filter(state=0)
        for workstation_ in workstations:
            if workstation_.host_name == 'Zabbix server':
                continue
            ping_host(workstation_.ip)
        for docker_node_ in docker_nodes:
            ping_host(docker_node_.ip)
        for apply_node_ in apply_nodes:
            ping_host(apply_node_.ip)
        sleep(1)

def cascade_apply(request):
    if request.user.is_authenticated and request.user.is_superuser:
        apply_list = cascade_list.objects.filter(is_ping=True, is_communicate=False)
        return render(request, 'admins/cascade_apply.html', {
            'cascade_list': apply_list,
        })

def agree_cascade(request):
    if request.user.is_authenticated and request.user.is_superuser:
        if request.method == "POST":
            ip = request.POST.get('ip')
            apply_node = cascade_list.objects.get(ip=ip)
            apply_node.is_communicate = True
            apply_node.save()
            return HttpResponse(json.dumps({"st": 1}), content_type="application/json")
        else:
            return HttpResponse(json.dumps({"st": 2}), content_type="application/json")

def quit_cascade(request):
    if request.method == 'POST':
        ip = request.POST.get('ip')
        print(request.POST)
        apply_node = cascade_list.objects.get(ip=ip)
        apply_node.is_communicate = False
        apply_node.save()
        return HttpResponse(json.dumps({"st": 1}), content_type="application/json")
    else:
        return HttpResponse(json.dumps({"st": 2}), content_type="application/json")


def Allocation_init():
    global docker_lock 
    docker_lock = threading.Lock()
    # 启动动态调度的定时任务，此处10分钟执行一次
    threading.Timer(600, DynamicDockerAllocation, ()).start()