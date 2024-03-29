import ast
import json
import requests


from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from MyApp.models import *
from MyApp.global_def import *


# Create your views here.
# 是web后端交互层，也叫视图逻辑层。也就是用来和我们前端交互的。
# 调用的HttpResponse函数是用来返回一个字符串的，后续返回的json格式字符串也是用它，
# HttpResponseRedirect 是用来重定向到其他url上的。
# render是用来返回html页面和页面初始数据的。

def glodict(request):
    userimg = str(request.user.id)+'.png' #写死png后缀，上传强制转成png
    res = {"username":request.user.username, "userimg":userimg}
    return res




# 上传用户头像
def user_upload(request):
    file = request.FILES.get("fileUpload",None) # 靠name获取上传的文件，如果没有，避免报错，设置成None

    if not file:
        return HttpResponseRedirect('/home/') #如果没有则返回到首页

    new_name = str(request.user.id) + '.png' #设置好这个新图片的名字
    destination = open("MyApp/static/user_img/"+new_name, 'wb+')  # 打开特定的文件进行二进制的写操作
    for chunk in file.chunks():  # 分块写入文件
        destination.write(chunk)
    destination.close()

    return HttpResponseRedirect('/home/') #返回到首页


@login_required
def welcome(request):
    # return  HttpResponse("欢迎进入主页")
    return render(request, 'welcome.html')


@login_required
def home(request, log_id=''):
    """
    最后有多疑的同学提问了，那么其他用户为啥一定要 先经过login.html 登陆成功 再进入home.html主页呢？她直接访问：ip:8000/home/ 不可以么？
    答案是：目前可以直接访问，不信你不登陆试试看，一样可以。那是因我们进入home页面的函数 home()  并没有强制要求 检查登陆状态。
    所以django是默认放行的。那么要如何避免这种钻空子的状况呢？
    答案很简单，首先我们要给home()函数 加上django自带的登陆态检查装饰符login_required ! 导入后，直接加在home函数头上即可！
    :param request:
    :return:
    """
    # return  HttpResponse("欢迎进入主页")
    return render(request, 'welcome.html', {"whichHTML": "home.html", "oid": request.user.id, "ooid":log_id
                                            ,**glodict(request)})


def child(request, eid, oid, ooid):
    """

    :param request:
    :param eid: 是我们要进入的html文件名字
    :param oid:大家可以先不用管这个oid，这个oid是灰色的，我们目前还是不会启用它，但是千万不要删除它，它后面会有大用
    :return:
    """
    res = child_json(eid, oid, ooid)
    return render(request, eid, res)


