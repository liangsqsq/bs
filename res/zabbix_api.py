import requests

# url = 'http://192.168.8.129/zabbix/api_jsonrpc.php'


class Zabbix:
    def __init__(self, url, user, password):
        '''
        初试化zabbix对象
        :param url: str, 'http://ip/zabbix/api_jsonrpc.php'
        :param user: str, 'Admin'
        :param password: str, 'zabbix'
        '''
        self.url = url
        self.user = user
        self.password = password
        self.login()

    def login(self):
        ''' 登录并获取auth口令 '''
        data = {
            "jsonrpc": "2.0",
            "method": "user.login",
            "id": 1,
            "params": {
                "user": self.user,
                "password": self.password
            }
        }
        response = requests.post(url=self.url, json=data).json()

        if response.get('error'):
            print(response.get('error'))
        elif response.get('result'):
            self.auth = response.get('result')

        return response.get('result')

    def hostid_get(self, host_name):
        '''
        获取host_name的hostid用于获取其被监控的参数
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
                    "host",
                    "available"
                ]
            },
            "id": 2,
            "auth": self.auth
        }
        response = requests.post(url=self.url, json=data).json()
        # print('hostid_get response:\n', response)

        return response.get('result', [])

    def itemid_get(self, hostid, key):
        '''
        根据hostid和key（监控项的键名）来获取监控项的id
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
        response = requests.post(url=self.url, json=data).json()
        # print('itemid_get response:\n', response)

        return response.get('result', [])

    def _historys_get(self, itemid, history_type, limit):
        '''
        根据监控项的id获取其历史记录
        :param itemid: str, '23296'
        :param history_type:0 - numeric float;
                            1 - character;
                            2 - log;
                            3 - numeric unsigned;
                            4 - text.
                            Default: 3.
        :param limit: int, 需要放回的记录的条数
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
        response = requests.post(url=self.url, json=data).json()
        print('_historys_get response:\n', response)

        return response.get('result', [])

    def historys_get(self, host_name, key, history_type, limit):
        """
        根据四个参数获监控项的历史记录
        :param host_name:
        :param key:
        :param history_type:
        :param limit:
        :return:
        """
        hosts = self.hostid_get(host_name)
        print('hosts:\n', hosts)
        for host in hosts:
            if host["available"] == "1":
                items = self.itemid_get(host['hostid'], key)
                print('items:\n', items)
                for item in items:
                    historys = self._historys_get(item['itemid'], history_type, limit)
                    print('historys:\n', historys)
                    return historys
            else:
                return [
                    {
                        "value": -1
                    }
                ]

    def create_host(self, host_name, host_ip):
        """
        创建zabbix监控的主机,目前将模板定为Template OS Linux(id=10001)，组定为Linux servers(id=2)
        :param host_name: str, 主机名
        :param host_ip: str, 主机ip
        :return:
        """

        data = {
            "jsonrpc": "2.0",
            "method": "host.create",
            "params": {
                "host": host_name,
                "interfaces": [
                    {
                        "type": 1,
                        "main": 1,
                        "useip": 1,
                        "ip": host_ip,
                        "dns": "",
                        "port": 10050
                    }
                ],
                "groups": [
                    {
                        "groupid": "2"
                    }
                ],
                "templates": [
                    {
                        "templateid": "10001"
                    }
                ]
            },
            "auth": self.auth,
            "id": 1
        }
        response = requests.post(url=self.url, json=data).json()
        return response.get('result', {})

    def get_template_id(self, template_name):
        """
        根据模板名称来获取模板的id，将来可能需要为节点设置不同的模板
        :param template_name: 模板名称
        :return:
        """

        data = {
            "jsonrpc": "2.0",
            "method": "template.get",
            "params": {
                "output": "templateid",
                "filter": {
                    "host": template_name
                }
            },
            "auth": self.auth,
            "id": 1
        }
        response = requests.post(url=self.url, json=data).json()
        return response.get('result', [])

    def get_group_id(self, group_name):
        """
        根据组名来获取组id，将来可能需要为节点设置不同的组
        :param group_name: 组名
        :return:
        """

        data = {
            "jsonrpc": "2.0",
            "method": "hostgroup.get",
            "params": {
                "output": "groupid",
                "filter": {
                    "name": group_name
                }
            },
            "auth": self.auth,
            "id": 1
        }

        response = requests.post(url=self.url, json=data).json()
        return response.get('result', [])

    def get_all_hosts(self):
        data = {
            "jsonrpc": "2.0",
            "method": "host.get",
            "params": {
                "output": [
                    "hostid",
                    "host"
                ],
                "selectInterfaces": [
                    "interfaceid",
                    "ip",
                    "available"
                ]
            },
            "id": 1,
            "auth": self.auth
        }

        response = requests.post(url=self.url, json=data).json()
        return response.get('result', [])

    def get_available_host(self):
        data = {
            "jsonrpc": "2.0",
            "method": "host.get",
            "params": {
                "filter": {
                    "available": 1
                },
                "output": [
                    "hostid",
                    "host"
                ],
                "selectInterfaces": [
                    "interfaceid",
                    "ip"
                ]
            },
            "id": 1,
            "auth": self.auth
        }

        response = requests.post(url=self.url, json=data).json()
        return response.get('result', [])

    def delete_host(self, host_id):
        data = {
            "jsonrpc": "2.0",
            "method": "host.delete",
            "params": [
                host_id
            ],
            "auth": self.auth,
            "id": 1
        }

        response = requests.post(url=self.url, json=data).json()
        return response.get('result', {})

    def make_host_available(self, host_id):
        data = {
            "jsonrpc": "2.0",
            "method": "host.update",
            "params": {
                "hostid": host_id,
                "available": 1
            },
            "auth": self.auth,
            "id": 1
        }
        response = requests.post(url=self.url, json=data).json()
        return response.get('result', {})

    def make_host_no_available(self, host_id):
        data = {
            "jsonrpc": "2.0",
            "method": "host.update",
            "params": {
                "hostid": host_id,
                "available": 2
            },
            "auth": self.auth,
            "id": 1
        }
        response = requests.post(url=self.url, json=data).json()
        return response.get('result', {})

# if __name__ == '__main__':
#     url = 'http://192.168.8.129/zabbix/api_jsonrpc.php'
#     za = Zabbix(url, 'Admin', 'zabbix')
#     # za = Zabbix('dragonstack', 'zabbix')
#     # print(za.historys_get('Pi9', "system.cpu.util[,user]", 0, 10))
#     print(za._historys_get("29654", 0, 1))
