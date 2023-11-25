from django.shortcuts import render

# Create your views here.


def statisticTime(request):
    return render(request, "statistic.html")

def statisticBranchCom(request):
    return render(request, "statistic.html")

def statisticBranchStation(request):
    return render(request, "statistic.html")

def statisticStaff(request):
    return render(request, "statistic.html")

def BranchCom(request):
    return render(request, "branchCom.html")

def BranchStation(request):
    return render(request, "branchStation.html")

def ManageStaff(request):
    return render(request, "ManageStaff.html")

def ManageGetPack(request):
    return render(request, "GetPackageMag.html")

def ManageDeliverPack(request):
    return render(request, "DeliverPackMag.html")