import json

import requests
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse

from users.models import UserProfile
from vm.models import cascade_list, domain


def decorate_request_pindex(func):
    def inner(request, pindex):
        cascade_self = cascade_list.objects.get(is_self=True)
        last_index = request.path[:-1:].rfind('/')
        final_path = request.path[:last_index]+'_request/'
        re_list = []
        if cascade_self.is_master:
            cascade_slaves = cascade_list.objects.filter(is_communicate=True).exclude(id=cascade_self.id)
            for cascade_slave in cascade_slaves:
                re_content = requests.get('http://' + str(cascade_slave.ip) + ':' + str(cascade_slave.port) + final_path)
                re_list += eval(str(re_content.text))
        res = func(request, pindex, re_list)
        return res
    return inner

def decorate_request(func):
    def inner(request):
        cascade_self = cascade_list.objects.get(is_self=True)
        final_path = request.path[:-1:]+'_request/'
        re_list = []
        if cascade_self.is_master:
            cascade_slaves = cascade_list.objects.filter(is_communicate=True).exclude(id=cascade_self.id)
            for cascade_slave in cascade_slaves:
                re_content = requests.get(
                    'http://' + str(cascade_slave.ip) + ':' + str(cascade_slave.port) + final_path)
                re_list += eval(str(re_content.text))
        res = func(request, re_list)
        return res
    return inner

def decorate_vm_recv(func):
    def inner(request: WSGIRequest):
        domain_ip_list = [
            '/admins/refuse_vm/',
            '/admins/agree_vm/',
            '/admins/agree_install_vm/',
            '/admins/agree_build_vmNAT/',
            '/admins/agree_definit_vm/',
            '/container/agree_docker/',
            '/container/refuse_docker/',
            '/container/container_delete/',
            '/container/clear_volume/',
            '/container/container_shutdown/',
            '/container/container_start/',
            '/container/container_restart/',
            '/container/container_details/',
            '/admins/sync_domain/',
            '/admins/delete_domain/',
            '/admins/existing_workstation/',
            '/admins/delete_workstation/',
        ]
        param_dict = dict(request.POST)
        print(param_dict)
        cascade_self = cascade_list.objects.get(is_self=True)
        if cascade_self.is_master:
            from admins.views import find_vm_by_ip, find_vm_by_domain_ip
            if request.path in domain_ip_list:
                find_way = find_vm_by_domain_ip
            else:
                find_way = find_vm_by_ip
            if eval(find_way(request).content.decode()):
                res = func(request)
            else:
                cascade_slaves = cascade_list.objects.filter(is_communicate=True).exclude(id=cascade_self.id)
                for cascade_slave in cascade_slaves:
                    if eval(requests.post('http://' + str(cascade_slave.ip) + ':' + str(cascade_slave.port) + '/admins/' + find_way.__name__ + '/', param_dict).content.decode()):
                        res = requests.post('http://' + str(cascade_slave.ip) + ':' + str(cascade_slave.port) + request.path, param_dict)
                        return HttpResponse(json.dumps(eval(res.content.decode())), content_type="application/json")
        else:
            res = func(request)
        return res
    return inner

def decorate_existing_workstation(func):
    def inner(request: WSGIRequest):
        param_dict = dict(request.GET)
        print(param_dict)
        request.POST = request.GET
        final_path = request.path[:-1] + '_request/'
        cascade_self = cascade_list.objects.get(is_self=True)
        if cascade_self.is_master:
            from admins.views import find_vm_by_domain_ip
            if eval(find_vm_by_domain_ip(request).content.decode()):
                res = func(request)
            else:
                cascade_slaves = cascade_list.objects.filter(is_communicate=True).exclude(id=cascade_self.id)
                for cascade_slave in cascade_slaves:
                    if eval(requests.post('http://' + str(cascade_slave.ip) + ':' + str(
                        cascade_slave.port) + '/admins/find_vm_by_domain_ip/', param_dict).content.decode()):
                        re_content = requests.post(
                            'http://' + str(cascade_slave.ip) + ':' + str(cascade_slave.port) + final_path,
                            param_dict)
                        res = func(request, eval(str(re_content.text)))
        else:
            res = func(request)
        return res
    return inner

