from django.shortcuts import render
from .forms import Form
from django.views.generic import FormView,TemplateView
from .models import Pair,Market

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


class IndexView(TemplateView):
    
    def get(self,request):
        params={
            "forms":Form(),
            "msg":"",
        }
        return render(request=request,template_name="main/index.html",context=params)
    
    def post(self,request):
        
        market=Market.objects.filter(market=request.POST["market"])[0]
        choices=Pair.objects.filter(market=market)
        choices=[choice.pair for choice in choices]

        ##取引所で扱ってない通貨ペアが入力されたら強制的に書き換える
        request_cp=request.POST.copy() #そのままでは書き換えられないからコピー
        if not request.POST["pair"] in choices: #書き換え
            request_cp["pair"]=choices[0]
        ##

        ##通貨ペアを取引所で扱ってるものだけにする
        _form=Form(request_cp)
        _form.fields["pair"].choices=[(choice,choice) for choice in choices] 
        _form.base_fields["pair"].choices=[(choice,choice) for choice in choices] 
        ##

        params={
            "forms":_form,
            "msg":f"{request_cp['market']},{request_cp['pair']},{request_cp['date']}",
        }

        return render(request=request,template_name="main/index.html",context=params)