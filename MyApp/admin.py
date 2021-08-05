from django.contrib import admin

# Register your models here.
# 管理django后台的一个文件，我们要在后台中看到的数据库表都需要在这里注册，后续会详细说明
# 我们这里必须手动加上一句，从我的app里models 中导入所有类*
from MyApp.models import *
# 注册 刚刚的吐槽表：admin.site.register() 是注册用的函数，里面写类名，注意是类名，并不是类本身，所以不要加()

admin.site.register(DB_tucao)
admin.site.register(DB_home_href)
admin.site.register(DB_project)
admin.site.register(DB_apis)
admin.site.register(DB_apis_log)
admin.site.register(DB_cases)
admin.site.register(DB_step)
admin.site.register(DB_project_header)
admin.site.register(DB_host)
admin.site.register(DB_project_host)
admin.site.register(DB_login)
admin.site.register(DB_global_data)