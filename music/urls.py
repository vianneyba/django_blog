from django.urls import path, include
from rest_framework.routers import DefaultRouter
from music import views

app_name = "music"

router = DefaultRouter()
router.register(r'albums', views.AlbumList, basename='albums')

urlpatterns = [
    path('', views.index, name='index'),
    path('viewalbum/code/<pk>', views.view_album_by_code, name='index'),
    path('viewalbum/<pk>', views.view_album, name='view-album'),
    path('musicaddtracknote/', views.music_add_track_note, name='music-add-track-note'),
    path('musicaddalbumnote/', views.music_add_album_note, name='music-add-album-note'),
    path('search/', include(router.urls)),
    path('api/', include(router.urls)),
]