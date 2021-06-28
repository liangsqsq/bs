import os
import sys
import django
from django.core import serializers

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DockerCloud.settings')
django.setup()

update_database_path = "/home/server-1/update_database_file"

if __name__ == '__main__':
    update_database_file = open(update_database_path, 'r')
    data = update_database_file.readlines()
    for data_ in data:
        data_ = data_[:len(data_)-1]
        obj = serializers.deserialize("json", data_)
        for obj_ in obj:
            obj_.save()
    update_database_file.close()