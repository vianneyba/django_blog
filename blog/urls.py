from django.urls import path, include
from rest_framework import routers
from . import views

app_name = 'blog'

router = routers.DefaultRouter()
router.register(r'articles', views.ArticleViewset, basename='articles')

urlpatterns = [
    path('', views.index, name='index'),
    path('api/', include(router.urls)),
    path('category/<category>/', views.by_category, name='by-category'),
    path('article/publish/<pk>/<value>', views.publish_article, name='publish-article'),
    path('article/add/', views.add_article, name='add-article'),
    path('article/update/<pk>', views.update_article, name='update-article'),
    path('auteur/<author>/', views.by_author, name='by-author'),
    path('tag/<tag>/', views.by_tag, name='by-tag'),
    path('blog/<slug>/', views.by_slug, name='by-slug'),
]