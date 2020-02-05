from django.urls import path
from rango import views

app_name = 'rango'

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    #use of category_name_slug below must match parameter name in view definition
    path('category/<slug:category_name_slug>/', views.show_category, name='show_category'),
]