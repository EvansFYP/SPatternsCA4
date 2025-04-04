from django.conf import settings
from django.urls import path
from django.conf.urls.static import static
from . import views

app_name = "onlinelibrary"
urlpatterns = [


path("signup/", views.signup, name ="signup"),
path("signin/", views.signin, name = "signin"),
path("home/", views.home, name = "home"),
path("additem/", views.additem, name ="additem"),
path("viewitem/", views.viewitem, name ="viewitem"),
path('itemdetail/<int:item_id>/', views.itemdetail, name='itemdetail'),
path('item/delete/<int:item_id>/', views.deleteitem, name='deleteitem'),
path('item/edit/<int:item_id>/', views.edititem, name='edititem'),

]
