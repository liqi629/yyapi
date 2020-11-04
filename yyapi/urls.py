"""yyapi URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.urls import path, re_path

from MyApp.views import *


"""
Django1.1.x 版本
url() 方法：普通路径和正则路径均可使用，需要自己手动添加正则首位限制符号。
$ 匹配输入字符串的结尾位置
^ 匹配输入字符串的开始位置
实例
from django.conf.urls import url # 用 url 需要引入

urlpatterns = [
    url(r'^admin/$', admin.site.urls),
    url(r'^index/$', views.index), # 普通路径
    url(r'^articles/([0-9]{4})/$', views.articles), # 正则路径
]


Django 2.2.x 之后的版本
path：用于普通路径，不需要自己手动添加正则首位限制符号，底层已经添加。
re_path：用于正则路径，需要自己手动添加正则首位限制符号。
"""


urlpatterns = [
    path('admin/', admin.site.urls),
    path('welcome/', welcome), #进入欢迎页
    path('home/', home), #进入主页
    re_path(r"^child/(?P<eid>.+)/(?P<oid>.*)/$", child), # 返回子页面
    path('login/', login), #进入登录页
    path('login_action/', login_action), # 登录 动作
    path('register_action/', register_action), # 注册
    re_path(r'^accounts/login/$', login), # 非登录状态，自动跳回登录页面
    path('logout/', logout), # 退出
    path('pei/', pei), # 匿名吐槽
    path('help/', api_help), # 进入到帮助文档
    path('project_list/', project_list), # 进入到项目列表
    path('delete_project/', delete_project), # 删除项目
    path('add_project/', add_project), # 新增项目
    # 这里的id 是在url中的，所以要用正则的写法去代表。大家注意这里一定不要写错，否则404
    re_path('^apis/(?P<id>.*)/$', open_apis), # 进入接口库
    re_path('^cases/(?P<id>.*)/$', open_cases), # 进入用例设置
    re_path('^project_set/(?P<id>.*)/$', open_project_set), # 进入项目设置
    re_path(r'^save_project_set/(?P<id>.*)/$', save_project_set), # 保存项目设置
    re_path(r'^project_api_add/(?P<Pid>.*)/$', project_api_add), # 新增接口
    re_path(r'^project_api_del/(?P<id>.*)', project_api_del), # 删除接口
    path('save_bz/', save_bz), # 保存备注
    path('get_bz/', get_bz), # 获取备注
    re_path(r'^Api_save/$', Api_save), # 保存接口
    re_path(r'^get_api_data/$', get_api_data), # 获取接口数据
    re_path(r"^Api_send/$", Api_send), # 调试层发送请求
    path(r'copy_api/', copy_api),  # 复制接口

    # url(r'save_project_set/(?P<id>.*)/$', save_project_set),  # 保存项目设置
]
