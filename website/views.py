from functools import wraps
from django.shortcuts import render, HttpResponse, redirect
from backstage.models import *

# Create your views here.
def index(request):
    if request.method == "GET":
        print( *request.session.values())
        if request.session.values() == dict([]):
            userinfo = request.session['info']
            return render(request, "index.html", {'username': userinfo.username})
        else:
            return render(request, "index.html")
    else:
        if "PackId" in request.POST:
            return HttpResponse("快递单号")
        else:
            print(request.POST)
            return HttpResponse("发货订单")

def UserLogin(request):
    if request.method == "GET":
        return render(request, "login.html")
    else:
        username = request.POST.get("username")
        phone = request.POST.get("phone")
        userinfo = User.objects.filter(username=username, phone_number=phone).first()
        if userinfo is not None:
            request.session['info'] = {"id": userinfo.id, "username": userinfo.username}
            return redirect("/")
        else:
            error_message = "错误的用户名或手机号"
            return render(request, "login.html", {"error": error_message, "username": username, "phone": phone})