import os
import sys
import django
from django.core import serializers

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DockerCloud.settings')
django.setup()

from vm.models import *
from container.models import *
from res.models import *

max_info_path = "/home/server-1/max_info"
update_database_path = "/home/server-1/update_database_file"

def get_right_info(kword):
    max_info_file = open(max_info_path, 'r')
    max_info_lines = max_info_file.readlines()
    number = 0
    for line in max_info_lines:
        if line.find(kword) != -1:
            y_index = line.find(":")
            number = line[y_index+1: len(line)-1]
            if number == "None":
                number = 0
            break
    max_info_file.close()
    return int(number)

def update_database():
    # update the img
    vm_os_max = get_right_info("vm_vm_os")
    vm_oss_find = vm_os.objects.all()
    for vm_os_ in vm_oss_find:
        vm_os_.id += vm_os_max

    data = serializers.serialize("json", vm_oss_find)
    update_database_file.write(data + "\n")

    # update the docker img
    docker_img_max = get_right_info("container_docker_img")
    docker_imgs_find = docker_img.objects.all()
    for docker_img_ in docker_imgs_find:
        docker_img_.id += docker_img_max

    data = serializers.serialize("json", docker_imgs_find)
    update_database_file.write(data + "\n")

    domain_list = []
    new_vm_apply_list = []
    workstation_list = []
    vm_list = []
    deploy_apply_list = []
    port_apply_list = []
    vm_available_list = []
    new_docker_apply_list = []
    docker_node_list = []
    container_list = []
    container_available_list = []

    # update the domain
    domain_max = get_right_info("vm_domain")
    # print(domain_max)
    domains_find = domain.objects.all()
    for domain_ in domains_find:
        # update the vm_apply
        new_vm_apply_max = get_right_info("vm_new_vm_apply")
        new_vm_applys_find = new_vm_apply.objects.filter(region_id=domain_.id)
        for new_vm_apply_ in new_vm_applys_find:
            new_vm_apply_.id += new_vm_apply_max
            new_vm_apply_.region_id += domain_max
            new_vm_apply_.os_version_id += vm_os_max
        new_vm_apply_list.append(new_vm_applys_find)

        # update the workstation
        workstations_max = get_right_info("vm_workstation")
        workstations_find = workstation.objects.filter(belong_id=domain_.id)
        for workstation_ in workstations_find:
            # update the vm
            vm_max = get_right_info("vm_vm")
            vms_find = vm.objects.filter(belong_id=workstation_.id)
            for vm_ in vms_find:
                # update the deploy_apply
                deploy_apply_max = get_right_info("vm_deploy_apply")
                deploy_applys_find = deploy_apply.objects.filter(vm_id=vm_.id)
                for deploy_apply_ in deploy_applys_find:
                    deploy_apply_.id += deploy_apply_max
                    deploy_apply_.vm_id += vm_max
                deploy_apply_list.append(deploy_applys_find)

                # update the port_apply
                port_apply_max = get_right_info("vm_port_apply")
                port_applys_find = port_apply.objects.filter(vm_id=vm_.id)
                for port_apply_ in port_applys_find:
                    port_apply_.id += port_apply_max
                    port_apply_.vm_id += vm_max
                port_apply_list.append(port_applys_find)

                vm_.id += vm_max
                vm_.belong_id += workstations_max
                vm_.os_id += vm_os_max
                vm_.region_id += domain_max
            vm_list.append(vms_find)

            workstation_.id += workstations_max
            workstation_.belong_id += domain_max

            # update the vm_available
            vm_available_max = get_right_info("vm_vm_available")
            vm_availables_find = vm_available.objects.filter(belong_id=workstation_.id)
            for vm_available_ in vm_availables_find:
                vm_available_.id += vm_available_max
                vm_available_.belong_id += workstations_max
                vm_available_.os_id += vm_os_max
                vm_available_.region_id += domain_max
            vm_available_list.append(vm_availables_find)

        workstation_list.append(workstations_find)

        # update the new_docker_apply
        new_docker_apply_max = get_right_info("container_new_docker_apply")
        new_docker_applys_find = new_docker_apply.objects.filter(regionID_id=domain_.id)
        for new_docker_apply_ in new_docker_applys_find:
            new_docker_apply_.id += new_docker_apply_max
            new_docker_apply_.img_version_id += docker_img_max
            new_docker_apply_.regionID_id += domain_max
        new_docker_apply_list.append(new_docker_applys_find)

        # update the docker node
        docker_node_max = get_right_info("container_docker_node")
        docker_nodes_find = docker_node.objects.filter(belong_id=domain_.id)
        for docker_node_ in docker_nodes_find:
            # update the container
            container_max = get_right_info("container_container")
            containers_find = container.objects.filter(node_id=docker_node_.id)
            for container_ in containers_find:
                container_.id += container_max
                container_.img_id += docker_img_max
                container_.node_id += docker_node_max
                container_.region_id += domain_max
            container_list.append(containers_find)

            # update the container_available
            container_available_max = get_right_info("container_container_available")
            container_availables_find = container_available.objects.filter(node_id=docker_node_.id)
            for container_available_ in container_availables_find:
                container_available_.id += container_available_max
                container_available_.img_id += docker_img_max
                container_available_.node_id += docker_node_max
                container_available_.region_id += domain_max
            container_available_list.append(container_availables_find)

            docker_node_.id += docker_node_max
            docker_node_.belong_id += domain_max
        docker_node_list.append(docker_nodes_find)

        domain_.id += domain_max
    domain_list.append(domains_find)

    for item in domain_list:
        data = serializers.serialize("json", item)
        update_database_file.write(data + "\n")

    for item in new_vm_apply_list:
        data = serializers.serialize("json", item)
        update_database_file.write(data + "\n")

    for item in workstation_list:
        data = serializers.serialize("json", item)
        update_database_file.write(data + "\n")

    for item in vm_list:
        data = serializers.serialize("json", item)
        update_database_file.write(data + "\n")

    for item in deploy_apply_list:
        data = serializers.serialize("json", item)
        update_database_file.write(data + "\n")

    for item in port_apply_list:
        data = serializers.serialize("json", item)
        update_database_file.write(data + "\n")

    for item in vm_available_list:
        data = serializers.serialize("json", item)
        update_database_file.write(data + "\n")

    for item in new_docker_apply_list:
        data = serializers.serialize("json", item)
        update_database_file.write(data + "\n")

    for item in docker_node_list:
        data = serializers.serialize("json", item)
        update_database_file.write(data + "\n")

    for item in container_list:
        data = serializers.serialize("json", item)
        update_database_file.write(data + "\n")

    for item in container_available_list:
        data = serializers.serialize("json", item)
        update_database_file.write(data + "\n")

    class_1_max = get_right_info("res_classes_1")
    class_2_max = get_right_info("res_classes_2")
    class_3_max = get_right_info("res_classes_3")
    classes_find = classes.objects.all()
    for classes_ in classes_find:
        if classes_.class_name == 1:
            classes_.number += class_1_max
        elif classes_.class_name == 2:
            classes_.number += class_2_max
        else:
            classes_.number += class_3_max

    data = serializers.serialize("json", classes_find)
    update_database_file.write(data + "\n")

    model_101_max = get_right_info("res_model_101")
    model_102_max = get_right_info("res_model_102")
    model_103_max = get_right_info("res_model_103")
    model_104_max = get_right_info("res_model_104")
    model_105_max = get_right_info("res_model_105")
    model_106_max = get_right_info("res_model_106")
    model_201_max = get_right_info("res_model_201")
    model_202_max = get_right_info("res_model_202")
    model_203_max = get_right_info("res_model_203")
    model_204_max = get_right_info("res_model_204")
    model_205_max = get_right_info("res_model_205")
    model_206_max = get_right_info("res_model_206")
    model_301_max = get_right_info("res_model_301")
    model_302_max = get_right_info("res_model_302")
    models_find = model.objects.all()
    for model_ in models_find:
        if model_.model_name == 101:
            model_.number += model_101_max
        elif model_.model_name == 102:
            model_.number += model_102_max
        elif model_.model_name == 103:
            model_.number += model_103_max
        elif model_.model_name == 104:
            model_.number += model_104_max
        elif model_.model_name == 105:
            model_.number += model_105_max
        elif model_.model_name == 106:
            model_.number += model_106_max
        elif model_.model_name == 201:
            model_.number += model_201_max
        elif model_.model_name == 202:
            model_.number += model_202_max
        elif model_.model_name == 203:
            model_.number += model_203_max
        elif model_.model_name == 204:
            model_.number += model_204_max
        elif model_.model_name == 205:
            model_.number += model_205_max
        elif model_.model_name == 206:
            model_.number += model_206_max
        elif model_.model_name == 301:
            model_.number += model_301_max
        else:
            model_.number += model_302_max

    data = serializers.serialize("json", models_find)
    update_database_file.write(data + "\n")

    transfer_max = get_right_info("res_transfer")
    transfers_find = transfer.objects.all()
    for transfer_ in transfers_find:
        transfer_.id += transfer_max

    data = serializers.serialize("json", transfers_find)
    update_database_file.write(data + "\n")

if __name__ == '__main__':
    update_database_file = open(update_database_path, 'w')
    update_database()
    update_database_file.close()
