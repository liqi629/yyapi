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
from MyApp.views_tools import *


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
    re_path(r"^child/(?P<eid>.+)/(?P<oid>.*)/(?P<ooid>.*)/$",child), # 返回子页面
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
    path(r'error_request/', error_request), # 调用异常测试接口
    re_path(r"^Api_send_home/$", Api_send_home), # 首页发送请求
    re_path(r"^Home_save_api/$", Home_save_api), # 首页发送请求

    path('get_home_log/', get_home_log), # 获取最新请求记录
    path('get_api_log_home/',get_api_log_home ), # 获取完整得单一得请求记录数据
    re_path(r'^home_log/(?P<log_id>.*)/$', home), # 再次进入首页，这次带着记录
    re_path(r'^add_case/(?P<eid>.*)/$', add_case), # 用例库-添加用例
    re_path(r'^del_case/(?P<eid>.*)/(?P<oid>.*)/$', del_case), # 用例库-删除用例
    re_path(r'^copy_case/(?P<eid>.*)/(?P<oid>.*)/$', copy_case), # 用例库-复制用例
    path('get_small/', get_small), # 获取小用例步骤得列表数据
    path('add_new_step/', add_new_step), # 新增小步骤接口
    re_path('^delete_step/(?P<eid>.*)/', delete_step), # 删除小步骤接口
    path(r'get_step/', get_step), # 获取步骤得数据
    path(r'save_step/', save_step), # 保存步骤得数据
    path(r'user_upload/', user_upload), # 上传头像
    path(r'step_get_api/', step_get_api), # 步骤详情页获取接口数据。即步骤详情页选择接口，然后获取接口的数据
    path(r'Run_Case/', Run_Case), # 运行大用例
    re_path(r'^look_report/(?P<eid>.*)/$', look_report), # 查看报告
    path(r'save_project_header/', save_project_header), # 保存项目公共请求头
    path(r'save_case_name/', save_case_name), # 保存用例名称，用例库页面左侧栏
    path(r'project_get_login/', project_get_login),  # 获取项目登录态接口
    path(r'project_login_save/', project_login_save),  # 保存项目登录态接口
    path(r'project_login_send/',project_login_send), # 调试登录态接口

    #-----------------小工具------------------------
    path(r'tools_zhengjiao/',zhengjiao), # 进入小工具-正交生成
    path(r'zhengjiao_play/',zhengjiao_play), # 正交生成
    path(r'zhengjiao_excel/',zhengjiao_excel), # 正交生成excel
    path(r'tools_bianjie/',bianjie), # 进入小工具-正交生成
    path(r'bianjie_play/',bianjie_play), # 正交生成
    re_path(r'^search/$',search),#首页搜索功能

    re_path('^global_data/(?P<id>.*)/', global_data), # 进入全局变量
    path(r'global_data_add/',global_data_add), # 增加一个全局变量
    path(r'global_data_delete/',global_data_delete), # 删除全局变量
    path(r'global_data_save/',global_data_save), # 删除全局变量

    path(r'global_data_change_check/',global_data_change_check), # 更改项目的生效变量组

    # url(r'save_project_set/(?P<id>.*)/$', save_project_set),  # 保存项目设置
]