def decorate_add_domain(func):
    def inner(request: WSGIRequest):
        cascade_self = cascade_list.objects.get(is_self=True)
        final_path = request.path[:-1] + '_request/'
        server_list = []
        if cascade_self.is_master:
            communication_servers = cascade_list.objects.filter(is_communicate=True)
            for communication_server in communication_servers:
                server_list.append(communication_server.ip)
            if request.method == 'GET':
                res = func(request, server_list)
            else:
                desc_server = request.POST.get('server')
                find_server = cascade_list.objects.get(ip=desc_server)
                if find_server.is_self:
                    res = func(request, server_list)
                else:
                    re_content = requests.post(
                        'http://' + str(desc_server) + ':' + str(find_server.port) + final_path,
                        dict(request.POST)).content.decode()
                    res = func(request, server_list, re_content)
        else:
            server_list.append(cascade_self.ip)
            res = func(request, server_list)
        return res
    return inner

def decorate_add_workstation(func):
    def inner(request: WSGIRequest):
        cascade_self = cascade_list.objects.get(is_self=True)
        final_path = request.path[:-1] + '_request/'
        server_list = []
        domain_list = []
        if cascade_self.is_master:
            communication_servers = cascade_list.objects.filter(is_communicate=True)
            for communication_server in communication_servers:
                server_list.append(communication_server.ip)
            domains = domain.objects.all()
            for domain_ in domains:
                domain_dict = {}
                domain_dict['id'] = domain_.id
                domain_dict['domain'] = domain_.domain
                domain_list.append(domain_dict)
            if request.method == 'GET':
                res = func(request, server_list, domain_list)
            else:
                server_ip = request.POST.get('server')
                find_cascade = cascade_list.objects.get(ip=server_ip)
                param_dict = dict(request.POST)
                if find_cascade.is_master:
                    res = func(request, server_list, domain_list)
                else:
                    message = requests.post('http://' + str(find_cascade.ip) + ':' + str(find_cascade.port) + final_path, param_dict).content.decode()
                    res = func(request, server_list, domain_list, message)
        else:
            server_list.append(cascade_self.ip)
            domains = domain.objects.all()
            for domain_ in domains:
                domain_dict = {}
                domain_dict['id'] = domain_.id
                domain_dict['domain'] = domain_.domain
                domain_list.append(domain_dict)
            res = func(request, server_list, domain_list)
        return res
    return inner

def decorate_get_domain_by_ip(func):
    def inner(request: WSGIRequest):
        server_ip = request.POST.get('server_ip')
        param_dict = dict(request.POST)
        find_cascade = cascade_list.objects.get(ip=server_ip)
        if find_cascade.is_self:
            re_content = func(request)
            res_domain = eval(str(re_content.content.decode()))['domain']
            res_os = eval(str(re_content.content.decode()))['os']
            res_docker_os = eval(str(re_content.content.decode()))['docker_os']
        else:
            re_content = requests.post('http://' + str(find_cascade.ip) + ':' + str(find_cascade.port) + request.path,
                                       param_dict)
            res_domain = eval(str(re_content.text))['domain']
            res_os = eval(str(re_content.text))['os']
            print(eval(str(re_content.text)))
            res_docker_os = eval(str(re_content.text))['docker_os']
        print(res_domain)
        print(res_os)
        print(res_docker_os)
        return HttpResponse(json.dumps({
            'domain': res_domain,
            'os': res_os,
            'docker_os': res_docker_os,
        }), content_type="application/json")

    return inner

def decorate_virtualhost(func):
    def inner(request: WSGIRequest):
        server_list = []
        servers = cascade_list.objects.filter(is_communicate=True)
        for server_ in servers:
            server_list.append(server_.ip)
        res = func(request, server_list)
        return res
    return inner

