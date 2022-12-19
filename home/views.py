from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import redirect


# Create your views here.

def index(request):
    context = {}
    html_template = loader.get_template('index.html')
    return HttpResponse(html_template.render(context, request))


def pages(request):
    context = {}

    load_template = request.path.split('/')[-1]
    # MENU ADMIN
    if load_template == 'admin':
        return HttpResponseRedirect(reverse('admin:index'))

    # ====== OTHER MENU ======
    # if load_template == 'about.html':
    #     return redirect('/about.html')

    context['segment'] = load_template
    html_template = loader.get_template(load_template)
    return HttpResponse(html_template.render(context, request))
