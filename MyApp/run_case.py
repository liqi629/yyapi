import time
import unittest
import re, json
import requests
from MyApp.A_WQRFhtmlRunner import HTMLTestRunner

class Test(unittest.TestCase):
    '''
    测试类13910629673
    '''
    def demo(self, step):
        time.sleep(3)

        api_method = step.api_method
        api_url = step.api_url
        api_host = step.api_host
        api_header = step.api_header
        api_body_method = step.api_body_method
        api_body = step.api_body
        get_path = step.get_path
        get_zz = step.get_zz
        assert_zz = step.assert_zz
        assert_qz = step.assert_qz
        assert_path = step.assert_path


        mock_res = step.mock_res

        if mock_res not in ['', None, 'None']:
            res = mock_res
        else:

            # 检查是否需要进行替换占位符
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

            # 输出请求数据
            print("[apibody是：]" + api_body)
            print('[host]', api_host)
            print('[url]', api_url)
            print('[header]', api_header)
            print('[method]', api_method)
            print('[body_method]', api_body_method)
            print('[body]', api_body)

            # 实际发送请求
            try:
                header = json.loads(api_header)
            except:
                header = eval(api_header)
            # 拼接完整的url
            if api_host[-1] == '/' and api_url[0] == '/':  # 都有/
                url = api_host[:-1] + api_url
            elif api_host[-1] != '/' and api_url[0] != '/':  # 都没有/
                url = api_host + '/' + api_url
            else:  # 肯定有一个有/
                url = api_host + api_url

            if api_body_method == 'none' or api_body_method == 'null':
                response = requests.request(api_method.upper(), url, headers=header, data={})

            elif api_body_method == 'form-data':
                files = []
                payload = {}
                for i in eval(api_body):
                    payload[i[0]] = i[1]
                response = requests.request(api_method.upper(), url, headers=header, data=payload, files=files)

            elif api_body_method == 'x-www-form-urlencoded':
                header['Content-Type'] = 'application/x-www-form-urlencoded'
                payload = {}
                for i in eval(api_body):
                    payload[i[0]] = i[1]
                response = requests.request(api_method.upper(), url, headers=header, data=payload)

            else:  # 这时肯定是raw的五个子选项：
                if api_body_method == 'Text':
                    header['Content-Type'] = 'text/plain'

                if api_body_method == 'JavaScript':
                    header['Content-Type'] = 'text/plain'

                if api_body_method == 'Json':
                    header['Content-Type'] = 'text/plain'

                if api_body_method == 'Html':
                    header['Content-Type'] = 'text/plain'

                if api_body_method == 'Xml':
                    header['Content-Type'] = 'text/plain'
                response = requests.request(api_method.upper(), url, headers=header, data=api_body.encode('utf-8'))
            response.encoding = "utf-8"
            res = response.text
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
                这里我们要注意一u'y下，正则提取出来的东西，我们很难确定它的值的类型，
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
    setattr(tool, "__doc__", u"%s"%step.name)
    return tool


def make_def(steps):
    """
    Python zfill() 方法返回指定长度的字符串，原字符串右对齐，前面填充0。
    :param steps:
    :return:
    """
    for i in range(len(steps)):
        setattr(Test, 'test_'+str(steps[i].index).zfill(3), make_defself(steps[i]))




def run(Case_id, Case_name, steps):
    make_def(steps)
    suit = unittest.makeSuite(Test)
    filename = 'MyApp/templates/Reports/%s.html'%Case_id
    fp = open(filename, 'wb')
    runner = HTMLTestRunner(fp,title='接口测试平台测试报告:%s'%Case_name,description='用例描述')
    runner.run(suit)
if __name__ == '__main__':
    unittest.main()