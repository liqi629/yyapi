import json

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from MyApp.models import *


# Create your views here.
# 是web后端交互层，也叫视图逻辑层。也就是用来和我们前端交互的。
# 调用的HttpResponse函数是用来返回一个字符串的，后续返回的json格式字符串也是用它，
# HttpResponseRedirect 是用来重定向到其他url上的。
# render是用来返回html页面和页面初始数据的。


@login_required
def welcome(request):
    # return  HttpResponse("欢迎进入主页")
    return render(request, 'welcome.html')


@login_required
def home(request):
    """
    最后有多疑的同学提问了，那么其他用户为啥一定要 先经过login.html 登陆成功 再进入home.html主页呢？她直接访问：ip:8000/home/ 不可以么？
    答案是：目前可以直接访问，不信你不登陆试试看，一样可以。那是因我们进入home页面的函数 home()  并没有强制要求 检查登陆状态。
    所以django是默认放行的。那么要如何避免这种钻空子的状况呢？
    答案很简单，首先我们要给home()函数 加上django自带的登陆态检查装饰符login_required ! 导入后，直接加在home函数头上即可！
    :param request:
    :return:
    """
    # return  HttpResponse("欢迎进入主页")
    return render(request, 'welcome.html', {"whichHTML": "home.html", "oid": ""})


def child(request, eid, oid):
    """

    :param request:
    :param eid: 是我们要进入的html文件名字
    :param oid:大家可以先不用管这个oid，这个oid是灰色的，我们目前还是不会启用它，但是千万不要删除它，它后面会有大用
    :return:
    """
    res = child_json(eid, oid)
    return render(request, eid, res)


def child_json(eid, oid=''):
    """
    控制不同的页面返回不同的数据：数据分发器
    它专门用来接收页面名字，然后去不同的数据库中查找数据，进行整理后 返回给child()函数，再由child函数返回给前端浏览器。
    这个函数后期要处理的事情非常之多，所以有必要让他成为一个层级的存在，类似于我们开发同事那边的中台。
    负责和数据库交互，然后整理数据，返回给业务层函数。
    里面很简单，就是个if判断，如果eid是Home.html这个页面，那么就去数据库DB_home_href中拿走所有超链接传送门数据，返回。
    orm的使用上一个常用查询代码就是：类名.objets.all() 取出来的数据格式其实是queryset。
    接下来我们想一个问题，我们要给前端返回的数据，格式上是有严格要求的，只能是字典。但是我们刚刚从数据库取出来的这个date是一个类似列表的格式，要怎么办呢？
    很简单，我们新建一个字典res,然后把date作为res的一个键值对的值即可。
    :param eid: 我们要进入的html文件名字
    :return:res是个字典，可以直接让我们child函数返回给前端
    """
    res = {}  # 我们在最开始给res = {} 即可。这样如果有控制说res={什么数据} 也可以，没有指定的那就是不需要数据，就当{}空字典返回即可
    if eid == 'home.html':
        data = DB_home_href.objects.all()
        res = {"hrefs": data}
    if eid == 'project_list.html':
        data = DB_project.objects.all()
        res = {"projects": data}
    if eid == 'P_apis.html':
        project = DB_project.objects.filter(id=oid)[0]
        apis = DB_apis.objects.filter(project_id=oid)
        res = {"project": project, "apis": apis}
    if eid == 'P_cases.html':
        project = DB_project.objects.filter(id=oid)[0]
        res = {"project": project}
    if eid == 'P_project_set.html':
        project = DB_project.objects.filter(id=oid)[0]
        res = {"project": project}
    return res


def login(request):
    return render(request, 'login.html')


