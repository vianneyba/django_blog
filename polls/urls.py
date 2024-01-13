from django.urls import path
from polls import views

app_name = 'polls'

urlpatterns = [
    path('add_title_suggestion/', views.add_title_suggestion, name='add-title-suggestion'),
    path('valid_top/', views.valid_liste_title, name='valid-top')
]