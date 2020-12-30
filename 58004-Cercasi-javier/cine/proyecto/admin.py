from django.contrib import admin
from .models import Pelicula, Sala, Proyeccion, Reserva


class PeliculaAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'start_date', 'end_date', 'status')
    list_filter = ('status', 'start_date')
# Para cambiar la forma en la que un modelo se despliega en la interfaz de
# administración definimos una clase ModelAdmin (que describe el diseño)


class SalaAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'row', 'seat')
    list_filter = ('status',)


class ProyeccionAdmin(admin.ModelAdmin):
    list_display = ('pk', 'sala', 'pelicula', 'start_date', 'end_date', 'status')
    list_filter = ('status', 'pelicula')


class ReservaAdmin(admin.ModelAdmin):
    list_display = ('pk', 'proyeccion', 'time_r', 'row', 'seat')
    list_filter = ('time_r', 'proyeccion')


admin.site.register(Pelicula, PeliculaAdmin)
admin.site.register(Sala, SalaAdmin)
admin.site.register(Proyeccion, ProyeccionAdmin)
admin.site.register(Reserva, ReservaAdmin)

# registrar un modelo, o modelos, con el sitio de administracion
