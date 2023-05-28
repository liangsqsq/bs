"""
WSGI config for DockerCloud project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

from admins.views import Allocation_init, cascade_communicate_thread, recv_thread

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DockerCloud.settings')

application = get_wsgi_application()

cascade_communicate_thread()

recv_thread()

Allocation_init()

