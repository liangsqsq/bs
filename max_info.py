import os
import sys
import django
from django.core import serializers
from django.db.models import Max

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DockerCloud.settings')
django.setup()

from vm.models import *
from container.models import *
from res.models import *

file_path = "/home/server-1/max_info"

def get_max(file_path):
    vm_deploy_apply = deploy_apply.objects.aggregate(Max('id'))['id__max']
    vm_domain = domain.objects.aggregate(Max('id'))['id__max']
    vm_new_vm_apply = new_vm_apply.objects.aggregate(Max('id'))['id__max']
    vm_port_apply = port_apply.objects.aggregate(Max('id'))['id__max']
    vm_vm = vm.objects.aggregate(Max('id'))['id__max']
    vm_vm_available = vm_available.objects.aggregate(Max('id'))['id__max']
    vm_vm_os = vm_os.objects.aggregate(Max('id'))['id__max']
    vm_workstation = workstation.objects.aggregate(Max('id'))['id__max']

    container_container = container.objects.aggregate(Max('id'))['id__max']
    container_container_available = container_available.objects.aggregate(Max('id'))['id__max']
    container_docker_img = docker_img.objects.aggregate(Max('id'))['id__max']
    container_docker_node = docker_node.objects.aggregate(Max('id'))['id__max']
    container_docker_node_available = docker_node_available.objects.aggregate(Max('id'))['id__max']
    container_new_docker_apply = new_docker_apply.objects.aggregate(Max('id'))['id__max']

    res_classes_1 = classes.objects.get(class_name=1).number
    res_classes_2 = classes.objects.get(class_name=2).number
    res_classes_3 = classes.objects.get(class_name=3).number
    res_model_101 = model.objects.get(model_name=101).number
    res_model_102 = model.objects.get(model_name=102).number
    res_model_103 = model.objects.get(model_name=103).number
    res_model_104 = model.objects.get(model_name=104).number
    res_model_105 = model.objects.get(model_name=105).number
    res_model_106 = model.objects.get(model_name=106).number
    res_model_201 = model.objects.get(model_name=201).number
    res_model_202 = model.objects.get(model_name=202).number
    res_model_203 = model.objects.get(model_name=203).number
    res_model_204 = model.objects.get(model_name=204).number
    res_model_205 = model.objects.get(model_name=205).number
    res_model_206 = model.objects.get(model_name=206).number
    res_model_301 = model.objects.get(model_name=301).number
    res_model_302 = model.objects.get(model_name=302).number

    res_transfer = transfer.objects.aggregate(Max('id'))['id__max']

    max_info_file = open(file_path, 'w')
    max_info_file.write("vm_deploy_apply:" + str(vm_deploy_apply) + "\n")
    max_info_file.write("vm_domain:" + str(vm_domain) + "\n")
    max_info_file.write("vm_new_vm_apply:" + str(vm_new_vm_apply) + "\n")
    max_info_file.write("vm_port_apply:" + str(vm_port_apply) + "\n")
    max_info_file.write("vm_vm:" + str(vm_vm) + "\n")
    max_info_file.write("vm_vm_available:" + str(vm_vm_available) + "\n")
    max_info_file.write("vm_vm_os:" + str(vm_vm_os) + "\n")
    max_info_file.write("vm_workstation:" + str(vm_workstation) + "\n")
    max_info_file.write("container_container:" + str(container_container) + "\n")
    max_info_file.write("container_container_available:" + str(container_container_available) + "\n")
    max_info_file.write("container_docker_img:" + str(container_docker_img) + "\n")
    max_info_file.write("container_docker_node:" + str(container_docker_node) + "\n")
    max_info_file.write("container_docker_node_available:" + str(container_docker_node_available) + "\n")
    max_info_file.write("container_new_docker_apply:" + str(container_new_docker_apply) + "\n")
    max_info_file.write("res_classes_1:" + str(res_classes_1) + "\n")
    max_info_file.write("res_classes_2:" + str(res_classes_2) + "\n")
    max_info_file.write("res_classes_3:" + str(res_classes_3) + "\n")
    max_info_file.write("res_model_101:" + str(res_model_101) + "\n")
    max_info_file.write("res_model_102:" + str(res_model_102) + "\n")
    max_info_file.write("res_model_103:" + str(res_model_103) + "\n")
    max_info_file.write("res_model_104:" + str(res_model_104) + "\n")
    max_info_file.write("res_model_105:" + str(res_model_105) + "\n")
    max_info_file.write("res_model_106:" + str(res_model_106) + "\n")
    max_info_file.write("res_model_201:" + str(res_model_201) + "\n")
    max_info_file.write("res_model_202:" + str(res_model_202) + "\n")
    max_info_file.write("res_model_203:" + str(res_model_203) + "\n")
    max_info_file.write("res_model_204:" + str(res_model_204) + "\n")
    max_info_file.write("res_model_205:" + str(res_model_205) + "\n")
    max_info_file.write("res_model_206:" + str(res_model_206) + "\n")
    max_info_file.write("res_model_301:" + str(res_model_301) + "\n")
    max_info_file.write("res_model_302:" + str(res_model_302) + "\n")
    max_info_file.write("res_transfer:" + str(res_transfer) + "\n")

    max_info_file.close()
if __name__ == '__main__':
    get_max()
