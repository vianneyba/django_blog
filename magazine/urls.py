from django.urls import path
from magazine import views

app_name = 'magazine'

urlpatterns = [
    path('add-paragraph/<pk>/', views.add_paragraph, name='add-paragraph'),
    path('add-photo/<pk>/', views.add_photo, name='add-photo'),
    path('add-insert/<pk>/', views.add_insert, name='add-insert'),
    path('add-link/<pk>/', views.add_link, name='add-link'),
    path('add-score/<pk>/', views.add_score, name='add-score'),
    path('view-article/<pk>/', views.view_article, name='view-article'),
    path('', views.write_article, name='write-article'),
]