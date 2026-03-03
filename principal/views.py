from django.shortcuts import render
from principal.models import Inmueble, Inmobiliaria
from principal.populateDB import extraer_pisos
from principal.whoosh.whoosh_trabajo import almacenar_bd_whoosh
from django.shortcuts import render, redirect
from django.utils import timezone
from django.core.paginator import Paginator
from datetime import timedelta
from whoosh.index import open_dir
from whoosh.writing import AsyncWriter
from whoosh.qparser import QueryParser, OrGroup, plugins, MultifieldParser
from whoosh.query import NumericRange, DateRange
from datetime import datetime

################################### BS ###################################

def inicio(request):
    num_inmuebles=Inmueble.objects.all().count()
    num_inmobiliarias=Inmobiliaria.objects.all().count()
    return render(request,'inicio.html', {'num_inmuebles':num_inmuebles, 'num_inmobiliarias': num_inmobiliarias})

def listar_inmuebles(request):
    inmuebles = Inmueble.objects.all()
    num_inmuebles = inmuebles.count()

    paginator = Paginator(inmuebles, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'inmuebles.html', {
        'inmuebles': page_obj,
        'num_inmuebles': num_inmuebles,
        'page_obj': page_obj,
    })

def listar_inmobiliarias(request):
    inmobiliarias=Inmobiliaria.objects.all()
    num_inmobiliarias=Inmobiliaria.objects.all().count()
    return render(request,'mostrarinmobiliarias.html', {'inmobiliarias':inmobiliarias, 'num_inmobiliarias':num_inmobiliarias})

def cargar_bd(request):
    paginas = request.GET.get('num_pags', None)
    if not paginas:
        return render(request, 'cargaBD.html', {'mensaje': 'Selecciona cuántas páginas quieres cargar (entre 3 y 10).'})

    try:
        paginas_int = int(paginas)
        if paginas_int < 3 or paginas_int > 10:
            raise ValueError
    except ValueError:
        return render(request, 'cargaBD.html', {'mensaje': 'El número de páginas debe estar entre 3 y 10.'})

    num_inmuebles, num_inmobiliarias = extraer_pisos(paginas_int)
    mensaje = "Se han almacenado: " + str(num_inmuebles) + " inmuebles y " + str(num_inmobiliarias) + " inmobiliarias en la base de datos."
    return render(request, 'cargaBD.html', {'mensaje': mensaje})

def carga(request):
    if request.method=='POST':
        if 'Aceptar' in request.POST:      
            num_inmuebles, num_inmobiliarias = extraer_pisos()
            mensaje="Se han almacenado: " + str(num_inmuebles) +" inmuebles y " + str(num_inmobiliarias) + " inmobiliarias en la base de datos."
            return render(request, 'cargaBD.html', {'mensaje':mensaje})
        else:
            return redirect("/")
           
    return render(request, 'confirmacion.html')

def buscarrangodeprecios(request):
    precio_max = request.GET.get('precio_max', None)
    precio_min = request.GET.get('precio_min', None)
    inmuebles = []
    mostrar_resultados = False
    
    if precio_max:
        try:
            precio_max_float = float(precio_max)
            precio_min_float = float(precio_min)
            inmuebles = Inmueble.objects.filter(precio__gte=precio_min_float, precio__lte=precio_max_float).order_by('precio')
            mostrar_resultados = True
        except ValueError:
            precio_max = None
            precio_min = None
    
    context = {
        'inmuebles': inmuebles,
        'precio_max': precio_max,
        'precio_min': precio_min,
        'mostrar_resultados': mostrar_resultados,
    }
    
    return render(request, 'buscarrangodeprecios.html', context)

def buscarporhabitaciones(request):
    num_habitaciones = request.GET.get('habitaciones', None)
    inmuebles = []
    mostrar_resultados = False
    
    opciones_raw = Inmueble.objects.values_list('habitaciones', flat=True).distinct().order_by('habitaciones')
    
    opciones_habitaciones = []
    for opcion in opciones_raw:
        if opcion is None:
            opciones_habitaciones.append((None, 'no hay información'))
        else:
            opciones_habitaciones.append((opcion, str(opcion)))
    
    if num_habitaciones:
        if num_habitaciones.lower() == 'none':
            inmuebles = Inmueble.objects.filter(habitaciones__isnull=True).order_by('precio')
            mostrar_resultados = True
        else:
            try:
                num_habitaciones_int = int(num_habitaciones)
                inmuebles = Inmueble.objects.filter(habitaciones=num_habitaciones_int).order_by('precio')
                mostrar_resultados = True
            except ValueError:
                num_habitaciones = None
    
    context = {
        'inmuebles': inmuebles,
        'habitaciones': num_habitaciones,
        'mostrar_resultados': mostrar_resultados,
        'opciones_habitaciones': opciones_habitaciones,
    }
    
    return render(request, 'buscarporhabitaciones.html', context)

def anunciosdehoy(request):
    hace_un_dia = timezone.now() - timedelta(days=1)
    
    inmuebles = Inmueble.objects.filter(fecha_actualizacion__gte=hace_un_dia)
    
    context = {
        'inmuebles': inmuebles,
    }
    
    return render(request, 'anunciosdehoy.html', context)


################################### WHOOSH ###################################

def cargar_bd_whoosh(request):
    almacenar_bd_whoosh()
    
    try:
        ix = open_dir("Index")
        with ix.searcher() as searcher:
            num_inmuebles = searcher.doc_count_all()
    except:
        num_inmuebles = 0
    
    return render(request,'inicio_whoosh.html', {'num_inmuebles':num_inmuebles})

