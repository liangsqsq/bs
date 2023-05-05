import json

from django.core.paginator import Paginator
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
import docker

from admins.decorate import decorate_request_pindex, decorate_vm_recv, decorate_add_workstation, decorate_virtualhost, \
    decorate_apply
from admins.sshConnection import ssh_Auth
from container.customUtils import mount_file, mount_volume, setPort
from container.models import *
from res.models import transfer, model, classes
from res.zabbix_api import Zabbix
from users.models import UserProfile
from vm.models import domain, new_vm_apply, deploy_apply, port_apply, vm

@decorate_virtualhost
def dockerselect(request, server_list=None):
    if request.user.is_authenticated:
        domains = domain.objects.all().order_by("id")
        dockerimgs = docker_img.objects.all().order_by("id")
        # node_list = docker_node.objects.all().order_by("id")
        node_list = docker_node.objects.filter(belong=domains.first())
        user = UserProfile.objects.get(username=request.user.username)

        if user.is_superuser:
            new_vm_apply_count = new_vm_apply.objects.filter(state=0).aggregate(Count('state'))['state__count']
            vm_deploy_apply_count = deploy_apply.objects.filter(state=0).aggregate(Count('state'))['state__count']
            vm_port_apply_count = port_apply.objects.filter(state=0).aggregate(Count('state'))['state__count']
            new_container_apply_count = new_docker_apply.objects.filter(state=0).aggregate(Count('state'))[
                'state__count']
            return render(request, "container/dockerselect.html", {
                'user': user,
                'domain_list': domains,
                'img_list': dockerimgs,
                'node_list': node_list,
                'new_vm_apply_count': int(new_vm_apply_count),
                'vm_deploy_apply_count': int(vm_deploy_apply_count),
                'vm_port_apply_count': int(vm_port_apply_count),
                'new_container_apply_count': int(new_container_apply_count),
                'count': int(new_vm_apply_count) + int(vm_deploy_apply_count) + int(vm_port_apply_count)+
                         int(new_container_apply_count),
                'server_list': server_list,
            })
        else:
            apply_vm_count = new_vm_apply.objects.filter(user=user).aggregate(Count('state'))['state__count']
            apply_deport_count = deploy_apply.objects.filter(user=user).aggregate(Count('state'))['state__count']
            apply_port_count = port_apply.objects.filter(user=user).aggregate(Count('state'))['state__count']
            apply_container_count = container.objects.filter(user=user, state=0, is_del=0).aggregate(Count('state'))[
                'state__count']
            return render(request, "container/dockerselect.html", {
                'user': user,
                'domain_list': domains,
                'img_list': dockerimgs,
                'node_list': node_list,
                'apply_vm_count': int(apply_vm_count),
                'apply_deport_count': int(apply_deport_count),
                'apply_port_count': int(apply_port_count),
                'apply_container_count': int(apply_container_count),
                'count': int(apply_vm_count) + int(apply_deport_count) + int(apply_port_count)+int(apply_container_count),
                'server_list': server_list,
            })
    else:
        return render(request, "index.html")

@decorate_add_workstation
def add_dockerNode(request,server_list=None, domain_list=None, message=None):
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
                            return render(request, "container/add_dockerNode.html", {
                                "message": message,
                                'communication_list': server_list,
                                "domain_list": domain_list,
                            })
                else:
                    set_zabbix = False
                docker_node.objects.create(host_name=hostname, ip=IP, ssh_port=SSH_port, user=username, pwd=password,
                                           home_dir=homeDir, belong_id=domainID, is_zabbix=set_zabbix)
                message = "节点添加成功"
            else:
                message = "添加失败，请确认相关信息"
            # ret = domain.objects.all()
            return render(request, "container/add_dockerNode.html", {
                "message": message,
                'communication_list': server_list,
                "domain_list": domain_list,
            })
        # 取到所有的domain get请求中
        return render(request, "container/add_dockerNode.html", {
            'communication_list': server_list,
            "domain_list": domain_list,
        })

