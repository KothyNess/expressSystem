import json
import math
from datetime import datetime, date
from functools import wraps
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.shortcuts import render, redirect
from backstage.models import *
from django.core.serializers import serialize
from backstageForm import *

# Create your views here.


'''
总计概览
'''


def get_al_statistic():
    company_count = BranchOffice.objects.distinct().values("id").count()
    station_count = Station.objects.distinct().values("id").count()
    staff_count = Courier.objects.distinct().values("id").count()
    pack_count = Parcel.objects.distinct().values("timestamp").count()
    return {"company": company_count, "stations": station_count, "staff": staff_count, "packs": pack_count}


'''
装饰器，验证登陆
'''


def login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('admin'):
            # 如果没有 user_token 的 cookie，则重定向到登录页
            return redirect('/backstage/login/')
        return view_func(request, *args, **kwargs)

    return wrapper


def login_required_staff(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('staff'):
            # 如果没有 user_token 的 cookie，则重定向到登录页
            return redirect('/backstage/login/')
        return view_func(request, *args, **kwargs)

    return wrapper


'''
是否已经登录验证装饰器
'''


def is_login(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.session.get('admin'):
            # 如果有 user_token 的 cookie
            return redirect('/backstage/statistic/time/')
        if request.session.get('staff'):
            # 如果有 user_token 的 cookie
            return redirect('/backstage/staff/delivery/')
        return view_func(request, *args, **kwargs)

    return wrapper


'''
404页面
'''


def Page404(request, exception):
    return render(request, "404.html", {}, status=404)


"""
登录界面
"""


@is_login
def adminLogin(request):
    if request.method == "GET":
        return render(request, "Adminlogin.html")
    else:
        username = request.POST.get("username")
        password = request.POST.get("password")
        admin_info = Admin.objects.filter(username=username, password=password).first()
        staff_info = Courier.objects.filter(username=username, password=password).first()
        if admin_info:
            request.session['admin'] = {'id': admin_info.id, 'admin': admin_info.admin_name}
            return redirect("/backstage/statistic/time")
        else:
            if staff_info:
                request.session['staff'] = {'id': staff_info.id, 'name': staff_info.name}
                request.session.save()
                return redirect("/backstage/staff/")
            error_message = "账号或密码错误"
            return render(request, 'Adminlogin.html',
                          {'error': error_message, 'username': username, 'password': password})


@login_required
def adminLogout(request):
    request.session.clear()
    return redirect("/backstage/login/")


@login_required_staff
def staffLogout(request):
    request.session.clear()
    return redirect("/backstage/login/")


@is_login
@login_required
def bs_page(request):
    pass


'''
综合统计界面
'''

def format_date(input_date):
    try:
        # 尝试转换 "Oct. 18, 2023" 格式的日期
        formatted_date = datetime.strptime(input_date, '%b. %d, %Y').date()
        return formatted_date.strftime('%Y-%m-%d')
    except ValueError:
        # 如果日期不是上述格式，直接返回原值
        return input_date


@login_required
def statisticTime(request):
    user_info = request.session['admin']
    al_statistic = get_al_statistic()

    if 'date' in request.GET:  # 如果模板传递了date值
        target_date_raw = request.GET.get('date')
        if target_date_raw != "0":
            target_date = format_date(target_date_raw)  # 转换日期格式
        else:
            target_date = None  # 如果选择为"0"，则设置为None表示返回所有数据
        request.session['date_choice'] = target_date  # 存储到session
        request.session.save()
    else:
        target_date = request.session.get('date_choice')  # 从session中获取

    unique_dates = Statistics.objects.values_list('date', flat=True).distinct()
    formatted_unique_dates = [format_date(str(date)) for date in unique_dates]

    # 根据 target_date 过滤统计数据
    if not target_date:
        statistics_for_date = Statistics.objects.all()
    else:
        statistics_for_date = Statistics.objects.filter(date=target_date)

    # 使用一个字典保存每个日期的汇总统计数据
    date_statistics = {}

    for stat in statistics_for_date:
        date_raw = stat.date
        formatted_date = format_date(str(date_raw))  # 转换日期格式

        if formatted_date not in date_statistics:
            date_statistics[formatted_date] = {'pickups': 0, 'dispatch': 0, 'delivery': 0}

        date_statistics[formatted_date]['pickups'] += stat.pickup_count
        date_statistics[formatted_date]['dispatch'] += stat.dispatch_count
        date_statistics[formatted_date]['delivery'] += stat.delivery_count

    # 将字典转换为列表，以便进行分页
    date_statistics_list = list(date_statistics.items())

    # 添加分页
    paginator = Paginator(date_statistics_list, 10)  # 每页显示10个项目
    page = request.GET.get('page')

    try:
        statistics = paginator.page(page)
    except PageNotAnInteger:
        # 如果页面不是整数，展示第一页
        statistics = paginator.page(1)
    except EmptyPage:
        # 如果页面超出范围 (例如 9999)，展示最后一页
        statistics = paginator.page(paginator.num_pages)

    # ...

    return render(request, "statistic.html", {
        "admin_name": user_info['admin'],
        "active": "date",
        "type": "时间",
        "dates": formatted_unique_dates,
        "al_statistic": al_statistic,
        "selected_date": target_date,
        "statistics": statistics,  # 使用分页后的数据
    })

@login_required
def statisticBranchCom(request):
    user_info = request.session['admin']
    al_statistic = get_al_statistic()

    if 'company' in request.GET:  # 如果模板传递了company值
        target_company = int(request.GET.get('company', '0'))
        request.session['company_choice'] = target_company  # 存储到session
        request.session.save()
    else:
        target_company = request.session.get('company_choice', '0')  # 从session中获取，没有则默认为'0'

    unique_companies = Statistics.objects.values_list('branch_office', flat=True).distinct()
    companies = BranchOffice.objects.filter(id__in=unique_companies)

    # 根据 target_company 过滤统计数据
    if target_company == 0 or target_company == None:
        statistics_for_company = Statistics.objects.all()
    else:
        statistics_for_company = Statistics.objects.filter(branch_office=target_company)

    # 使用一个字典保存每个公司的汇总统计数据
    company_statistics = {}

    for stat in statistics_for_company:
        company_id = stat.branch_office.id
        company_name = stat.branch_office.name  # 假设 BranchOffice 有一个 name 字段

        if company_id not in company_statistics:
            company_statistics[company_id] = {'name': company_name, 'pickups': 0, 'dispatch': 0, 'delivery': 0}

        company_statistics[company_id]['pickups'] += stat.pickup_count
        company_statistics[company_id]['dispatch'] += stat.dispatch_count
        company_statistics[company_id]['delivery'] += stat.delivery_count

    # 将字典转换为列表，以便进行分页
    company_statistics_list = list(company_statistics.values())

    # 添加分页
    paginator = Paginator(company_statistics_list, 10)  # 每页显示10条记录
    page = request.GET.get('page')

    try:
        paginated_statistics = paginator.page(page)
    except PageNotAnInteger:
        # 如果页面不是整数，展示第一页
        paginated_statistics = paginator.page(1)
    except EmptyPage:
        # 如果页面超出范围，展示最后一页
        paginated_statistics = paginator.page(paginator.num_pages)

    # ...

    return render(request, "statistic.html", {
        "admin_name": user_info['admin'],
        "active": "company",
        "type": "分公司",
        "companies": companies,
        "al_statistic": al_statistic,
        "selected_company": target_company,
        "statistics": paginated_statistics,  # 使用分页后的统计数据
    })


@login_required
def statisticBranchStation(request):
    user_info = request.session['admin']
    al_statistic = get_al_statistic()

    if 'station' in request.GET:  # 如果模板传递了station值
        target_station = int(request.GET.get('station', '0'))
        request.session['station_choice'] = target_station  # 存储到session
        request.session.save()
    else:
        target_station = int(request.session.get('station_choice', '0'))  # 从session中获取，没有则默认为'0'

    unique_stations = Statistics.objects.values_list('station', flat=True).distinct()
    stations = Station.objects.filter(id__in=unique_stations)

    # 根据 target_station 过滤统计数据
    if target_station == 0 or target_station == None:
        statistics_for_station = Statistics.objects.all()
    else:
        statistics_for_station = Statistics.objects.filter(station=target_station)

    # 使用一个字典保存每个快递站的汇总统计数据
    station_statistics = {}

    for stat in statistics_for_station:
        station_id = stat.station.id
        station_name = stat.station.name  # 假设 Station 有一个 name 字段

        if station_id not in station_statistics:
            station_statistics[station_id] = {'name': station_name, 'pickups': 0, 'dispatch': 0, 'delivery': 0}

        station_statistics[station_id]['pickups'] += stat.pickup_count
        station_statistics[station_id]['dispatch'] += stat.dispatch_count
        station_statistics[station_id]['delivery'] += stat.delivery_count

    # 将字典转换为列表，以便进行分页
    station_statistics_list = list(station_statistics.values())

    # 添加分页
    paginator = Paginator(station_statistics_list, 10)  # 每页显示10条记录
    page = request.GET.get('page')

    try:
        paginated_statistics = paginator.page(page)
    except PageNotAnInteger:
        # 如果页面不是整数，展示第一页
        paginated_statistics = paginator.page(1)
    except EmptyPage:
        # 如果页面超出范围，展示最后一页
        paginated_statistics = paginator.page(paginator.num_pages)

    # ...

    return render(request, "statistic.html", {
        "admin_name": user_info['admin'],
        "active": "station",
        "type": "快递站",
        "stations": stations,
        "al_statistic": al_statistic,
        "selected_station": target_station,
        "statistics": paginated_statistics,  # 使用分页后的统计数据
    })

@login_required
def statisticStaff(request):
    user_info = request.session['admin']
    al_statistic = get_al_statistic()

    if 'courier' in request.GET:  # 如果模板传递了courier值
        target_courier = int(request.GET.get('courier', '0'))
        request.session['courier_choice'] = target_courier  # 存储到session
        request.session.save()
    else:
        target_courier = int(request.session.get('courier_choice', '0'))  # 从session中获取，没有则默认为'0'

    unique_couriers = Statistics.objects.values_list('courier', flat=True).distinct()
    couriers = Courier.objects.filter(id__in=unique_couriers)

    # 根据 target_courier 过滤统计数据
    if target_courier == 0 or target_courier == None:
        statistics_for_courier = Statistics.objects.all()
    else:
        statistics_for_courier = Statistics.objects.filter(courier=target_courier)

    # 使用一个字典保存每个快递员的汇总统计数据
    courier_statistics = {}

    for stat in statistics_for_courier:
        courier_id = stat.courier.id
        courier_name = stat.courier.name  # 假设 Courier 有一个 name 字段

        if courier_id not in courier_statistics:
            courier_statistics[courier_id] = {'name': courier_name, 'pickups': 0, 'dispatch': 0, 'delivery': 0}

        courier_statistics[courier_id]['pickups'] += stat.pickup_count
        courier_statistics[courier_id]['dispatch'] += stat.dispatch_count
        courier_statistics[courier_id]['delivery'] += stat.delivery_count

    # 将字典转换为列表，以便进行分页
    courier_statistics_list = list(courier_statistics.values())

    # 添加分页
    paginator = Paginator(courier_statistics_list, 10)  # 每页显示10条记录
    page = request.GET.get('page')

    try:
        paginated_statistics = paginator.page(page)
    except PageNotAnInteger:
        # 如果页面不是整数，展示第一页
        paginated_statistics = paginator.page(1)
    except EmptyPage:
        # 如果页面超出范围，展示最后一页
        paginated_statistics = paginator.page(paginator.num_pages)

    # ...

    return render(request, "statistic.html", {
        "admin_name": user_info['admin'],
        "active": "staff",
        "type": "快递员",
        "couriers": couriers,
        "al_statistic": al_statistic,
        "selected_courier": target_courier,
        "statistics": paginated_statistics,  # 使用分页后的统计数据
    })

'''
分公司管理
'''


@login_required
def BranchCom(request):
    user_info = request.session['admin']
    al_statistic = get_al_statistic()
    company_all = BranchOffice.objects.all()
    paginator = Paginator(company_all, 10)  # 每页显示10个对象
    page = request.GET.get('page')
    try:
        # 生成当前页的对象列表
        pages = paginator.page(page)
    except PageNotAnInteger:
        # 如果页码不是整数，显示第一页
        pages = paginator.page(1)
    except EmptyPage:
        # 如果页码超出范围，显示最后一页
        pages = paginator.page(paginator.num_pages)
    return render(request, "branchCom.html",
                  {"admin_name": user_info['admin'],
                   "al_statistic": al_statistic,
                   'pages': pages})


@login_required
def BranchComAdd(request):
    # 预处理数据
    provinces = [
        "北京市", "天津市", "河北省", "山西省", "内蒙古自治区",
        "辽宁省", "吉林省", "黑龙江省", "上海市", "江苏省",
        "浙江省", "安徽省", "福建省", "江西省", "山东省",
        "河南省", "湖北省", "湖南省", "广东省", "广西壮族自治区",
        "海南省", "重庆市", "四川省", "贵州省", "云南省",
        "西藏自治区", "陕西省", "甘肃省", "青海省", "宁夏回族自治区",
        "新疆维吾尔自治区", "台湾省", "香港特别行政区", "澳门特别行政区"
    ]
    # 获取和设置session信息
    user_info = request.session['admin']

    # 当使用get方法时
    if request.method == "GET":
        return render(request, "branchComOperate.html", {"admin_name": user_info['admin'], "provinces": provinces})
    else:
        # 获取输入信息
        city = request.POST['city']
        name = request.POST['name']

        # 当不含邮此数据时进行添加
        if BranchOffice.objects.filter(city=city, name=name).first() is None:
            BranchOffice.objects.create(city=city, name=name)
            return redirect("/backstage/company/")
        else:
            error = "该公司已存在"
            selected_province = request.POST.get('city', None)
            return render(request, "branchComOperate.html",
                          {"admin_name": user_info['admin'], "name": name, "error": error,
                           "provinces": provinces, "selected_province": selected_province})


@login_required
def BranchComEdit(request, comid):
    # 预处理数据
    provinces = [
        "北京市", "天津市", "河北省", "山西省", "内蒙古自治区",
        "辽宁省", "吉林省", "黑龙江省", "上海市", "江苏省",
        "浙江省", "安徽省", "福建省", "江西省", "山东省",
        "河南省", "湖北省", "湖南省", "广东省", "广西壮族自治区",
        "海南省", "重庆市", "四川省", "贵州省", "云南省",
        "西藏自治区", "陕西省", "甘肃省", "青海省", "宁夏回族自治区",
        "新疆维吾尔自治区", "台湾省", "香港特别行政区", "澳门特别行政区"
    ]

    # 获取和设置session信息
    user_info = request.session['admin']
    company_info = BranchOffice.objects.filter(id=comid).first()

    # 当使用get方法时
    if request.method == "GET":
        return render(request, "branchComOperate.html",
                      {"admin_name": user_info['admin'], "provinces": provinces, "name": company_info.name,
                       'selected_province': company_info.city, "id": company_info.id})
    # 使用Post方法时
    else:
        # 获取输入信息
        comID = request.POST['id']
        city = request.POST['city']
        name = request.POST['name']

        # 当含有此数据时进行更新
        if BranchOffice.objects.filter(id=comID).first() is not None:
            BranchOffice.objects.filter(id=comID).update(city=city, name=name)
            return redirect("/backstage/company/")
        else:
            error = "该公司已不存在"
            selected_province = request.POST.get('city', None)
            return render(request, "branchComOperate.html",
                          {"admin_name": user_info['admin'], "name": name, "error": error,
                           "provinces": provinces, "selected_province": selected_province})


def BranchComDelete(request, comid):
    if BranchOffice.objects.filter(id=comid).first() is not None:
        BranchOffice.objects.filter(id=comid).delete()
        return redirect("/backstage/company/")
    else:
        return redirect("/backstage/404/")


'''
分站管理
'''


@login_required
def BranchStation(request):
    # 获取和设置session信息
    user_info = request.session.get('admin', {})
    selected_company = request.session.get('company_choice')
    if 'company' in request.GET:
        selected_company = request.GET.get('company')
        request.session['company_choice'] = selected_company
        request.session.save()

    al_statistic = get_al_statistic()
    company_info = BranchOffice.objects.all()

    # 根据选择的公司筛选站点信息
    if selected_company == '0' or selected_company is None:
        stations_filter_info = Station.objects.all().order_by('id')
    else:
        selected_company_obj = BranchOffice.objects.filter(id=selected_company).first()
        stations_filter_info = Station.objects.filter(branch_office=selected_company_obj).order_by('id')
        selected_company = selected_company_obj

    # 分页处理
    paginator = Paginator(stations_filter_info, 10)
    page = request.GET.get('page')
    try:
        pages = paginator.page(page)
    except PageNotAnInteger:
        pages = paginator.page(1)
    except EmptyPage:
        pages = paginator.page(paginator.num_pages)

    # 渲染模板
    return render(
        request,
        "branchStation.html",
        {
            "admin_name": user_info.get('admin'),
            "al_statistic": al_statistic,
            'companies': company_info,
            'selected_company': selected_company,
            'pages': pages
        }
    )


@login_required
def BranchStationAdd(request):
    # 获取session信息
    user_info = request.session.get('admin', {})

    # 获取所有分公司信息
    company_info = BranchOffice.objects.all()

    if request.method == "GET":
        return render(
            request,
            "branchStationOperate.html",
            {"admin_name": user_info.get('admin'), 'companies': company_info}
        )

    else:
        # 获取提交的表单数据
        company_id = request.POST.get('company')
        name = request.POST.get('name')

        # 查询对应的公司
        company = BranchOffice.objects.filter(id=company_id).first()

        # 检查快递站是否已经存在
        existing_station = Station.objects.filter(branch_office=company, name=name).first()

        if existing_station is None:
            # 如果不存在，创建新的快递站
            Station.objects.create(branch_office=company, name=name)
            return redirect("/backstage/station/")

        else:
            # 如果已存在，返回错误信息
            error = "该快递站已存在"
            return render(
                request,
                "branchStation.html",
                {
                    "admin_name": user_info.get('admin'),
                    "name": name,
                    "error": error,
                    "selected_province": company_id
                }
            )


@login_required
def BranchStationEdit(request, staid):
    # 获取session信息
    user_info = request.session.get('admin', {})

    # 获取编辑的快递站和所有分公司信息
    editStation = Station.objects.filter(id=staid).first()
    company_info = BranchOffice.objects.all()

    if request.method == "GET":
        return render(
            request,
            "branchStationOperate.html",
            {
                "admin_name": user_info.get('admin'),
                'companies': company_info,
                "name": editStation.name,
                'selected_company': editStation.branch_office.id,
                'id': editStation.id
            }
        )
    else:
        # 获取提交的表单数据
        company_id = request.POST.get('company')
        station_id = request.POST.get('id')
        name = request.POST.get('name')

        # 查询对应的公司
        company = BranchOffice.objects.filter(id=company_id).first()

        # 查找是否有这个快递站
        existing_station = Station.objects.filter(id=station_id).first()

        if existing_station:
            # 如果存在，更新快递站信息
            Station.objects.filter(id=station_id).update(branch_office=company, name=name)
            return redirect("/backstage/station/")
        else:
            # 如果不存在，返回错误信息
            error = "该快递站已不存在"
            return render(
                request,
                "branchStation.html",
                {
                    "admin_name": user_info.get('admin'),
                    "name": name,
                    "error": error,
                    "selected_province": company_id
                }
            )


@login_required
def BranchStationDelete(request, staid):
    # 如果存在快递站，进行删除
    if Station.objects.filter(id=staid).first() is not None:
        Station.objects.filter(id=staid).delete()
        return redirect("/backstage/station/")
    # 如果不存在，进入404页面
    else:
        return redirect("/backstage/404/")


'''
    快递员管理
'''


@login_required
def ManageStaff(request):
    user_info = request.session.get('admin', {})
    selected_company = request.session.get('company_choice')
    selected_station = request.session.get('station_choice')

    # Update session data for selected company and station
    if 'company' in request.GET:
        selected_company = request.GET['company']
        request.session['company_choice'] = selected_company
        request.session.save()

    if 'station' in request.GET:
        selected_station = request.GET['station']
        request.session['station_choice'] = selected_station
        request.session.save()

    al_statistic = get_al_statistic()
    company_info = BranchOffice.objects.all()
    station_info = Station.objects.all()

    # Filter staff based on the selected station
    if selected_station == '0' or selected_station is None:
        if selected_company != '0':
            selected_company_obj = BranchOffice.objects.filter(id=selected_company).first()
            staff_filter_info = Courier.objects.filter(station__branch_office=selected_company_obj).all()
        else:
            staff_filter_info = Courier.objects.all().order_by('id')
    else:
        selected_station_obj = Station.objects.filter(id=selected_station).first()
        staff_filter_info = Courier.objects.filter(station=selected_station_obj).order_by('id')
        if selected_station_obj:
            selected_station = selected_station_obj.id

    # Pagination
    paginator = Paginator(staff_filter_info, 10)
    page = request.GET.get('page')

    try:
        pages = paginator.page(page)
    except PageNotAnInteger:
        pages = paginator.page(1)
    except EmptyPage:
        pages = paginator.page(paginator.num_pages)

    # Render template
    return render(request, "ManageStaff.html", {
        "admin_name": user_info.get('admin'),
        "al_statistic": al_statistic,
        "companies": company_info,
        "stations": station_info,
        "pages": pages,
        "select_company": selected_company,
        "select_station": selected_station
    })


def get_stations(request):
    company_id = request.GET.get('company', None)
    if company_id == '0':
        stations = list(Station.objects.all().values('id', 'name'))
    else:
        company_obj = BranchOffice.objects.filter(id=company_id).first()
        stations = list(Station.objects.filter(branch_office=company_obj).values('id', 'name'))
    return JsonResponse(stations, safe=False)


@login_required
def ManageStaffAdd(request):
    # 获取session数据和所需数据
    user_info = request.session['admin']
    companies = BranchOffice.objects.all()
    if request.method == "GET":
        return render(request, 'staffOperate.html',
                      {
                          "admin_name": user_info['admin'],
                          "companies": companies
                      })
    else:
        staff_station = request.POST.get('station')
        staff_name = request.POST.get('staff_name')
        staff_username = request.POST.get('staff_username')
        staff_passwd = request.POST.get('staff_passwd')
        staff_station_obj = Station.objects.filter(id=staff_station).first()
        Courier.objects.create(name=staff_name, station=staff_station_obj, username=staff_username,
                               password=staff_passwd)
        return redirect('/backstage/staff/')


@login_required
def ManageStaffEdit(request, staffid):
    # 获取session数据和所需数据
    user_info = request.session['admin']
    companies = BranchOffice.objects.all()
    # request方法为GET时
    if request.method == "GET":

        # 返回选择的员工信息
        staff_info = Courier.objects.filter(id=staffid).first()
        selected_company = staff_info.station.branch_office.id
        selected_station = staff_info.station.id
        # 为找到员工信息跳转之404页面
        if staff_info is None:
            return redirect('/backstage/404/')
        return render(request, 'staffOperate.html',
                      {
                          "admin_name": user_info['admin'],
                          "companies": companies,
                          'company': staff_info.station.branch_office.id,
                          'station': staff_info.station.id,
                          'staff_name': staff_info.name,
                          'staff_username': staff_info.username,
                          'staff_passwd': staff_info.password,
                          'id': staff_info.id,
                          'selected_company': selected_company,
                          'selected_station': selected_station,
                      })
    # request方法为POST时，修改相应员工信息
    else:
        staff_id = request.POST.get('id')
        staff_station = request.POST.get('station')
        staff_name = request.POST.get('staff_name')
        staff_username = request.POST.get('staff_username')
        staff_passwd = request.POST.get('staff_passwd')
        staff_station_obj = Station.objects.filter(id=staff_station).first()
        if staff_station_obj is not None:
            Courier.objects.filter(id=staff_id).update(name=staff_name, station=staff_station_obj,
                                                       username=staff_username,
                                                       password=staff_passwd)
        else:
            return redirect('/backstage/404/')
        return redirect('/backstage/staff/')


@login_required
def ManageStaffDelete(request, staffid):
    # 如果存在快递员，进行删除
    if Courier.objects.filter(id=staffid).first() is not None:
        Courier.objects.filter(id=staffid).delete()
        return redirect("/backstage/staff/")
    # 如果不存在，进入404页面
    else:
        return redirect("/backstage/404/")


'''
    包裹管理
'''


@login_required
def ManagePack(request):
    # session信息
    user_info = request.session['admin']
    selected_company = request.session.get('company_choice')
    selected_station = request.session.get('station_choice')

    # 更新选择的company 和station信息
    if 'company' in request.GET:
        selected_company = request.GET['company']
        request.session['company_choice'] = selected_company
        request.session.save()

    if 'station' in request.GET:
        selected_station = request.GET['station']
        request.session['station_choice'] = selected_station
        request.session.save()

    al_statistic = get_al_statistic()
    company_info = BranchOffice.objects.all()

    # Filter station based on the selected station
    if selected_station == '0' or selected_station is None:
        if selected_company != '0':
            selected_company_obj = BranchOffice.objects.filter(id=selected_company).first()
            pack_filter_info = Parcel.objects.filter(get_company=selected_company_obj).all()
        else:
            pack_filter_info = Parcel.objects.all().order_by('timestamp')
    else:
        selected_station_obj = Station.objects.filter(id=selected_station).first()
        pack_filter_info = Parcel.objects.filter(get_station=selected_station_obj).order_by('timestamp')
        if selected_station_obj:
            selected_station = selected_station_obj.id
    # Pagination
    paginator = Paginator(pack_filter_info, 10)
    page = request.GET.get('page')

    try:
        pages = paginator.page(page)
    except PageNotAnInteger:
        pages = paginator.page(1)
    except EmptyPage:
        pages = paginator.page(paginator.num_pages)

    return render(request, "GetPackageMag.html",
                  {
                      "admin_name": user_info['admin'],
                      'al_statistic': al_statistic,
                      "companies": company_info,
                      "pages": pages,
                      "selected_company": selected_company,
                      "selected_station": selected_station,
                  })


@login_required
def ManagePackEdit(request, packID):
    # 获取session信息
    user_info = request.session['admin']
    companies = BranchOffice.objects.all()
    # request方法为GET时
    if request.method == "GET":

        # 返回选择的员工信息
        pack_info = Parcel.objects.filter(timestamp=packID).first()
        # 原始数据
        selected_get_company = pack_info.get_company.id
        selected_get_station = pack_info.get_station.id
        selected_deliver_company = pack_info.destination_branch.id
        selected_deliver_station = pack_info.destination_station.id
        # 未找到员工信息跳转之404页面
        if pack_info is None:
            return redirect('/backstage/404/')
        return render(request, 'PackOperate.html',
                      {
                          "admin_name": user_info['admin'],
                          "companies": companies,
                          'pack_info': pack_info,
                          'selected_get_company': selected_get_company,
                          'selected_get_station': selected_get_station,
                          'selected_deliver_company': selected_deliver_company,
                          'selected_deliver_station': selected_deliver_station,
                      })
    # request方法为POST时，修改相应员工信息
    else:
        # 获取快递号
        timestamp = request.POST.get('packID')
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
            Parcel.objects.filter(timestamp=timestamp).update(
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
            message = {
                'info': '提交成功，请等待的快递员接收包裹， 您的包裹总价格为',
                'price': price
            }
        else:
            return redirect('/backstage/404/')
        return redirect('/backstage/Pack/')


@login_required
def ManagePackDelete(request, packID):
    # 如果存在包裹，进行退回
    if Parcel.objects.filter(timestamp=packID).first() is not None:
        parcel_info = Parcel.objects.filter(timetamp=packID).first()
        Shipment.objects.filter(parcel=parcel_info).update(status=111)
        return redirect("/backstage/Pack/")
    # 如果不存在，进入404页面
    else:
        return redirect("/backstage/404/")


'''
    发货管理
    提示:status： 100 为接收到订单
        status： 101 为快递员接收到快递
        status： 102 为分公司之间传输
        status： 103 为到达目的地分公司
        status： 104 为快递员派送中
        status： 105 为包裹订单完成
        status： 111 为错误信息：主要为退件
'''


@login_required
def manage_deliver_pack(request):
    # 获取用户和统计信息
    user_info = request.session['admin']
    al_statistic = get_al_statistic()

    # 更新session中的company和station
    selected_company = request.GET.get('company', request.session.get('company_choice', '0'))
    selected_station = request.GET.get('station', request.session.get('station_choice', '0'))

    request.session['company_choice'] = selected_company
    request.session['station_choice'] = selected_station
    request.session.save()

    from django.db.models import Max, F

    # 根据选择的company和station筛选Shipment
    if selected_station == '0':
        shipments = Shipment.objects.all()
        if selected_company != '0':
            shipments = shipments.filter(parcel__get_company__id=selected_company)
    else:
        shipments = Shipment.objects.filter(parcel__get_station_id=selected_station)

    # 对每个包裹，找到最新的Shipment ID
    latest_shipments = shipments.values('parcel').annotate(latest_shipment_id=Max('id'))

    # 将这些ID转换为一个列表
    latest_shipment_ids = [item['latest_shipment_id'] for item in latest_shipments]

    # 使用上面的ID列表来筛选Shipment对象
    latest_shipments = Shipment.objects.filter(id__in=latest_shipment_ids)

    # 对Shipment数据进行分页
    paginator = Paginator(latest_shipments, 10)
    page = request.GET.get('page')

    try:
        pages = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        pages = paginator.page(1)

    context = {
        "admin_name": user_info['admin'],
        'al_statistic': al_statistic,
        'pages': pages,
        'companies': BranchOffice.objects.all(),
        'selected_company': selected_company,
        'selected_station': selected_station,
    }

    return render(request, "DeliverPackMag.html", context)


'''
    快递员简短url
'''


@is_login
@login_required
def staff_page(request):
    pass


'''
    快递员操作
'''

from django.db.models import OuterRef, Subquery

from django.db.models import OuterRef, Subquery


@login_required_staff
def staff_pack_manage(request):
    user_info = request.session.get('staff')
    courier = Courier.objects.get(id=user_info['id'])

    # 待接收的包裹与待递送的包裹
    get_parcel = Parcel.objects.filter(get_courier=courier)
    deliver_parcel = Parcel.objects.filter(deliver_courier=courier)

    # 获取每个包裹的最新Shipment的ID
    def get_latest_shipment_ids(parcel_set):
        latest_shipments = Shipment.objects.filter(parcel=OuterRef('pk')).order_by('-id')
        return parcel_set.annotate(
            latest_shipment_id=Subquery(latest_shipments.values('id')[:1])
        ).values_list('latest_shipment_id', flat=True)

    latest_get_shipment_ids = get_latest_shipment_ids(get_parcel)
    latest_deliver_shipment_ids = get_latest_shipment_ids(deliver_parcel)

    # 根据最新的Shipment ID以及状态筛选Shipment信息
    get_parcel_info = Shipment.objects.filter(id__in=latest_get_shipment_ids, status='100').order_by('id')
    deliver_parcel_info_103 = Shipment.objects.filter(id__in=latest_deliver_shipment_ids, status='103').order_by('id')
    deliver_parcel_info_104 = Shipment.objects.filter(id__in=latest_deliver_shipment_ids, status='104').order_by('id')

    # 合并两个状态为'103'和'104'的deliver parcel信息
    deliver_parcel_info = deliver_parcel_info_103.union(deliver_parcel_info_104).order_by('id')

    # 分页函数
    def paginate_shipment_data(shipments, page_key):
        paginator = Paginator(shipments, 10)
        page = request.GET.get(page_key)
        try:
            return paginator.page(page)
        except (PageNotAnInteger, EmptyPage):
            return paginator.page(1)

    # 进行分页操作
    pages_get = paginate_shipment_data(get_parcel_info, 'page_get')
    pages_delivery = paginate_shipment_data(deliver_parcel_info, 'page_delivery')

    # 构建上下文数据
    context = {
        'staff_info': user_info,
        'pages_get': pages_get,
        'pages_delivery': pages_delivery,
        'get_parcel_count': get_parcel_info.count(),
        'deliver_parcel_count': deliver_parcel_info.count()
    }

    # 渲染模板
    if request.method == "GET":
        return render(request, 'DeliverPackOperate.html', context)


from django.db.models import OuterRef, Subquery


@login_required_staff
def company_pack_manage(request):
    # 获取当前登录员工的信息
    user_info = request.session.get('staff')
    courier = Courier.objects.get(id=user_info['id'])

    # 根据员工所在的分公司筛选包裹
    company_deliver_parcel = Parcel.objects.filter(get_company=courier.station.branch_office)
    company_get_parcel = Parcel.objects.filter(destination_branch=courier.station.branch_office)

    # 获取每个包裹的最新Shipment的ID
    def get_latest_shipment_ids(parcel_set):
        latest_shipments = Shipment.objects.filter(parcel=OuterRef('pk')).order_by('-id')
        return parcel_set.annotate(
            latest_shipment_id=Subquery(latest_shipments.values('id')[:1])
        ).values_list('latest_shipment_id', flat=True)

    latest_get_shipment_ids = get_latest_shipment_ids(company_deliver_parcel)
    latest_deliver_shipment_ids = get_latest_shipment_ids(company_get_parcel)

    # 根据最新的Shipment ID以及状态筛选Shipment信息
    company_deliver_parcel_info = Shipment.objects.filter(id__in=latest_get_shipment_ids, status='101').order_by('id')
    company_get_parcel_info = Shipment.objects.filter(id__in=latest_deliver_shipment_ids, status='102').order_by('id')

    # 分页函数
    def paginate_shipment_data(shipments, page_key):
        paginator = Paginator(shipments, 10)
        page = request.GET.get(page_key)
        try:
            return paginator.page(page)
        except (PageNotAnInteger, EmptyPage):
            return paginator.page(1)

    # 进行分页操作
    pages_get = paginate_shipment_data(company_deliver_parcel_info, 'page_get')
    pages_delivery = paginate_shipment_data(company_get_parcel_info, 'page_delivery')

    # 构建上下文数据
    context = {
        'staff_info': user_info,
        'pages_get': pages_get,
        'pages_delivery': pages_delivery,
        'company_deliver_parcel_count': company_deliver_parcel_info.count(),
        'company_get_parcel_count': company_get_parcel_info.count()
    }

    # 渲染模板
    if request.method == "GET":
        return render(request, 'DeliverCompanyOperate.html', context)


'''
    接收/送达 操作
    提示:status： 100 为接收到订单
        status： 101 为快递员接收到快递
        status： 102 为分公司之间传输
        status： 103 为到达目的地分公司
        status： 104 为快递员派送中
        status： 105 为包裹订单完成
        status： 111 为错误信息：主要为退件
'''


@login_required_staff
def get_success(request, parcelID):
    if request.method == "GET":
        staff_info = request.session.get('staff')
        courier_obj = Courier.objects.filter(id=staff_info['id']).first()
        parcel_obj = Parcel.objects.filter(timestamp=parcelID).first()

        # 获取当前时间
        current_time = timezone.now()
        current_date = current_time.date()

        # 定义一个中文格式的时间字符串
        chinese_time_format = "%Y年%m月%d日%H时"
        # 使用strftime方法来格式化时间
        formatted_time = current_time.strftime(chinese_time_format)

        Shipment.objects.create(parcel=parcel_obj, status=101, info=formatted_time + courier_obj.name + "已经收到包裹")

        # 获取或创建统计记录
        statistic, created = Statistics.objects.get_or_create(
            date=current_date,
            branch_office=courier_obj.station.branch_office,
            station=courier_obj.station,
            courier=courier_obj
        )

        # 更新揽件统计
        statistic.pickup_count += 1
        statistic.save()

        return redirect('/backstage/staff/')  # 重定向到页面或URL


@login_required_staff
def deliver_success(request, parcelID):
    if request.method == "GET":
        staff_info = request.session.get('staff')
        courier_obj = Courier.objects.filter(id=staff_info['id']).first()
        parcel_obj = Parcel.objects.filter(timestamp=parcelID).first()

        # 获取当前时间
        current_time = timezone.now()
        current_date = current_time.date()

        # 定义一个中文格式的时间字符串
        chinese_time_format = "%Y年%m月%d日%H时"
        # 使用strftime方法来格式化时间
        formatted_time = current_time.strftime(chinese_time_format)
        Shipment.objects.create(parcel=parcel_obj, status=104,
                                info=formatted_time + courier_obj.name + "已经开始派送包裹")
        # 获取或创建统计记录
        statistic, created = Statistics.objects.get_or_create(
            date=current_date,
            branch_office=courier_obj.station.branch_office,
            station=courier_obj.station,
            courier=courier_obj
        )

        # 更新揽件统计
        statistic.delivery_count += 1
        statistic.save()

        return redirect('/backstage/staff/')  # 重定向到某个页面或URL


def finish(request, parcelID):
    if request.method == "GET":
        staff_info = request.session.get('staff')
        courier_obj = Courier.objects.filter(id=staff_info['id']).first()
        parcel_obj = Parcel.objects.filter(timestamp=parcelID).first()

        # 获取当前时间
        current_time = timezone.now()

        # 定义一个中文格式的时间字符串
        chinese_time_format = "%Y年%m月%d日%H时"
        # 使用strftime方法来格式化时间
        formatted_time = current_time.strftime(chinese_time_format)

        Shipment.objects.create(parcel=parcel_obj, status=105,
                                info=formatted_time + courier_obj.name + "已到达至" + parcel_obj.destination_station.name)

        return redirect('/backstage/staff/')  # 重定向到页面或URL


'''
    送入分公司/分公司发出/送至另一分公司
'''


@login_required_staff
def send_to_company(request, parcelID):
    if request.method == "GET":
        staff_info = request.session.get('staff')
        courier_obj = Courier.objects.filter(id=staff_info['id']).first()
        parcel_obj = Parcel.objects.filter(timestamp=parcelID).first()

        # 获取当前时间
        current_time = timezone.now().date()

        # 定义一个中文格式的时间字符串
        chinese_time_format = "%Y年%m月%d日%H时"
        # 使用strftime方法来格式化时间
        formatted_time = current_time.strftime(chinese_time_format)
        Shipment.objects.create(parcel=parcel_obj, status=102,
                                info=formatted_time + "快件已送至" + courier_obj.station.branch_office.name)
        latest_parcel = Parcel.objects.latest('timestamp')
        # 获取当前时间
        current_time = timezone.now()
        current_date = current_time.date()
        # 获取或创建统计记录
        statistic, created = Statistics.objects.get_or_create(
            date=current_date,
            branch_office=Parcel.objects.filter(timestamp=latest_parcel.timestamp).first().get_company,
            station=Parcel.objects.filter(timestamp=latest_parcel.timestamp).first().get_station,
            courier=Parcel.objects.filter(timestamp=latest_parcel.timestamp).first().get_courier
        )

        # 更新揽件统计
        statistic.dispatch_count += 1
        statistic.save()

        return redirect('/backstage/staff/company/')  # 重定向到某个页面或URL


@login_required_staff
def distinction_company_get(request, parcelID):
    if request.method == "GET":
        staff_info = request.session.get('staff')
        courier_obj = Courier.objects.filter(id=staff_info['id']).first()
        parcel_obj = Parcel.objects.filter(timestamp=parcelID).first()

        # 获取当前时间
        current_time = timezone.now().date()

        # 定义一个中文格式的时间字符串
        chinese_time_format = "%Y年%m月%d日%H时"
        # 使用strftime方法来格式化时间
        formatted_time = current_time.strftime(chinese_time_format)
        Shipment.objects.create(parcel=parcel_obj, status=103,
                                info=formatted_time + "快件已到达" + courier_obj.station.branch_office.name)
        return redirect('/backstage/staff/company/')  # 重定向到某个页面或URL


'''
    退回操作
'''


@login_required_staff
def send_back(request, parcelID):
    if request.method == "GET":
        parcel_obj = Parcel.objects.filter(timestamp=parcelID).first()
        # 获取当前时间
        current_time = timezone.now()

        # 定义一个中文格式的时间字符串
        chinese_time_format = "%Y年%m月%d日%H时"
        # 使用strftime方法来格式化时间
        formatted_time = current_time.strftime(chinese_time_format)

        Shipment.objects.create(parcel=parcel_obj, status=111,
                                info=formatted_time + "包裹已退回")

        return redirect('/backstage/staff/')  # 重定向到页面或URL
