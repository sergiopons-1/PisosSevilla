from bs4 import BeautifulSoup
import urllib.request
import re
from datetime import datetime
import shutil
from whoosh.index import create_in
from whoosh.fields import Schema, TEXT, DATETIME, ID, NUMERIC
from django.utils import timezone

# lineas para evitar error SSL
import os, ssl
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context

def extraer_inmueble():
    """
    titulo                       
    habitaciones                 
    baños                              
    superficie util              
    precio                       
    antiguedad (en algunos pone conservacion)           
    referencia          
    Ubicacion (barrio/zona)       
    planta            
    ultima_actualizacion
    url inmueble   
    inmobiliaria que realiza la venta
    link de inmobiliaria                      
   """

    lista_pisos = []

    PAGINAS = 3
   
    for pagina in range(1, PAGINAS + 1):
        url1 = f"https://www.pisos.com/venta/pisos-sevilla_capital/"+str(pagina)+"/"
        f1 = urllib.request.urlopen(url1)
        s1 = BeautifulSoup(f1, "lxml")
        lista_inmuebles = s1.find_all("div", class_="ad-preview--has-desc")

        for inmueble in lista_inmuebles:
            detalles = inmueble.find("div", class_="ad-preview__info")
            titulo = detalles.find("a", class_="ad-preview__title").get_text(strip=True)
            antiguedad = "No hay informacion al respecto"
            precio_a = detalles.find("span", class_="ad-preview__price").get_text(strip=True)
            precio = re.sub(r"[^\d]", "", precio_a)
            url_piso = "https://www.pisos.com" + detalles.find("a", class_="ad-preview__title")['href']

            f2 = urllib.request.urlopen(url_piso)
            s2 = BeautifulSoup(f2, "lxml")

            ubicacion = detalles.find("p", class_="p-sm ad-preview__subtitle").get_text(strip=True)


            caracteristicas = s2.find("div", class_="features__content")
            habitaciones = None
            baños = None
            superficie_util = "No hay informacion al respecto"
            planta = "No hay informacion al respecto"
            antiguedad = "No hay informacion al respecto"
            referencia = "No hay informacion al respecto"
            if caracteristicas:
                
                hab = caracteristicas.find("span", string="Habitaciones: ")
                if hab:
                    habitaciones = int(hab.find_next_sibling("span").string.strip())

                bañ=caracteristicas.find("span", string="Baños: ")
                if bañ:
                    baños = int(bañ.find_next_sibling("span").string.strip())
                    
                sup = caracteristicas.find("span", string="Superficie útil: ")
                if sup:
                    superficie_util = sup.find_next_sibling("span").string.strip().replace("m²", " ")
                    
                pla = caracteristicas.find("span", string="Planta: ") 
                if pla:
                    planta = pla.find_next_sibling("span").string.strip()
                    
                ant = caracteristicas.find("span", string="Antigüedad: ")
                if ant:
                    antiguedad = ant.find_next_sibling("span").string.strip()
                
                ref = caracteristicas.find("span", string="Referencia: ")
                if ref:
                    referencia = ref.find_next_sibling("span").string.strip()

            fecha_texto = s2.find("p", class_="last-update__date").get_text(strip=True)
            fecha_match = re.search(r'\d{2}/\d{2}/\d{4}', fecha_texto)
            if fecha_match:
                fecha_naive = datetime.strptime(fecha_match.group(), '%d/%m/%Y')
                fecha = timezone.make_aware(fecha_naive)
            else:
                fecha = None

            inmobiliaria = "No hay información al respecto"
            link_inmobiliaria = ""
            inm = s2.find("p", class_="owner-info__name")
            if inm:
                inmobiliaria = inm.a.get_text(strip=True)
                link_inmobiliaria = "https://www.pisos.com" + inm.a['href']

            lista_pisos.append((titulo, float(precio), url_piso, habitaciones, baños, superficie_util, planta, antiguedad, referencia, ubicacion, fecha, inmobiliaria, link_inmobiliaria))

    return lista_pisos


def almacenar_bd_whoosh():
    schem = Schema(
        titulo=TEXT(stored=True, phrase=True),
        precio=NUMERIC(stored=True, numtype=float),
        url=ID(stored=True, unique=True),
        habitaciones=NUMERIC(stored=True, numtype=int),
        banos=NUMERIC(stored=True, numtype=int),
        superficie_util=TEXT(stored=True),
        planta=TEXT(stored=True),
        antiguedad=TEXT(stored=True),
        referencia=ID(stored=True),
        ubicacion=TEXT(stored=True),
        fecha=DATETIME(stored=True),
        inmobiliaria=TEXT(stored=True),
        link_inmobiliaria=ID(stored=True)
    )

    if os.path.exists("Index"):
        shutil.rmtree("Index")
    os.mkdir("Index")

    ix = create_in("Index", schema=schem)
    writer = ix.writer()
    i = 0
    inmuebles = extraer_inmueble()
    datos_almacenados = []
    for p in inmuebles:
        inmueble_dict = {'titulo': str(p[0]), 'precio': float(p[1]) if p[1] is not None else None, 'url': str(p[2]), 'habitaciones': int(p[3]) if p[3] is not None else None, 'banos': int(p[4]) if p[4] is not None else None, 'superficie_util': str(p[5]) if p[5] is not None else "", 'planta': str(p[6]) if p[6] is not None else "", 'antiguedad': str(p[7]) if p[7] is not None else "", 'referencia': str(p[8]) if p[8] is not None else "", 'ubicacion': str(p[9]) if p[9] is not None else "", 'fecha': p[10], 'inmobiliaria': str(p[11]) if p[11] is not None else "", 'link_inmobiliaria': str(p[12]) if p[12] is not None else ""}
        datos_almacenados.append(inmueble_dict)
        writer.add_document(
            titulo=str(p[0]),
            precio=float(p[1]) if p[1] is not None else None,
            url=str(p[2]),
            habitaciones=int(p[3]) if p[3] is not None else None,
            banos=int(p[4]) if p[4] is not None else None,
            superficie_util=str(p[5]) if p[5] is not None else "",
            planta=str(p[6]) if p[6] is not None else "",
            antiguedad=str(p[7]) if p[7] is not None else "",
            referencia=str(p[8]) if p[8] is not None else "",
            ubicacion=str(p[9]) if p[9] is not None else "",
            fecha=p[10] if p[10] is not None else None,
            inmobiliaria=str(p[11]) if p[11] is not None else "",
            link_inmobiliaria=str(p[12]) if p[12] is not None else ""
        )
        i += 1
    writer.commit()
    return i, datos_almacenados