def add_dockerNode_request(request):
    hostname = request.POST.get("hostname")
    IP = request.POST.get("IP")
    SSH_port = request.POST.get("SSH")
    username = request.POST.get("username", None)
    password = request.POST.get("password", None)
    domainID = request.POST.get("domain")
    homeDir = request.POST.get("home")
    is_zabbix = request.POST.get("is_zabbix")

    if ssh_Auth(IP, SSH_port, username, password, homeDir) == True:
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
                set_zabbix = False
            docker_node.objects.create(host_name=hostname, ip=IP, ssh_port=SSH_port, user=username, pwd=password,
                                       home_dir=homeDir, belong_id=domainID, is_zabbix=set_zabbix)
            message = "节点添加成功"
        else:
            message = "添加失败，请确认相关信息"
    # ret = domain.objects.all()
    return HttpResponse(message)

@decorate_apply
def apply_docker(request):
    """
    用户申请容器
    """
    if request.method == "POST":
        # if request.user.is_authenticated:
        try:
            User = UserProfile.objects.get(username=request.user.username)
        except:
            username = request.POST.get('username')
            User = UserProfile.objects.get(username=username)
        # 获取创建容器所需信息
        docker_region = request.POST.get('docker_region')
        classes = int(request.POST.get("selected_class"))
        model = int(request.POST.get("selected_classNum"))
        img = request.POST.get('docker_img')
        img_version = docker_img.objects.get(img_name=img)
        memory = request.POST.get('memory')
        cpu = request.POST.get('cpu')
        node = request.POST.get('node')
        print(docker_region, memory, cpu)
        mydomain = domain.objects.get(id=int(docker_region))
        mynode = docker_node.objects.get(id=int(node))
        gw_ip = mydomain.gw_ip
        my_docker_apply = new_docker_apply.objects.create(username=User, gateway_ip=gw_ip, img_version=img_version,
                                                          cpu_cores=int(cpu), memory=float(memory), region_name=mydomain.domain,
                                                          domain_node=mynode.ip,classes=classes, model=model)
        st = 1

    else:
        st = 2

    return HttpResponse(json.dumps({"st": st}), content_type="application/json")

@decorate_add_workstation
def add_dockerImg(request, server_list=None, domain_list=None, message=None):
    if message:
        return render(request, "admins/add_img.html", {
            "message": message,
            'communication_list': server_list,
            "domain_list": domain_list,
        })
    if request.user.is_superuser == 1:
        if request.method == "POST":
            underSystem = request.POST.get("osVersion")
            img_name = request.POST.get("img_name")
            point = request.POST.get("mount_point")
            imgPort = request.POST.get("imgPort")
            imgDomain = request.POST.get("imgDomain")
            command=request.POST.get("imgCommand")
            tag = request.POST.get("tag_name")
            repository_name = request.POST.get("repository_name")

            docker_img.objects.create(img_name=img_name, mountPoint=point, underSystem=underSystem, port=imgPort,
                                      tag=tag, repository=repository_name,command=command)
            if True:
                message = "添加成功"
            else:
                message = "添加失败，请确认相关信息"
            # ret = domain.objects.all()
            return render(request, "container/add_dockerImg.html", {
                "message": message,
                'communication_list': server_list,
                "domain_list": domain_list,
            })
        # 取到所有的domain get请求中
        return render(request, "container/add_dockerImg.html", {
            'communication_list': server_list,
            "domain_list": domain_list,
        })

def add_dockerImg_request(request):
    underSystem = request.POST.get("osVersion")
    img_name = request.POST.get("img_name")
    point = request.POST.get("mount_point")
    imgPort = request.POST.get("imgPort")
    imgDomain = request.POST.get("imgDomain")
    command = request.POST.get("imgCommand")
    tag = request.POST.get("tag_name")
    repository_name = request.POST.get("repository_name")

    docker_img.objects.create(img_name=img_name, mountPoint=point, underSystem=underSystem, port=imgPort,
                              tag=tag, repository=repository_name, command=command)
    if True:
        message = "添加成功"
    else:
        message = "添加失败，请确认相关信息"
    # ret = domain.objects.all()
    return HttpResponse(message)

