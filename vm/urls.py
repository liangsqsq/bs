from django.urls import path
from . import views

app_name = 'vm'

urlpatterns = [
    path('virtualhost/', views.virtualhost, name='virtualhost'),
    path('apply_vm/', views.apply_vm, name='apply_vm'),
    path('start_vm/', views.start_vm, name='start_vm'),
    path('shutdown_vm/', views.shutdown_vm, name='shutdown_vm'),
]
