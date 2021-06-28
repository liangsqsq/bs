import paramiko
import libvirt
import time

FLAG_FAILURE = 0
FLAG_SUCCESS = 1
FLAG_CONN_FAILURE = 2
FLAG_VM_GEN_FAILURE = 3
FLAG_VM_START_FAILURE = 4
FLAG_VM_SHUTDOWN_FAILURE = 5
FLAG_VM_DEL_FAILURE = 6
FLAG_VM_SET_FAILURE = 7


def libvirtConn(HOSTNAME, IP, PORT, USER):
    '''build remote qemu and storagePool connection
    Args:
        TYPE: all strings
    Returns:
        conn,pool
    '''
    conn = libvirt.open(
        "qemu+ssh://" + USER + "@" + IP + ":" + PORT + "/system")
    print("qemu connection success to " + HOSTNAME)
    pool = conn.storagePoolLookupByName('default')
    return conn, pool


def getVolXML(apply_isPersistent, vm_name, apply_disk, image_path, template_path):
    if apply_isPersistent == True:
        with open('VOLXML', 'r') as f:
            volxml = f.read()
        volxml = volxml.replace('VOLUME_NAME', vm_name + '.qcow2').replace('DISK_SIZE', str(apply_disk)).replace(
            'VOLUME_PATH', image_path)
        return volxml
    else:
        with open('Backing_VOLXML', 'r') as f:
            volxml = f.read()
        volxml = volxml.replace('VOLUME_NAME', vm_name + '.qcow2').replace('DISK_SIZE', str(apply_disk)).replace(
            'VOLUME_PATH', image_path).replace('BACKING_FILE', template_path)
        return volxml


def getVMXML(my_vm_name, apply_mem, apply_cpu, image_path, noVNC_PORT, cdrom_path, isPersistent, installWay):
    with open('VMXML', 'r') as f:
        vmxml = f.read()
    vmxml = vmxml.replace('domainname', my_vm_name).replace('CURRENT_MEM', str(apply_mem)).replace(
        'VCPU_NUM', str(apply_cpu)).replace('DISK_PATH', image_path).replace('VNC_PORT', str(noVNC_PORT))
    if installWay == 'iso' and isPersistent == True:
        vmxml = vmxml.replace('CDROM_PATH', cdrom_path)
        return vmxml
    else:
        vmxml = vmxml.replace('<source file=\'CDROM_PATH\'/>', '').replace('<boot dev=\'cdrom\'/>', '')
        return vmxml

def getSnapshotXML(snapshotName,diskpath):
     with open('snapshotXML','r') as f:
         snapshotxml=f.read()
         snapshotxml=snapshotxml.replace('snapshotName',snapshotName).replace('diskPath',diskpath)
         return snapshotxml

def customIMG(server, vmname, os, vmpwd):
    print('-------------------Customize IMG-------------------')
    # 使用用户名，密码建立ssh链接
    trans = paramiko.Transport((server.ip, int(server.ssh_port)))
    try:
        trans.connect(username=server.user, password=server.pwd)
    except:
        print(server.hostname + " ssh connection false")
        return False
    ssh = paramiko.SSHClient()
    ssh._transport = trans

    if os.default_user.find('ubuntu') != -1:
        sysprep_cmd = 'virt-sysprep -d ' + vmname + ' --firstboot-command \'dpkg-reconfigure openssh-server\' --password ' + os.default_user + ':password:' + vmpwd + \
                      ' --root-password password:' + vmpwd
    elif os.default_user.find('centos') != -1:
        sysprep_cmd = 'virt-sysprep -d ' + vmname + ' --firstboot-command \'openssh-server\' --password ' + os.default_user + ':password:' + vmpwd + \
                      ' --root-password password:' + vmpwd
    else:
        sysprep_cmd = 'virt-sysprep -d ' + vmname

    print('sysprep cmd :' + sysprep_cmd)

    stdin, stdout, stderr = ssh.exec_command(sysprep_cmd)
    if stderr:
        print('stderr : ' + stderr.read().decode())
    trans.close()
    ssh.close()


def setWinPwd(server, vmname, username, vmpwd):
    print('-------------------set Windows Password-------------------')
    # 使用用户名，密码建立ssh链接
    trans = paramiko.Transport((server.ip, int(server.ssh_port)))
    try:
        trans.connect(username=server.user, password=server.pwd)
    except:
        print(server.hostname + " ssh connection false")
        return False
    ssh = paramiko.SSHClient()
    ssh._transport = trans

    cmd = 'virsh set-user-password --domain '+ vmname + ' --user '+ username + ' --password '+ vmpwd
    print('cmd :' + cmd)

    stdin, stdout, stderr = ssh.exec_command(cmd)
    if stderr:
        print('stderr : ' + stderr.read().decode())
    trans.close()
    ssh.close()


