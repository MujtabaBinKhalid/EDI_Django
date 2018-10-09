from django.urls import path
from . import views
from django.conf.urls import url

app_name = 'login'
urlpatterns = [
    # /login/
    url(r'^$', views.index, name="index"),




]
