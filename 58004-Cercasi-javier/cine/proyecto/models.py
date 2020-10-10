from django.db import models


class Pelicula(models.Model):
    name = models.CharField(max_length=70, blank=False)
    duration = models.IntegerField(max_length=10)  # Duracion en minutos
    description = models.CharField(max_length=200, default=False)  # descripcion breve
    detail = models.CharField(max_length=200)
    gender = models.CharField(max_length=30)
    classification = models.CharField(max_length=5)
    status = models.CharField(max_length=15)
    start_date = models.DateField()
    end_date = models.DateField()


