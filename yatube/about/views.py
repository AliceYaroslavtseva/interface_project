from django.views.generic.base import TemplateView


class IMommyHere(TemplateView):
    template_name = 'about/author.html'


class Tech(TemplateView):
    template_name = 'about/tech.html'
