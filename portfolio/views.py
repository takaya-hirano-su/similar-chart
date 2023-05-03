from django.shortcuts import render

# Create your views here.
def get(request):
    return render(request=request,template_name="portfolio/portfolio.html",context={})
    