@decorate_request_pindex
def docker_verify(request, pindex, data=None):
    """容器审核"""
    if request.user.is_superuser == 1:
        badge_audit = new_docker_apply.objects.all().order_by("-apply_time")
        res_list = []
        for deploy in badge_audit:
            res_dist = {}
            res_dist['username'] = deploy.username.username
            res_dist['id'] = deploy.id
            res_dist['img_version'] = deploy.img_version.img_name
            res_dist['mount_point'] = deploy.img_version.mountPoint
            res_dist['memory'] = deploy.memory
            res_dist['cpu_cores'] = deploy.cpu_cores
            find_domain = domain.objects.get(domain=deploy.region_name)
            res_dist['region'] = find_domain.gw_ip
            node = docker_node.objects.get(ip=deploy.domain_node)
            res_dist['domain_node'] = node.host_name
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
                display_list = [1, 2, 3, 4, 5]
            elif paginator.num_pages - page.number <= 2:
                display_list = paginator.page_range[paginator.num_pages - 5:paginator.num_pages + 1:1]
            else:
                display_list = [page.number - 2, page.number - 1, page.number, page.number + 1, page.number + 2]
        return render(request, 'container/docker_verify.html', {'data': page,
                                                                'dist': paginator.num_pages - page.number,
                                                                'display_list': display_list})

def docker_verify_request(request):
    badge_audit = new_docker_apply.objects.all().order_by("-apply_time")
    res_list = []
    for deploy in badge_audit:
        res_dist = {}
        res_dist['username'] = deploy.username.username
        res_dist['id'] = deploy.id
        res_dist['img_version'] = deploy.img_version.img_name
        res_dist['mount_point'] = deploy.img_version.mountPoint
        res_dist['memory'] = deploy.memory
        res_dist['cpu_cores'] = deploy.cpu_cores
        find_domain = domain.objects.get(domain=deploy.region_name)
        res_dist['region'] = find_domain.gw_ip
        node = docker_node.objects.get(ip=deploy.domain_node)
        res_dist['domain_node'] = node.host_name
        res_dist['apply_time'] = deploy.apply_time.strftime('%Y-%m-%d %H:%M:%S')
        res_dist['state'] = deploy.state
        res_list.append(res_dist)

    return HttpResponse(str(res_list))

@decorate_vm_recv
def agree_docker(request):
    if request.method == "POST":
        docker_id = request.POST.get("apply_id")
        my_docker_apply = new_docker_apply.objects.get(id=docker_id)
        class_name = my_docker_apply.classes
        model_name = my_docker_apply.model
        user_name = my_docker_apply.username.username
        user = UserProfile.objects.get(username=user_name)
        # 获取分配资源所需要的容器信息
        apply_cpu = my_docker_apply.cpu_cores*256
        apply_mem = my_docker_apply.memory*1000
        apply_domain = domain.objects.get(domain=my_docker_apply.region_name)
        #apply_domain = my_docker_apply.regionID
        # 镜像对象
        img_ver = my_docker_apply.img_version
        print(img_ver)
        # node
        node=docker_node.objects.get(ip=my_docker_apply.domain_node)
        # 获取镜像信息
        img_info = my_docker_apply.img_version
        # 建立连接(demo)并获取镜像
        base_url = 'tcp://' + node.ip + ':2375'
        C = docker.DockerClient(base_url=base_url, version='auto', timeout=10)
        print(C)
        # 创建宿主机上的挂载目录文件(如果有)
        # if img_ver.mountPoint != "":
        #     # 使用容器卷方式
        #     dictory, string,list1= mount_volume(user, img_ver, node)
        #     print(dictory, string,list1)
        # else:
        #     dictory = None
        #     list1=None
        #     string=None
        # 端口映射字典
        # if img_ver.port != "":
        #     portlist = setPort(user, img_ver, node)
        #     print(portlist)
        # else:
        #     portlist = None
        # example
        # c2=C.containers.run('qindun:v1',detach=True,tty=True,stdin_open=True,name='ha3',command='/home/qindun/run',volumes = str,ports=portlist)
        # 运行容器
        command = img_ver.command
        images = img_ver.repository + ':' + img_ver.tag
        # my_docker_num = container.objects.filter(user=my_docker_apply.username).count() + 1
        # name1 = user_name + '_' + img_ver.img_name
        # name = str(my_docker_num) + name1
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
            name = str(vm_count+1)+"admin"
        else:
            name = str(container_count+1)+"admin"
        print(images, name)
        c2 = C.containers.run(images, detach=True, tty=True, stdin_open=True, name=name,
                              command=command, volumes={"/home/jar": {"bind": "/home/jar", "mode": "rw"}})
        print("hello")

        if c2:
            st=7
            agree_container = container.objects.create(Only_Id=c2.id,name=name, port="22", cpu_cores=apply_cpu,
                                                           memory=apply_mem,img=img_ver,volume_name="/home/jar",
                                                   mountPoint="/home/jar", node=node, region=apply_domain, user=user)
            agree_transfer = transfer.objects.create(resource_name=name,classes=class_name, model=model_name)
            agree_transfer.save()
            agree_model = model.objects.get(model_name=model_name)
            agree_model.number = agree_model.number+1
            agree_model.save()
            my_agree_classes = classes.objects.get(class_name=agree_transfer.classes)
            my_agree_classes.number = my_agree_classes.number + 1
            my_agree_classes.save()
            my_docker_apply.state = 1
            my_docker_apply.save()
            agree_container.save()
            agree_container.state = 0

            return HttpResponse(json.dumps({"st": 1}), content_type="application/json")
        else:
            return HttpResponse(json.dumps({"st": 2}), content_type="application/json")

