from django.urls import path
from . import views

app_name = 'res'

urlpatterns=[
      path('getSources/', views.getSources, name='getSources'),
      path('get_node_info/', views.get_node_info, name='get_node_info'),
      path('get_res_info/', views.get_res_info, name='get_res_info'),
]