def login_action(request):
    """
    开始继续写验证用户名密码代码：
    这里我们必须引入一个django的库，专门验证登陆的。叫做auth。
    然后 用我们前端给的用户名和密码，调用这个auth函数，去用户库里查询用户，我们的引用变量自定义为user， 这个auth函数如果在库里找到了这个用户，那么就会给你返回这个用户实体，否则就给你返回None
    所以我们接下来就要 判断，这个user是一个用户实体，还是一个None
    修改login函数中成功登陆的分支，给他加上：
    如果用户一但登陆成功，就调用django的真正登陆函数auth.login。然后顺便把这个登陆状态也就是成功的用户名当作session写进用户的浏览器内，之后用户就可以成功进入各个页面了
    :param request:
    :return:
    """
    u_name = request.GET['username']
    p_word = request.GET['password']
    # 开始 联通 django 用户库，查看用户名密码是否正确
    from django.contrib import auth
    user = auth.authenticate(username=u_name, password=p_word)
    if user is not None:
        # 进行正确的动作 HttpResponseRedirect函数是重定向浏览器链接的
        # 前端 想给后端 传数据，发送请求，如果不是表单提交，或者超链接。只用我们的异步接口请求(就是我们前面用的$.get("url",{参数}{返回动作函数}))  的话，那么后端无论怎么写重定向语句，都是徒劳的，前端并不会直接跳转去/home/。
        # 但是我们又不想去大改前端的登陆架构，用什么办法弥补呢？
        # 答案很简单，后端可以返回诸如 True/False  0/1  成功/失败  这种字符串。因为前端的js函数里接受到ret就是这个后端返回的字符串。所以前端js可以根据这个ret来作出不同的处理，比如跳转到/home/。
        # return HttpResponseRedirect('/home/')
        auth.login(request, user)
        request.session['user'] = u_name
        return HttpResponse('成功')
    else:
        # 返回前端告诉前端用户名/密码不对
        return HttpResponse('失败')


def register_action(request):
    """
    从这个django.contrib/auth.models 库里倒入里User方法。(其实User是orm方式操作用户表的实例)
    然后我们直接用User.objects.create_user方法生成一个用户，参数为用户名和密码。然后保存这个生成的用户 就是注册成功了
    但是如果用户表中已存在这个用户名，那么，这个生成语句就会报错。所以我们用try来捕获这个异常，如果发送错误那就是“用户已经存在”，如实给用户返回这句话。如果没问题，那么就返回 注册成功
    :param request:
    :return:
    """
    u_name = request.GET['username']
    p_word = request.GET['password']
    # 开始 联通 django 用户库，查看用户名密码是否正确
    from django.contrib.auth.models import User
    try:
        user = User.objects.create_user(username=u_name, password=p_word)
        user.save()
        return HttpResponse('注册成功')
    except:
        return HttpResponse('注册失败~用户名好像已经存在了~')


def logout(request):
    """
    这里我们是可以直接用HttpResponseRedirect重定向函数 给直接重定到登陆页面/login/的。
    因我前面讲了，如果是a标签的href 或者form表单提交 这种会触发页面刷新的情况，后端函数都可以直接让用户重定向。但是如果是异步请求$.get() 则不可以
    :param request:
    :return:
    """
    from django.contrib import auth
    auth.logout(request)
    return HttpResponseRedirect('/login/')


def pei(request):
    """
    DB_tucao是我们的类，它下面有个objects的方法，内部还有子方法create，create方法就是创建数据库记录，参数就是我们的字段内容，
    不过我们本来有4个字段：id user text ctime ,因为id为自动创建不用我们操心，ctime也是自动填入也不用我们操心，所以我们这里只写user 和 text即可。
    user就是吐槽的用户名，我前文提到过，所有请求的信息包括请求者的登陆用户名都存放在reqeust这个参数中，它里面的user.username就是请求的用户名了。
    我们拿出来当作吐槽表的用户名，tucao_text就是吐槽内容,赋值给text。为了不写错，我们可以打开models.py再确认一下有没有拼写类错误
    :param request:
    :return:
    """
    tucao_text = request.GET['tucao_text']
    DB_tucao.objects.create(user=request.user.username, text=tucao_text)
    return HttpResponse('')


def api_help(request):
    """
    帮助
    :param request:
    :return:
    """
    return render(request, 'welcome.html', {"whichHTML": "help.html", "oid": ""})


def project_list(request):
    """
    项目列表
    :param request:
    :return:
    """
    return render(request, 'welcome.html', {"whichHTML": "project_list.html", "oid": ""})


def delete_project(request):
    """
    .filter() 方法可以找出所有符合的数据记录，当然这里我们肯定只能找到一条。但是返回的仍然是一个类似列表的格式，虽然只有一个元素。
    后接.delete()方法 ，可以删除。然后直接返回给前端，证明事办完了。前端就会自动刷新，用户看到的就是 这个项目不见了。
    :param request:
    :return:
    """
    id = request.GET['id']
    DB_project.objects.filter(id=id).delete()
    DB_apis.objects.filter(project_id=id).delete()
    return HttpResponse('')


def add_project(request):
    """
    接收project_name
    去项目表新建项目
    回给前端一个空证明已经成功完成
    这里我们新学到了一个数据库新增数据的方法：
    表的类名.objects.create()
    括号内写各个字段的值，这里我们的项目名字已经获取到，创建者名字就从request参数中的user.username方法获取到(只要有登陆态的都肯定有名字)
    其他俩个参数 备注/其他管理员 都是空。
    :param request:
    :return:
    """
    project_name = request.GET['project_name']
    DB_project.objects.create(name=project_name, remark='', user=request.user.username, other_user='')
    return HttpResponse('')


