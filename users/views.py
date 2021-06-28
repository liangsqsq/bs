import sys

from configobj import ConfigObj
from django.contrib.auth import authenticate, login, logout
import json
import time

import libvirt
import paramiko
from django.core.paginator import Paginator
from django.db.models import Count
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from container.models import *
from admins.customVM import getMacFromIp, getMacFromName, getVMIp, libvirtConn
from admins.getVMInfo import getVMInfo
from admins.sshConnection import connection_SSH
from utils.email_send import send_register_email
from vm.models import *
from .forms import LoginForm, RegisterForm
from .models import group, EmailVerifyRecord
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.shortcuts import redirect
from django.urls import reverse
import uuid
import json

# Create your views here.
config = ConfigObj("config.ini", encoding='UTF8')

LOGIN_FAILURE = 0
LOGIN_SUCCESS = 1
LOGIN_LOCK = 2


def index(request):
    if request.user.is_authenticated:
        user = UserProfile.objects.get(username=request.user.username)
        print("login : " + request.user.username)
        # print(user.is_superuser,type(user.is_superuser))
        if user.is_superuser:
            new_vm_apply_count = new_vm_apply.objects.filter(state=0).aggregate(Count('state'))['state__count']
            vm_deploy_apply_count = deploy_apply.objects.filter(state=0).aggregate(Count('state'))['state__count']
            vm_port_apply_count = port_apply.objects.filter(state=0).aggregate(Count('state'))['state__count']
            new_container_apply_count = new_docker_apply.objects.filter(state=0).aggregate(Count('state'))[
                'state__count']
            # print(new_vm_apply_count,vm_deploy_apply_count,vm_port_apply_count)
            return render(request, "overview.html", {'user': user,
                                                  'new_vm_apply_count': int(new_vm_apply_count),
                                                  'vm_deploy_apply_count': int(vm_deploy_apply_count),
                                                  'vm_port_apply_count': int(vm_port_apply_count),
                                                  'new_container_apply_count': int(new_container_apply_count),
                                                  'count': int(new_vm_apply_count) + int(vm_deploy_apply_count) + int(
                                                      vm_port_apply_count) + int(new_container_apply_count)})
        else:
            apply_vm_count = new_vm_apply.objects.filter(user=user).aggregate(Count('state'))['state__count']
            apply_deport_count = deploy_apply.objects.filter(user=user).aggregate(Count('state'))['state__count']
            apply_port_count = port_apply.objects.filter(user=user).aggregate(Count('state'))['state__count']
            apply_container_count = container.objects.filter(user=user,state=0,is_del=0).aggregate(Count('state'))[
                'state__count']
            print(apply_container_count)
            return render(request, "overview.html", {'user': user,
                                                  'apply_vm_count': int(apply_vm_count),
                                                  'apply_deport_count': int(apply_deport_count),
                                                  'apply_port_count': int(apply_port_count),
                                                  'apply_container_count': int(apply_container_count),
                                                  'count': int(apply_vm_count) + int(apply_deport_count) + int(
                                                      apply_port_count) + int(apply_container_count)})
    else:
        return render(request, 'overview.html')


def useremail(request):
    if request.method == "POST":
        email = request.POST.get('email')
        send_register_email(email, "register")
        all_records = EmailVerifyRecord.objects.filter(email=email).last()
        print(all_records)
        if all_records.code:
            st = 1
        return HttpResponse(json.dumps({"st": st}), content_type="application/json")


def loginv(request):
    if request.method == "POST":
        login_form = LoginForm(request.POST)
        if login_form.is_valid:
            user_name = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(username=user_name, password=password)
            print(user_name, password, user)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    print('login success')
                    st = LOGIN_SUCCESS
                else:
                    print('user is locked')
                    st = LOGIN_LOCK
            else:
                st = LOGIN_FAILURE
            return HttpResponse(json.dumps({"st": st}), content_type="application/json")

    return render(request, "users/login.html")


