
from django.contrib import admin
from django.urls import include, path
from service.views import tcpRequest
from main.views import startingThreads
from django.conf.urls import url

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'', include("Login.urls")),
    path('index/', include("main.urls")),
]


try:
    print ("hello-1")
    startingThreads(repeat=5)
except KeyboardInterrupt:
    print("Service Ended !! ")


# try:
#     print ("hello-2")
#     statusReports(repeat=300)
# except KeyboardInterrupt:
#     print("Service Ended !! ")

