from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^', include('proyecto.urls')),        # Cualquier peticion que se haga al proyecto, va a urls.py
]
