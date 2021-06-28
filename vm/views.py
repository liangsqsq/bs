import json

from django.db.models import Count
from django.shortcuts import render
from django.http import HttpResponse

from admins.decorate import decorate_virtualhost, decorate_apply
from container.models import *
from users.models import UserProfile
from .models import *
from admins.customVM import shutdownVM, startVM
# Create your views here.

@decorate_virtualhost
def virtualhost(request, server_list=None):
    if request.user.is_authenticated:
        domains = domain.objects.all().order_by("id")
        OSs = vm_os.objects.all().order_by(("id"))

        user = UserProfile.objects.get(username=request.user.username)
        if user.is_superuser:
            new_vm_apply_count = new_vm_apply.objects.filter(state=0).aggregate(Count('state'))['state__count']
            vm_deploy_apply_count = deploy_apply.objects.filter(state=0).aggregate(Count('state'))['state__count']
            vm_port_apply_count = port_apply.objects.filter(state=0).aggregate(Count('state'))['state__count']
            new_container_apply_count = new_docker_apply.objects.filter(state=0).aggregate(Count('state'))[
                'state__count']
            return render(request, "vm/virtualhost.html", {
                'user': user,
                'domain_list': domains,
                'os_list': OSs,
                'new_vm_apply_count': int(new_vm_apply_count),
                'vm_deploy_apply_count': int(vm_deploy_apply_count),
                'vm_port_apply_count': int(vm_port_apply_count),
                'new_container_apply_count': int(new_container_apply_count),
                'count': int(new_vm_apply_count)+int(vm_deploy_apply_count)+int(vm_port_apply_count)+int(new_container_apply_count),
                'server_list': server_list,
            })
        else:
            apply_vm_count = new_vm_apply.objects.filter(user=user).aggregate(Count('state'))['state__count']
            apply_deport_count = deploy_apply.objects.filter(user=user).aggregate(Count('state'))['state__count']
            apply_port_count = port_apply.objects.filter(user=user).aggregate(Count('state'))['state__count']
            apply_container_count = container.objects.filter(user=user, state=0, is_del=0).aggregate(Count('state'))[
                'state__count']
            return render(request, "vm/virtualhost.html", {
                'user': user,
                'domain_list': domains,
                'os_list': OSs,
                'apply_vm_count': int(apply_vm_count),
                'apply_deport_count': int(apply_deport_count),
                'apply_port_count': int(apply_port_count),
                'apply_container_count': int(apply_container_count),
                'count': int(apply_vm_count)+int(apply_deport_count)+int(apply_port_count)+int(apply_container_count),
                'server_list': server_list,
            })
    else:
        return render(request, "index.html")


# 用户申请虚拟机
@decorate_apply
def apply_vm(request):
    if request.method == "POST":
        # if request.user.is_authenticated:
        try:
            User = UserProfile.objects.get(username=request.user.username)
        except:
            username = request.POST.get('username')
            User = UserProfile.objects.get(username=username)
        if request.user.is_authenticated:
            User = UserProfile.objects.get(username=request.user.username)
        # 获取创建虚拟机所需信息
        vm_region = request.POST.get('vm_region')
        vm_type = request.POST.get('vm_type')
        password = request.POST.get('password')
        disk = request.POST.get('disk')
        memory = request.POST.get('memory')
        cpu = request.POST.get('cpu')
        vm_isPersistent = request.POST.get('usetime')
        installway = request.POST.get('installway')
        classes = int(request.POST.get("selected_class"))
        model = int(request.POST.get("selected_classNum"))

        print(vm_region, vm_type, password, disk, memory, cpu, vm_isPersistent, installway,classes, model)

        mydomain = domain.objects.get(id=int(vm_region))
        myvm_os = vm_os.objects.get(os_version=vm_type)

        gw_ip = mydomain.gw_ip
        my_vm_apply = new_vm_apply.objects.create(user=User, gateway_ip=gw_ip, os_version=myvm_os,
                                                  cpu_cores=int(cpu), memory=int(memory), disk=int(disk),
                                                  password=password, region=mydomain, isPersistent=vm_isPersistent,
                                                  installway=installway, classes=classes, model=model)
        my_vm_apply.save()
        st = 1

    else:
        st = 2

    return HttpResponse(json.dumps({"st": st}), content_type="application/json")


def start_vm(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            vm_name = request.POST.get('vm_name')
            print(vm_name)
            VM = vm.objects.get(name=vm_name)
            server = VM.belong

            flag = startVM(vm_name, server)
            if flag != True:
                return HttpResponse(json.dumps({"st": flag}), content_type="application/json")

            VM.power_state = 'running'
            VM.save()
            return HttpResponse(json.dumps({"st": flag}), content_type="application/json")


def shutdown_vm(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            vm_name = request.POST.get('vm_name')
            print(vm_name)
            VM = vm.objects.get(name=vm_name)
            server = VM.belong

            flag = shutdownVM(vm_name, server)
            if flag != True:
                print("flag = " + flag)
                return HttpResponse(json.dumps({"st": flag}), content_type="application/json")

            VM.power_state = 'shutoff'
            VM.save()
            return HttpResponse(json.dumps({"st": flag}), content_type="application/json")
