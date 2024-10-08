from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from vianneyba import views

urlpatterns = [
    path('', views.index, name='index'),
    path('admin/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('launch-game/', include('game.urls')),
    path('music/', include('music.urls')),
    path('accounts/', include('authenticate.urls')),
    path('comments/', include('comment.urls')),
    path('i-like/', include('like_dislike.urls')),
    path('article/', include('magazine.urls')),
    path('polls/', include('polls.urls')),
    path('blog/', include('blog.urls')),
]

handler404 = "vianneyba.views.handler404"
handler500 = "vianneyba.views.handler500"