from django.urls import path
from . import views

app_name = 'users'

urlpatterns=[
    path('login/', views.loginv, name='login'),
    path('regist/', views.register, name='regist'),
    path('logout/', views.logoutv, name='logout'),
    path('username/', views.is_user_exist, name='is_user_exist'),
    path('usercontrol/', views.user_control, name='usercontrol'),
    path('vnc/', views.show_vnc, name='vnc'),
    path('applydeploy/', views.applydeploy, name='applydeploy'),
    path('applyport/', views.applyport, name='applyport'),
    path('user_info/', views.user_info, name='user_info'),
    path('updateUserInfo/', views.updateUserInfo, name='updateUserInfo'),
    path('useremail/',views.useremail,name='useremail'),
    path('vmcheck/',views.vmcheck,name='vmcheck'),
    path('portRecords/',views.portRecords,name='portRecords'),
    path('configurationRecords/',views.configurationRecords,name='configurationRecords'),
    path('forget/',views.forget,name='forget'),
    path('forgetemail/',views.forgetemail,name='forgetemail'),
    path('changepwd/',views.changepwd,name='changepwd'),
    path('change/',views.change,name='change'),
    path('importvm/',views.importvm,name='importvm'),
    path('regetVMIP/',views.regetVMIP,name='regetVMIP'),
    path('snapshotlist/',views.snapshotlist,name='snapshotlist'),
    path('snapshotRevert/',views.snapshotRevert,name='snapshotRevert'),
    path('user_changePwd/', views.user_changePwd, name='user_changePwd'),
    path('container_list/',views.container_list,name='container_list'),
    path('regetVMIP/',views.regetVMIP,name='regetVMIP'),
    path('snapshotlist/',views.snapshotlist,name='snapshotlist'),
    path('snapshotRevert/',views.snapshotRevert,name='snapshotRevert'),
    path('user_changePwd/', views.user_changePwd, name='user_changePwd'),
]