def decorate_apply(func):
    def inner(request: WSGIRequest):
        server_ip = request.POST.get('server_ip')
        find_cascade = cascade_list.objects.get(ip=server_ip)
        param_dict = dict(request.POST)
        try:
            username = UserProfile.objects.get(username=request.user.username).username
        except:
            username = request.POST.get('username')
        param_dict['username'] = username
        if find_cascade.is_self:
            res = func(request)
        else:
            re_content = requests.post('http://' + str(find_cascade.ip) + ':' + str(find_cascade.port) + request.path, param_dict).content.decode()
            res = HttpResponse(json.dumps(eval(re_content)), content_type="application/json")
        return res
    return inner

def decorate_get_node_by_name(func):
    def inner(request: WSGIRequest):
        server_ip = request.POST.get('server_ip')
        param_dict = dict(request.POST)
        find_cascade = cascade_list.objects.get(ip=server_ip)
        if find_cascade.is_self:
            re_content = func(request)
            res = eval(str(re_content.content.decode()))
        else:
            re_content = requests.post('http://' + str(find_cascade.ip) + ':' + str(find_cascade.port) + request.path, param_dict)
            res = eval(str(re_content.text))['node']
        print(res)
        return HttpResponse(json.dumps({
            'node': res,
        }), content_type='application/json')
    return inner

def decorate_node_apply(func):
    def inner(request: WSGIRequest):
        cascade_self = cascade_list.objects.get(is_self=True)
        final_path = request.path[:-1] + '_request'
        re_list = []
        domain_list = []
        server_list = []
        cascade_communicates = cascade_list.objects.filter(is_communicate=True)
        for cascade_communicate in cascade_communicates:
            server_list.append(cascade_communicate.ip)
        domains = domain.objects.all()
        for domain_ in domains:
            domain_list.append(domain_.domain)
        if cascade_self.is_master:
            cascade_slaves = cascade_list.objects.filter(is_communicate=True).exclude(id=cascade_self.id)
            for cascade_slave in cascade_slaves:
                re_content = requests.get('http://' + str(cascade_slave.ip) + ':' + str(cascade_slave.port) + final_path)
                print(re_content)
                re_list += eval(str(re_content.text))
        res = func(request, re_list, server_list, domain_list)
        return res
    return inner

def decorate_agree_zabbix_node(func):
    def inner(request: WSGIRequest):
        server_ip = request.POST.get('server_ip')
        param_dict = dict(request.POST)
        find_cascade = cascade_list.objects.get(ip=server_ip)
        if find_cascade.is_self:
            res = func(request)
        else:
            re_content = requests.post('http://' + str(find_cascade.ip) + ':' + str(find_cascade.port) + request.path, param_dict).content.decode()
            res = HttpResponse(json.dumps(eval(re_content)), content_type="application/json")
        return res
    return inner

def decorate_getSources(func):
    def inner(request: WSGIRequest):
        cascade_self = cascade_list.objects.get(is_self=True)
        radar_count = 0
        compute_resource_count = 0
        weapon_count = 0
        host = []
        all_node_info = []
        if cascade_self.is_master:
            cascade_slaves = cascade_list.objects.filter(is_communicate=True).exclude(id=cascade_self.id)
            for cascade_slave in cascade_slaves:
                re_content = requests.post('http://' + str(cascade_slave.ip) + ':' + str(cascade_slave.port) + request.path)
                normal_data = json.loads(re_content.text)
                radar_count += normal_data['radar_count']
                compute_resource_count += normal_data['computer_resource_count']
                weapon_count += normal_data['weapon_count']
                host += normal_data['host']
                all_node_info += normal_data['all_node_info']
        res = func(request, radar_count, compute_resource_count, weapon_count, host, all_node_info)
        return res
    return inner

def decorate_get_node_info(func):
    def inner(request: WSGIRequest):
        node_name_info = request.POST.get('node_name')
        server_id = node_name_info.split('_')[1]
        param_dict = dict(request.POST)
        find_cascade = cascade_list.objects.get(id=server_id)
        if find_cascade.is_self:
            res = func(request)
            return res
        else:
            re_content = requests.post('http://' + str(find_cascade.ip) + ':' + str(find_cascade.port) + request.path, param_dict).content.decode()
            print(re_content)
            return HttpResponse(json.dumps(eval(re_content)), content_type='application/json')
    return inner
