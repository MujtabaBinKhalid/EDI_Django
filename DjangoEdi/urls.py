
from django.contrib import admin
from django.urls import include, path
from service.views import tcpRequest
urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', include("Login.urls")),
    path('index/', include("main.urls")),
]
try:
    tcpRequest(repeat=300, repeat_until=None)
except KeyboardInterrupt:
    print("Service Ended !! ")
