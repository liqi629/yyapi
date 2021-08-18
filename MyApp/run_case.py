import time
import unittest
import re, json
import requests
from MyApp.A_WQRFhtmlRunner import HTMLTestRunner


# 添加下面代码，让本文将有数据库权限
import sys, os, django
path = "../yyapi"
sys.path.append(path)
os.environ.setdefault("DJANGO_STTFINGS_MODULE", "yyapi.settings")
django.setup()
from MyApp.models import *
from MyApp.global_def import *




class Test(unittest.TestCase):
    '''
    测试类
    '''
    @classmethod
    def setUpClass(cls) -> None:
        print('收尾功能')
        try:
            for i in login_res_list:
                if i['Case_id'] == cls.Case_id:
                    print('进行删除中:{}'.format(cls.Case_id))
                    login_res_list.remove(i)
                    break
        except:
            pass

    def demo(self, step):
        time.sleep(3)
        #获取项目id
        project_id = DB_cases.objects.filter(id=DB_step.objects.filter(id=step.id)[0].Case_id)[0].project_id
        api_method = step.api_method
        api_url = step.api_url
        api_url = global_datas_replace(project_id,api_url)

        api_host = step.api_host
        api_host = global_datas_replace(project_id, api_host)

        api_header = step.api_header
        api_header = global_datas_replace(project_id, api_header)
        api_body_method = step.api_body_method

        api_body = step.api_body
        api_body = global_datas_replace(project_id, api_body)
        get_path = step.get_path
        get_zz = step.get_zz
        assert_zz = step.assert_zz
        assert_qz = step.assert_qz
        assert_path = step.assert_path


        mock_res = step.mock_res

        ts_project_headers = step.public_header.split(',') #获取公共请求头
        if api_header =='':
            api_header = '{}'

        if mock_res not in ['', None, 'None']:
            res = mock_res
        else:
            """
            检查是否需要进行替换占位符，rlist_url/header/body。      ##参数名##
            re.findall(pattern, string, flags=0)  通过正则表达式将符合的对象取出来 pattern-->正则表达式 string-->需要处理的字符串 flags-->说明匹配模式，如是否大小写re.I
            replace() 方法把字符串中的 old（旧字符串） 替换成 new(新字符串)，如果指定第三个参数max，则替换不超过 max 次。str.replace(old, new[, max])
            第一个请求 肯定不应该有 变量替换，所有此处是已经有变量获取之后的一个替换，去看 下文的  get_path  这里 将变量名设置为全局变量且已经赋值。所有这里的
            api_url = api_url.replace("##"+i+"##", str(eval(i))) 是将提取出来的变量的值进行了替换
            """
            rlist_url = re.findall(r'##(.+?)##', api_url)
            for i in rlist_url:
                api_url = api_url.replace("##"+i+"##", str(eval(i)))

            rlist_header = re.findall(r'##(.+?)##', api_header)
            for i in rlist_header:
                api_header = api_header.replace("##"+i+"##", repr(str(eval(i))))
            if api_body_method == 'none':
                pass
            elif api_body_method == 'form-data' or api_body_method =='x-www-form-urlencoded' :

                rlist_body = re.findall(r"##(.*?)##", api_body)
                for i in rlist_body:
                    api_body = api_body.replace("##" + i + "##", str(eval(i)))

            elif api_body_method == 'Json' :

                rlist_body = re.findall(r"##(.*?)##", api_body)
                for i in rlist_body:
                    api_body = api_body.replace("##" + i + "##", repr(eval(i)))

            else:

                rlist_body = re.findall(r"##(.*?)##", api_body)
                for i in rlist_body:
                    api_body = api_body.replace("##" + i + "##", str(eval(i)))



            # 实际发送请求
            # 处理header
            try:
                header = json.loads(api_header)
            except:
                header = eval(api_header)

            # 在这遍历公共请求头，并把其加入到header字典中
            for i in ts_project_headers:
                if i == '': #如果没有勾选任何公共请求头，那么这个ts_project_headers 就是[""] ，里面有个空字符的元素，然后这个空字符去数据库搜索对应的请求头内容的时候，搜不到报错。
                    continue

                project_header = DB_project_header.objects.filter(id=i)[0]
                header[project_header.key] = project_header.value





            # 输出请求数据
            print("[apibody是：]" + api_body)
            print('[host]', api_host)
            print('[url]', api_url)
            print('[header]', header)
            print('[method]', api_method)
            print('[body_method]', api_body_method)
            print('[body]', api_body)
            # 拼接完整的url
            if api_host[-1] == '/' and api_url[0] == '/':  # 都有/
                url = api_host[:-1] + api_url
            elif api_host[-1] != '/' and api_url[0] != '/':  # 都没有/
                url = api_host + '/' + api_url
            else:  # 肯定有一个有/
                url = api_host + api_url

            # 登陆态代码：
            """
            1. 如何清理

2. 如何设置和规定 这个同项目不允许重叠执行的高幂等性

3. 目前项目A尚未运行完，项目B开始运行，就会把login_res这个变量给重新赋值，导致项目A后续的步骤发觉login_res已经不是自己的项目id后，就会重新生成新的，然后项目B的后续步骤再次赋值，发生俩个项目甚至多个项目互相抢这个变量的情况。

4. 所谓的时间戳变量还真的有用么？



解决方案：

1. 设置一个登陆态存放的列表，删掉自己用例id的登陆态就可以

2.设置一个字段，放在数据库的用例表中，执行开始时候修改为1，执行结束或报错收尾都修改为0，重叠执行的时候先判断 是否为0，如果不为0 则返回说该用例正在运行中，请稍后再启动！

3. 不再用一个字典作为登陆态login_res的内容，而是改造成一个列表，所有的大用例的登陆态都在里面存放，靠着用例id区分，互相不再影响。删除自己的也好删除。使用的时候 就直接去这个列表中搜索，搜不到就创建新的。

4. 时间戳变量无用了，可以删除相关设计代码。

接下来我们要做的事是，在这个大用例执行结束后，从列表中删除掉它的专属login_res。那么如何判断当前这个step是最后一个步骤呢？ 这里我仍然有俩个思路：



在首次执行的时删除掉之前旧的login_res，或者在最后一次执行完删除。当然最好放在setupClass 或 teardownClass内，但是这里需要知道当前的大用例id，想办法传给set..或tear.... ，建议使用类变量 而 非global的方式，原因大家都知道，不然又容易引起新的干扰bug出现了。

另一个安全的办法是在这个step生成的demo函数生成的时候，给一个标记信号，来告诉demo函数，这个是大用例的最后一个step了，执行完 记得删除大用例的login_res。



根据方法论指导，我选择第一种方式开始试验：

那么具体是在一开始初始化清空还是 结尾删除呢，我倾向于一开始。这样防止如果前一个用例执行到一半报错等，没有正常结束，导致没运行到teardownClass的问题。



代码如下，首先我们要去修改run_cases.py最下面的函数，让它们把Case_id给带进去：
            """
            api_login = step.api_login  # 获取登陆开关
            if api_login == 'yes':  # 需要判断
                Case_id = DB_step.objects.filter(id=step.id)[0].Case_id  # 先求出当前执行step所属的case_id
                global login_res_list  # 新建一个登陆态列表
                try:
                    eval('login_res_list')
                except:
                    login_res_list = []  # 判断是否存在，若不存在，则创建空的，一般只有平台重启后才会触发一次

                # 去login_res_list中查找是否已经存在
                for i in login_res_list:
                    if i['Case_id'] == Case_id:  # 说明找到了.直接用。
                        login_res = i
                        break
                else:  # 说明没找到，要创建
                    from MyApp.views import project_login_send_for_other
                    login_res = project_login_send_for_other(project_id)
                    login_res['Case_id'] = Case_id  # 给它加入 大用例id 标记
                    login_res_list.append(login_res)

                # 运行到这的时候，可以肯定已经有了这个login res了
                print(login_res)
                # 开始插入代码url/header/body
                ## url插入
                if '?' not in url:
                    url += '?'
                    if type(login_res) == dict:
                        for i in login_res.keys():
                            url = + i + '=' + login_res[i] + '&'
                else:  # 证明已经有参数了
                    if type(login_res) == dict:
                        for i in login_res.keys():
                            url += '&' + i + '=' + login_res[i]
                ## header插入
                if type(login_res) == dict:
                    header.update(login_res)
            else:
                login_res = {}

            ## 输出请求数据
            print('\n')
            print('【url】：', url)
            print('【header】：', json.dumps(header))
            print('【method】：', api_method)
            print('【body_method】：', api_body_method)
            print('【body】：', api_body)  # 目前graphQL方法的显示上仍然未优化

            if api_body_method == 'none' or api_body_method == 'null':
                if type(login_res) == dict:
                    response = requests.request(api_method.upper(), url, headers=header, data={})
                else:
                    response = login_res.request(api_method.upper(), url, headers=header, data={})

            elif api_body_method == 'form-data':
                files = []
                # payload = {}
                # for i in eval(api_body):
                #     payload[i[0]] = i[1]
                # if type(login_res) == dict:
                #     for i in login_res.keys():
                #         payload[i] = login_res[i]
                payload = ()
                for i in eval(api_body):
                    payload += ((i[0], i[1]),)
                if type(login_res) == dict:
                    for i in login_res.keys():
                        payload += ((i,login_res[i]),)
                    response = requests.request(api_method.upper(), url, headers=header, data=payload, files=files)
                else:
                    response = login_res.request(api_method.upper(), url, headers=header, data=payload, files=files)

            elif api_body_method == 'x-www-form-urlencoded':
                header['Content-Type'] = 'application/x-www-form-urlencoded'
                # payload = {}
                # for i in eval(api_body):
                #     payload[i[0]] = i[1]
                #
                # if type(login_res) == dict:
                payload = ()
                for i in eval(api_body):
                    payload += ((i[0], i[1]),)
                if type(login_res) == dict:
                    for i in login_res.keys():
                        payload += ((i, login_res[i]),)
                    response = requests.request(api_method.upper(), url, headers=header, data=payload)
                else:
                    response = login_res.request(api_method.upper(), url, headers=header, data=payload)
            elif api_body_method == 'GraphQL':
                header['Content-Type'] = 'application/json'
                query=api_body.split('*WQRF*')[0]
                graphql=api_body.split('*WQRF*')[1]
                try:
                    eval(graphql)
                except:
                    graphql = '{}'
                payload = '{"query":"s%","variables":s%}' % (query,graphql)
                if type(login_res) == dict:
                    response = requests.request(api_method.upper(),url,headers=header,data=payload)
                else:
                    response = login_res.request(api_method.upper(), url, headers=header, data=payload)
            else:  # 这时肯定是raw的五个子选项：
                if api_body_method == 'Text':
                    header['Content-Type'] = 'text/plain'

                if api_body_method == 'JavaScript':
                    header['Content-Type'] = 'text/plain'

                if api_body_method == 'Json':
                    api_body = json.loads(api_body)
                    for i in login_res.keys():
                        api_body[i] = login_res[i]
                    api_body = json.dumps(api_body)
                    header['Content-Type'] = 'text/plain'

                if api_body_method == 'Html':
                    header['Content-Type'] = 'text/plain'

                if api_body_method == 'Xml':
                    header['Content-Type'] = 'text/plain'
                if type(login_res) == dict:
                    response = requests.request(api_method.upper(), url, headers=header, data=api_body.encode('utf-8'))
                else:
                    response = login_res.request(api_method.upper(), url, headers=header, data=api_body.encode('utf-8'))
            response.encoding = "utf-8"
            res = response.text
            DB_host.objects.update_or_create(host=api_host)
        print("【返回体是】"+res)

        # 对返回值res进行提取：
        # 路径提取
        if get_path != '':
            for i in get_path.split('\n'):
                key = i.split('=')[0].rstrip()
                path = i.split('=')[1].rstrip()
                """
                这个解析的过程中，我们对path用/进行分割，然后分别判断每一段，如果不是[开头，
                那说明是提取的是字典key，否则就是[数字]这样的列表下标。所以一开始设置的空字串py_path 要逐个累加解析过的每一段
                """
                py_path = ""
                for j in path.split('/'):
                    if j != '':
                        if j[0] != '[':
                            py_path += '["%s"]'%j
                        else:
                            py_path +=j
                value = eval("%s%s"%(json.loads(res), py_path))
                exec ('global %s\n%s = %s'%(key, key, value))
        # 正则提取
        if get_zz != '':
            for i in get_zz.split('\n'):
                key = i.split('=')[0].rstrip()
                zz = i.split('=')[1].rstrip()
                value = re.findall(zz, res)[0]
                """
                这里我们要注意一下，正则提取出来的东西，我们很难确定它的值的类型，
                因为如果真实返回值是如： "a":"1" 这时候，然后恰好用户又设置成: a":"(.*?)" 这样，
                那我们取到的只是1 ，我们不能擅作主张的把这个1变成整形，因为这个1的确是字符串“1”，
                而且也可能是使用者不是写错 而是故意要取出来当作整形或者字符串，所以为了避免这种纠纷，
                我暂时规定正则提取出来的全部按照字符串处理～也欢迎大家集思广益，提出更妥善的方案，
                其中也要考虑我们擅自把1变成整形尚且不表，把abc也变成整形就会报错的情况。
                """
                exec('global %s\n%s = "%s"' % (key,key, value))
        # 对返回值res进行断言：
        # 断言-路径法
        if assert_path !='':
            for i in assert_path.split('\n'):
                path = i.split('=')[0].rstrip()
                want = eval(i.split('=')[1].lstrip())
                py_path = ""
                for j in path.split('/'):
                    if j != '':
                        if j[0] != '[':
                            py_path += '["%s"]'% j
                        else:
                            py_path +=j
                # print('[want]'+want)
                # print('【py_path】'+py_path)
                # print('[json.loads(res)]'+str("%s" % json.loads(res)))
                value = eval("%s%s" % (json.loads(res), py_path))
                self.assertEqual(want, value, '值不等')
        # 断言-正则
        if assert_zz !='':
            for i in assert_zz.split('\n'):
                zz = i.split('=')[0].rstrip()
                want = i.split('=')[1].lstrip()

                value = re.findall(zz, res)[0]
                self.assertEqual(want, value, '值不等')

