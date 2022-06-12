from django.urls import path, include
from rest_framework import routers
from . import views

app_name = 'game'

router = routers.DefaultRouter()
router.register(r'games', views.GamesViewset, basename='games')

urlpatterns = [
    # path('', views.index, name='index'),
    path('', views.list_game, name='list-game'),
    path('api/', include(router.urls)),
    # path('article/publish/<pk>/<value>', views.publish_article, name='publish-article'),
    # path('article/add/', views.add_article, name='add-article'),
    # path('article/update/<pk>', views.update_article, name='update-article'),
    # path('auteur/<author>/', views.by_author, name='by-author'),
    # path('tag/<tag>/', views.by_tag, name='by-tag'),
    path('run/<pk>/', views.run_game, name='run-game'),
]