from bs4 import BeautifulSoup
import urllib.request
import re
from datetime import datetime
from django.utils import timezone


def extraer_inmuebles(pags):
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
    inmuebles = []
    inmobiliaria_set = set()
    PAGINAS = pags
   
    for pagina in range(1, PAGINAS + 1):
        url1 = f"https://www.pisos.com/venta/pisos-sevilla_capital/"+str(pagina)+"/"
        f1 = urllib.request.urlopen(url1)
        s1 = BeautifulSoup(f1, "lxml")
        lista_inmuebles = s1.find_all("div", class_="ad-preview--has-desc")

        for inmueble in lista_inmuebles:
            detalles = inmueble.find("div", class_="ad-preview__info")
            titulo = detalles.find("a", class_="ad-preview__title").get_text(strip=True)
            antiguedad = "No hay información al respecto"
            precio = None
            precio_a = detalles.find("span", class_="ad-preview__price").get_text(strip=True)
            if precio_a:
                precio = re.sub(r"[^\d]", "", precio_a)
            url_piso = "https://www.pisos.com" + detalles.find("a", class_="ad-preview__title")['href']

            f2 = urllib.request.urlopen(url_piso)
            s2 = BeautifulSoup(f2, "lxml")

            ubicacion = detalles.find("p", class_="p-sm ad-preview__subtitle").get_text(strip=True)


            caracteristicas = s2.find("div", class_="features__content")
            habitaciones = None
            baños = None
            referencia = None
            planta = "No hay información al respecto"
            fecha = None
            referencia = "No hay información al respecto"
            if caracteristicas:
                
                hab = caracteristicas.find("span", string="Habitaciones: ")
                if hab:
                    habitaciones = int(hab.find_next_sibling("span").string.strip())

                bañ=caracteristicas.find("span", string="Baños: ")
                if bañ:
                    baños = int(bañ.find_next_sibling("span").string.strip())
                    
                
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
            inmobiliaria = "No hay información al respecto"
            link_inmobiliaria = ""
            inm = s2.find("p", class_="owner-info__name")
            if inm:
                inmobiliaria = inm.a.get_text(strip=True)
                link_inmobiliaria = "https://www.pisos.com" + inm.a['href']

            inmuebles.append({
                'titulo': titulo,
                'precio': float(precio) if precio else None,
                'url': url_piso,
                'habitaciones': habitaciones,
                'baños': baños,
                'planta': planta,
                'antiguedad': antiguedad,
                'referencia': referencia,
                'ubicacion': ubicacion,
                'fecha': fecha,
                'inmobiliaria': inmobiliaria,
                'link_inmobiliaria': link_inmobiliaria,
            })
            inmobiliaria_set.add((inmobiliaria, link_inmobiliaria))
    return inmuebles, inmobiliaria_set