def make_defself(step):
    def tool(self):
        Test.demo(self, step)
    setattr(tool, "__doc__", u"%s"%step.name)   #__doc__：获取到注释内容，这里通过setattr函数将测试用例中的步骤名称设置为注释内容
    return tool


def make_def(steps,Case_id):
    """
    Python zfill() 方法返回指定长度的字符串，原字符串右对齐，前面填充0。
    dir(Test):获取子方法列表
     delattr：可以删除类的子方法
    :param steps:
    :return:
    """
    # 在每个用例运行前，都检查一下该Test类，把其中的不属于原始状态的方法即 test_开头的 都删除即可
    Test.Case_id = Case_id
    for fun in dir(Test):
        if 'test_' in fun:
            delattr(Test,fun)
    for i in range(len(steps)):
        setattr(Test, 'test_'+str(steps[i].index).zfill(3), make_defself(steps[i]))    #index执行步骤的序号
        # 设置Test类，test_001(举例) ，test_001的内容 使用后面的make_defself填充

        #make_defself（steps[i]），将第一个步骤的内容传到make_defself，在这个函数中，使用步骤名称做了一个注释，返回返回了 Test.demo
        # Test.demo传入的步骤内容，通过demo函数，解析内容，发起request请求





def run(Case_id, Case_name, steps):
    make_def(steps,Case_id)   #将所有测试用例的步骤，构造成Test类中的 test_001  test_002等
    # suite = unittest.makeSuite(Test) # 将所有步骤放在一个suit集合里
    #升级到Python3后，发现makeSuite没有啦！其实是被下面这段代码取代了
    suite = unittest.TestLoader().loadTestsFromTestCase(Test)
    filename = 'MyApp/templates/Reports/%s.html'%Case_id #设置测试报告存储
    fp = open(filename, 'wb')
    runner = HTMLTestRunner(fp,title='接口测试平台测试报告:%s'%Case_name,description='用例描述')
    runner.run(suite)# 运行测试集合
if __name__ == '__main__':
    unittest.main()