def register(request):
    if request.method == "POST":
        register_form = RegisterForm(request.POST)
        if register_form.is_valid:
            username = request.POST.get('username')
            realname = request.POST.get('realname')
            email = request.POST.get('email')
            password = request.POST.get('password')
            emailcode = request.POST.get('emailcode')
            records = EmailVerifyRecord.objects.filter(code=emailcode).last()
            if records:
                UserProfile.objects.create_user(username=username, email=email, password=password, is_active=True,
                                                realname=realname)
                st = 1
                print('register success')
                # 创建owncloud账户

                return HttpResponse(json.dumps({"st": st}), content_type="application/json")
            else:
                st = 0
                return HttpResponse(json.dumps({"st": st}), content_type="application/json")
    else:
        st = 2
        return render(request, 'users/registe.html', {"st": st})


def logoutv(request):
    logout(request)
    return render(request, "index.html")


def is_user_exist(request):
    # GET方法获取表单
    if request.method == "GET":
        user_rec = request.GET.get('fieldId')
        user_name = request.GET.get('fieldValue')
        filterResult = UserProfile.objects.filter(username=user_name)
        result = [0, 0, 0]
        result[0] = user_rec
        # 用户名存在
        if len(filterResult) > 0:
            result[1] = False
            print(result)
            result = json.dumps(result)
            return HttpResponse(result, content_type="application/json")
        else:
            # 用户名不存在
            result[1] = True
            print(result)
            result = json.dumps(result)
            return HttpResponse(result, content_type="application/json")
    else:
        result = [0, 0, 0]
        result[1] = False
        result = json.dumps(result)
        return HttpResponse(result, content_type="application/json")
        # uf = UserForm()
        # return render_to_response("registe.html", {'uf': uf})


def user_control(request):
    if request.user.is_authenticated:
        user = UserProfile.objects.get(username=request.user.username)
        # user = UserProfile.objects.filter(username=request.user.username)[0]
        vms = vm.objects.filter(user=user, is_del='0')

        return render(request, 'users/usercontrol.html', {'vm_list': vms})
    else:
        return render(request, 'index.html')


def vmcheck(request):
    if request.user.is_authenticated:
        user = UserProfile.objects.get(username=request.user.username)
        vminfo = new_vm_apply.objects.filter(user=user).order_by('-apply_time')
        return render(request, 'users/vmcheck.html', {'vminfo': vminfo})


def portRecords(request):
    if request.user.is_authenticated:
        user = UserProfile.objects.get(username=request.user.username)
        port_applys = port_apply.objects.filter(user=user).order_by('-apply_time')
        return render(request, 'users/portRecords.html', {'portList': port_applys})


def configurationRecords(request):
    if request.user.is_authenticated:
        user = UserProfile.objects.get(username=request.user.username)
        deploy_applys = deploy_apply.objects.filter(user=user).order_by('-apply_time')
        return render(request, 'users/configurationRecords.html', {'con_list': deploy_applys})


