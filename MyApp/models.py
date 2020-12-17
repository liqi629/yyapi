from django.db import models


# Create your models here.
# 是用来设置数据库格式的，django采用的是orm方式来和数据库进行交互，默认使用sqlite3轻量级的数据库
# 到这里我们 已经完成大半。接下来就是用命令，操作manage.py这个管家，让他去按照我刚刚写的这个类 去操作sqlite3数据库吧。要是已经有这个吐槽表就更新，没有就创建。
# 这里需要用到的俩个命令，我们在前文已经用过了，就是在创建超级管理员的时候的俩条命令：同步表结构并生效：makemigrations 和 migrate


class DB_tucao(models.Model):
    """
    表明我们最好有点特殊风格和标准，以免我们后续调用时分不清这是个orm映射类 还是普通的类，我就在前面写DB_。必须继承models.Model,这样django才会把它当作orm的映射类来真实的去操作sqlite3
    按照此格式，调用models下的各种方法定义字段。括号内就是约束条件。
    CharField 是字符串。DateTimeField是时间。max_length是最大允许长度，null=True ，是允许为Null, auto_now ,是自动填入时间无需我们手动填入了。
    关于这里其实有几十种不同的格式之多，我们可以百度orm 字段方法来获取其他的，不过我们目前讲的只用到来字符串最多。
    """
    user = models.CharField(max_length=30, null=True)  # 吐槽人名字
    text = models.CharField(max_length=1000, null=True)  # 吐槽内容
    ctime = models.DateTimeField(auto_now=True)  # 创建时间

    def __str__(self):
        """
        我们在admin后台 想要操作数据库，里面的具体记录列表 并不会像mysql的客户端一样，显示所有内容，是需要我们自定义的去设计要显示什么，理解起来就像 我们要在这个__str__函数内设计一个view视图。
        return self.text 就是创建一个视图，让我们之后在后台管理平台，这个表的内容时，先显示text 也就是吐槽内容，然后我们点进去就可以看到全部内容了。
        + str(self.ctime)就是它顺便在后面显示创建的时间。为啥不看用户名呢？因为这并不是我们所关心的，要想看可以到时候点进去边界页面看所有详细信息。
        :return:
        """
        return self.text + str(self.ctime)


class DB_home_href(models.Model):
    name = models.CharField(max_length=30, null=True)  # 超链接名字
    href = models.CharField(max_length=2000, null=True)  # 超链接内容

    def __str__(self):
        return self.name


class DB_project(models.Model):
    name = models.CharField(max_length=100, null=True)  # 项目的名字
    remark = models.CharField(max_length=1000, null=True)  # 项目备注
    user = models.CharField(max_length=15, null=True)  # 项目创建者的名字
    other_user = models.CharField(max_length=200, null=True)  # 项目其他的创建者

    def __str__(self):
        return self.name


class DB_apis(models.Model):
    project_id = models.CharField(max_length=10,null=True) #项目id
    name =  models.CharField(max_length=100,null=True) #接口名字
    api_method =  models.CharField(max_length=10,null=True) #请求方式
    api_url =  models.CharField(max_length=1000,null=True) #url
    api_header =  models.CharField(max_length=1000,null=True) #请求头
    api_login =  models.CharField(max_length=10,null=True) #是否带登陆态
    api_host =  models.CharField(max_length=100,null=True) #域名
    des =  models.CharField(max_length=100,null=True) #描述
    body_method =  models.CharField(max_length=20,null=True) #请求体编码格式
    api_body =  models.CharField(max_length=1000,null=True) #请求体
    result =  models.TextField(null=True) #返回体 因为长度巨大，所以用大文本方式存储
    sign =  models.CharField(max_length=10,null=True) #是否验签
    file_key =  models.CharField(max_length=50,null=True) #文件key
    file_name =  models.CharField(max_length=50,null=True) #文件名
    public_header =  models.CharField(max_length=1000,null=True) #全局变量-请求头

    last_body_method = models.CharField(max_length=20, null=True) # 上次请求体编码格式
    last_api_body = models.CharField(max_length=1000, null=True) # 上次请求体
    def __str__(self):
        return self.name


class DB_apis_log(models.Model):
    """
    存储用户的请求记录
    """
    user_id = models.CharField(max_length=10,null=True) #所属用户id

    api_method =  models.CharField(max_length=10,null=True) #请求方式
    api_url =  models.CharField(max_length=1000,null=True) #url
    api_header =  models.CharField(max_length=1000,null=True) #请求头
    api_login =  models.CharField(max_length=10,null=True) #是否带登陆态
    api_host =  models.CharField(max_length=100,null=True) #域名

    body_method =  models.CharField(max_length=20,null=True) #请求体编码格式
    api_body =  models.CharField(max_length=1000,null=True) #请求体
    sign =  models.CharField(max_length=10,null=True) #是否验签
    file_key =  models.CharField(max_length=50,null=True) #文件key
    file_name =  models.CharField(max_length=50,null=True) #文件名

    def __str__(self):
        return self.api_url


class DB_cases(models.Model):
    project_id = models.CharField(verbose_name="所属项目id", max_length=10, null=True)
    name = models.CharField(verbose_name="用例名字", max_length=50, null=True,default='')

    def __str__(self):
        return self.name

class DB_step(models.Model):
    Case_id = models.CharField(max_length=10, null=True)  # 所属大用例id
    name = models.CharField(max_length=50, null=True)  # 步骤名字
    index = models.IntegerField(null=True)  # 执行步骤
    api_method = models.CharField(max_length=10, null=True)  # 请求方式
    api_url = models.CharField(max_length=1000, null=True)  # url
    api_host = models.CharField(max_length=100, null=True)  # host
    api_header = models.CharField(max_length=1000, null=True)  # 请求头
    api_body_method = models.CharField(max_length=10, null=True,default='')  # 请求体编码类型,设置默认值‘’，避免null返回前端。这样返回的none
    api_body = models.CharField(max_length=10, null=True)  # 请求体
    get_path = models.CharField(max_length=500, null=True)  # 提取返回值-路径法
    get_zz = models.CharField(max_length=500, null=True)  # 提取返回值-正则
    assert_zz = models.CharField(max_length=500, null=True)  # 断言返回值-正则
    assert_qz = models.CharField(max_length=500, null=True)  # 断言返回值-全文检索存在
    assert_path = models.CharField(max_length=500, null=True)  # 断言返回值-路径法
    mock_res = models.CharField(max_length=1000,null=True) # mock返回值
    public_header = models.CharField(max_length=1000,null=True) # 全局变量-请求头


    def __str__(self):
        return self.name



class DB_project_header(models.Model):
    """
    公共请求头数据表
    """
    project_id = models.CharField(max_length=10,null=True) #所属项目id
    name = models.CharField(max_length=20,null=True) #请求头变量名字
    key =  models.CharField(max_length=20,null=True) #请求头header的 key
    value = models.TextField(null=True) #请求头的value，因为有可能cookie较大，达到几千字符，所以采用大文本方式存储

    def __str__(self):
        return self.name