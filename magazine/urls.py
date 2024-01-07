from django.urls import path, include
from rest_framework.routers import DefaultRouter
from magazine import views

app_name = 'magazine'

router = DefaultRouter()
router.register(r'articles', views.ArticleList, basename='articles')

urlpatterns = [
    path('view/<slug>/', views.view, name='view'),
    path('add-paragraph/<pk>/', views.add_paragraph, name='add-paragraph'),
    path('add-photo/<pk>/', views.add_photo, name='add-photo'),
    path('add-photo-insert/<pk>/<pk_insert>', views.add_photo_insert, name='add-photo-insert'),
    path('add-insert/<pk>/', views.add_insert, name='add-insert'),
    path('add-link/<pk>/', views.add_link, name='add-link'),
    path('add-score/<pk>/', views.add_score, name='add-score'),
    path('add-opinion/<pk>', views.add_opinion, name='add-opinion'),
    path('view-article/<pk>/', views.view_article, name='view-article'),
    path('', views.write_article, name='write-article'),
    path('api/', include(router.urls)),
]