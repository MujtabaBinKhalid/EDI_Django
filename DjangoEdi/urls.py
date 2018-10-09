
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', include("Login.urls")),
    path('index/', include("main.urls")),

]
