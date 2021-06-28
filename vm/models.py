from django.db import models
from users.models import UserProfile

from django.utils import timezone

# Create your models here.
class domain(models.Model):
    domain = models.CharField(max_length=50)
    location = models.CharField(max_length=100)
    gw_ip = models.GenericIPAddressField()
    port = models.IntegerField()
    user = models.CharField(max_length=20, null=True)
    pwd = models.CharField(max_length=20, null=True)
    state = models.BooleanField(default=True)
    vt_type = models.CharField(max_length=20,default='KVM')
    deploy_time = models.DateTimeField(default=timezone.now)
    sync_time = models.DateTimeField(null=True, default=None)
    home_dir = models.CharField(max_length=30, null=True)



class workstation(models.Model):
    host_name = models.CharField(max_length=20)
    ip = models.GenericIPAddressField()
    ssh_port = models.IntegerField()
    user = models.CharField(max_length=20, null=True)
    pwd = models.CharField(max_length=20, null=True)
    belong = models.ForeignKey(domain, on_delete=models.PROTECT)
    deploy_time = models.DateTimeField(default=timezone.now)
    home_dir = models.CharField(max_length=30, null=True)
    state = models.BooleanField(default=True)
    is_zabbix = models.BooleanField(default=False, null=False)


class vm_os(models.Model):
    os_version = models.CharField(max_length=30)
    iso_path = models.CharField(max_length=100, null=True)
    template_path = models.CharField(max_length=100, null=True)
    default_user = models.CharField(max_length=15, null=True, default=None)
    default_pwd = models.CharField(max_length=30, null=True, default=None)
    default_port = models.IntegerField(null=True, default=None)


class new_vm_apply(models.Model):
    user = models.ForeignKey(UserProfile,on_delete=models.PROTECT)
    gateway_ip = models.GenericIPAddressField()
    region = models.ForeignKey(domain,on_delete=models.PROTECT)
    os_version = models.ForeignKey(vm_os,on_delete=models.PROTECT)
    cpu_cores = models.IntegerField()
    memory = models.IntegerField()
    disk = models.IntegerField()
    password = models.CharField(max_length=50)
    apply_time = models.DateTimeField(default=timezone.now)
    state = models.IntegerField(default=0,
                                help_text=('0:no deal;1:agree;2:refuse;'))
    isPersistent = models.BooleanField(default=True,
                                       help_text=('true:persistent;false:transitent'))
    installway = models.CharField(max_length=10, default='clone')
    classes = models.IntegerField(null=True)
    model = models.IntegerField(null=True)


class vm(models.Model):
    belong = models.ForeignKey(workstation, on_delete=models.PROTECT)
    # uuid = models.CharField(max_length=60, null=True)
    name = models.CharField(max_length=50, null=True)
    os = models.ForeignKey(vm_os, on_delete=models.PROTECT)
    vCPUs = models.IntegerField(default=0)
    memory = models.IntegerField(default=0)
    diskSize = models.IntegerField(default=0)
    diskAllocation = models.IntegerField(null=True)
    diskType = models.CharField(max_length=20, default='qcow2')
    ip = models.GenericIPAddressField(null=True)
    gateway_ip = models.GenericIPAddressField()
    region = models.ForeignKey(domain, on_delete=models.PROTECT)
    os_version = models.CharField(max_length=50, null=True)
    password = models.CharField(max_length=100, null=True)
    user = models.ForeignKey(UserProfile, on_delete=models.PROTECT)
    apply_time = models.DateTimeField(null=True)
    start_time = models.DateTimeField(default=timezone.now, null=True)
    power_state = models.CharField(max_length=20, null=True, default='running')
    state = models.BooleanField(default=True,
                                help_text=('true:normal; false:not using or will be recycle'))
    is_del = models.BooleanField(default=False,
                                 help_text=('true:not deleted; false:deleted'))
    noVNC_port = models.IntegerField(null=True)
    isPersistent = models.BooleanField(default=True,
                                       help_text=('true:persistent;false:transitent'))
    conn_port = models.IntegerField(null=True, default=None)