def show_vnc(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            vm_name = request.POST.get('vm_name')
            # vm_gwip = request.POST.get('vmname2')
            print('vm name :' + vm_name)
            vm_hostip = vm.objects.get(name=vm_name).belong.ip
            print('vm host ip :' + vm_hostip)
            HOST_PORT = config['novnc']['host_port']
            WEBSOCKIFY_PORT = config['novnc']['websockify_port']

            index = 'http://' + vm_hostip + ':' + HOST_PORT + '/vnc_lite.html?host=' + vm_hostip + '&port=' + WEBSOCKIFY_PORT + \
                    '&path=websockify/?token=' + vm_name
            print('index:' + index)
            st = 1
            return HttpResponse(json.dumps({"st": st, "index": index}), content_type="application/json")
        else:
            st = 2
            return HttpResponse(json.dumps({"st": st}), content_type="application/json")


def applydeploy(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            vm_name = request.POST.get('VMNAME')
            memory = request.POST.get('MEMORY')
            cpus = request.POST.get('CPU')
            diskSize = request.POST.get('DISK')

            user = UserProfile.objects.get(username=request.user.username)
            vms = vm.objects.filter(user=user, is_del='0')

            print(memory, cpus, diskSize, vm_name, user)
            for apply_vm in vms:
                if vm_name == apply_vm.name:
                    deploy = deploy_apply.objects.create(vm=apply_vm, vCPUs=int(cpus), memory=int(memory),
                                                         diskSize=int(diskSize), user=user)
                    deploy.save()

                    message = "申请成功，等待管理员审核"
                    return render(request, "users/usercontrol.html", {"message": message, 'vm_list': vms})
            message = "找不到此虚拟机!"
            return render(request, "users/usercontrol.html", {"message": message, 'vm_list': vms})


def applyport(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            vm_name = request.POST.get('VMNAME')
            port = request.POST.get('PORT')
            print(vm_name, port)

            user = UserProfile.objects.get(username=request.user.username)
            vms = vm.objects.filter(user=user, is_del='0')

            for apply_vm in vms:
                if vm_name == apply_vm.name:
                    portApply = port_apply.objects.create(vm=apply_vm, vmPort=int(port), user=user)
                    portApply.save()

                    message = "端口申请成功，等待管理员审核"
                    return render(request, "users/usercontrol.html", {"message": message, 'vm_list': vms})
            message = "找不到此虚拟机!"
            return render(request, "users/usercontrol.html", {"message": message, 'vm_list': vms})


def user_info(request):
    if request.user.is_authenticated:
        user = UserProfile.objects.filter(username=request.user.username)[0]
        data = {}
        data['username'] = user.username
        data['realname'] = user.realname
        grouptype = group.objects.get(id=user.group_type)
        data['group'] = grouptype.gname

        data['regtime'] = user.date_joined
        data['logtime'] = user.last_login
        data['email'] = user.email
        return render(request, 'users/userInfo.html', {'data': data})


def updateUserInfo(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            username = request.user.username
            new_username = request.POST.get('username')
            old_password = request.POST.get('old-password')
            new_password = request.POST.get('password')
            new_email = request.POST.get('email')
            print(new_username, new_email)

            if not (new_username or new_email):
                return HttpResponse(json.dumps({"st": 2}), content_type="application/json")
            user = UserProfile.objects.filter(username=username)[0]
            if new_username:
                user.username = new_username
                username = new_username
            if new_email:
                user.email = new_email
            user.save()
            user = UserProfile.objects.filter(username=username)[0]
            data = {}
            data['username'] = user.username
            data['email'] = user.email
            return HttpResponse(json.dumps({"st": 1}), content_type="application/json")


def forget(request):
    return render(request, 'users/forget.html')


def forgetemail(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        token = str(uuid.uuid4()).replace('-', '')
        # 发送邮件
        request.session[token] = username
        print(token)
        print(request.session.get(token))
        service_ip = config['host']['ip']
        service_port = config['host']['port']
        path = 'http://' + service_ip + ':' + service_port + '/users/changepwd?token={}'.format(token)  # 链接域名需要改
        subject = '邮箱验证'
        message = '''
        验证成功，点击<a href='{}'>重置密码</a>
        <br>如链接不可用，复制以下内容至浏览器进行重置：
        {}
        <br>
        <br>
        <br>DragonStack开发团队
            '''.format(path, path)
        st = send_mail(subject=subject, message="", from_email=settings.EMAIL_HOST_USER,
                       recipient_list=[email], html_message=message)
    return HttpResponse(json.dumps({"st": st}), content_type="application/json")


def changepwd(request):
    token = request.GET.get('token')
    username = request.session.get(token)
    return render(request, 'users/changepwd.html', {'username': username})


def change(request):
    if request.method == "POST":
        password = request.POST.get('password')
        username = request.POST.get('username')
        print(password)
        print(username)
        user = UserProfile.objects.filter(username=username)[0]
        print(user)
        pwd = make_password(password)
        user.password = pwd
        print(user.password)
        user.save()
        print(user, user.username, user.password)
        st = 1
        return HttpResponse(json.dumps({"st": st}), content_type="application/json")
    else:
        st = 0
        return HttpResponse(json.dumps({"st": st}), content_type="application/jsongit ")


def importvm1(request):
    # 0代表失败，1代表成功，2代表导入对象已被认领
    if request.user.is_authenticated:
        if request.method == "POST":
            request_data = request.body
            request_dict = json.loads(request_data.decode('utf-8'))
            vmip = request_dict.get("vmip")
            try:
                findvm = vm.objects.get(ip=vmip, is_del=0)
                return JsonResponse({"state": 2})
            except:
                port = request_dict.get("port")
                username = request_dict.get("username")
                password = request_dict.get("password")
                gwip = request_dict.get("gwip")
                user = UserProfile.objects.get(username=request.user.username)
                print("---------------connect to vm ----------------")
                isConn = connection_SSH(vmip, int(port), username, password)
                if isConn:
                    print("-----------ssh connection success------------")
                    try:
                        findDomain = domain.objects.get(gw_ip=gwip)
                    except:
                        return JsonResponse({"state": 0})
                    mac_addr = getMacFromIp(findDomain, vmip)
                    if mac_addr == 0:
                        return JsonResponse({"state": 0})
                    workstations = workstation.objects.filter(belong=findDomain)
                    for workstation_find in workstations:
                        w_user = workstation_find.user
                        w_gwip = workstation_find.ip
                        w_port = workstation_find.ssh_port
                        conn = libvirt.open("qemu+ssh://" + w_user + "@" + w_gwip + ":" + str(w_port) + "/system")
                        if conn == None:
                            print('libvirt connect false' + workstation_find.host_name)
                            continue
                        else:
                            storagePool = conn.storagePoolLookupByName('default')
                            print('libvirt connect success' + workstation_find.host_name)
                            activeVMs = conn.listDomainsID()
                            for activeVM in activeVMs:
                                w_vm = conn.lookupByID(activeVM)
                                vm_mem = (int(int(w_vm.info()[2]) / 1024 / 1024))
                                vm_name = w_vm.name()
                                find_mac = getMacFromName(workstation_find, vm_name)
                                if find_mac == mac_addr:
                                    try:
                                        findOS = vm_os.objects.get(os_version="unknown", default_user=username)
                                    except:
                                        findOS = vm_os.objects.create(os_version="unknown", default_user=username)
                                        findOS.save()
                                    isActive, isPersistent, cpus, maxmem, diskSize, diskAllocation, format_type = getVMInfo(
                                        w_vm, storagePool)
                                    new_vm = vm.objects.create(name=vm_name,
                                                               vCPUs=cpus, memory=vm_mem,
                                                               diskSize=diskSize,
                                                               diskType=format_type,
                                                               os_version=findOS.os_version, os=findOS,
                                                               ip=vmip, password=password,
                                                               belong=workstation_find,
                                                               gateway_ip=findDomain.gw_ip,
                                                               region=findDomain,
                                                               user=user, conn_port=port,
                                                               isPersistent=isPersistent,
                                                               power_state="running",
                                                               state=isActive, is_del=0)
                                    new_vm.save()
                                    return JsonResponse({"state": 1})
                    return JsonResponse({"state": 0})
                else:
                    print("-----------ssh connection false------------")
                    return JsonResponse({"state": 0})


def importvm(request):
    # 0代表失败，1代表成功，2代表导入对象已被认领
    if request.user.is_authenticated:
        if request.method == "POST":
            request_data = request.body
            request_dict = json.loads(request_data.decode('utf-8'))
            vmip = request_dict.get("vmip")
            try:
                findvm = vm.objects.get(ip=vmip, is_del=0)
                return JsonResponse({"state": 2})
            except:
                port = request_dict.get("port")
                username = request_dict.get("username")
                password = request_dict.get("password")
                user = UserProfile.objects.get(username=request.user.username)
                print("---------------connect to vm ----------------")
                isConn = connection_SSH(vmip, int(port), username, password)
                if isConn:
                    print("-----------ssh connection success------------")
                    try:  # create a unkown domain
                        findDomain = domain.objects.get(domain="unknown")
                    except:
                        findDomain = domain.objects.create(domain="unknown",
                                                           location="unknown",
                                                           gw_ip="unknown",
                                                           port=0,
                                                           state=1,
                                                           vt_type="unknown")
                        findDomain.save()
                    try:  # create a unkonwn workstation
                        findWorkstation = workstation.objects.get(host_name="unknown")
                    except:
                        findWorkstation = workstation.objects.create(host_name="unknown",
                                                                     ip="unknown",
                                                                     ssh_port=0,
                                                                     belong=findDomain)
                    try:  # create a unkonwn vm os
                        findOS = vm_os.objects.get(os_version="unknown", default_user=username)
                    except:
                        findOS = vm_os.objects.create(os_version="unknown", default_user=username)
                        findOS.save()
                    new_vm = vm.objects.create(
                        vCPUs=0, memory=0,
                        diskSize=0,
                        diskType="unknown",
                        os_version=findOS.os_version, os=findOS,
                        password=password,
                        belong=findWorkstation,
                        gateway_ip=vmip,
                        region=findDomain,
                        user=user, conn_port=port,
                        isPersistent=1,
                        power_state="running",
                        state=1, is_del=0)
                    new_vm.save()
                    return JsonResponse({"state": 1})
                else:
                    print("-----------ssh connection false------------")
                    return JsonResponse({"state": 0})


def regetVMIP(request):
    if request.user.is_authenticated:
        user = UserProfile.objects.get(username=request.user.username)
        vms = vm.objects.filter(user=user, is_del='0')
        # conn, pool = libvirtConn(server.host_name, server.ip, str(server.ssh_port), server.user)
        if vms:
            # conn = libvirt.open("qemu+ssh://" + server.user + "@" + server.ip + ":" + str(server.ssh_port) + "/system")
            for vminfo in vms:
                conn = libvirt.open(
                    "qemu+ssh://" + vminfo.belong.user + "@" + vminfo.belong.ip + ":" + str(
                        vminfo.belong.ssh_port) + "/system")
                dom = conn.lookupByName(vminfo.name)
                ip = getVMIp(dom)
                print(ip)
                vminfo.ip = ip
                vminfo.save()
        vms = vm.objects.filter(user=user, is_del='0')
        return render(request, "users/usercontrol.html", {'vm_list': vms})


def snapshotlist(request):
    if request.user.is_authenticated:
        user = UserProfile.objects.get(username=request.user.username)
        snapshots = snapshot.objects.filter(username=user, is_exist=True)
        return render(request, 'users/snapshotlist.html', {'snapshots': snapshots})


def snapshotRevert(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            domName = request.POST.get("vm_name")
            snapshotname = request.POST.get("snapshot_name")
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
                info = dom.snapshotLookupByName(snapshotname)
                Flag = dom.revertToSnapshot(info)
                print(Flag)
                flag = 1
            except:
                print("snapshot revert failed")
                flag = 2
            return HttpResponse(json.dumps({"st": flag}), content_type="application/json")


def user_changePwd(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            old_pwd = request.POST.get('old_pwd')
            new_pwd = request.POST.get('new_pwd')
            user = UserProfile.objects.filter(username=request.user.username)[0]
            if user.check_password(old_pwd):
                user.set_password(new_pwd)
                user.save()
                return HttpResponse(json.dumps({"st": 1}), content_type="application/json")
            else:
                return HttpResponse(json.dumps({"st": 0}), content_type="application/json")


def container_list(request):
    if request.user.is_authenticated:
        user = UserProfile.objects.get(username=request.user.username)
        containerlist = container.objects.filter(is_del=0,user=user).order_by('-start_time')
        return render(request, 'users/container_list.html', {'containerlist': containerlist})

