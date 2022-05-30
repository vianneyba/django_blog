from django.urls import path
from . import views

app_name = 'comment'
urlpatterns = [
	path('add/<int:article_id>/', views.add, name='add'),
	path('view', views.view, name='view')
]