@decorate_vm_recv
def refuse_docker(request):
    if request.method == "POST":
        docker_id = request.POST.get("apply_id")
        my_docker_apply = new_docker_apply.objects.get(id=docker_id)
        my_docker_apply.state=2
        my_docker_apply.save()
        st = 1
        return HttpResponse(json.dumps({"st": st}), content_type="application/json")
    else:
        return render(request, 'index.html')

@decorate_request_pindex
def container_manage(request, pindex, data=None):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            containerlist=container.objects.filter(is_del=0).order_by('-start_time')
            res_list = []
            for container_ in containerlist:
                res_dist = {}
                res_dist['username'] = container_.user.username
                res_dist['name'] = container_.name
                res_dist['img_name'] = container_.img.img_name
                res_dist['memory'] = container_.memory
                res_dist['cpu_cores'] = container_.cpu_cores
                if transfer.objects.get(resource_name=container_.name).classes == 1:
                    mountPoint = "无人机"
                elif transfer.objects.get(resource_name=container_.name).classes == 2:
                    mountPoint = "无人车"
                else:
                    mountPoint = "无人船"
                res_dist['mount_point'] = mountPoint
                res_dist['volume_name'] = str(transfer.objects.get(resource_name=container_.name).model)
                res_dist['node_ip'] = container_.node.ip
                res_dist['gw_ip'] = container_.region.gw_ip
                res_dist['domain'] = container_.region.domain
                res_dist['port'] = container_.port
                res_dist['is_del'] = container_.is_del
                res_dist['state'] = container_.state
                res_list.append(res_dist)
            if data:
                res_list += data
            paginator = Paginator(res_list, 10)
            page = paginator.page(pindex)
            if paginator.num_pages <= 5:
                display_list = paginator.page_range
            else:
                if page.number <= 3:
                    display_list = [1, 2, 3, 4, 5]
                elif paginator.num_pages - page.number <= 2:
                    display_list = paginator.page_range[paginator.num_pages - 5:paginator.num_pages + 1:1]
                else:
                    display_list = [page.number - 2, page.number - 1, page.number, page.number + 1, page.number + 2]
            return render(request, 'container/container_manage.html', {'containerlist': page,
                                                           'dist': paginator.num_pages - page.number,
                                                           'display_list': display_list})

def container_manage_request(request):
    containerlist = container.objects.filter(is_del=0).order_by('-start_time')
    res_list = []
    for container_ in containerlist:
        res_dist = {}
        res_dist['username'] = container_.user.username
        res_dist['name'] = container_.name
        res_dist['img_name'] = container_.img.img_name
        res_dist['memory'] = container_.memory
        res_dist['cpu_cores'] = container_.cpu_cores
        if transfer.objects.get(resource_name=container_.name).classes == 1:
            mountPoint = "无人机"
        elif transfer.objects.get(resource_name=container_.name).classes == 2:
            mountPoint = "无人车"
        else:
            mountPoint = "无人船"
        res_dist['mount_point'] = mountPoint
        res_dist['volume_name'] = str(transfer.objects.get(resource_name=container_.name).model)
        res_dist['node_ip'] = container_.node.ip
        res_dist['gw_ip'] = container_.region.gw_ip
        res_dist['domain'] = container_.region.domain
        res_dist['port'] = container_.port
        res_dist['is_del'] = container_.is_del
        res_dist['state'] = container_.state
        res_list.append(res_dist)

    return HttpResponse(str(res_list))

