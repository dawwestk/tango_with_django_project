from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse
from rango.models import Category, Page
from django.contrib.auth import authenticate, login
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm

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

def add_category(request):
    form = CategoryForm()

    # HTTP POST?
    if request.method == "POST":
        form = CategoryForm(request.POST)

        # if the form valid?
        if form.is_valid():
            form.save(commit=True)
            # redirect back to index
            return redirect('/rango/')
        else:
            # form contained errors
            # print them to the terminal
            print(form.errors)

    return render(request, 'rango/add_category.html', {'form': form})

def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None

    # Can't add page to a non-existent Category
    if category is None:
        return redirect('/rango/')

    form = PageForm()

    if request.method == "POST":
        form = PageForm(request.POST)

        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()

                return redirect(reverse('rango:show_category', kwargs={'category_name_slug': category_name_slug}))
        else:
            print(form.errors)

    context_dict = {'form': form, 'category': category}
    return render(request, 'rango/add_page.html', context=context_dict)

def register(request):
    registered = False

    if request.method == 'POST':
        # attempt to grab info from the raw form info
        user_form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST)

        # if the two forms are valid
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()

            # now hash the password, and update
            user.set_password(user.password)
            user.save()

            # now sort out the UserProfile instance
            # needed the User attribute first so commit = False for now
            profile = profile_form.save(commit=False)
            profile.user = user

            # did the user provide a picture
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            profile.save()

            # profile registrationg was successful
            registered = True
        else:
            # something was wrong on the forms
            print(user_form.errors, profile_form.errors)
    else:
        # not an HTTP POST
        # render blank forms for user input
        user_form = UserForm()
        profile_form = UserProfileForm()

    return render(request, 'rango/register.html', context = {'user_form': user_form, 'profile_form': profile_form, 'registered': registered})

def user_login(request):
    if request.method == 'POST':
        # gather username and password from form
        # use request.POST.get('') as it returns None if not found
        # rather than a KeyError if we used request.POST['']
        username = request.POST.get('username')
        password = request.POST.get('password')

        # built-in django machinery checks if this combination is valid
        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)
                return redirect(reverse('rango:index'))
            else:
                return HttpResponse("Your Rango account is disabled.")
        else:
            # login details do not match any User
            print(f"Invalid login details: {username}, {password}")
            return HttpResponse("Invalid login details supplied.")

    else:
        # not a POST request
        return render(request, 'rango/login.html')




