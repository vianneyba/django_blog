from django.urls import path
from .views import RequestCreateView

app_name = "requests_box"

urlpatterns = [
    path("demande/", RequestCreateView.as_view(), name="create"),
]