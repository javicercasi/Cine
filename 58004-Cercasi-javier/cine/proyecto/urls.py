from django.conf.urls import url
from proyecto import views

urlpatterns = [
    url(r'^api/proyecto$', views.pelicula_list),
    url(r'^api/proyecto/(?P<pk>[0-9]+)$', views.pelicula_detail), #pk=como un primary key, que lo tome literal, y llame a la funcion view.pelicula
    url(r'^api/proyecto/published$', views.pelicula_list_published)
]
