from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def index(request):
    # constructu a dictionary to pass template engine as its context
    # boldmessage matches template variable in index.html
    context_dict = {'boldmessage': 'Crunchy, creamy, cookie, candy, cupcake!'}

    # return rendered response to send to the client
    return render(request, 'rango/index.html', context=context_dict)


def about(request):
    return render(request, 'rango/about.html', {})