def installVM(VMname, applyVM, applyOS, server, img_path, noVNC_PORT):
    '''
    Args:
        VMname:
        applyVM: new_vm_apply instance
        applyOS: vm_os instance
        server: workstation instance
        img_path: where is VM's img
        noVNC_PORT: TYPE-int

    Process:
        libvirt connection  ->
        get VM xml and VOLUME xml   ->
        if ISO install:
            create VOLUME -> define VM -> start VM
        if CLONE install:
            copy from template -> virt-sysprep customize VM -> startVM -> get VM IP
        if NOT persistent:
            create VM ->start VM ->get VM IP

    Returns:
        FLAG SUCCESS OR FAILURE
    '''
    print('-------------------Install VM -------------------')
    # get information about vm to apply
    apply_cpu = applyVM.cpu_cores
    apply_mem = applyVM.memory
    apply_disk = applyVM.disk
    isPersistent = applyVM.isPersistent
    install_way = applyVM.installway
    vmpwd = applyVM.password

    # get information about img about template
    template_path = applyOS.template_path
    cdrom_path = applyOS.iso_path

    try:
        conn,pool = libvirtConn(server.host_name,server.ip,str(server.ssh_port),server.user)
    except:
        return FLAG_CONN_FAILURE

    # get VOLUME XML
    volxml = getVolXML(isPersistent, VMname, apply_disk, img_path, template_path)
    # get VM XML
    vmxml = getVMXML(VMname, apply_mem, apply_cpu, img_path, noVNC_PORT, cdrom_path, isPersistent, install_way)

    if isPersistent == True:
        if install_way == 'iso':
            try:
                # DEFINE VOLUME XML
                pool.createXML(volxml, 0)
                # DEFINE VM XML
                conn.defineXML(vmxml)
                vmip = None
                print('vm define success')
            except:
                return FLAG_VM_GEN_FAILURE
        elif install_way == 'clone':
            try:
                template_name = template_path.split('/')[-1]
                print('template img : ' + template_name)
                template = pool.storageVolLookupByName(template_name)
                pool.createXMLFrom(volxml, template)
                pool.refresh()
                vol = pool.storageVolLookupByName(VMname + '.qcow2')
                vol.resize(apply_disk * 1024 * 1024 * 1024)
                conn.defineXML(vmxml)
                print('vm define success')
            except:
                return FLAG_VM_GEN_FAILURE
        if vmpwd:
            customIMG(server, VMname, applyOS, vmpwd)

        dom = conn.lookupByName(VMname)
        try:
            # START Domain
            dom.setAutostart(1)
            dom.create()
            print('vm start success')
        except:
            return FLAG_VM_START_FAILURE
        if install_way == 'clone':
            # get vm ip address
            vmip = getVMIp(dom)
            #set windows vm password
            if applyOS.default_user.find('ubuntu')== -1 and applyOS.default_user.find('centos')== -1:
                setWinPwd(server,VMname,applyOS.default_user,vmpwd)

    else:
        try:
            pool.createXML(volxml, 0)
            conn.createXML(vmxml)
            dom = conn.lookupByName(VMname)
            vmip = getVMIp(dom)
        except:
            return FLAG_VM_GEN_FAILURE

    conn.close()
    return FLAG_SUCCESS, vmip


def deleteVM(vm_name, server, isPersistent):
    '''
    Args:
        vm name:
        server:
        isPersistent:
    Returns:
        FLAG SUCCESS OR FAILURE
    '''
    print('-------------------Delete VM-------------------')
    try:
        conn,pool = libvirtConn(server.host_name,server.ip,str(server.ssh_port),server.user)
    except:
        return FLAG_CONN_FAILURE

    dom = conn.lookupByName(vm_name)
    flag = dom.isActive()
    if flag:
        dom.destroy()
        if isPersistent:
            dom.undefine()
    else:
        dom.undefine()
    try:
        pool.storageVolLookupByName(vm_name + '.qcow2').delete(0)
        conn.close()
        return FLAG_SUCCESS
    except:
        print('delete vol false')
        conn.close()
        return FLAG_VM_DEL_FAILURE


