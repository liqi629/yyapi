接口测试平台

python版本3.6.5
django版本3.1.2

使用方法：

1.安装Python3环境

2.下载代码到本地并解压

3.cmd到根目录下安装相关依赖包

pip install -r requirements.txt

4.cmd到根目录下，让 Django 知道我们在我们的模型有一些变更

python manage.py makemigrations

5.创造或修改表结构

python manage.py migrate 

6.创建超级用户，用于登录后台管理

python manage.py createsuperuser

7.运行启动django服务

python manage.py runserver 0.0.0.0:8000

8.现在就可以访问 http://127.0.0.1:8000/login 进行登录， http://127.0.0.1:8000/admin 为后台管理平台