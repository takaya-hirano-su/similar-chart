from django.shortcuts import render
from .forms import Form

# Create your views here.
def index(request):

    if request.method=="POST":
        params={
            "forms":Form(request.POST),
            "msg":f"{request.POST['market']},{request.POST['pair']},{request.POST['date']}"
        }
    else:
        params={
            "forms":Form(),
            "msg":""
        }

    return render(request=request,template_name="main/index.html",context=params)