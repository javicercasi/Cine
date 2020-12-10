from django.db import models


class Pelicula(models.Model):
    name = models.CharField(max_length=70, blank=False)
    duration = models.IntegerField()  # Duracion en minutos
    description = models.CharField(max_length=200, default=False)  # descripcion breve
    detail = models.CharField(max_length=200)
    gender = models.CharField(max_length=30)
    classification = models.CharField(max_length=5)
    status = models.CharField(max_length=15)
    start_date = models.DateField()
    end_date = models.DateField()


class Sala(models.Model):
    name = models.CharField(max_length=70, blank=False)
    status = models.CharField(max_length=15)
    row = models.IntegerField()
    seat = models.IntegerField()


class Proyeccion(models.Model):
    sala = models.ForeignKey(Sala, on_delete=models.CASCADE)
    pelicula = models.ForeignKey(Pelicula, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    time = models.TimeField()   # Hora de proyeccion
    status = models.CharField(max_length=10)


class Reserva(models.Model):
    proyeccion = models.ForeignKey(Proyeccion, on_delete=models.CASCADE)
    time_r = models.DateField()
    row = models.IntegerField()
    seat = models.IntegerField()
