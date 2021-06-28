from django.urls import path
from . import views

app_name = 'container'

urlpatterns=[
   path('dockerslelect/', views.dockerselect, name='dockerselect'),
   path('add_dockerNode/', views.add_dockerNode, name='add_dockerNode'),
   path('apply_docker/', views.apply_docker, name='apply_docker'),
   path('add_dockerImg/',views.add_dockerImg,name='add_dockerImg'),
   path('docker_verify/<pindex>',views.docker_verify,name='docker_verify'),
#   path('agree_dockers/', views.agree_dockers, name='agree_dockers'),
   path('agree_docker/',views.agree_docker,name='agree_docker'),
   path('refuse_docker/',views.refuse_docker,name='refuse_docker'),
   path('container_manage/<pindex>',views.container_manage,name='container_manage'),
   path('container_delete/',views.container_delete,name='container_delete'),
   path('container_shutdown/',views.container_shutdown,name='container_shutdown'),
   path('container_start/',views.container_start,name='container_start'),
   path('container_restart/',views.container_restart,name='container_restart'),
   path('clear_volume/',views.clear_volume,name='clear_volume'),
   path('container_details/',views.container_details,name='container_details'),
   path('docker_verify_request/', views.docker_verify_request, name='docker_verify_request'),
   path('container_manage_request/', views.container_manage_request, name='container_manage_request'),
   path('add_dockerNode_request/', views.add_dockerNode_request, name='add_dockerNode_request'),
   path('add_dockerImg_request/', views.add_dockerImg_request, name='add_dockerImg_request'),
]
