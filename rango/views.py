from django.shortcuts import render
from django.http import HttpResponse
from rango.models import Category, Page

# Create your views here.
def index(request):
    # construct a dictionary to pass template engine as its context
    # boldmessage matches template variable in index.html
    # query database for all categories, order by number of likes
    # retrieve only top 5, place in context_dict
    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]

    context_dict = {}
    context_dict['boldmessage'] = 'Crunchy, creamy, cookie, candy, cupcake!'
    context_dict['categories'] = category_list
    context_dict['pages'] = page_list

    # return rendered response to send to the client
    return render(request, 'rango/index.html', context=context_dict)


def about(request):
    return render(request, 'rango/about.html', {})

def show_category(request, category_name_slug):
    context_dict = {}

    try:
        # find category from slug?
        category = Category.objects.get(slug=category_name_slug)

        # retrieve all pages in this category (using filter())
        pages = Page.objects.filter(category=category)

        # Add results to context dict
        context_dict['pages'] = pages

        # Also add category to verify (in the template) it exists
        context_dict['category'] = category
    except Category.DoesNotExist:
        context_dict['category'] = None
        context_dict['pages'] = None

    return render(request, 'rango/category.html', context=context_dict)