def shutdownVM(vm_name, server):
    print('-------------------shutdown VM-------------------')
    try:
        conn,pool = libvirtConn(server.host_name,server.ip,str(server.ssh_port),server.user)
    except:
        return FLAG_CONN_FAILURE

    try:
        dom = conn.lookupByName(vm_name)
        dom.shutdown()
        conn.close()
        return FLAG_SUCCESS
    except:
        conn.close()
        return FLAG_VM_SHUTDOWN_FAILURE


def startVM(vm_name, server):
    print('-------------------start VM-------------------')

    try:
        conn,pool = libvirtConn(server.host_name,server.ip,str(server.ssh_port),server.user)
    except:
        return FLAG_CONN_FAILURE

    try:
        dom = conn.lookupByName(vm_name)
        dom.create()
        conn.close()
        return FLAG_SUCCESS
    except:
        conn.close()
        return FLAG_VM_START_FAILURE


def getVMIp(domain):
    print('-------------------get VM IP-------------------')
    # get vm ip
    vmip = None
    while vmip == None:
        try:
            time.sleep(5)
            ifaces = domain.interfaceAddresses(libvirt.VIR_DOMAIN_INTERFACE_ADDRESSES_SRC_AGENT, 0)
            if ifaces:
                for (name, val) in ifaces.items():
                    if name == 'lo':
                        continue
                    if val['addrs']:
                        for ipaddr in val['addrs']:
                            if ipaddr['type'] == libvirt.VIR_IP_ADDR_TYPE_IPV4:
                                vmip = ipaddr['addr']
                                print(" VIR_IP_ADDR_TYPE_IPV4 = " + vmip)
                                return vmip
        except:
            print('WAIT:VM IP is not obtained...')


def setVMConfiguration(server, vmname, vcpus, mem, diskSize):
    print('-------------------set VM Configuration-------------------')

    try:
        conn,pool = libvirtConn(server.host_name,server.ip,str(server.ssh_port),server.user)
    except:
        return FLAG_CONN_FAILURE

    dom = conn.lookupByName(vmname)
    vol = pool.storageVolLookupByName(vmname + '.qcow2')
    flag = dom.isActive()
    if not flag:
        dom.create()
        time.sleep(15)

    try:
        dom.setVcpusFlags(vcpus, flags=2)
        dom.setMemoryFlags(mem * 1024 * 1024, flags=2)
        vol.resize(diskSize * 1024 * 1024 * 1024)
    except:
        conn.close()
        return FLAG_VM_SET_FAILURE

    conn.close()
    return FLAG_SUCCESS

def getMacFromIp(findDomain, vmip):
    trans = paramiko.Transport((findDomain.gw_ip, int(findDomain.port)))
    try:
        trans.connect(username=findDomain.user, password=findDomain.pwd)
    except:
        print("domain connect ssh false")
        return 0
    ssh = paramiko.SSHClient()
    ssh._transport = trans
    arp_cmd = "bash -lc \'arp " + vmip + "\' | awk '{print $3}'"
    print(arp_cmd)
    stdin, stdout, stderr = ssh.exec_command(arp_cmd)

    mac_addr = stdout.read().decode().split("\n")[1]
    print("get mac address from ip is " + mac_addr)
    trans.close()
    ssh.close()
    return mac_addr

def getMacFromName(server, vm_name):
    trans = paramiko.Transport((server.ip, int(server.ssh_port)))
    try:
        trans.connect(username=server.user, password=server.pwd)
    except:
        print("server connect ssh false")
        return 0
    ssh = paramiko.SSHClient()
    ssh._transport = trans
    stdin, stdout, stderr = ssh.exec_command("virsh dumpxml " + vm_name + " | grep 'mac address'")
    mac_addr = stdout.read().decode().strip()[-20:-3:1]
    print("get mac address from name is " + mac_addr)
    return mac_addr

def migrateVM(vm_name, server, isPersistent, dest_user, dest_ip, dest_post):
    print('-------------------Migrate VM-------------------')
    try:
        conn,pool = libvirtConn(server.host_name,server.ip,str(server.ssh_port),server.user)
        dest_conn = libvirt.open("qemu+ssh://" + dest_user + "@" + dest_ip + ":" + dest_post + "/system")
    except:
        return FLAG_CONN_FAILURE

    dom = conn.lookupByName(vm_name)

    try:
        new_dom = dom.migrate(dest_conn, 0, None, None, 0)
        conn.close()
        dest_conn.close()
        return FLAG_SUCCESS
    except:
        print('migrate vol false')
        conn.close()
        dest_conn.close()
        return FLAG_FAILURE

