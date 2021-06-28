import paramiko
import os

def connection_SSH(ip, port, user, pwd):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        res = ssh.connect(hostname=ip, port=port, username=user, password=pwd, timeout=5)
        ssh.close()
        return True
    except:
        print(ip + " ssh connection false")
        return False


def ssh_Auth(ip, port, user, pwd,homedir):
    """
    os.system("cmd")    if success return 0;else false.
    os.path.expanduser  把path中包含的"~"和"~user"转换成用户目录
    """

    if os.path.exists(os.path.expanduser("~/.ssh/id_rsa")) and os.path.exists(os.path.expanduser("~/.ssh/id_rsa.pub")):
        pass
    else:
        if os.system("ssh-keygen -t rsa -P '' -f ~/.ssh/id_rsa"):
            return False

    # 使用用户名，密码建立ssh链接
    trans = paramiko.Transport((ip, int(port)))
    try:
        trans.connect(username=user, password=pwd)
    except:
        print(ip + " ssh connection false")
        return False

    ssh = paramiko.SSHClient()
    ssh._transport = trans
    sftp = paramiko.SFTPClient.from_transport(trans)

    remote_authkeypath = homedir+"/.ssh/authorized_keys"
    remote_backkeypath = homedir+"/.ssh/filebackkey.pub"
    print(remote_authkeypath, remote_backkeypath)
    try:
        sftp.put(os.path.expanduser("~/.ssh/id_rsa.pub"), remote_backkeypath)
        ssh.exec_command("cat " + remote_backkeypath + " >> " + remote_authkeypath)
    except:
        print("ssh-pubkey copy error")
        return False

    try:
        # stdin, stdout, stderr = ssh.exec_command('lsb_release -a')
        # resout = stdout.read().decode()
        # if "Ubuntu" in resout:
        #     print("Ubuntu")
        # else:
        #     print("Centos")
        ssh.exec_command("chmod 600 " + remote_authkeypath)
        ssh.exec_command("service sshd restart")
    except:
        print("ssh restart error")
        return False

    trans.close()
    return True