@decorate_vm_recv
def container_delete(request):
    if request.method == "POST":
        container_name=request.POST.get("container_name")
        print(container_name)
        myContainer=container.objects.get(name=container_name)
        node=myContainer.node
        volume_name=myContainer.volume_name
        base_url = 'tcp://' + node.ip + ':2375'
        try:
            flag = 1
            try:
                C = docker.DockerClient(base_url=base_url, version='auto', timeout=10)
                c=C.containers.get(myContainer.Only_Id)
            except:
                flag = 3
            c.stop()
            c.remove(v=True)
            # C.volumes.prune()
        except:
            flag=2
        # 以下两行接表示删除
        # myContainer.state=1
        # myContainer.is_del=1
        mytransfer = transfer.objects.get(resource_name=container_name)
        mymodel = model.objects.get(model_name=mytransfer.model)
        mymodel.number = mymodel.number-1
        mymodel.save()
        my_classes = classes.objects.get(class_name=mytransfer.classes)
        my_classes.number = my_classes.number - 1
        my_classes.save()
        mytransfer.delete()
        myContainer.delete()
        # myContainer.save()
        return HttpResponse(json.dumps({"st": flag,"container_data": {
            "container_id": myContainer.Only_Id,
            "node_ip":node.ip
        }}), content_type="application/json")

@decorate_vm_recv
def clear_volume(request):
    if request.method == "POST":
        container_data = eval(request.POST.get("container_data"))
        container_id=container_data["container_id"]
        node_ip=container_data["node_ip"]
        base_url = 'tcp://' + node_ip + ':2375'
        C = docker.DockerClient(base_url=base_url, version='auto', timeout=10)
        C.volumes.prune()
        return HttpResponse(json.dumps({"st": 1}), content_type="application/json")

@decorate_vm_recv
def container_shutdown(request):
    if request.method == "POST":
        container_name=request.POST.get("container_name")
        user_name=request.POST.get("user_name")
        print(container_name)
        myContainer=container.objects.get(name=container_name)
        node = myContainer.node
        base_url = 'tcp://' + node.ip + ':2375'
        try:
            flag = 1
            try:
                C = docker.DockerClient(base_url=base_url, version='auto', timeout=10)
                c = C.containers.get(myContainer.Only_Id)
            except:
                flag = 3
            c.stop()
        except:
            flag = 2
        #stop
        myContainer.state=1
        myContainer.save()
        return HttpResponse(json.dumps({"st": flag}), content_type="application/json")

@decorate_vm_recv
def container_start(request):
    if request.method == "POST":
        container_name=request.POST.get("container_name")
        user_name=request.POST.get("user_name")
        print(container_name)
        myContainer=container.objects.get(name=container_name)
        node = myContainer.node
        base_url = 'tcp://' + node.ip + ':2375'
        try:
            flag = 1
            try:
                C = docker.DockerClient(base_url=base_url, version='auto', timeout=10)
                c = C.containers.get(myContainer.Only_Id)
            except:
                flag = 3
            c.start()
        except:
            flag = 2
            # start
        myContainer.state = 0
        myContainer.save()
        return HttpResponse(json.dumps({"st": flag}), content_type="application/json")

@decorate_vm_recv
def container_restart(request):
    if request.method == "POST":
        container_name=request.POST.get("container_name")
        user_name=request.POST.get("user_name")
        print(container_name)
        myContainer=container.objects.get(name=container_name)
        if myContainer.state == 0:
            node = myContainer.node
            base_url = 'tcp://' + node.ip + ':2375'
            try:
                flag = 1
                try:
                    C = docker.DockerClient(base_url=base_url, version='auto', timeout=10)
                    c = C.containers.get(myContainer.Only_Id)
                except:
                    flag = 3
                c.restart()
            except:
                flag = 2
            myContainer.state=0
            myContainer.save()
            return HttpResponse(json.dumps({"st": flag}), content_type="application/json")
        else:
            flag=4
            return HttpResponse(json.dumps({"st": flag}), content_type="application/json")

@decorate_vm_recv
def container_details(request):
    if request.method == "POST":
        container_name=request.POST.get("container_name")
        user_name=request.POST.get("user_name")
        myContainer = container.objects.get(name=container_name)
        if myContainer:
            flag=1
        else:
            flag=2
        volume=myContainer.mountPoint
        volume_name=myContainer.volume_name
        print(volume)
        return HttpResponse(json.dumps({"st": flag,"volume":volume,"volume_name":volume_name}), content_type="application/json")
