from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse
from rango.models import Category, Page, UserProfile
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from datetime import datetime
from rango.bing_search import run_query
from django.views import View
from django.utils.decorators import method_decorator

class IndexView(View):
    def get(self, request):
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

        # keep this call to increment the counter
        visitor_cookie_handler(request)

        # return rendered response to send to the client
        response = render(request, 'rango/index.html', context=context_dict)
        return response

class AboutView(View):
    def get(self, request):
        context_dict = {}

        visitor_cookie_handler(request)
        context_dict['visits'] = request.session['visits']

        return render(request, 'rango/about.html', context_dict)

class ShowCategoryView(View):

    def create_context_dict(self, category_name_slug):
        context_dict = {}

        try:
            # find category from slug?
            category = Category.objects.get(slug=category_name_slug)

            # retrieve all pages in this category (using filter())
            pages = Page.objects.filter(category=category)
            page_list = pages.order_by('-views')
            # Add results to context dict
            context_dict['pages'] = page_list

            # Also add category to verify (in the template) it exists
            context_dict['category'] = category
        except Category.DoesNotExist:
            context_dict['category'] = None
            context_dict['pages'] = None

        return context_dict

    def get(self, request, category_name_slug):
        context_dict = self.create_context_dict(category_name_slug)
        return render(request, 'rango/category.html', context_dict)

    @method_decorator(login_required)
    def post(self, request, category_name_slug):
        context_dict = self.create_context_dict(category_name_slug)
        query = request.POST.get('query').strip()

        if query:
            context_dict['results_list'] = run_query(query)
            context_dict['query'] = query

        return render(request, 'rango/category.html', context_dict)

class AddCategoryView(View):
    @method_decorator(login_required)
    def get(self, request):
        form = CategoryForm()
        return render(request, 'rango/add_category.html', {'form': form})

    @method_decorator(login_required)
    def post(self, request):
        form = CategoryForm(request.POST)

        # if the form valid?
        if form.is_valid():
            form.save(commit=True)
            # redirect back to index
            return redirect(reverse('rango:index'))
        else:
            # form contained errors
            # print them to the terminal
            print(form.errors)

        return render(request, 'rango/add_category.html', {'form': form})
'''
@login_required
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
'''

class AddPageView(View):
    def get_category_name(self, category_name_slug):
        try:
            category = Category.objects.get(slug=category_name_slug)
        except Category.DoesNotExist:
            category = None

        return category

    @method_decorator(login_required)
    def get(self, request, category_name_slug):
        form = PageForm()
        category = self.get_category_name(category_name_slug)

        if category is None:
            return redirect(reverse('rango:index'))

        context_dict = {'form': form, 'category': category}
        return render(request, 'rango/add_page.html', context_dict)

    @method_decorator(login_required)
    def post(self, request, category_name_slug):
        form = PageForm(request.POST)
        category = self.get_category_name(category_name_slug)

        if category is None:
            return redirect(reverse('rango:index'))

        if form.is_valid():
            page = form.save(commit=False)
            page.category = category
            page.views = 0
            page.save()

            return redirect(reverse('rango:show_category', kwargs={'category_name_slug': category_name_slug}))
        else:
            print(form.errors)

        context_dict = {'form': form, 'category': category}
        return render(request, 'rango/add_page.html', context_dict)


'''
    --------------- Login/Registration code now handled by registration-redux
    
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

@login_required
def user_logout(request):
    # We know the user is logged in because of the decorator
    logout(request)
    return redirect(reverse('rango:index'))

    --------------- Login/Registration code now handled by registration-redux
'''

class RestrictedView(View):
    @method_decorator(login_required)
    def get(self, request):
        return render(request, 'rango/restricted.html')

def visitor_cookie_handler(request):
    # get number of visits to site
    # use the COOKIES.get() function
    visits = int(get_server_side_cookie(request, 'visits', '1'))    # default = 1 if nothing found

    last_visit_cookie = get_server_side_cookie(request, 'last_visit', str(datetime.now()))
    last_visit_time = datetime.strptime(last_visit_cookie[:-7], '%Y-%m-%d %H:%M:%S')

    # if its been more than a day since last visit
    if (datetime.now() - last_visit_time).days > 0:
        visits = visits + 1
        # update the last visit cookie
        request.session['last_visit'] = str(datetime.now())
    else:
        # set the last visit cookie
        request.session['last_visit'] = last_visit_cookie

    request.session['visits'] = visits

def get_server_side_cookie(request, cookie, default_val=None):
    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val

'''
def search(request):
    result_list = []
    query = ''
    if request.method == 'POST':
        query = request.POST['query'].strip()
        if query:
            result_list = run_query(query)
    return render(request, 'rango/search.html', {'result_list': result_list, 'query': query})
'''

class GoToView(View):
    def get(self, request):
        page_id = request.GET.get('page_id')
        try:
            page = Page.objects.get(id=page_id)
            page.views = page.views + 1
            page.save()
            return redirect(page.url)
        except Page.DoesNotExist:
            return redirect(reverse('index'))

class RegisterProfileView(View):
    @method_decorator(login_required)
    def get(self, request):
        form = UserProfileForm()
        context_dict = {'form': form}
        return render(request, 'rango/profile_registration.html', context_dict)

    @method_decorator(login_required)
    def post(self, request):
        profile_form = UserProfileForm(request.POST, request.FILES)
        # if the form is valid
        if profile_form.is_valid():
            # now sort out the UserProfile instance
            # needed the User attribute first so commit = False for now
            profile = profile_form.save(commit=False)
            profile.user = request.user
            # did the user provide a picture
            # if 'picture' in request.FILES:
            #    profile.picture = request.FILES['picture']

            profile.save()
            return redirect(reverse('rango:index'))
        else:
            print(profile_form.errors)

        context_dict = {'form': profile_form}
        return render(request, 'rango/profile_registration.html', context_dict)

class ProfileView(View):
    def get_user_details(self, username):
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return None

        user_profile = UserProfile.objects.get_or_create(user=user)[0]
        form = UserProfileForm({'website': user_profile.website, 'picture': user_profile.picture})

        return (user, user_profile, form)

    @method_decorator(login_required)
    def get(self, request, username):
        try:
            (user, user_profile, form) = self.get_user_details(username)
        except TypeError:
            return redirect(reverse('rango:index'))

        context_dict = {'user_profile': user_profile, 'selected_user': user, 'form': form}

        return render(request, 'rango/profile.html', context_dict)

    @method_decorator(login_required)
    def post(self, request, username):
        try:
            (user, user_profile, form) = self.get_user_details(username)
        except TypeError:
            return redirect(reverse('rango:index'))

        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)

        if form.is_valid():
            form.save(commit=True)
            return redirect(reverse('rango:profile', kwargs={'username': username}))
        else:
            print(form.errors)

        context_dict = {'user_profile': user_profile, 'selected_user': user, 'form': form}
        return render(request, 'rango/profile.html', context_dict)

class ListProfileView(View):
    @method_decorator(login_required)
    def get(self, request):
        profiles = UserProfile.objects.all()

        return render(request, 'rango/list_profiles.html', {'user_profile_list': profiles})





