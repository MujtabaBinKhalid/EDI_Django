
from django.contrib import admin
from django.urls import include, path
#from service.views import tcpRequest
from django.conf.urls import url

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'', include("Login.urls")),
    path('index/', include("main.urls")),
    path('status/', include("statusReport.urls")),
]

# try:
#     tcpRequest(repeat=300, repeat_until=None)
# except KeyboardInterrupt:
#     print("Service Ended !! ")
