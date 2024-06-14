from django.urls import path
from django.contrib.auth.views import LogoutView, LoginView
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),  # 登录页面
    path('login/', views.login_view, name='login'),  # 登录页面
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),  # 登出页面
    path('register/', views.register_view, name='register'),  # 注册页面
    path('dashboard/', views.dashboard, name='dashboard'),  # 仪表盘页面
    path('dashboard2/', views.dashboard2, name='dashboard2'),  # 仪表盘2页面
    path('uinfo/', views.uinfo_view, name='uinfo'),  # 用户信息页面
    path('dialog/', views.dialog, name='dialog'),  # 对话页面
    path('dialog2/', views.dialog2, name='dialog2'),  # 对话2页面
    path('upload_audio/', views.upload_audio, name='upload_audio'),  # 上传音频页面
    path('upload_child_input/', views.upload_child_input, name='upload_child_input'),  # 上传儿童输入页面
    path('update_mood/', views.update_mood, name='update_mood'),  # 更新心情页面
    path('update_mood_pro/', views.update_mood_pro, name='update_mood_pro'),  # 更新心情进度页面
    path('upload/', views.upload_avatar, name='upload_avatar'),  # 上传头像页面
    path('show/', views.show_avatar, name='show_avatar'),  # 显示头像页面
    path('log/', views.log_view, name='log'),  # 日志页面
    path('statistics/', views.statistics_view, name='statistics')  # 统计页面
    # 其他 URL 映射
]
