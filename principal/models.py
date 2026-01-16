from django.db import models

class Inmobiliaria(models.Model):
    nombre = models.CharField(max_length=200)
    link = models.URLField(null=True, blank=True)

    def __str__(self):
        return self.nombre
    
class Inmueble(models.Model):
    titulo = models.CharField(max_length=200)
    precio = models.FloatField()
    url = models.URLField()
    habitaciones = models.IntegerField(null=True, blank=True)
    banos = models.IntegerField(null=True, blank=True)
    planta = models.CharField(max_length=100, null=True, blank=True)
    antiguedad = models.CharField(max_length=100, null=True, blank=True)
    referencia = models.CharField(max_length=100, null=True, blank=True)
    ubicacion = models.CharField(max_length=300)
    fecha_actualizacion = models.DateTimeField(null=True, blank=True)
    inmobiliaria = models.ForeignKey('Inmobiliaria', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.titulo

