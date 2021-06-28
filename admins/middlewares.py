from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin

from admins.zabbix_api import Zabbix
from container.models import docker_node
from vm.models import workstation, domain, apply_node


class hasNewZabbix(MiddlewareMixin):
    def process_request(self, request):
        if request.method == 'GET':
            url = 'http://127.0.0.1/zabbix/api_jsonrpc.php'
            za = Zabbix(url, 'Admin', 'zabbix')
            za.login()
            hosts = za.get_available_host()
            host_num = len(hosts)
            new_zabbix_count = apply_node.objects.filter(state=0).count()
            if host_num > new_zabbix_count:
                for host in hosts:
                    ip = host["interfaces"][0]["ip"]
                    if ip == "127.0.0.1":
                        continue
                    elif apply_node.objects.filter(ip=ip):
                        continue
                    else:
                        print(ip)
                        try:
                            f = open('/home/xidian/' + ip + '_recode', 'r')
                        except:
                            apply_node.objects.create(host_name=ip, ip=ip)
                        else:
                            recode_list = f.readlines()
                            ssh_port = recode_list[0][0:len(recode_list[0])-1]
                            user = recode_list[1][0:len(recode_list[1])-1]
                            pwd = recode_list[2][0:len(recode_list[2])-1]
                            home_dir = recode_list[3][0:len(recode_list[3])-1]
                            apply_node.objects.create(host_name=ip, ip=ip, ssh_port=int(ssh_port),
                                                      user=user, pwd=pwd, home_dir=home_dir)

class delete_unavailable(MiddlewareMixin):
    def process_request(self, request):
        if request.method == 'GET':
            request_nodes = apply_node.objects.all()
            for request_node in request_nodes:
                node_ip = request_node.ip
                print(node_ip)
                url = 'http://127.0.0.1/zabbix/api_jsonrpc.php'
                za = Zabbix(url, 'Admin', 'zabbix')
                za.login()
                is_available = za.hostid_get(node_ip)[0]["available"]
                if is_available == '1':
                    continue
                else:
                    print(node_ip)
                    request_node.delete()
                    try:
                        find_workstation = workstation.objects.get(ip=node_ip)
                    except:
                        try:
                            find_docker_node = docker_node.objects.get(ip=node_ip)
                        except:
                            continue
                        else:
                            find_docker_node.delete()
                    else:
                        find_workstation.delete()
