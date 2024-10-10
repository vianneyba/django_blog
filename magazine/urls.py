from django.urls import path, include
from rest_framework.routers import DefaultRouter
from magazine import views

app_name = 'magazine'

urlpatterns = [
    path('add-article', views.add_article, name='add-article'),
    path('view-article/<m_type>/<pk>/', views.view_article, name='view-article'),      # Vue d'un test
    path('ini-to-html/', views.ini_to_html, name='ini-to-html'),
    path('', views.list_articles, name='list-articles'),                                # Liste tous les tests
    path('import/<id_mag>/<title_mag>/<num_mag>', views.import_mag, name='import-mag'),
    path('view-page', views.view_page, name='view-page'),                               # Vue pour voir et modifier un test d'un magazine
    path('search-article', views.search_article, name='search-article'),                # Vue de recherche d'un test d'un magazine
    path('view', views.view_magazine, name='view-magazine'),
    path('scan', views.scan, name='scan'),
    
]