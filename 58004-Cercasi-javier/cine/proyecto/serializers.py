from rest_framework import serializers
from proyecto.models import Pelicula, Proyeccion, Sala, Reserva


class PeliculaSerializer(serializers.ModelSerializer):

    class Meta:
        model = Pelicula
        fields = ('id',
                  'name',
                  'duration',
                  'description',
                  'detail',
                  'gender',
                  'classification',
                  'status',
                  'start_date',
                  'end_date')


class ProyeccionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Proyeccion
        fields = ('id',
                  'start_date',
                  'end_date',
                  'time',
                  'status',
                  'pelicula',
                  'sala')


class SalaSerializer(serializers.ModelSerializer):

    class Meta:
        model = Sala
        fields = ('id',
                  'name',
                  'status',
                  'row',
                  'seat')


class ReservaSerializer(serializers.ModelSerializer):

    class Meta:
        model = Reserva
        fields = ('id',
                  'time_r',
                  'row',
                  'seat',
                  'proyeccion')
