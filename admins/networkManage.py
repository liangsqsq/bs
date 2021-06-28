import paramiko
import random
import time

FLAG_CONN_NAT = 0
FLAG_OTHER_NAT = 1

CONN_START_PORT = 40000
CONN_END_PORT = 45000
OTHER_START_PORT = 45001
OTHER_END_PORT = 50000


def getAvailablePort(channel, start_port, end_port):
    print('-------------------get Available Port-------------------')
    while True:
        dport = str(random.randint(start_port, end_port))
        channel.send("sudo iptables -t nat -nL | grep " + dport)
        channel.send("\n")
        buff = ''
        while not buff.endswith('# '):
            resp = channel.recv(999)
            buff += resp.decode('utf-8')
        print(buff)
        if buff.count('\n') == 1:
            print('no record')
            return dport
        else:
            print('Port ' + dport + ' is already used')


def buildVMNAT(gw, vmip, vmport, flags=FLAG_CONN_NAT):
    print('-------------------build VM NAT-------------------')

    trans = paramiko.Transport((gw.gw_ip, int(gw.port)))
    try:
        trans.connect(username=gw.user, password=gw.pwd)
    except:
        print(gw.domain + " ssh connection false")
        return False
    ssh = paramiko.SSHClient()
    ssh._transport = trans

    channel = ssh.invoke_shell()
    time.sleep(0.1)
    channel.send("sudo su\n")
    buff = ''
    while not buff.endswith(': '):
        resp = channel.recv(999)
        buff += resp.decode('utf-8')
    print(buff)
    channel.send(gw.pwd)
    channel.send('\n')
    buff = ''
    while not buff.endswith('# '):
        resp = channel.recv(999)
        buff += resp.decode('utf-8')
    print(buff)
    print("------end------")

    if flags == FLAG_CONN_NAT:
        DPORT = getAvailablePort(channel, CONN_START_PORT, CONN_END_PORT)
    elif flags == FLAG_OTHER_NAT:
        DPORT = getAvailablePort(channel, OTHER_START_PORT, OTHER_END_PORT)

    nat_cmd = 'iptables -t nat -A PREROUTING -i eth1 -p tcp --dport ' + DPORT + ' -j DNAT --to-destination ' + vmip + ':' + str(
        vmport) + ';service iptables save'
    print('nat cmd :' + nat_cmd)

    channel.send(nat_cmd)
    channel.send("\n")
    buff = ''
    while not buff.endswith('# '):
        resp = channel.recv(999)
        buff += resp.decode('utf-8')
    print(buff)

    trans.close()
    ssh.close()
    return int(DPORT)


def delPort(gw, vmip, DPORT, vmport):
    trans = paramiko.Transport((gw.gw_ip, int(gw.port)))
    try:
        trans.connect(username=gw.user, password=gw.pwd)
    except:
        print(gw.domain + " ssh connection false")
        return False
    ssh = paramiko.SSHClient()
    ssh._transport = trans

    channel = ssh.invoke_shell()
    time.sleep(0.1)
    channel.send("sudo su\n")
    buff = ''
    while not buff.endswith(': '):
        resp = channel.recv(999)
        buff += resp.decode('utf-8')
    print(buff)
    channel.send(gw.pwd)
    channel.send('\n')
    buff = ''
    while not buff.endswith('# '):
        resp = channel.recv(999)
        buff += resp.decode('utf-8')
    print(buff)
    print("------end------")

    DPORT = str(DPORT)
    nat_cmd = 'iptables -t nat -D PREROUTING -i eth1 -p tcp --dport ' + DPORT + ' -j DNAT --to-destination ' + vmip + ':' + str(
        vmport) + \
              ';service iptables save'
    print('del nat cmd :' + nat_cmd)

    channel.send(nat_cmd)
    channel.send("\n")
    buff = ''
    while not buff.endswith('# '):
        resp = channel.recv(999)
        buff += resp.decode('utf-8')
    print(buff)

    trans.close()
    ssh.close()
    return True
