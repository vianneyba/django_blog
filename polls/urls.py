from django.urls import path
from . import views

app_name = "polls"

urlpatterns = [
    path("vote/<slug:slug>/", views.vote, name="vote"),
]