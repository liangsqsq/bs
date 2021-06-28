import requests

url = 'http://192.168.1.2/zabbix/api_jsonrpc.php'


class Zabbix:
    def __init__(self, user, password):
        '''

        :param user: str, 'Admin'
        :param password: str, 'zabbix'
        '''
        self.user = user
        self.password = password
        self.login()

    def login(self):
        data = {
            "jsonrpc": "2.0",
            "method": "user.login",
            "id": 1,
            "params": {
                "user": self.user,
                "password": self.password
            }
        }

        response = requests.post(url=url, json=data).json()
        # print(response)

        if response.get('error'):
            print(response.get('error'))
        elif response.get('result'):
            self.auth = response.get('result')

        return response.get('result')

    def hostid_get(self, host_name):
        '''

        :param host_name: str, 'Zabbix server'
        :return: list, [{'hostid': '10084', 'host': 'Zabbix server'}]
        '''
        data = {
            "jsonrpc": "2.0",
            "method": "host.get",
            "params": {
                "filter": {
                    "host": [host_name]
                },
                "output": [
                    "hostid",
                    "host"
                ]
            },
            "id": 2,
            "auth": self.auth
        }
        response = requests.post(url=url, json=data).json()
        # print()
        # print(response)

        return response.get('result', [])

    def itemid_get(self, hostid, key):
        '''

        :param hostid: str, '10084'
        :param key: str, 'system.cpu.load[percpu,avg1]'
        :return:list, [{'key_': 'system.cpu.load[percpu,avg1]', 'itemid': '23296',
                        'name': 'Processor load (1 min average per core)' }]
        '''
        data = {
            "jsonrpc": "2.0",
            "method": "item.get",
            "params": {
                "output": [
                    "key_",
                    "name",
                    'itemid',
                    # "extend"
                ],
                "hostids": hostid,
                "filter": {
                    "key_": key
                },
            },
            "auth": self.auth,
            "id": 1
        }
        response = requests.post(url=url, json=data).json()
        # print(response)
        return response.get('result', [])

    def _historys_get(self, itemid, history_type, limit):
        '''

        :param itemid: str, '23296'
        :param history_type:0 - numeric float;
                            1 - character;
                            2 - log;
                            3 - numeric unsigned;
                            4 - text.
                            Default: 3.
        :param limit: int,
        :return:
        '''
        data = {
            "jsonrpc": "2.0",
            "method": "history.get",
            "params": {
                "output": "extend",
                "history": history_type,
                "itemids": itemid,
                "sortfield": "clock",
                "sortorder": "DESC",
                "limit": limit
            },
            "auth": self.auth,
            "id": 1
        }
        response = requests.post(url=url, json=data).json()
        # print(response)

        return response.get('result', [])

    def historys_get(self, host_name, key, history_type, limit):
        hosts = self.hostid_get(host_name)
        # print(hosts)
        for host in hosts:
            items = self.itemid_get(host['hostid'], key)
            # print(items)
            for item in items:
                historys = self._historys_get(item['itemid'], history_type, limit)
                # print(historys)
                return historys


# if __name__ == '__main__':
    # za = Zabbix('Admin', 'zabbix')
    #r = za.login()
    #hosts = za.hostid_get('Zabbix server')
    #print(hosts)
    #for host in hosts:
    #   items = za.itemid_get(host['hostid'], "system.cpu.load[percpu,avg1]")
    #   print(items)
    #    for item in items:
    #        historys = za._historys_get(item['itemid'], 0, 10)
    #        print(historys)

    #get_hosts


    # #cpu
    # cpu_idle = za.historys_get('Zabbix server', "system.cpu.util[,idle]", 0, 1)[0]["value"]
    # # print("cpu idlo:"+ cpu_idle)
    # cpu_user = za.historys_get('Zabbix server', "system.cpu.util[,user]", 0, 1)[0]["value"]
    # cpu_system = za.historys_get('Zabbix server', "system.cpu.util[,system]", 0, 1)[0]["value"]
    #
    # #mem
    # mem_available = za.historys_get('Zabbix server', "vm.memory.size[available]", 3, 1)[0]["value"]
    # men_total = za.historys_get('Zabbix server', "vm.memory.size[total]", 3, 1)[0]["value"]
    #
    # #disk
    # disk_total = za.historys_get('Zabbix server', "vfs.fs.size[/,total]", 3, 1)[0]["value"]
    #
    # disk_free = za.historys_get('Zabbix server', "vfs.fs.size[/,free]", 3, 1)[0]["value"]
    #
    # #net
    # net_out = float(za.historys_get('Zabbix server', "net.if.out[br0]", 3, 1)[0]["value"])/1024
    # net_in = float(za.historys_get('Zabbix server', "net.if.in[br0]", 3, 1)[0]["value"])/1024
    #
    # print(net_out,net_in)

    #
    # dic1 = {
    #     "cpu_idle":cpu_idle,
    #     "cpu_user":cpu_user,
    #     "cpu_system":cpu_system,
    #     "mem_available":mem_available,
    #     "men_total":men_total,
    #     "disk_total": disk_total,
    #     "disk_free": disk_free
    # }
    # host_name = 循环
    # dic2 = {"host_name":host_name, "\"{}\"".format(host_name):dic1}
    # return jsonify(dic2)
    #

    # # network
    # za.historys_get('Zabbix server', "vfs.fs.size[/,free]", 3, 1)
    # za.historys_get('Zabbix server', "system.hostname", 1, 1)

    # print(za.hostid_get("Zabbix server"))
    # print(za.hostid_get("pi"))