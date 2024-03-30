"""Views of pages app."""
from http import HTTPStatus

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.generic import TemplateView


class AboutPage(TemplateView):
    """Template view for about page."""

    template_name = 'pages/about.html'


class RulesPage(TemplateView):
    """Template view for rules page."""

    template_name = 'pages/rules.html'


def forbidden(request: HttpRequest, exception) -> HttpResponse:
    """View function for 403 page."""
    return render(request, 'pages/403.html', status=HTTPStatus.FORBIDDEN)


def csrf_failure(request: HttpRequest, reason='') -> HttpResponse:
    """View function for 403 CSRF failure page."""
    return render(request, 'pages/403csrf.html', status=HTTPStatus.FORBIDDEN)


def page_not_found(request: HttpRequest, exception) -> HttpResponse:
    """View function for 404 page."""
    return render(request, 'pages/404.html', status=HTTPStatus.NOT_FOUND)


def server_failure(request: HttpRequest) -> HttpResponse:
    """View function for 505 page."""
    return render(
        request, 'pages/500.html', status=HTTPStatus.INTERNAL_SERVER_ERROR
    )
