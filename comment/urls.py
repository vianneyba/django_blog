from django.urls import path
from . import views

app_name = 'comment'
urlpatterns = [
	path('add/<int:article_id>/', views.add, name='add'),
	path('update/<int:article_id>/<int:comment_id>', views.update, name='update')
]