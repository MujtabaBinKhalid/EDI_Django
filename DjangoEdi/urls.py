
from django.contrib import admin
from django.urls import include, path
#from service.views import tcpRequest
from statusService.views import statusReports
from django.conf.urls import url

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'', include("Login.urls")),
    path('index/', include("main.urls")),
]

try:
    # tcpRequest(repeat=300, repeat_until=None)
    statusReports(repeat=300, repeat_until=None)
except KLOeyboardInterrupt:
    print("Service Ended !! ")
