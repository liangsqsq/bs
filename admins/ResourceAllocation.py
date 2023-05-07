import libvirt
import sys

from vm.models import workstation


def ResourceAllocation(domain, vcpu, mem, disk):
    print('-------------------Resource Allocaiton-------------------')
    workstation_list = workstation.objects.filter(belong=domain,state=1)
    print(mem,disk)
    isGetServer = False
    for server in workstation_list:
        conn = libvirt.open("qemu+ssh://" + server.user + "@" + server.ip + ":" + str(server.ssh_port) + "/system")
        if conn == None:
            print('Failed to open connection to' + server.host_name, file=sys.stderr)
        pool = conn.storagePoolLookupByName('default')

        # CPU is Available
        # current_vcpu = 0
        # vms = conn.listAllDomains(0)
        # for vm in vms:
        #     if vm.isActive() == True:
        #         current_vcpu += vm.maxVcpus()
        #     else:
        #         pass
        # MaxVcpus = conn.getMaxVcpus(None)
        # available_vcpu = MaxVcpus - current_vcpu

        FreeMem = conn.getFreeMemory() / 1024 / 1024 / 1024
        FreePoolDisk = pool.info()[3] / 1024 / 1024 / 1024
        print(str(FreeMem),str(FreePoolDisk))

        if (FreeMem > mem):
            print("The server " + server.host_name + " can define this vm")
            isGetServer = True
            break

        print("The server " + server.host_name + " can't define this vm")

    if isGetServer == False:
        print("No resource")
        return None
        # return server
    else:
        return server