def open_apis(request, id):
    """
    这里比较难，大家注意看。一直以来我们都带着这个空字符串的oid。
    现在是首次启用。
    什么时候用：当我们进入一个页面需要返回数据的时候，如果数据一致，没什么特殊区分，那就不需要。
    不过需要区分，比如这里进入不同的项目详情页，就要带入不同的项目数据的时候，我们就需要启用oid。此时这个oid里面就是我们可以用来区分数据的参数，也就是项目id。
    :param request:
    :param id:
    :return:
    """
    project_id = id
    return render(request, 'welcome.html', {"whichHTML": "P_apis.html", "oid": project_id})


def open_cases(request, id):
    project_id = id
    return render(request, 'welcome.html', {"whichHTML": "P_cases.html", "oid": project_id})


def open_project_set(request, id):
    project_id = id
    return render(request, 'welcome.html', {"whichHTML": "P_project_set.html", "oid": project_id})


def save_project_set(request, id):
    project_id = id
    name = request.GET['name']
    remark = request.GET['remark']
    other_user = request.GET['other_user']

    DB_project.objects.filter(id=project_id).update(name=name, remark=remark, other_user=other_user)
    return HttpResponse('')


def project_api_add(request, Pid):
    """
    注意其中 的orm新建数据的方法：create() 其中我只写了所属项目id，其他十几项字段都没写就会默认为空或None
    最后返回的时候，因为页面会刷新，所以要返回一个路由而不是什么json串或页面。这里用了强制重定向到项目接口库。
    如果不这样做， 那么我们新增接口后浏览器顶部的地址是：/project_api_add/项目id/  这样看起来没什么问题，但是如果这时候用户刷新页面，
    就会导致再次请求这个新增接口路由，导致更多意料之外的新接口诞生。所以我们这里强制转换路由为接口库初始：/apis/项目id/ ,
    这样用户怎么刷新也不会出现问题。后续很多href类这种会导致页面刷新的后端函数最好都如此重定向到初始路由，以免出现问题。
    :param request:
    :param Pid:项目id
    :return:
    """
    project_id = Pid
    DB_apis.objects.create(project_id=project_id)
    return HttpResponseRedirect('/apis/%s/' % project_id)


def project_api_del(request, id):
    """
    删除接口
    这样就完成了删除功能，但是这里我们要思考一个问题。
    我们要怎么返回呢？ 还要保持住之前的初始地址，那就必须要有项目id，但是项目id我们没传...
    不过好在我们传入了接口id，我们在删除这个接口之前，可以利用它找到它所属的项目id，然后再删除即可
    :param request:
    :param id:接口id
    :return:
    """
    project_id = DB_apis.objects.filter(id=id)[0].project_id
    DB_apis.objects.filter(id=id).delete()
    return HttpResponseRedirect('/apis/%s/' % project_id)


def save_bz(request):
    api_id = request.GET['api_id']
    bz_value = request.GET['bz_value']
    DB_apis.objects.filter(id=api_id).update(des=bz_value)
    return HttpResponse('')


def get_bz(request):
    api_id = request.GET['api_id']
    bz_value = DB_apis.objects.filter(id=api_id)[0].des
    return HttpResponse(bz_value)


def Api_save(request):
    """
    保存接口
    :param request:
    :return:
    """
    api_id= request.GET['api_id']
    api_name = request.GET['api_name']
    ts_method = request.GET['ts_method']
    ts_url = request.GET['ts_url']
    ts_host = request.GET['ts_host']
    ts_header = request.GET['ts_header']
    ts_body_method = request.GET['ts_body_method']
    ts_api_body = request.GET['ts_api_body']

    DB_apis.objects.filter(id=api_id).update(
        api_method = ts_method,
        api_url = ts_url,
        api_host = ts_host,
        api_header = ts_header,
        body_method = ts_body_method,
        api_body = ts_api_body,
        name = api_name,
    )
    return HttpResponse('success')


def get_api_data(request):
    """
    第一句是获取到前端过来的接口id
    第二句是拿到这个接口的字典格式数据
    第三句是返回给前端，但是数据要变成json串。
    这段代码很常用，大家最好死记硬背下来。
    :param request:
    :return:
    """
    api_id = request.GET['api_id']
    api = DB_apis.objects.filter(id = api_id).values()[0]
    return HttpResponse(json.dumps(api), content_type='application/json')