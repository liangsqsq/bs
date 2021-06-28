from django.db import models

from django.utils import timezone
from vm.models import domain
from users.models import UserProfile

class docker_img(models.Model):
    img_name=models.CharField(max_length=50,null=True)
    mountPoint=models.CharField(max_length=100,null=True)
    underSystem=models.CharField(max_length=50,null=True)
    port= models.CharField(max_length=100,null=True)
    command=models.CharField(max_length=100,null=True)
    repository = models.CharField(max_length=50,null=True)
    tag = models.CharField(max_length=20,null=True)
    deploy_time = models.DateTimeField(default=timezone.now)


class docker_node(models.Model):
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

class new_docker_apply(models.Model):
    username = models.ForeignKey(UserProfile,on_delete=models.PROTECT)
    gateway_ip = models.GenericIPAddressField()
    region_name = models.CharField(max_length=20, null=True)
    img_version = models.ForeignKey(docker_img,on_delete=models.PROTECT)
    cpu_cores = models.IntegerField()
    memory = models.FloatField()
    apply_time = models.DateTimeField(default=timezone.now)
    #节点IP
    domain_node=models.CharField(max_length=20, null=True)
    state = models.IntegerField(default=0,
                                help_text=('0:no deal;1:agree;2:refuse;'))
    classes = models.IntegerField(null=True)
    model = models.IntegerField(null=True)

class container(models.Model):
    Only_Id=models.CharField(max_length=240,null=True)
    name=models.CharField(max_length=50,null=True)
    port= models.CharField(max_length=100,null=True)
    user = models.ForeignKey(UserProfile,on_delete=models.PROTECT)
    cpu_cores = models.IntegerField()
    memory = models.FloatField()
    mountPoint=models.CharField(max_length=254,null=True)
    volume_name=models.CharField(max_length=254,null=True)
    img=models.ForeignKey(docker_img,on_delete=models.PROTECT)
    region=models.ForeignKey(domain,on_delete=models.PROTECT)
    node=models.ForeignKey(docker_node,on_delete=models.PROTECT)
    state=models.IntegerField(default=0,
                                help_text=('0:running;1:stop;'))
    is_del = models.BooleanField(default=False,
                                 help_text=('true:not deleted; false:deleted'))
    start_time = models.DateTimeField(default=timezone.now, null=True)

class container_available(models.Model):
    Only_Id = models.CharField(max_length=240, null=True)
    name = models.CharField(max_length=50, null=True)
    port = models.CharField(max_length=100, null=True)
    user = models.ForeignKey(UserProfile, on_delete=models.PROTECT)
    cpu_cores = models.IntegerField()
    memory = models.FloatField()
    mountPoint = models.CharField(max_length=254, null=True)
    volume_name = models.CharField(max_length=254, null=True)
    img = models.ForeignKey(docker_img, on_delete=models.PROTECT)
    region = models.ForeignKey(domain, on_delete=models.PROTECT)
    node = models.ForeignKey(docker_node, on_delete=models.PROTECT)
    state = models.IntegerField(default=0,
                                help_text=('0:running;1:stop;'))
    is_del = models.BooleanField(default=False,
                                 help_text=('true:not deleted; false:deleted'))
    start_time = models.DateTimeField(default=timezone.now, null=True)

class docker_node_available(models.Model):
    host_name = models.CharField(max_length=20)
    ip = models.CharField(max_length=39)
    ssh_port = models.IntegerField()
    user = models.CharField(max_length=20, null=True)
    pwd = models.CharField(max_length=20, null=True)
    home_dir = models.CharField(max_length=20, null=True)

