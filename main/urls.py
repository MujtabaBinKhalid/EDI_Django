from django.urls import path
from . import views
from django.conf.urls import url

app_name = 'main'
urlpatterns = [
    # /indexPage/
    url(r'^$', views.index, name="index"),
    url(r'^creatingAccount/$', views.accountCreation, name="account"),
    url(r'^logout$', views.logout, name="logout")
]
