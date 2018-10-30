from django.urls import path
from . import views
from django.conf.urls import url

app_name = 'status_report'
urlpatterns = [
    url(r'^generatingReport/$', views.generatingReport, name="generating_report"),
]
