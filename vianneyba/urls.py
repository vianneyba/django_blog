from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('', include('blog.urls')),
    path('accounts/', include('authenticate.urls')),
    path('comments/', include('comment.urls')),
    path('i-like/', include('like_dislike.urls')),
]

handler404 = "vianneyba.views.handler404"
handler500 = "vianneyba.views.handler500"