class vm_available(models.Model):
    belong = models.ForeignKey(workstation, on_delete=models.PROTECT)
    # uuid = models.CharField(max_length=60, null=True)
    name = models.CharField(max_length=50, null=True)
    os = models.ForeignKey(vm_os, on_delete=models.PROTECT)
    vCPUs = models.IntegerField(default=0)
    memory = models.IntegerField(default=0)
    diskSize = models.IntegerField(default=0)
    diskAllocation = models.IntegerField(null=True)
    diskType = models.CharField(max_length=20, default='qcow2')
    ip = models.GenericIPAddressField(null=True)
    gateway_ip = models.GenericIPAddressField()
    region = models.ForeignKey(domain, on_delete=models.PROTECT)
    os_version = models.CharField(max_length=50, null=True)
    password = models.CharField(max_length=100, null=True)
    user = models.ForeignKey(UserProfile, on_delete=models.PROTECT)
    apply_time = models.DateTimeField(null=True)
    start_time = models.DateTimeField(default=timezone.now, null=True)
    power_state = models.CharField(max_length=20, null=True, default='running')
    state = models.BooleanField(default=True,
                                help_text=('true:normal; false:not using or will be recycle'))
    is_del = models.BooleanField(default=False,
                                 help_text=('true:not deleted; false:deleted'))
    noVNC_port = models.IntegerField(null=True)
    isPersistent = models.BooleanField(default=True,
                                       help_text=('true:persistent;false:transitent'))
    conn_port = models.IntegerField(null=True, default=None)


class deploy_apply(models.Model):
    vm = models.ForeignKey(vm, on_delete=models.CASCADE)
    vCPUs = models.IntegerField(default=0)
    memory = models.IntegerField(default=0)
    diskSize = models.IntegerField(default=0)
    apply_time = models.DateTimeField(default=timezone.now)
    operate_time = models.DateTimeField(null=True, default=None)
    state = models.IntegerField(default=0,
                                help_text=('0:no deal;1:agree;2:refuse;'))
    user = models.ForeignKey(UserProfile,on_delete=models.PROTECT)


class port_apply(models.Model):
    vm = models.ForeignKey(vm, on_delete=models.CASCADE)
    vmPort = models.IntegerField()
    mapPort = models.IntegerField(null=True, default=None)
    apply_time = models.DateTimeField(default=timezone.now)
    operate_time = models.DateTimeField(null=True, default=None)
    state = models.IntegerField(default=0,
                                help_text=('0:no deal;1:agree;2:refuse;3:delete'))
    user = models.ForeignKey(UserProfile,on_delete=models.PROTECT)

class snapshot(models.Model):
    snapshotName= models.CharField(max_length=50, null=True)
    vmname =models.ForeignKey(vm,on_delete=models.PROTECT)
    username=models.ForeignKey(UserProfile,on_delete=models.PROTECT)
    snapshotId=models.CharField(max_length=50,null=True)
    start_time = models.DateTimeField(default=timezone.now, null=True)
    is_exist = models.BooleanField(default=True,
                                 help_text=('true:not deleted; false:deleted'))

class cascade_list(models.Model):
    ip = models.GenericIPAddressField()
    port = models.IntegerField()
    is_communicate = models.BooleanField(default=False, null=True, help_text=(
        'false: no communicate; true: communicate'
    ))
    is_self = models.BooleanField(default=False, help_text=(
        'false: is not the ip of mine, true: is the ip of mine'
    ))
    is_master = models.BooleanField(default=False, null=True, help_text=(
        'false: is not the master of the cascade, true: is the master of the cascade'
    ))
    is_ping = models.BooleanField(default=False, null=True, help_text=(
        'false: no ping, true: ping'
    ))

class apply_node(models.Model):
    host_name = models.CharField(max_length=20)
    ip = models.GenericIPAddressField()
    ssh_port = models.IntegerField(null=True)
    user = models.CharField(max_length=20, null=True)
    pwd = models.CharField(max_length=20, null=True)
    belong = models.ForeignKey(domain, on_delete=models.PROTECT, null=True)
    deploy_time = models.DateTimeField(default=timezone.now)
    home_dir = models.CharField(max_length=30, null=True)
    state = models.IntegerField(default=0,
                                help_text=('0:no deal;1:agree'))
