from principal.models import Inmueble, Inmobiliaria
from bs4 import BeautifulSoup
import urllib.request
import re
from datetime import datetime
from django.utils import timezone
from principal.beautifulSoup.beautifulSoup import extraer_inmuebles
def extraer_pisos():
    """
    titulo                       
    habitaciones                 
    baños                         
    precio                       
    antiguedad (en algunos pone conservacion)           
    referencia          
    Ubicacion (barrio/zona)       
    planta            
    ultima_actualizacion
    url                    
    inmobiliaria que realiza la venta      
   """
def extraer_pisos():
    Inmueble.objects.all().delete()
    Inmobiliaria.objects.all().delete()

    lista_inmuebles, inmobiliaria_set = extraer_inmuebles()
    
    inmobiliaria_map = {}
    for (nombre_inm, link_inm) in inmobiliaria_set:
        obj, _ = Inmobiliaria.objects.get_or_create(nombre=nombre_inm, link=link_inm)
        inmobiliaria_map[(nombre_inm, link_inm)] = obj

    for inmueble in lista_inmuebles:
        key = (inmueble['inmobiliaria'], inmueble['link_inmobiliaria'])
        inmobiliaria_obj = inmobiliaria_map.get(key)
        Inmueble.objects.create(
            titulo=inmueble['titulo'],
            precio=float(inmueble['precio']),
            url=inmueble['url'],
            habitaciones=inmueble['habitaciones'],
            banos=inmueble['baños'],
            planta=inmueble['planta'],
            antiguedad=inmueble['antiguedad'],
            referencia=inmueble['referencia'],
            ubicacion=inmueble['ubicacion'],
            fecha_actualizacion=inmueble['fecha'],
            inmobiliaria=inmobiliaria_obj
        )

    return ((Inmueble.objects).count(), (Inmobiliaria.objects).count())