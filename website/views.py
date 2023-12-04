import json
from datetime import datetime
import math
from functools import wraps

from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.shortcuts import render, HttpResponse, redirect
from backstage.models import *

# Create your views here.

from django.http import JsonResponse


def save_scroll_position(request):
    if request.method == "POST":
        data = json.loads(request.body)
        scroll_position = data.get('scrollPosition')

        # 你可以在这里使用滚动位置，例如保存到数据库或进行其他操作
        # ...
        request.session['scrollPosition'] = scroll_position
        request.session.save()
        return JsonResponse({"status": "success"})
    return JsonResponse({"status": "error"})


def get_stations_index(request):
    province = request.GET.get('get_city', None)
    company_id = BranchOffice.objects.filter(city=province).first()
    if province == '0':
        stations = list(Station.objects.all().values('id', 'name'))
    else:
        company_obj = BranchOffice.objects.filter(id=company_id).first()
        stations = list(Station.objects.filter(branch_office=company_obj).values('id', 'name'))
    return JsonResponse(stations, safe=False)


def index(request):
    # 方法为GET时返回页面
    companies = BranchOffice.objects.all()
    if request.method == "GET":
        # 判断是否登录
        if request.session.get("common"):
            userinfo = request.session['common']
            return render(request, "index.html",
                          {
                              'username': userinfo['username'],
                              'phone': User.objects.filter(username=userinfo['username']).first().phone_number,
                              'companies': companies,
                          })
        else:
            return render(request, "index.html",
                          {
                              'companies': companies,
                          })
    # 方法为POST时
    else:
        # 快递查询
        if "PackId" in request.POST:
            PackID = request.POST.get('PackId')
            if PackID == '' or not Parcel.objects.filter(timestamp=PackID).exists():
                pack_info = None
            else:
                pack_info = Shipment.objects.filter(parcel__timestamp=PackID).order_by('id')
            if request.session.get("common"):
                userinfo = request.session['common']
                return render(request, "index.html",
                              {
                                  'username': userinfo['username'],
                                  'phone': User.objects.filter(username=userinfo['username']).first().phone_number,
                                  'packID': PackID,
                                  'pack_info': pack_info,
                                  'companies': companies,
                              })
            else:
                return render(request, "index.html",
                              {
                                  'packID': PackID,
                                  'pack_info': pack_info,
                                  'companies': companies,
                              })
        # 寄送快递
        else:
            # 获取post值
            object_name = request.POST.get('object_name')
            username = request.POST.get("username")
            phone_number = request.POST.get("phone_number")
            recipient = request.POST.get('recipient')
            recipient_number = request.POST.get('recipient_number')
            get_company = request.POST.get('get_company')
            get_station = request.POST.get('get_station')
            deliver_company = request.POST.get("deliver_company")
            deliver_station = request.POST.get("deliver_station")
            weight = request.POST.get("weight")

            # 获取相应的数据库值
            get_company_obj = BranchOffice.objects.filter(id=get_company).first()
            get_station_obj = Station.objects.filter(id=get_station).first()
            deliver_company_obj = BranchOffice.objects.filter(id=deliver_company).first()
            deliver_station_obj = Station.objects.filter(id=deliver_station).first()

            # 快递员
            get_courier = Courier.objects.filter(station=get_station_obj).order_by('?').first()
            deliver_courier = Courier.objects.filter(station=deliver_station_obj).order_by('?').first()

            # 确保 User 对象存在
            user_obj, created = User.objects.get_or_create(username=username, phone_number=phone_number)
            recipient_obj, created = User.objects.get_or_create(username=recipient, phone_number=recipient_number)

            # 计算包裹价格
            weight = float(weight)
            weight = math.ceil(weight)
            price = weight * 10 + 2 * 0.01

            # 添加包裹
            if user_obj and recipient_obj:  # 确保两者都不是 None
                Parcel.objects.create(
                    user=user_obj,
                    recipient=recipient_obj,
                    object_name=object_name,
                    weight=weight,
                    get_company=get_company_obj,
                    get_station=get_station_obj,
                    get_courier=get_courier,
                    destination_branch=deliver_company_obj,
                    destination_station=deliver_station_obj,
                    deliver_courier=deliver_courier,
                    Price=price,
                )
                # 将包裹信息添加入快递状态表中
                try:
                    latest_parcel = Parcel.objects.latest('timestamp')
                    # 获取当前时间
                    current_time = datetime.now()
                    # 定义一个中文格式的时间字符串
                    chinese_time_format = "%Y年%m月%d日%H时"
                    # 使用strftime方法来格式化时间
                    formatted_time = current_time.strftime(chinese_time_format)

                    '''
                        提示:status： 100 为接收到订单
                            status： 101 为快递员接收到快递
                            status： 102 为分公司之间传输
                            status： 103 为目的地收到快递
                            status： 104 已经到了目的快递站
                            status： 105 包裹订单完成
                            status： 111 错误信息：主要为退件
                    '''
                    Shipment.objects.create(
                        parcel=Parcel.objects.filter(timestamp=latest_parcel.timestamp).first(),
                        status=100,
                        info=formatted_time + " " + latest_parcel.user.username + "的包裹订单已接收，等待快递员上门"
                    )

                except ObjectDoesNotExist:
                    print("没有找到任何Parcel对象")

                message = {
                    'info': f'提交成功，快递编号为：{ latest_parcel.timestamp }请等待的快递员接收包裹， 您的包裹总价格为',
                    'price': price
                }
            else:
                message = {
                    'info': "未成功提交",
                    'error': '请联系管理员'
                }

            # 判断是否登录
            if request.session.get("common"):
                userinfo = request.session['common']
                return render(request, "index.html",
                              {
                                  'username': userinfo['username'],
                                  'phone': User.objects.filter(username=userinfo['username']).first().phone_number,
                                  'companies': companies,
                                  'message': message,
                              })
            else:
                return render(request, "index.html",
                              {
                                  'companies': companies,
                                  'message': message,
                              })


def UserLogin(request):
    # 方法为GET时
    if request.method == "GET":
        return render(request, "login.html")
    # 方法为POST时
    else:
        # 获取数据
        username = request.POST.get("username")
        phone = request.POST.get("phone")
        userinfo = User.objects.filter(username=username, phone_number=phone).first()

        # 查找到用户
        if userinfo is not None:
            request.session['common'] = {"id": userinfo.id, "username": userinfo.username}
            return redirect("/")
        # 为查找到用户
        else:
            error_message = "错误的用户名或手机号"
            return render(request, "login.html", {"error": error_message, "username": username, "phone": phone})


'''
    登出操作
'''


def logout(request):
    request.session.clear()
    return redirect("/")
