"""ExpressSys URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from website.views import *
from backstage.views import *

urlpatterns = [
    path("admin/", admin.site.urls),
    # 获取与分公司相对应的快递站
    path("get_station_index/", get_stations_index),
    path("save-scroll-position/", save_scroll_position),
    # 主页url
    path("", index),
    path("login/", UserLogin),
    path("logout/", logout),
    # 后台url

    # 后台登录url
    path("backstage/login/", adminLogin),
    path("backstage/", bs_page),

    path("backstage/adminLogout/", adminLogout),
    path("backstage/staffLogout/", staffLogout),
    # 后台404错误url
    path("backstage/404/", Page404),
    # 后台统计url
    path("backstage/statistic/time/", statisticTime),
    path("backstage/statistic/station/", statisticBranchStation),
    path("backstage/statistic/company/", statisticBranchCom),
    path("backstage/statistic/staff/", statisticStaff),
    # 后台分公司url
    path("backstage/company/", BranchCom),
    path("backstage/company/add/", BranchComAdd),
    path("backstage/company/edit/<int:comid>/", BranchComEdit),
    path("backstage/company/delete/<int:comid>/", BranchComDelete),
    # 后台快递站url
    path("backstage/station/", BranchStation),
    path("backstage/station/add/", BranchStationAdd),
    path("backstage/station/edit/<int:staid>/", BranchStationEdit),
    path("backstage/station/delete/<int:staid>/", BranchStationDelete),
    # 后台快递员url
    path('get_stations/', get_stations, name='get_stations'),
    path("backstage/staff/", ManageStaff),
    path("backstage/staff/add/", ManageStaffAdd),
    path("backstage/staff/edit/<int:staffid>/", ManageStaffEdit),
    path("backstage/staff/delete/<int:staffid>/", ManageStaffDelete),
    # 后台包裹管理url
    path("backstage/Pack/", ManagePack),
    path("backstage/Pack/edit/<int:packID>/", ManagePackEdit),
    path("backstage/Pack/delete/<int:packID>/", ManagePackDelete),

    path("backstage/deliverPack/", manage_deliver_pack),
    path("backstage/staff/", staff_page),
    path("backstage/staff/delivery/", staff_pack_manage),
    path("backstage/staff/company/", company_pack_manage),

    path("backstage/staff/get_success/<int:parcelID>/", get_success),
    path("backstage/staff/deliver_success/<int:parcelID>/", deliver_success),
    path("backstage/staff/send_back/<int:parcelID>/", send_back),
    path("backstage/staff/send_to_company/<int:parcelID>/", send_to_company),
    path("backstage/staff/distinction_company_get/<int:parcelID>/", distinction_company_get),
    path("backstage/staff/finish/<int:parcelID>/", finish),

]
