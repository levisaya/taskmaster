from django.template import RequestContext
from django.shortcuts import render


def taskmaster_main(request):
    return render(request, 'taskmaster_app/main.html', {'message': 'heeeelo!'})