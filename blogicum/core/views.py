from django.shortcuts import render
from django.http import HttpRequest, HttpResponse


def page_not_found(request: HttpRequest, exception) -> HttpResponse:
    return render(request, 'pages/404.html', status=404)


def csrf_failure(request, reason=''):
    return render(request, 'pages/403csrf.html', status=403)


def server_failure(request):
    return render(request, 'pages/500.html', status=500)
