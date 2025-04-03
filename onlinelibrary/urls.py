from django.urls import path

from . import views

app_name = "onlinelibrary"
urlpatterns = [


path("signup/", views.signup, name ="signup"),
path("signin/", views.signin, name = "signin"),
path("homeview/", views.homeview, name = "homeview"),



]