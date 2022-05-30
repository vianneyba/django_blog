from django.urls import path
from . import views

app_name= 'blog'
urlpatterns = [
    path('', views.index, name='index'),
    path('category/<category>/', views.by_category, name='by-category'),
    path('auteur/<author>/', views.by_author, name='by-author'),
    path('tag/<tag>/', views.by_tag, name='by-tag'),
    path('<slug>/', views.by_slug, name='by-slug'),
]