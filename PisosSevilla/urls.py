"""
URL configuration for PisosSevilla project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from principal import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.inicio),
    path('inmuebles/', views.listar_inmuebles),
    path('inmobiliarias/', views.listar_inmobiliarias),
    path('carga/', views.carga),
    path('buscarrangodeprecios/', views.buscarrangodeprecios, name ='buscarrangodeprecios'),
    path('buscarporhabitaciones/', views.buscarporhabitaciones, name='buscarporhabitaciones'),
    path('anunciosdehoy/', views.anunciosdehoy, name='anunciosdehoy'),


    path('carga_whoosh/', views.carga_whoosh),
    path('cargar_bd_whoosh/', views.cargar_bd_whoosh),
    path('inmuebles_whoosh/', views.listar_inmuebles_whoosh),
    path('buscar_por_titulo_whoosh/', views.buscar_por_titulo_whoosh, name='buscar_por_titulo_whoosh'),
    path('buscar_fecha_whoosh/', views.buscar_por_fecha_actualizacion_whoosh, name='buscar_por_fecha_actualizacion_whoosh'),
]