def child_json(eid, oid='', ooid=''):
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
    :param oid: 形参

    :return:res是个字典，可以直接让我们child函数返回给前端
    """
    res = {}  # 我们在最开始给res = {} 即可。这样如果有控制说res={什么数据} 也可以，没有指定的那就是不需要数据，就当{}空字典返回即可

    if eid == 'home.html':
        date = DB_home_href.objects.all()
        home_log = DB_apis_log.objects.filter(user_id=oid)[::-1]
        hosts = DB_host.objects.all()
        from django.contrib.auth.models import User
        user_projects = DB_project.objects.filter(user=User.objects.filter(id=oid)[0].username)

        # 个人数据看板
        count_project = len(user_projects)
        count_api = sum([len(DB_apis.objects.filter(project_id=i.id)) for i in user_projects])
        count_case = sum([len(DB_cases.objects.filter(project_id=i.id)) for i in user_projects])

        ziyuan_all = len(DB_project.objects.all()) + len(DB_apis.objects.all()) + len(DB_cases.objects.all())
        ziyuan_user = count_project + count_api + count_case
        ziyuan = int(ziyuan_user / ziyuan_all * 100) #个人看板的数据中，如果小数位过多，会被判断成很大的数据：
        # 如果要进行精度控制，可以使用格式
        #
        # '%.2f' % a
        #
        # 或者float('%.2f' % a)
        ziyuan = float('%.2f' % ziyuan)

        new_res = {
            "count_project": count_project,
            "count_api": count_api,
            "count_case": count_case,
            "count_report": '',
            "ziyuan": ziyuan,
        }

        if ooid == '':
            res = {"hrefs": date, "home_log": home_log, "hosts": hosts, "user_projects": user_projects}
        else:
            log = DB_apis_log.objects.filter(id=ooid)[0]
            res = {"hrefs": date, "home_log": home_log, "log": log, "hosts": hosts, "user_projects": user_projects}

        res.update(new_res)

    if eid == 'project_list.html':
        data = DB_project.objects.all()
        res = {"projects": data}
    if eid == 'P_apis.html':
        project = DB_project.objects.filter(id=oid)[0]
        apis = DB_apis.objects.filter(project_id=oid)
        # 我们给每个接口api，都新增了一个short_url，值为原始url的?号前面路由的部分，
        # 并且最大只要前50个字符串。
        for i in apis:
            # print(i.api_url)
            # url为空得时候，'NoneType' object has no attribute 'split' 报错，会导致页面打不开，此处进行判断，或者views.py中的新增接口函数，给它加上api_url=‘’
            # 或者使用try
            # if i.api_url !=None:
                # i.short_url = i.api_url.split('?')[0][:50]

            try:
                i.short_url = i.api_url.split('?')[0][:50]
            except:
                i.short_url = ''
        project_hrader = DB_project_header.objects.filter(project_id=oid)
        hosts = DB_host.objects.all()
        project_host = DB_project_host.objects.filter(project_id=oid)
        # 把apis进行包装后
        # 变成了P_apis，并且是异步加载
        # 每页最多15条。
        #
        # 而具体页码我们则是
        # 通过前端传入参数page, 如果第一次进入没有页码那么就默认为第一页，然后P_apis
        # 根据具体页码
        # 再次变身，成真正的该页码下所有的数据即接口列表。 然后把这些数据传给前端，仍然叫apis的字段就可以了。
        #
        # 但是这里我们
        # 需要想办法给这个
        # page变成真正的具体页码，还记得我们child_json如果想带上
        # 页码参数
        # 要怎么做了么？就是利用好ooid那个参数。这个备用参数，此时再次显现作用。
        P_apis = Paginator(apis,10,1)
        page = ooid
        try:
            P_apis = P_apis.page(page)
        except PageNotAnInteger:
            P_apis = P_apis.page(1)
        except EmptyPage:
            P_apis = P_apis.page(P_apis.num_pages)

        res = {"project": project, "apis": P_apis, 'project_header':project_hrader,'hosts':hosts,'project_host':project_host}
    if eid == 'P_cases.html':
        project = DB_project.objects.filter(id=oid)[0]
        Cases = DB_cases.objects.filter(project_id=oid)
        apis = DB_apis.objects.filter(project_id=oid)
        project_hrader = DB_project_header.objects.filter(project_id=oid)
        project_host = DB_project_host.objects.filter(project_id=oid)
        hosts = DB_host.objects.all()
        res = {"project":project,"Cases": Cases, "apis":apis,"project_header":project_hrader,'hosts':hosts,'project_host':project_host}
    if eid == 'P_project_set.html':
        project = DB_project.objects.filter(id=oid)[0]
        res = {"project": project}

    if eid == 'P_global_data.html':
        from django.contrib.auth.models import User
        project = DB_project.objects.filter(id=oid)[0]
        global_data = DB_global_data.objects.filter(user_id=project.user_id)
        res = {"project":project,"global_data":global_data}
        print(res)
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
    return render(request, 'welcome.html', {"whichHTML": "help.html", "oid": "",**glodict(request)})


def project_list(request):
    """
    项目列表
    :param request:
    :return:
    """
    return render(request, 'welcome.html', {"whichHTML": "project_list.html", "oid": "",**glodict(request)})


def delete_project(request):
    """
    删除项目
    .filter() 方法可以找出所有符合的数据记录，当然这里我们肯定只能找到一条。但是返回的仍然是一个类似列表的格式，虽然只有一个元素。
    后接.delete()方法 ，可以删除。然后直接返回给前端，证明事办完了。前端就会自动刷新，用户看到的就是 这个项目不见了。
    :param request:
    :return:
    """
    id = request.GET['id']
    DB_project.objects.filter(id=id).delete()
    DB_apis.objects.filter(project_id=id).delete() #删除旗下接口
    all_Case = DB_cases.objects.filter(project_id=id)
    for i in all_Case:
        DB_step.objects.filter(Case_id=i.id).delete() # 删除步骤
        i.delete()  #用例删除自己
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
    DB_project.objects.create(name=project_name, remark='', user=request.user.username,user_id=request.user.id ,other_user='')
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
    #这个参数 从前端获取，代码如上，具体怎么获取现在先不要管，我们赶紧回到child_json函数中把这个ooid 接收用起来。
    page = request.GET.get('page')
    return render(request, 'welcome.html', {"whichHTML": "P_apis.html", "oid": project_id,**glodict(request), "ooid":page})

def open_cases(request, id):
    project_id = id
    return render(request, 'welcome.html', {"whichHTML": "P_cases.html", "oid": project_id,**glodict(request)})


def open_project_set(request, id):
    project_id = id
    return render(request, 'welcome.html', {"whichHTML": "P_project_set.html", "oid": project_id,**glodict(request)})


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
    DB_apis.objects.create(project_id=project_id, api_method='none', body_method='none')
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
    ts_login = request.GET['ts_login']
    ts_header = request.GET['ts_header']
    ts_body_method = request.GET['ts_body_method']
    ts_project_headers = request.GET['ts_project_headers']

    if ts_body_method == '返回体':
        api = DB_apis.objects.filter(id=api_id)[0]
        ts_body_method = api.last_body_method
        ts_api_body = api.last_api_body
    else:
        ts_api_body = request.GET['ts_api_body']
    DB_apis.objects.filter(id=api_id).update(
        api_method = ts_method,
        api_url = ts_url,
        api_login = ts_login,
        api_host = ts_host,
        api_header = ts_header,
        body_method = ts_body_method,
        api_body = ts_api_body,
        name = api_name,
        public_header = ts_project_headers,
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


def Api_send(request):
    """
    调试层发送请求，提取所有数据
    :param request:
    :return:
    """
    api_id = request.GET['api_id']
    project_id = DB_apis.objects.filter(id=api_id)[0].project_id
    api_name = request.GET['api_name']
    ts_method = request.GET['ts_method']
    ts_url = request.GET['ts_url'] #需要全局变量替换
    ts_url = global_datas_replace(project_id,ts_url)
    ts_host = request.GET['ts_host']#需要全局变量替换
    ts_host = global_datas_replace(project_id,ts_host)
    ts_header = request.GET['ts_header'] #需要全局变量替换
    ts_header = global_datas_replace(project_id,ts_header)
    ts_body_method = request.GET['ts_body_method']
    ts_project_headers = request.GET['ts_project_headers'].split(',') #获取公共请求头
    ts_login = request.GET['ts_login']
    if ts_login == 'yes':#说明要调用登录态
        #有api_id，那么根据api_id查到所属项目id，
        login_res = project_login_send_for_other(project_id=DB_apis.objects.filter(id=api_id)[0].project_id)
    else:
        login_res = {}

    # 处理域名host
    if ts_host[:4] == '全局域名':
        prject_host_id = ts_host.split('-')[1]
        ts_host = DB_project_host.objects.filter(id=prject_host_id)[0].host
    if ts_body_method == '返回体':
        api = DB_apis.objects.filter(id=api_id)[0]
        ts_body_method = api.last_body_method
        ts_api_body = api.last_api_body

        if ts_body_method in ['', None, 'none']:
            return HttpResponse('请先选择请求体编码格式和请求头，再点击Send按钮发送请求！')
    else:
        ts_api_body = request.GET['ts_api_body'] # 需要替换全局变量
        ts_api_body = global_datas_replace(project_id,ts_api_body)
        api = DB_apis.objects.filter(id=api_id)
        api.update(last_body_method=ts_body_method, last_api_body=ts_api_body)
    # 发送请求获取返回值
    if ts_header =='': #请求头为空时候 我们不再报错返回，而是当作无请求头进行：
        ts_header = '{}'
    try:
        header = json.loads(ts_header) # 处理header
    except:
        return HttpResponse('请求头不符合json格式！')

    for i in ts_project_headers:
        if i != '':
            project_header = DB_project_header.objects.filter(id=i)[0]
            header[project_header.key] = project_header.value


    # 拼接完整url
    if ts_host[-1]=='/' and ts_url[0]=='/': # 都有/
        url = ts_host[:-1]+ts_url
    elif ts_host[-1] != '/' and ts_url[0] !='/': # 都没有/
        url = ts_host+'/'+ts_url
    else: #肯定有一个/
        url = ts_host+ts_url

    # 插入登录态字段
    ## url插入
    if '?' not in url:
        url +='?'
        if type(login_res) == dict:

            for i in login_res.keys():
                url =+ i+'='+login_res[i]+'&'
    else: # 证明已经有参数了
        if type(login_res) == dict:
            for i in login_res.keys():
                url += '&'+i+'='+login_res[i]
    ## header插入
    if type(login_res) == dict:
        header.update(login_res)

    #插入登录态
    #form-data和x-www...raw_json：

    try:
        if ts_body_method =='none':
            if type(login_res) == dict:
                response = requests.request(ts_method.upper(), url, headers=header, data={})
            else:
                response = login_res.request(ts_method.upper(), url, headers=header, data={})
        elif ts_body_method =='form-data':
            files = []
            payload = ()
            for i in eval(ts_api_body):
                payload += ((i[0],i[1]),)
            print(payload)
            if type(login_res) == dict:
                for i in login_res.keys():
                    payload[i] = login_res[i]
                response = requests.request(ts_method.upper(), url, headers=header, data=payload, files=files)
            else:
                response = login_res.request(ts_method.upper(), url, headers=header, data=payload, files=files)
        elif ts_body_method == 'x-www-form-urlencoded':
            header['Content-Type'] = 'application/x-www-form-urlencoded'
            # payload = {}
            # for i in ast.literal_eval(ts_api_body):#ast模块就是帮助Python应用来处理抽象的语法解析的。而该模块下的literal_eval()函数：则会判断需要计算的内容计算后是不是合法的python类型，如果是则进行运算，否则就不进行运算。
            #     payload[i[0]] = i[1]
            # if type(login_res) == dict:
            #     for i in login_res.keys():
            #         payload[i] = login_res[i]
            #     response = requests.request(ts_method.upper(), url, headers=header, data=payload)
            # else:
            #     response = login_res.request(ts_method.upper(), url, headers=header, data=payload)

            # 解决参数中key同名的问题，因为字典中不能重名，所以改成元组,多元元组
            #多元元组的添加元素写法，后面都有个小逗号，千万千万别忘了写！
            payload = ()
            for i in eval(ts_api_body):
                payload +=((i[0],i[1]),)

            if type(login_res) == dict:
                for i in login_res.keys():
                    payload += ((i,login_res[i]),)
                response = requests.request(ts_method.upper(), url, headers=header, data=payload)
            else:
                response = login_res.request(ts_method.upper(), url, headers=header, data=payload)

        elif ts_body_method == 'GraphQL':
            header['Content-Type'] = 'application/json'
            query=ts_body_method.split('*WQRF*')[0]
            graphql=ts_body_method.split('*WQRF*')[1]
            try:
                eval(graphql)
            except:
                graphql = '{}'
            payload = '{"query":"s%","variables":s%}' % (query,graphql)
            if type(login_res) == dict:
                response = requests.request(ts_body_method.upper(),url,headers=header,data=payload)
            else:
                response = login_res.request(ts_body_method.upper(), url, headers=header, data=payload)
        else:
            if ts_body_method == 'Text':
                header['Content-Type'] = 'text/plan'
            if ts_body_method == 'JavaScript':
                header['Content-Type'] = 'text/plan'
            if ts_body_method == 'Json':
                ts_api_body = json.loads(ts_api_body)
                for i in login_res.keys():
                    ts_api_body[i] = login_res[i]
                ts_api_body = json.dumps(ts_api_body)
                header['Content-Type'] = 'text/plan'
            if ts_body_method == 'Html':
                header['Content-Type'] = 'text/plan'
            if ts_body_method == 'Xml':
                header['Content-Type'] = 'text/plan'

            if type(login_res) == dict:
                response = requests.request(ts_method.upper(), url, headers=header, data=ts_api_body.encode('utf-8'))
            else:
                response = login_res.request(ts_method.upper(), url, headers=header, data=ts_api_body.encode('utf-8'))

        # 把返回值传送给前端页面

        response.encoding = 'utf-8'  # 解决接口的返回值中，中文会显示乱码的问题
        DB_host.objects.update_or_create(host=ts_host) #这句的意思是在host库中，新建或更新这个 host，也就是说，如果没有就创建，有就咋也不咋地。
        # print(response.cookies)
        return HttpResponse(response.text)
    except Exception as e:
        return HttpResponse(e)

def copy_api(request):
    """
    复制接口，api_id去数据库找到并拿出全部数据，再创建新的接口即可。
    :param request:
    :return:
    """
    api_id = request.GET['api_id']
    # 开始复制接口
    old_api = DB_apis.objects.filter(id=api_id)[0]

    DB_apis.objects.create(project_id=old_api.project_id,
                           name=old_api.name + '_副本',
                           api_method=old_api.api_method,
                           api_url=old_api.api_url,
                           api_header=old_api.api_header,
                           api_login=old_api.api_login,
                           api_host=old_api.api_host,
                           des=old_api.des,
                           body_method=old_api.body_method,
                           api_body=old_api.api_body,
                           result=old_api.result,
                           sign=old_api.sign,
                           file_key=old_api.file_key,
                           file_name=old_api.file_name,
                           public_header=old_api.public_header,
                           last_body_method=old_api.last_body_method,
                           last_api_body=old_api.last_api_body
                           )
    # 返回
    return HttpResponse('')


def error_request(request):
    api_id = request.GET['api_id']
    new_body = request.GET['new_body']
    span_text = request.GET['span_text']
    print(new_body)
    api = DB_apis.objects.filter(id=api_id)[0]
    method = api.api_method
    url = api.api_url
    host = api.api_host
    header = api.api_header
    body_method = api.body_method
    if header =='':
        header='{}'
    try:
        header = json.loads(header)  # 处理header
    except:
        return HttpResponse('请求头不符合json格式！')
    try:
        if host[-1] == '/' and url[0] =='/': #都有/
            url = host[:-1] + url
        elif host[-1] != '/' and url[0] !='/': #都没有/
            url = host+ '/' + url
        else: #肯定有一个有/
            url = host + url

        if body_method == 'form-data':
            files = []
            # payload = {}
            # for i in ast.literal_eval(new_body):
            #     payload[i[0]] = i[1]
            payload = ()
            for i in eval(new_body):
                payload += ((i[0],i[1]),)
            response = requests.request(method.upper(), url, headers=header, data=payload, files=files)
        elif body_method == 'x-www-form-urlencoded':
            header['Content-Type'] = 'application/x-www-form-urlencoded'
            # payload = {}
            # for i in ast.literal_eval(new_body):
            #     payload[i[0]] = i[1]
            payload = ()
            for i in eval(new_body):
                payload += ((i[0],i[1]),)
            response = requests.request(method.upper(), url, headers=header, data=payload)
        elif body_method == 'Json':
            header['Content-Type'] = 'text/plain'
            response = requests.request(method.upper(), url, headers=header, data=new_body.encode('utf-8'))
        else:
            return HttpResponse('非法的请求体类型')
        # 把返回值传递给前端页面
        response.encoding = "utf-8"
        res_json = {"response":response.text, "span_text":span_text}
        return HttpResponse(json.dumps(res_json), content_type='application/json')
    except:
        res_json = {"response": '对不起，接口未通！', "span_text": span_text}
        return HttpResponse(json.dumps(res_json), content_type='application/json')


def error_requesta(request):
    api_id = request.GET['api_id']
    new_body = request.GET['new_body']
    span_text= request.GET['span_text']

    api = DB_apis.objects.filter(id=api_id)[0]
    method = api.api_method
    url = api.api_url
    host = api.api_host
    header = api.api_header
    body_method = api.body_method
    try:
        header = json.loads(header)
    except:
        return HttpResponse('请求头不符合json格式！')

    if host[-1] == '/' and url[0] =='/': #都有/
        url = host[:-1] + url
    elif host[-1] != '/' and url[0] !='/': #都没有/
        url = host+ '/' + url
    else: #肯定有一个有/
        url = host + url

    try:
        if body_method == 'form-data':
            files = []
            payload = {}
            for i in ast.literal_eval(new_body):
                payload[i[0]] = i[1]
            response = requests.request(method.upper(), url, headers=header, data=payload, files=files)
        elif body_method == 'x-www-form-urlencoded':
            header['Content-Type'] = 'application/x-www-form-urlencoded'
            payload = {}
            for i in ast.literal_eval(new_body):
                payload[i[0]] = i[1]
            response = requests.request(method.upper(), url, headers=header, data=payload)
        elif body_method == 'Json':
            header['Content-Type'] = 'text/plain'
            response = requests.request(method.upper(), url, headers=header, data=new_body.encode('utf-8'))
        else:
            return HttpResponse('非法的请求体类型')
        # 把返回值传递给前端页面
        response.encoding = "utf-8"
        res_json = {"response":response.text,"span_text":span_text}
        return HttpResponse(json.dumps(res_json),content_type='application/json')
    except:
        res_json = {"response": '对不起，接口未通！', "span_text": span_text}
        print(res_json)
        return HttpResponse(json.dumps(res_json), content_type='application/json')




# 首页发送请求
def Api_send_home(request):
    # 提取所有数据

    ts_method = request.GET['ts_method']
    ts_url = request.GET['ts_url']
    ts_host = request.GET['ts_host']
    ts_header = request.GET['ts_header']
    ts_body_method = request.GET['ts_body_method']
    ts_api_body = request.GET['ts_api_body']

    # 发送请求获取返回值
    if ts_header =='':
        ts_header='{}'
    try:
        header = json.loads(ts_header) #处理header
    except:
        return HttpResponse('请求头不符合json格式！')
    if ts_body_method == '返回体':
        if ts_body_method in ['', None, 'none']:
            return HttpResponse('请先选择请求体编码格式，再点击Send按钮发送请求！')

        # 写入到数据库请求记录表中
    DB_apis_log.objects.create(user_id=request.user.id,
                               api_method=ts_method,
                               api_url=ts_url,
                               api_header=ts_header,
                               api_host=ts_host,
                               body_method=ts_body_method,
                               api_body=ts_api_body,
                               )



    # 拼接完整url
    if ts_host[-1] == '/' and ts_url[0] =='/': #都有/
        url = ts_host[:-1] + ts_url
    elif ts_host[-1] != '/' and ts_url[0] !='/': #都没有/
        url = ts_host+ '/' + ts_url
    else: #肯定有一个有/
        url = ts_host + ts_url
    try:
        if ts_body_method == 'none':
            response = requests.request(ts_method.upper(), url, headers=header, data={} )

        elif ts_body_method == 'form-data':
            files = []
            # payload = {}
            # for i in ast.literal_eval(ts_api_body):
            #     payload[i[0]] = i[1]
            payload = ()
            for i in eval(ts_api_body):
                payload += ((i[0],i[1]),)
            response = requests.request(ts_method.upper(), url, headers=header, data=payload, files=files )

        elif ts_body_method == 'x-www-form-urlencoded':
            header['Content-Type'] = 'application/x-www-form-urlencoded'
            # payload = {}
            # for i in ast.literal_eval(ts_api_body):
            #     payload[i[0]] = i[1]
            payload = ()
            for i in eval(ts_api_body):
                payload += ((i[0],i[1]),)
            response = requests.request(ts_method.upper(), url, headers=header, data=payload )
        elif ts_body_method == 'GraphQL':
            header['Content-Type'] = 'application/json'
            query=ts_body_method.split('*WQRF*')[0]
            graphql=ts_body_method.split('*WQRF*')[1]
            try:
                eval(graphql)
            except:
                graphql = '{}'
            payload = '{"query":"s%","variables":s%}' % (query,graphql)
            response = requests.request(ts_body_method.upper(),url,headers=header,data=payload)
        else: #这时肯定是raw的五个子选项：
            if ts_body_method == 'Text':
                header['Content-Type'] = 'text/plain'

            if ts_body_method == 'JavaScript':
                header['Content-Type'] = 'text/plain'

            if ts_body_method == 'Json':
                header['Content-Type'] = 'text/plain'

            if ts_body_method == 'Html':
                header['Content-Type'] = 'text/plain'

            if ts_body_method == 'Xml':
                header['Content-Type'] = 'text/plain'
            response = requests.request(ts_method.upper(), url, headers=header, data=ts_api_body.encode('utf-8'))

        # 把返回值传递给前端页面
        response.encoding = "utf-8"
        return HttpResponse(response.text)
    except Exception as e:
        return HttpResponse(str(e))


def get_home_log(request):
    """
    首页获取当前用户请求记录
    :param request:
    :return:
    """
    user_id = request.user.id
    all_logs = DB_apis_log.objects.filter(user_id=user_id)
    ret = {"all_logs":list(all_logs.values("id","api_method","api_host","api_url"))[::-1]}
    return HttpResponse(json.dumps(ret),content_type='application/json')



def get_api_log_home(request):
    """
    首页点击左侧请求记录触发得函数
    :param request:
    :return:
    """
    log_id = request.GET['log_id']
    log = DB_apis_log.objects.filter(id=log_id)
    ret = {"log":list(log.values())[0]}
    print(ret)

    return HttpResponse(json.dumps(ret),content_type='application/json')


# 首页保存请求数据
def Home_save_api(request):
  project_id = request.GET['project_id']
  ts_method = request.GET['ts_method']
  ts_url = request.GET['ts_url']
  ts_host = request.GET['ts_host']
  ts_header = request.GET['ts_header']
  ts_body_method = request.GET['ts_body_method']
  ts_api_body = request.GET['ts_api_body']

  DB_apis.objects.create(project_id=project_id,
                         name = '首页保存接口',
                         api_method = ts_method,
                         api_url = ts_url,
                         api_header = ts_header,
                         api_host = ts_host,
                         body_method = ts_body_method,
                         api_body = ts_api_body,
                         )

  return HttpResponse('')

def add_case(request, eid):
    """
    添加用例
    :param request:
    :param eid: 项目id
    :return:
    """
    DB_cases.objects.create(project_id=eid, name='')
    return HttpResponseRedirect('/cases/%s'%eid)


def del_case(request, eid,oid):
    """
    删除用例
    :param request:
    :param eid: 项目id
    :param oid: 用例id
    :return:
    """
    DB_cases.objects.filter(id=oid).delete()
    DB_step.objects.filter(Case_id=oid).delete()
    return HttpResponseRedirect('/cases/%s'%eid)


def copy_case(request, eid,oid):
    """
    复制用例
    :param request:
    :param eid: 项目id
    :param oid: 用例id
    :return:
    """
    old_case = DB_cases.objects.filter(id=oid)[0]
    DB_cases.objects.create(project_id=old_case.project_id, name=old_case.name+'_副本')

    return HttpResponseRedirect('/cases/%s'%eid)



def get_small(request):
    """
    获取小用例步骤得数据
    :param request:
    :return:
    """
    case_id = request.GET['case_id']
    steps = DB_step.objects.filter(Case_id=case_id).order_by('index')
    ret = {"all_steps": list(steps.values("index", "id", "name"))}
    return HttpResponse(json.dumps(ret), content_type='application/json')


def add_new_step(request):
    """
    新增步骤
    :param request:
    :return:
    """
    Case_id = request.GET['Case_id']
    all_len = len(DB_step.objects.filter(Case_id=Case_id))
    DB_step.objects.create(Case_id=Case_id, name='我是新步骤', index=all_len+1)
    return HttpResponse('')


def delete_step(request, eid):
    """
    删除步骤# 运用了双筛选和 大于写法 字段__gt =   注意是__  不是_
    :param request:
    :param eid: 步骤id
    :return:
    """
    step = DB_step.objects.filter(id=eid)[0] # 获取待删除得step
    index = step.index # 获取目标index
    Case_id = step.Case_id # 获取目标所属用例得id
    DB_step.objects.filter(id=eid).delete() # 删除目标step
    for i in DB_step.objects.filter(Case_id=Case_id).filter(index__gt = index):
        i.index -= 1 # 执行顺序自减1
        i.save()
    return HttpResponse('')



def get_step(request):
    """
    获取小步骤内容
    :param request:
    :return: 例如{"id": 44, "Case_id": "1", "name": "\u6211\u662f\u65b0\u6b65\u9aa4c",
    "index": 1, "api_method": "post", "api_url": "/hjhj/asd", "api_host": "https://www.asd.com",
     "api_header": "{}", "api_body_method": "Json", "api_body": "{\"a\":11}",
     "get_path": "1", "get_zz": "1", "assert_zz": "1", "assert_qz": "1", "assert_path": "1"}
    """
    step_id = request.GET['step_id']
    step = DB_step.objects.filter(id=step_id)
    steplist = list(step.values())[0]
    print(json.dumps(steplist))
    return HttpResponse(json.dumps(steplist), content_type='application/json')


def save_step(request):
    step_id = request.GET['step_id']
    name = request.GET['name']
    index = request.GET['index']
    step_method = request.GET['step_method']
    step_url = request.GET['step_url']
    step_host = request.GET['step_host']
    step_header = request.GET['step_header']
    ts_project_headers = request.GET['ts_project_headers']

    mock_res = request.GET['mock_res']
    step_body_method = request.GET['step_body_method']
    step_api_body = request.GET['step_api_body']

    get_path = request.GET['get_path']
    get_zz = request.GET['get_zz']
    assert_zz = request.GET['assert_zz']
    assert_qz = request.GET['assert_qz']
    assert_path = request.GET['assert_path']
    step_login = request.GET['step_login']


    DB_step.objects.filter(id=step_id).update(name=name,
                                              index=index,
                                              api_method=step_method,
                                              api_url=step_url,
                                              api_host=step_host,
                                              api_header=step_header,
                                              public_header = ts_project_headers,
                                              api_body_method=step_body_method,
                                              mock_res = mock_res,
                                              api_body=step_api_body,

                                              get_path=get_path,
                                              get_zz=get_zz,
                                              assert_zz=assert_zz,
                                              assert_qz=assert_qz,
                                              assert_path=assert_path,
                                              api_login = step_login
                                              )
    return HttpResponse('保存成功')


def step_get_api(request):
    api_id = request.GET['api_id']
    api = DB_apis.objects.filter(id=api_id).values()[0]
    return HttpResponse(json.dumps(api), content_type='application/json')



def Run_Case(request):
    """
    运行大用例
    :param request:
    :return:
    """
    Case_id = request.GET['Case_id']
    Case = DB_cases.objects.filter(id=Case_id)[0]
    steps = DB_step.objects.filter(Case_id=Case_id)
    from MyApp.run_case import run
    run(Case_id, Case.name, steps)
    return HttpResponse('')


def look_report(request, eid):
    Case_id = eid
    return render(request, 'Reports/%s.html'%Case_id)

def save_project_header(request):
    """
    保存项目公共请求头
    :param request:
    :return:
    """
    project_id = request.GET['project_id']
    req_names = request.GET['req_names']
    req_keys = request.GET['req_keys']
    req_values = request.GET['req_values']
    req_ids = request.GET['req_ids']

    names = req_names.split(',')
    keys = req_keys.split(',')
    values = req_values.split(',')
    ids = req_ids.split(',')

    for i in range(len(ids)):
        if names[i] != '':
            if ids[i]=='new':
                DB_project_header.objects.create(project_id=project_id, name=names[i], key=keys[i], value=values[i])
            else:
                DB_project_header.objects.filter(id=ids[i]).update(name=names[i], key=keys[i], value=values[i])
        else:
            try:
                DB_project_header.objects.filter(id=ids[i]).delete()
            except:
                pass
    return HttpResponse('')


def save_case_name(request):
    """保存用例名称"""
    id = request.GET['id']
    name = request.GET['name']
    DB_cases.objects.filter(id=id).update(name=name)
    return HttpResponse('')


def save_project_host(request):
    """
    保存项目公共域名
    :param request:
    :return:
    """
    project_id = request.GET['project_id']
    req_names = request.GET['req_names']
    req_hosts = request.GET['req_hosts']
    req_ids = request.GET['req_ids']

    names = req_names.split(',')
    hosts = req_hosts.split(',')
    ids = req_ids.split(',')

    for i in range(len(ids)):
        if names[i] != '':
            if ids[i]=='new':
                DB_project_host.objects.create(project_id=project_id, name=names[i], host=hosts[i])
            else:
                DB_project_host.objects.filter(id=ids[i]).update(name=names[i], host=hosts[i])
        else:
            try:
                DB_project_host.objects.filter(id=ids[i]).delete()
            except:
                pass
    return HttpResponse('')

# 获取登录态接口
def project_get_login(request):
    # 获取登录态接口
    project_id = request.GET['project_id']
    try:
        login = DB_login.objects.filter(project_id=project_id).values()[0]
    except:
        login = {"project_id": project_id, "api_method": "none", "api_url": "", "api_header": "{}", "api_host": "",
                 "body_method": "none",
                 "api_body": "","set":""}
    return HttpResponse(json.dumps(login),content_type='application/json')




# 保存登陆态接口
def project_login_save(request):
    # 提取所有数据
    project_id = request.GET['project_id']
    login_method = request.GET['login_method']
    login_url = request.GET['login_url']
    login_host = request.GET['login_host']
    login_header = request.GET['login_header']
    login_body_method = request.GET['login_body_method']
    login_api_body = request.GET['login_api_body']
    login_response_set = request.GET['login_response_set']
    # 保存数据更新或新建 upate_or_create
    #
    # 意思就是 如果存在就更新，不存在就创建。
    DB_login.objects.update_or_create(
        defaults={
            "api_method": login_method,
            "api_url": login_url,
            "api_header": login_header,
            "api_host": login_host,
            "body_method": login_body_method,
            "api_body": login_api_body,
            "set": login_response_set,
        },
        project_id=project_id
    )
    # 返回
    return HttpResponse('success')
#调式登录态接口
def project_login_send(request):
    """
    调式登录态接口
    :param request:
    :return:
    """
    # 第一步，获取前端数据
    project_id = request.GET['project_id']
    login_method = request.GET['login_method']
    login_url = request.GET['login_url']
    login_url = global_datas_replace(project_id,login_url)
    login_host = request.GET['login_host']
    login_host = global_datas_replace(project_id,login_host)
    login_header = request.GET['login_header']
    login_header = global_datas_replace(project_id, login_header)
    login_body_method = request.GET['login_body_method']
    login_api_body = request.GET['login_api_body']
    login_api_body = global_datas_replace(project_id, login_api_body)
    login_response_set = request.GET['login_response_set']
    if login_header =='':
        login_header='{}'

    # 第二步，发送请求
    try:
        header = json.loads(login_header)  # 处理header
    except:
        return HttpResponse('请求头不符合json格式！')

    # 拼接完整url
    if login_host[-1] == '/' and login_url[0] == '/':  # 都有/
        url = login_host[:-1] + login_url
    elif login_host[-1] != '/' and login_url[0] != '/':  # 都没有/
        url = login_host + '/' + login_url
    else:  # 肯定有一个有/
        url = login_host + login_url
    try:
        if login_body_method == 'none':
            response = requests.request(login_method.upper(), url, headers=header, data={})
        elif login_body_method == 'form-data':
            files = []
            # payload = {}
            # for i in eval(login_api_body):
            #     payload[i[0]] = i[1]
            payload = ()
            for i in eval(login_api_body):
                payload += ((i[0], i[1]),)
            response = requests.request(login_method.upper(), url, headers=header, data=payload, files=files)

        elif login_body_method == 'x-www-form-urlencoded':
            header['Content-Type'] = 'application/x-www-form-urlencoded'
            # payload = {}
            # for i in eval(login_api_body):
            #     payload[i[0]] = i[1]
            payload = ()
            for i in eval(login_api_body):
                payload += ((i[0], i[1]),)
            response = requests.request(login_method.upper(), url, headers=header, data=payload)

        elif login_body_method == 'GraphQL':
            header['Content-Type'] = 'application/json'
            query = login_api_body.split('*WQRF*')[0]
            graphql = login_api_body.split('*WQRF*')[1]
            try:
                eval(graphql)
            except:
                graphql = '{}'
            payload = '{"query":"%s","variables":%s}' % (query, graphql)
            response = requests.request(login_method.upper(), url, headers=header, data=payload)


        else:  # 这时肯定是raw的五个子选项：
            if login_body_method == 'Text':
                header['Content-Type'] = 'text/plain'

            if login_body_method == 'JavaScript':
                header['Content-Type'] = 'text/plain'

            if login_body_method == 'Json':
                header['Content-Type'] = 'text/plain'

            if login_body_method == 'Html':
                header['Content-Type'] = 'text/plain'

            if login_body_method == 'Xml':
                header['Content-Type'] = 'text/plain'
            response = requests.request(login_method.upper(), url, headers=header, data=login_api_body.encode('utf-8'))

        # 把返回值传递给前端页面
        response.encoding = "utf-8"
        DB_host.objects.update_or_create(host=login_host)
        try:
            res = response.json()
        except:
            end_res = {"response":response.text, "get_res": '只能提取json格式'}
            return HttpResponse(json.dumps(end_res), content_type='application/json')

        # 第三步，对返回值进行提取

        # 先判断是否cookie持久化，若是，则不处理
        if login_response_set =='cookie':
            end_res = {"response":login_response_set,"get_res":"cookie保持会话，无需提取返回值"}
        else:

            get_res = ''  # 声明提取结果存放
            for i in login_response_set.split('\n'):
                if i == "":
                    continue
                else:
                    i = i.replace(' ', '')
                    key = i.split('=')[0]  # 拿出key
                    path = i.split('=')[1]  # 拿出路径
                    value = res
                    for j in path.split('/')[1:]:
                        value = value[j]
                    get_res += key + '="' + value + '"\n'
            # 第四步，返回前端
            end_res = {"response": response.text, "get_res": get_res}
        return HttpResponse(json.dumps(end_res), content_type='application/json')

    except Exception as e:
        end_res = {"response": str(e), "get_res": ''}
        return HttpResponse(json.dumps(end_res), content_type='application/json')


# 调用登陆态接口
def project_login_send_for_other(project_id):
    # 第一步，获取数据
    login_api= DB_login.objects.filter(project_id=project_id)[0]
    login_method = login_api.api_method
    login_url = login_api.api_url
    login_url = global_datas_replace(project_id,login_url)
    login_host = login_api.api_host
    login_host = global_datas_replace(project_id, login_host)
    login_header = login_api.api_header
    login_header = global_datas_replace(project_id, login_header)
    login_body_method = login_api.body_method
    login_api_body = login_api.api_body
    login_api_body = global_datas_replace(project_id, login_api_body)
    login_response_set = login_api.set
    if login_header =='':
        login_header ='{}'
    # 第二步，发送请求
    try:
        header = json.loads(login_header) #处理header
    except:
        return HttpResponse('请求头不符合json格式！')

    # 拼接完整url
    if login_host[-1] == '/' and login_url[0] =='/': #都有/
        url = login_host[:-1] + login_url
    elif login_host[-1] != '/' and login_url[0] !='/': #都没有/
        url = login_host+ '/' + login_url
    else: #肯定有一个有/
        url = login_host + login_url



    try:
        if login_body_method == 'none':
            # 先判断是否需要cookie持久化
            if login_response_set == 'cookie':
                a = requests.session()
                a.request(login_method.upper(), url, headers=header, data={})
                return a
            else:
                response = requests.request(login_method.upper(), url, headers=header, data={} )
        elif login_body_method == 'form-data':
            files = []
            # payload = {}
            # for i in eval(login_api_body):
            #     payload[i[0]] = i[1]
            payload = ()
            for i in eval(login_api_body):
                payload += ((i[0], i[1]),)
            # 先判断是否需要cookie持久化
            if login_response_set == 'cookie':
                a = requests.session()
                a.request(login_method.upper(), url, headers=header, data=payload, files=files )
                return a
            else:
                response = requests.request(login_method.upper(), url, headers=header, data=payload, files=files )

        elif login_body_method == 'x-www-form-urlencoded':
            header['Content-Type'] = 'application/x-www-form-urlencoded'
            # payload = {}
            # for i in eval(login_api_body):
            #     payload[i[0]] = i[1]
            payload = ()
            for i in eval(login_api_body):
                payload += ((i[0], i[1]),)
            # 先判断是否需要cookie持久化
            if login_response_set == 'cookie':
                a = requests.session()
                a.request(login_method.upper(), url, headers=header, data=payload)
                return a
            else:
                response = requests.request(login_method.upper(), url, headers=header, data=payload )

        elif login_body_method == 'GraphQL':
            header['Content-Type'] = 'application/json'
            query = login_api_body.split('*WQRF*')[0]
            graphql = login_api_body.split('*WQRF*')[1]
            try:
                eval(graphql)
            except:
                graphql = '{}'
            payload = '{"query":"%s","variables":%s}' % (query, graphql)
            # 先判断是否需要cookie持久化
            if login_response_set == 'cookie':
                a = requests.session()
                a.request(login_method.upper(), url, headers=header, data=payload)
                return a
            else:
                response = requests.request(login_method.upper(), url, headers=header, data=payload )

        else: #这时肯定是raw的五个子选项：
            if login_body_method == 'Text':
                header['Content-Type'] = 'text/plain'

            if login_body_method == 'JavaScript':
                header['Content-Type'] = 'text/plain'

            if login_body_method == 'Json':
                header['Content-Type'] = 'text/plain'

            if login_body_method == 'Html':
                header['Content-Type'] = 'text/plain'

            if login_body_method == 'Xml':
                header['Content-Type'] = 'text/plain'
            # 先判断是否需要cookie持久化
            if login_response_set == 'cookie':
                a = requests.session()
                a.request(login_method.upper(), url, headers=header, data=login_api_body.encode('utf-8'))
                return a
            else:
                response = requests.request(login_method.upper(), url, headers=header, data=login_api_body.encode('utf-8'))
        # 把返回值传递给前端页面
        response.encoding = "utf-8"
        DB_host.objects.update_or_create(host=login_host)
        res = response.json()
        # 第三步，对返回值进行提取
        get_res = {} #声明提取结果存放
        for i in login_response_set.split('\n'):
            if i == "":
                continue
            else:
                i = i.replace(' ','')
                key = i.split('=')[0] #拿出key
                path = i.split('=')[1]  #拿出路径
                value = res
                for j in path.split('/')[1:]:
                    value = value[j]
                get_res[key] = value
        return get_res
    except Exception as e:
        return {}


def search (request):
    key = request.GET['key']
    # 项目名搜哦所
    projects = DB_project.objects.filter(name__contains=key)  # 获取name包含key的所有项目
    plist = [{"url": "/apis/%s/"%i.id, "text": i.name, "type": "project"} for i in projects]
    # 接口名搜索
    apis = DB_apis.objects.filter(name__contains=key)  # 获取name包含key的所有接口
    alist = [{"url": "/apis/%s/"%i.project_id, "text": i.name, "type": "api"} for i in apis]

    res = {"results": plist + alist}
    return HttpResponse(json.dumps(res), content_type='application/json')


def global_data(request,id):
    project_id = id
    return render(request, 'welcome.html', {"whichHTML": "P_global_data.html", "oid": project_id,**glodict(request)})


def global_data_add(request):
    """
    新增一个全局变量
    :param request:
    :return:
    """
    project_id = request.GET['project_id']
    user_id = DB_project.objects.filter(id=project_id)[0].user_id
    DB_global_data.objects.create(name='新变量',data='',user_id=user_id)
    return HttpResponse('')

def global_data_delete(request):
    """
    删除一个全局变量
    :param request:
    :return:
    """
    id = request.GET['id']

    DB_global_data.objects.filter(id=id).delete()
    return HttpResponse('')


def global_data_save(request):
    """
    保存一个全局变量
    :param request:
    :return:
    """

    global_id = request.GET['global_id']
    if global_id == '':
        return HttpResponse('error')
    global_name =request.GET['global_name']
    global_data = request.GET['global_data']
    # 检查重名
    datas = DB_global_data.objects.filter(name=global_name)
    if len(datas) >0: #大于0 说明查到了数据，但是要看下是不是自己本身，而且最大肯定只有一个
        if datas[0].id != global_id:# 发现这一个和本身id不同，那就是重名
            return HttpResponse('error')

    DB_global_data.objects.filter(id=global_id).update(name=global_name,data=global_data)
    return HttpResponse('')


def global_data_change_check(request):
    """
    更改项目的生效变量组
    :param request:
    :return:
    """
    project_id = request.GET['project_id']
    global_datas = request.GET['global_datas']
    DB_project.objects.filter(id=project_id).update(global_datas=global_datas)
    return HttpResponse('')
