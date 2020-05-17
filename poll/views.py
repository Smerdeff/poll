from django.shortcuts import render

def home(request):
    #return render_to_response('encash/home.html')
    return render(request,'home.html')
