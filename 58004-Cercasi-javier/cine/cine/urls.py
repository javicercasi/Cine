from django.conf.urls import url, include

urlpatterns = [
    url(r'^', include('proyecto.urls')),
]
# cualquier requerimiento pedido, anda a proyecto.urls.py
