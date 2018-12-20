from django.urls import path
from . import views
from django.conf.urls import url

app_name = 'main'
urlpatterns = [
    url(r'^$', views.index, name="index"),
    url(r'^creatingAccount/$', views.accountCreation, name="account"),
    url(r'^statusReport/$', views.statusReport, name="report"),
    url(r'^companyActiveLoads/$', views.activeLoads, name="activeLoads"),
    url(r'^logout$', views.logout, name="logout"),
    url(r'^generatingReport/$', views.generatingReport, name="generating_report"),
    url(r'^statusPaths/$', views.creatingStatusPaths, name="status_paths"),
    url(r'^establishingConnection/$', views.establishingConnection, name="establishingConnection"),
]
