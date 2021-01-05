from django.shortcuts import render
from django.http.response import JsonResponse
from rest_framework.parsers import JSONParser
from rest_framework import status
from proyecto.models import Pelicula, Proyeccion, Sala, Reserva
from proyecto.serializers import (PeliculaSerializer, ReservaSerializer,
                                  SalaSerializer, ProyeccionSerializer)
from rest_framework.decorators import api_view
from datetime import datetime, timedelta, date
import operator

# Get peliculas:

@api_view(['GET', 'POST', 'DELETE']) # decorador
def peliculas_list(request):
    if request.method == 'GET':
        peliculas = Pelicula.objects.all()      # Consultar todos los registros de la tabla
        rango = request.GET.get('rango', None)
        name = request.GET.get('name', None)
        if name is not None:
            peliculas = peliculas.filter(name__icontains=name)
        if rango is not None:
            peliculas = peliculas.filter(end_date__gte=(datetime.now() -
                                         timedelta(days=int(rango))),
                                         start_date__lte=(datetime.now() +
                                         timedelta(days=int(rango))))
        peliculas_serializer = PeliculaSerializer(peliculas, many=True)
        return JsonResponse(peliculas_serializer.data, safe=False)
        # Safe= False para serializacion de objetos

    elif request.method == 'POST':  # EL id no lo tengo que mandar
        pelicula_data = JSONParser().parse(request)  # Armar un parseo para recontruir el par clave valor
        pelicula_serializer = PeliculaSerializer(data=pelicula_data) #deserializar el dato json
        if pelicula_serializer.is_valid(): # si es valido, lo grabo en mi DB
            pelicula_serializer.save()
            return JsonResponse(pelicula_serializer.data, status=status.HTTP_201_CREATED)
        return JsonResponse(pelicula_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        count = Pelicula.objects.all().delete()
        return JsonResponse({'Message': '{} Films were deleted successfully!'.format(count[0])}, status=status.HTTP_204_NO_CONTENT)

# Get pelicula + Rango de fecha:

@api_view(['GET'])
def pelicula_detail(request, pk):
    try:
        pelicula = Pelicula.objects.get(pk=pk)
        inicio = datetime.strptime(request.GET.get('fecha', None), "%Y-%m-%d")
        fin = datetime.strptime(str(pelicula.end_date), "%Y-%m-%d")
    except Pelicula.DoesNotExist:
        return JsonResponse({'Message': 'The Film does not exist'}, status=status.HTTP_404_NOT_FOUND) 

    if request.method == 'GET':
        pelicula_serializer = PeliculaSerializer(pelicula)
        lista_fechas = ["Fechas en cartelera: "]
        lista_fechas += [(inicio + timedelta(days=d)).strftime("%Y-%m-%d") for d in range((fin - inicio).days + 1)] 
        if len(lista_fechas) == 1:
            lista_fechas += ["No se encuentra disponible"]
        return JsonResponse((pelicula_serializer.data, lista_fechas), safe=False)


# Get salas (Todas):

@api_view(['GET', 'POST', 'DELETE'])
def salas_list(request):
    if request.method == 'GET':
        sala = Sala.objects.all()
        name = request.GET.get('name', None)
        if name is not None:
            sala = sala.filter(name__icontains=name)

        salas_serializer = SalaSerializer(sala, many=True)
        return JsonResponse(salas_serializer.data, safe=False, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        sala = JSONParser().parse(request)
        salas_serializer = SalaSerializer(data=sala)
        if salas_serializer.is_valid():
            salas_serializer.save()
            return JsonResponse(salas_serializer.data, status=status.HTTP_201_CREATED)
        return JsonResponse(salas_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        count = Sala.objects.all().delete()
        return JsonResponse({'Message': '{} Cinemas were deleted successfully!'.format(count[0])}, status=status.HTTP_204_NO_CONTENT)


# Get sala:

@api_view(['GET', 'PUT', 'DELETE'])
def salas_detail(request, pk):
    try:
        sala = Sala.objects.get(pk=pk)
    except Sala.DoesNotExist:
        return JsonResponse({'Message': 'This Cinema does not exist'}, status=status.HTTP_404_NOT_FOUND) 

    if request.method == 'GET':
        sala_serializer = SalaSerializer(sala)
        return JsonResponse(sala_serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        sala_data = JSONParser().parse(request)
        sala_serializer = SalaSerializer(sala, data=sala_data)
        if sala_serializer.is_valid():
            sala_serializer.save()
            return JsonResponse(sala_serializer.data)
        return JsonResponse(sala_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        if sala.status == "Eliminada":
            sala.delete()
            return JsonResponse({'message': 'Sala was deleted successfully!'},
                                status=status.HTTP_204_NO_CONTENT)
        sala.status = "Eliminada"
        sala.save()
        return JsonResponse({'message': 'Sala cambio a estado Eliminado'},
                            status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
def proyecciones_list(request):

    try:
        inicio_in = request.GET.get('inicio', None)
        fin_in = request.GET.get('fin', None)
        dia = request.GET.get('dia', None)
        name = request.GET.get('name', None)
    except ValueError:
        pass

    fecha = date.today()
    proyecciones = Proyeccion.objects.all()

    if request.method == 'GET':
        # Get proyeccion + fecha:

        if dia is not None and name is not None:
            proyecciones_list = []
            sala_list = []
            pelicula_list = []
            butaca_list = []
            for proyeccion in proyecciones:
                lista_fechas = [(proyeccion.start_date + timedelta(days=d)).strftime("%Y-%m-%d") for d in range((proyeccion.end_date - proyeccion.start_date).days + 1)]
                pelicula = Pelicula.objects.get(id=proyeccion.pelicula.pk)
                sala = Sala.objects.get(id=proyeccion.sala.pk)
                butacas = Reserva.objects.filter(proyeccion=proyeccion.pk)
                if dia in lista_fechas:
                    if ((proyeccion.status == "Activo") and
                       (pelicula.status == "Activa") and
                       (sala.status == "Habilitada")):

                        if pelicula.name == name:
                            proyecciones_list.append(proyeccion)
                            sala_list.append(sala)
                            pelicula_list.append(pelicula)
                            for butaca in butacas:
                                if str(butaca.time_r) == dia:
                                    butaca_list.append(butaca)

            proyecciones_serializer = ProyeccionSerializer(proyecciones_list, many=True)
            sala_serializer = SalaSerializer(sala_list, many=True)
            pelicula_serializer = PeliculaSerializer(pelicula_list, many=True)
            b_serializer = ReservaSerializer(butaca_list, many=True)

            if len(proyecciones_list) == 0:
                proyecciones_list = ["La pelicula no se proyectara el dia seleccionado",]
                return JsonResponse((proyecciones_list), safe=False, status=status.HTTP_200_OK)
            return JsonResponse((proyecciones_serializer.data, sala_serializer.data, pelicula_serializer.data, ["Butacas Reservadas:"]+b_serializer.data), safe=False, status=status.HTTP_200_OK)

        # Get + rango de fecha:
        elif inicio_in is not None and fin_in is not None:
            inicio = datetime.strptime(inicio_in, "%Y-%m-%d")
            fin = datetime.strptime(fin_in, "%Y-%m-%d")
            proyecciones_list = []

            for proyeccion in proyecciones:
                lista_fechas_p = [(proyeccion.start_date + timedelta(days=d)).strftime("%Y-%m-%d") for d in range((proyeccion.end_date - proyeccion.start_date).days + 1)]
                lista_fechas_u = [(inicio + timedelta(days=d)).strftime("%Y-%m-%d") for d in range((fin - inicio).days + 1)]

                pelicula = Pelicula.objects.get(id=proyeccion.pelicula.pk)
                sala = Sala.objects.get(id=proyeccion.sala.pk)

                if len(lista_fechas_u) > len(lista_fechas_p):
                    x = lista_fechas_u
                    y = proyeccion.start_date
                    z = proyeccion.end_date

                if len(lista_fechas_u) <= len(lista_fechas_p):
                    x = lista_fechas_p
                    y = inicio_in
                    z = fin_in

                if str(y) in x or str(z) in x:
                    if ((proyeccion.status == "Activo") and
                       (pelicula.status == "Activa") and
                       (sala.status == "Habilitada")):
                        proyecciones_list.append(proyeccion)

        # GET todas proyectables:
        else:
            proyecciones_list = []
            for proyeccion in proyecciones:
                lista_fechas = [(proyeccion.start_date + timedelta(days=d)).strftime("%Y-%m-%d") for d in range((proyeccion.end_date - proyeccion.start_date).days + 1)]
                pelicula = Pelicula.objects.get(id=proyeccion.pelicula.pk)
                sala = Sala.objects.get(id=proyeccion.sala.pk)

                if str(fecha) in lista_fechas:
                    if ((proyeccion.status == "Activo") and
                       (pelicula.status == "Activa") and
                       (sala.status == "Habilitada")):
                        proyecciones_list.append(proyeccion)
                        lista_fechas = []

        proyeccion_serializer = ProyeccionSerializer(proyecciones_list, many=True)
        return JsonResponse(proyeccion_serializer.data, safe=False, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        proyecciones = JSONParser().parse(request)
        proyeccion_serializer = ProyeccionSerializer(data=proyecciones)
        if proyeccion_serializer.is_valid():
            proyeccion_serializer.save()
            return JsonResponse(proyeccion_serializer.data, status=status.HTTP_201_CREATED)
        return JsonResponse(proyeccion_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Get proyeccion.pk y put:
@api_view(['GET', 'PUT', 'DELETE'])
def proyecciones_detail(request, pk):
    try:
        proyeccion = Proyeccion.objects.get(pk=pk)
    except Proyeccion.DoesNotExist:
        return JsonResponse({'Message': 'La proyeccion no existe'},
                            status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        proyeccion_serializer = ProyeccionSerializer(proyeccion)
        return JsonResponse(proyeccion_serializer.data)

    if request.method == 'PUT':
        proyeccion_data = JSONParser().parse(request)
        proyeccion_serializer = ProyeccionSerializer(proyeccion, data=proyeccion_data)
        if proyeccion_serializer.is_valid():
            proyeccion_serializer.save()
            return JsonResponse(proyeccion_serializer.data)
        return JsonResponse(proyeccion_serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        proyeccion.delete()
        return JsonResponse({'Message': 'Proyeccion was deleted successfully!'},
                            status=status.HTTP_204_NO_CONTENT)


# Butacas
@api_view(['GET', 'POST', 'DELETE'])
def butacas_list(request):
    # Get butacas:
    if request.method == 'GET':
        butacas = Reserva.objects.all()
        butacas_serializer = ReservaSerializer(butacas, many=True)
        return JsonResponse(butacas_serializer.data, safe=False, status=status.HTTP_200_OK)

    if request.method == "POST":
        butaca = JSONParser().parse(request)
        butacas_serializer = ReservaSerializer(data=butaca)
        return posteo(butaca, butacas_serializer)

    elif request.method == 'DELETE':
        count = Reserva.objects.all().delete()
        return JsonResponse({'Message': '{} Butacas were deleted successfully!'.format(count[0])}, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'PUT', 'DELETE'])
def butacas_detail(request, pk):
    try:
        butaca_data = Reserva.objects.get(pk=pk)
    except Reserva.DoesNotExist:
        return JsonResponse({'Mensaje': 'La Butaca especificada no existe'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':     # Get + butaca:
        butaca_serializer = ReservaSerializer(butaca_data)
        return JsonResponse(butaca_serializer.data, safe=False, status=status.HTTP_200_OK)

    if request.method == "PUT":
        butaca = JSONParser().parse(request)
        butacas_serializer = ReservaSerializer(butaca_data, data=butaca)
        return posteo(butaca, butacas_serializer)

    elif request.method == 'DELETE':
        butaca_data.delete()
        return JsonResponse({'Message': 'Butaca was deleted successfully!'},
                            status=status.HTTP_204_NO_CONTENT)


def posteo(butaca, butacas_serializer):
    contador = num_vendidas = 0

    if butacas_serializer.is_valid():      # Ingresada por el usuario (clave)
        proyeccion = Proyeccion.objects.get(pk=butaca["proyeccion"])
        sala = Proyeccion.objects.get(pk=butaca['proyeccion']).sala

        if proyeccion.status == 'Activo':
            if (datetime.strptime(str(proyeccion.end_date), "%Y-%m-%d") >
               datetime.strptime(butaca["time_r"], "%Y-%m-%d") >=
               datetime.strptime(str(proyeccion.start_date), "%Y-%m-%d")):

                if int(butaca["row"]) <= sala.row and int(butaca["seat"]) <= sala.seat:
                    for butacas in Reserva.objects.filter(proyeccion=butaca["proyeccion"]):

                        num_vendidas = len(Reserva.objects.filter(proyeccion=butaca["proyeccion"]))

                        if butacas.row == butaca["row"] and butacas.seat != butaca["seat"]:
                            contador += 1           # Para que recorra si o si todos las butacas
                        if butacas.row != butaca["row"] and butacas.seat == butaca["seat"]:
                            contador += 1
                        if butacas.row != butaca["row"] and butacas.seat != butaca["seat"]:
                            contador += 1
                        if butacas.row == butaca["row"] and butacas.seat == butaca["seat"] and str(butacas.time_r) != butaca["time_r"]:
                            contador += 1

                    if contador == num_vendidas:
                        butacas_serializer.save()
                        return JsonResponse(butacas_serializer.data,
                                            status=status.HTTP_201_CREATED)
                    else:
                        return JsonResponse({'Mensaje': 'La Butaca ya fue vendida'},
                                            status=status.HTTP_200_OK)
                else:
                    return JsonResponse({'Mensaje': 'La Butaca es invalida'},
                                        status=status.HTTP_200_OK)
            else:
                return JsonResponse({'Mensaje': 'No hay proyeccion para ese dia'},
                                    status=status.HTTP_200_OK)
        else:
            return JsonResponse({'Mensaje': 'La proyeccion no esta activa'},
                                status=status.HTTP_200_OK)
    return JsonResponse(butacas_serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)

# Reportes:
@api_view(['GET'])
def reportes_list(request, pk=0):

    butacas = Reserva.objects.all()
    butacas_list = []

    try:
        inicio = datetime.strptime(request.GET.get('inicio', None), "%Y-%m-%d")
        fin = datetime.strptime(request.GET.get('fin', None), "%Y-%m-%d")
        lista_fechas_u = [(inicio + timedelta(days=d)).strftime("%Y-%m-%d") for d in range((fin - inicio).days + 1)]
    except TypeError:
        return JsonResponse({'Message': 'The query is wrong'}, status=status.HTTP_404_NOT_FOUND)

    # Entradas vendidas en un rango de tiempo:
    if inicio is not None and fin is not None and pk == 0:
        for butaca in butacas:
            if str(butaca.time_r) in lista_fechas_u:
                butacas_list.append(butaca)

    # Entradas vendidas en un rango de tiempo de una proyeccion particular:
    if pk != 0:
        try:
            butacas = Reserva.objects.filter(proyeccion=pk)
            for butaca in butacas:
                if str(butaca.time_r) in lista_fechas_u:
                    butacas_list.append(butaca)
        except Reserva.DoesNotExist:
            return JsonResponse({'Mensaje': 'La proyeccion no vendio butacas'}, status=status.HTTP_404_NOT_FOUND)

    if len(butacas_list) == 0:
        butacas_list = ["No hubo venta de butacas en ese rango"]
        return JsonResponse(butacas_list, safe=False, status=status.HTTP_200_OK)

    butacas_serializer = ReservaSerializer(butacas_list, many=True)
    return JsonResponse(["Entradas vendidas: "+str(len(butacas_list))]+butacas_serializer.data, safe=False, status=status.HTTP_200_OK)

# Ranking mas vendidas dado rango de tiempo:

@api_view(['GET'])
def reportes_ranking(request):
    butacas = Reserva.objects.all()
    butacas_fecha = []
    butacas_dic = {}
    x = 0
    contador = 0

    try:
        inicio = datetime.strptime(request.GET.get('inicio', None), "%Y-%m-%d")
        fin = datetime.strptime(request.GET.get('fin', None), "%Y-%m-%d")
        lista_fechas_u = [(inicio + timedelta(days=d)).strftime("%Y-%m-%d") for d in range((fin - inicio).days + 1)]
    except TypeError:
        return JsonResponse({'Message': 'The query is wrong'}, status=status.HTTP_404_NOT_FOUND)

    # Filtrado por fechas:
    if inicio is not None and fin is not None:
        for butaca in butacas:
            if str(butaca.time_r) in lista_fechas_u:
                butacas_fecha.append(butaca)

        for butaca in butacas_fecha:
            proyeccion = butaca.proyeccion
            pelicula = Pelicula.objects.get(pk=proyeccion.pelicula.pk)

            if proyeccion.pk != x and pelicula.name not in butacas_dic:
                butacas_dic[pelicula.name] = 1
                x = proyeccion.pk
            else:
                butacas_dic[pelicula.name] += 1

        butacas_ord = dict(sorted(butacas_dic.items(), key=operator.itemgetter(1), reverse=True))
        butacas_fecha = {}
        for elemento in butacas_ord.items():    # Ordenado por numeros:
            contador += 1
            if contador <= 5:
                butacas_fecha[elemento[0]] = elemento[1]

        d3 = {**{"Ranking de proyecciones": "5"}, **butacas_fecha}
    return JsonResponse(d3, safe=False, status=status.HTTP_200_OK)

# Entradas vendidas de peliculas activas:

@api_view(['GET'])
def reporte_peliculas(request):
    butacas = Reserva.objects.all()
    butacas_dic = {}
    x = 0

    for butaca in butacas:
        proyeccion = butaca.proyeccion
        pelicula = Pelicula.objects.get(pk=proyeccion.pelicula.pk)

        if pelicula.status == "Activa":
            if proyeccion.pk != x and pelicula.name not in butacas_dic:
                butacas_dic[pelicula.name] = 1
                x = proyeccion.pk
            else:
                butacas_dic[pelicula.name] += 1
    d3 = {**{"Estadisticas": "Entradas vendidas por pelicula"}, **butacas_dic}
    return JsonResponse(d3, safe=False, status=status.HTTP_200_OK)
