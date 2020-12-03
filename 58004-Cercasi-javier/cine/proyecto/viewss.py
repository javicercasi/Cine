from django.shortcuts import render
from django.http.response import JsonResponse
from rest_framework.parsers import JSONParser
from rest_framework import status
from proyecto.models import Pelicula, Proyeccion, Sala, Reserva
from proyecto.serializers import PeliculaSerializer, ReservaSerializer, SalaSerializer, ProyeccionSerializer
from rest_framework.decorators import api_view


@api_view(['GET', 'POST', 'DELETE']) # decorador
def pelicula_list(request):
    if request.method == 'GET':
        peliculas = Pelicula.objects.all() #devolverme todos los elementos de la tabla

        name = request.GET.get('name', None) #si el titulo no tiene nada, que filtre por lo que tenga algo
        if name is not None:
            peliculas = peliculas.filter(name__icontains=name)

        peliculas_serializer = PeliculaSerializer(peliculas, many=True) #serializa las pelicula traidas
        return JsonResponse(peliculas_serializer.data, safe=False)  #Esa serializacion la usa para la respuesta del JSON

    elif request.method == 'POST':  # EL id no lo tengo que mandar
        pelicula_data = JSONParser().parse(request)  # Armar un parseo para recontruir el par clave valor
        pelicula_serializer = PeliculaSerializer(data=pelicula_data) #deserializar el dato
        if pelicula_serializer.is_valid(): # si es valido, lo grabo en mi DB
            pelicula_serializer.save()
            return JsonResponse(pelicula_serializer.data, status=status.HTTP_201_CREATED)
        return JsonResponse(pelicula_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        count = Pelicula.objects.all().delete()
        return JsonResponse({'message': '{} Tutorials were deleted successfully!'.format(count[0])}, status=status.HTTP_204_NO_CONTENT)



@api_view(['GET', 'PUT', 'DELETE'])
def pelicula_detail(request, pk): # Dato mandado clave para traer el dato
    # find tutorial by pk (id)
    try:
        print("PKKKK", pk)
        pelicula = Pelicula.objects.get(pk=pk) # Intenta cargar del modelo pelicula, mandandole como paramentro pk, si no responde, manda el 404
    except Pelicula.DoesNotExist:
        return JsonResponse({'message': 'The Film does not exist'}, status=status.HTTP_404_NOT_FOUND) 

    if request.method == 'GET':
        pelicula_serializer = PeliculaSerializer(pelicula) # Lo serializaba
        return JsonResponse(pelicula_serializer.data)

    elif request.method == 'PUT':  # Mandar en la url el id y el json con los datos modificados
        pelicula_data = JSONParser().parse(request)
        pelicula_serializer = PeliculaSerializer(pelicula, data=pelicula_data) 
        if pelicula_serializer.is_valid():
            pelicula_serializer.save()
            return JsonResponse(pelicula_serializer.data)
        return JsonResponse(pelicula_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        pelicula.delete()   # EL dato leido al principio lo eliminamos
        return JsonResponse({'message': 'Tutorial was deleted successfully!'}, status=status.HTTP_204_NO_CONTENT)
        # 204 es que se borro bien


@api_view(['GET'])
def pelicula_list_published(request):  # Leemos todos los datos de la BD, con una condicion de los publicados
    peliculas = Pelicula.objects.filter(published=True)

    if request.method == 'GET':
        peliculas_serializer = PeliculaSerializer(peliculas, many=True)  #Serializa lo de peliculas para el json
        return JsonResponse(peliculas_serializer.data, safe=False)