def carga_whoosh(request):
    if request.method=='POST':
        if 'Aceptar' in request.POST:      
            num_inmuebles, datos_almacenados = almacenar_bd_whoosh()
            mensaje="Se han almacenado: " + str(num_inmuebles) +" inmuebles en la base de datos mediante Whoosh."
            return render(request, 'cargaBD.html', {'mensaje':mensaje})
        else:
            return redirect("/")
           
    return render(request, 'confirmacion_whoosh.html')

def listar_inmuebles_whoosh(request):
    inmuebles = []
    mensaje = None
    total_inmuebles = 0

    try:
        ix = open_dir("Index")
        
        with ix.searcher() as searcher:
            results = searcher.documents()

            for result in results:
                inmuebles.append({k: result.get(k) for k in ['titulo', 'precio', 'url', 'habitaciones', 'banos', 'superficie_util', 'planta', 'antiguedad', 'referencia', 'ubicacion', 'fecha', 'inmobiliaria', 'link_inmobiliaria']})
            total_inmuebles = len(inmuebles)
            
            inmuebles = sorted(inmuebles, key=lambda x: int(x['precio']) if x['precio'] else 0, reverse=True)

        mensaje = "Inmuebles mostrados exitosamente."
    except Exception as e:
        mensaje = f"Error al mostrar los inmuebles: {str(e)}"
    
    print(total_inmuebles)

    return render(request, 'inmuebles_whoosh.html', {
        'mensaje': mensaje,
        'inmuebles': inmuebles,
        'total_inmuebles': total_inmuebles,
    })

def buscar_por_titulo_whoosh(request):
    inmuebles = []
    mensaje = None
    frase = request.GET.get('frase', '').strip()
    mostrar_resultados = False

    if frase:
        try:
            ix = open_dir("Index")
            
            with ix.searcher() as searcher:
                parser = MultifieldParser(["titulo", "ubicacion"], schema=ix.schema, group=OrGroup)
                query = parser.parse(frase)
                
                results = searcher.search(query, limit=None)
                
                for result in results:
                    inmuebles.append({
                        'titulo': result.get('titulo'),
                        'precio': result.get('precio'),
                        'url': result.get('url'),
                        'habitaciones': result.get('habitaciones'),
                        'banos': result.get('banos'),
                        'superficie_util': result.get('superficie_util'),
                        'planta': result.get('planta'),
                        'antiguedad': result.get('antiguedad'),
                        'referencia': result.get('referencia'),
                        'ubicacion': result.get('ubicacion'),
                        'fecha': result.get('fecha'),
                        'inmobiliaria': result.get('inmobiliaria'),
                        'link_inmobiliaria': result.get('link_inmobiliaria')
                    })
                
                mostrar_resultados = True
                mensaje = f"Se encontraron {len(inmuebles)} inmuebles que contienen '{frase}'"
                
        except Exception as e:
            mensaje = f"Error al buscar inmuebles: {str(e)}"
    
    return render(request, 'buscar_por_titulo_whoosh.html', {
        'inmuebles': inmuebles,
        'frase': frase,
        'mensaje': mensaje,
        'mostrar_resultados': mostrar_resultados,
    })

def buscar_por_fecha_actualizacion_whoosh(request):
    inmuebles = []
    mensaje = None
    fecha_inicio = request.GET.get('fecha_inicio', '').strip()
    fecha_fin = request.GET.get('fecha_fin', '').strip()
    mostrar_resultados = False

    if fecha_inicio and fecha_fin:
        try:
            fecha_inicio_dt = datetime.strptime(fecha_inicio, '%d/%m/%Y')
            fecha_fin_dt = datetime.strptime(fecha_fin, '%d/%m/%Y')
            
            fecha_inicio_dt = fecha_inicio_dt.replace(hour=0, minute=0, second=0)
            fecha_fin_dt = fecha_fin_dt.replace(hour=23, minute=59, second=59)
            
            fecha_inicio_dt = timezone.make_aware(fecha_inicio_dt)
            fecha_fin_dt = timezone.make_aware(fecha_fin_dt)
            
            ix = open_dir("Index")
            
            with ix.searcher() as searcher:
                results = searcher.documents()
                
                for result in results:
                    fecha_inmueble = result.get('fecha')
                    
                    if fecha_inmueble and fecha_inicio_dt <= fecha_inmueble <= fecha_fin_dt:
                        inmuebles.append({
                            'titulo': result.get('titulo'),
                            'precio': result.get('precio'),
                            'url': result.get('url'),
                            'habitaciones': result.get('habitaciones'),
                            'banos': result.get('banos'),
                            'superficie_util': result.get('superficie_util'),
                            'planta': result.get('planta'),
                            'antiguedad': result.get('antiguedad'),
                            'referencia': result.get('referencia'),
                            'ubicacion': result.get('ubicacion'),
                            'fecha': fecha_inmueble,
                            'inmobiliaria': result.get('inmobiliaria'),
                            'link_inmobiliaria': result.get('link_inmobiliaria')
                        })
                
                inmuebles = sorted(inmuebles, key=lambda x: x['fecha'] if x['fecha'] else datetime.min.replace(tzinfo=timezone.utc), reverse=True)
                
                mostrar_resultados = True
                mensaje = f"Se encontraron {len(inmuebles)} inmuebles actualizados entre {fecha_inicio} y {fecha_fin}"
                
        except ValueError as ve:
            mensaje = "Error: El formato de fecha debe ser DD/MM/AAAA"
        except Exception as e:
            mensaje = f"Error al buscar inmuebles: {str(e)}"
    
    return render(request, 'buscar_por_fecha_actualizacion_whoosh.html', {
        'inmuebles': inmuebles,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'mensaje': mensaje,
        'mostrar_resultados': mostrar_resultados,
    })
