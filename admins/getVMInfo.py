import libvirt
from xml.dom import minidom


def getVMInfo(domain, storagePool):
    state, maxmem, mem, cpus, cput = domain.info()

    # flag: is domain active
    isActive = domain.isActive()
    if isActive == True:
        pass
    else:
        isActive == False
    isPersistent = domain.isPersistent()
    if isPersistent == True:
        pass
    else:
        isPersistent == False

    raw_xml = domain.XMLDesc(0)
    xml = minidom.parseString(raw_xml)
    diskTypes = xml.getElementsByTagName('disk')

    # get domain volume name and type
    for diskType in diskTypes:
        if diskType.getAttribute('device') == 'disk':
            diskNodes = diskType.childNodes
            for diskNode in diskNodes:
                if diskNode.nodeName == 'driver':
                    for attr in diskNode.attributes.keys():
                        if diskNode.attributes[attr].name == 'type':
                            format_type = diskNode.attributes[attr].value  # format_type:qcow2/raw/...
                            # print(format_type)
                            break
                elif diskNode.nodeName == 'source':
                    for attr in diskNode.attributes.keys():
                        if diskNode.attributes[attr].name == 'file':
                            vol_name = diskNode.attributes[attr].value.split("/")[-1]  # volume name
                            # print(vol_name)
                            break
                else:
                    pass
        else:
            pass

    try:
        vol = storagePool.storageVolLookupByName(vol_name)
        info = vol.info()
        diskSize = int(info[1] / 1024 / 1024 / 1024)
        diskAllocation = int(info[2] / 1024 / 1024 / 1024)

        return isActive, isPersistent, cpus, int(maxmem / 1024 / 1024), diskSize, diskAllocation, format_type
    except:
        print('error:' + vol_name)
        diskSize = 0
        diskAllocation = 0
        return isActive, isPersistent, cpus, int(maxmem / 1024 / 1024), diskSize, diskAllocation, format_type
