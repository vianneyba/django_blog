from django.urls import path
from . import views

app_name = 'like_dislike'
urlpatterns = [
	path('like', views.add_like, name='add-like'),
]