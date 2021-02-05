import xlrd
import xlwt
from xlutils import copy
import os
import random
import qrcode


from django.shortcuts import render
from django.contrib.auth.decorators import login_required
# Create your views here.
from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render
from MyApp.models import *
import json
import requests

from allpairspy import AllPairs

def glodict(request):
    userimg = str(request.user.id)+'.png' #写死png后缀，上传强制转成png
    res = {"username":request.user.username, "userimg":userimg}
    return res

# 进入正交工具页面
def zhengjiao(request):

    return render(request, 'welcome.html', {"whichHTML": "zhengjiao.html", "oid": request.user.id,**glodict(request)})

# 正交工具运行
def zhengjiao_play(request):

    end_values = request.GET['end_values'].split(',')

    new_values = [i.split('/') for i in end_values ]

    res =[]
    for i in AllPairs(new_values):
        res.append(i)

    d={"res":res}
    return HttpResponse(json.dumps(d),content_type="application/json")

# 正交工具导出excel
def zhengjiao_excel(request):
    end_keys = request.GET['end_keys'].split(',')
    end_values = request.GET['end_values'].split(',')
    new_values = [i.split('/') for i in end_values]
    res = []
    for i in AllPairs(new_values):
        res.append(i)
    # 先创建
    wqrf_book = xlwt.Workbook(encoding='utf-8') # 创建excel
    wqrf_sheet = wqrf_book.add_sheet("正交结果") # 创建sheet页
    for i in range(len(res)):
        case_index = '用例:'+str(i+1) # 用例序号
        hb = list(zip(end_keys,res[i])) #把key和value进行合并
        case = ','.join([':'.join(list(i)) for i in hb]) #进行格式化，便于阅读
        wqrf_sheet.write(i,0,case_index)  # 写入，i为行，0为第一例
        wqrf_sheet.write(i, 1, case)  # 写入，i为行，1为第二例
    wqrf_book.save('MyApp/static/tmp_zhengjiao.xls') #保存

    return HttpResponse('')

def zhengjiao_excel_bk(request):
    """
    	大小	正反
用例：1	A1	正面
用例：2	A2	正面
用例：3	A3	正面
用例：4	A3	反面

    :param request:
    :return:
    """
    end_keys = request.GET['end_keys'].split(',')
    end_values = request.GET['end_values'].split(',')

    new_values = [i.split('/') for i in end_values]

    res = []
    for i in AllPairs(new_values):
        res.append(i)

    # 先创建
    wqrf_book = xlwt.Workbook(encoding='utf-8')# 创建excel
    wqrf_sheet = wqrf_book.add_sheet("正交结果") # 创建sheet
    print(end_keys)
    for k in range(len(end_keys)):
        wqrf_sheet.write(0, k+1, end_keys[k])
    for i in range(len(res)):
        case_index = '用例：'+str(i+1) # 用例序号
        case = ','.join(res[i]) # 用例内容
        case_i = res[i]
        # print(case_i)
        wqrf_sheet.write(i+1,0,case_index)# 写入用例编号 参数分别为 行 列 内容  0为第一列
        # wqrf_sheet.write(i+1,1,case)# 写入用例内容 行 列 内容 1为第二列
        for j in range(len(case_i)):
            wqrf_sheet.write(i+1, j+1, case_i[j])  # 写入用例内容 行 列 内容 1为第二列
    wqrf_book.save('tmp_zhengjiao.xls') # 保存
    # print(res)
    return HttpResponse('')



# 进入边界工具页面
def bianjie(request):

    return render(request, 'welcome.html', {"whichHTML": "bianjie.html", "oid": request.user.id,**glodict(request)})



# 边界工具运行-随机中文
def bianjie_play(request):

    max_zn = request.GET['max_zn']
    res =''
    for i in range(int(max_zn)):
        head = random.randint(0xb0, 0xf7)
        body = random.randint(0xa1, 0xfe)
        val = f'{head:x} {body:x}'
        str = bytes.fromhex(val).decode('gb2312')
        res = res+str
        res_2 = res+'哈'


    # 正好是最大值
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(res)
    qr.make(fit=True)

    data_zn_img = qr.make_image(fill_color="black", back_color="white")
    data_zn_img.save('MyApp/static/zn_img.png')
    # 比最大值多一个
    qr_2 = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr_2.add_data(res_2)
    qr_2.make(fit=True)

    data_zn_img_2 = qr.make_image(fill_color="black", back_color="white")
    data_zn_img_2.save('MyApp/static/zn_img_2.png')


    zn_img ='zn_img.png'
    zn_img_2='zn_img_2.png'
    d = {"res": res, "res_add_1": res_2,"zn_img":zn_img,"zn_img_2":zn_img_2,}
    print(d)
    return HttpResponse(json.dumps(d),content_type="application/json")

# def glodict(request):
#     userimg = str(request.user.id)+'.png' #写死png后缀，上传强制转成png
#     res = {"username":request.user.username, "userimg":userimg}
#     return res