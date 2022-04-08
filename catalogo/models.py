from django.db import models
from django.contrib.auth.models import User
import matplotlib matplotlib.use('Agg')

class Genero(models.Model):
    """
    Modelo que representa un género literario (p. ej. ciencia ficción, poesía, etc.).
    """
    nombre = models.CharField(max_length=200, help_text="Ingrese el nombre del género (p. ej. Ciencia Ficción, Poesía Francesa etc.)")

    def __str__(self):
        """
        Cadena que representa a la instancia particular del modelo (p. ej. en el sitio de Administración)
        """
        return self.nombre

from django.urls import reverse #Used to generate URLs by reversing the URL patterns

class Libro(models.Model):
    """
    Modelo que representa un libro (pero no un Ejemplar específico).
    """

    titulo = models.CharField(max_length=200)

    autor = models.ForeignKey('Autor', on_delete=models.SET_NULL, null=True)
    # ForeignKey, ya que un libro tiene un solo autor, pero el mismo autor puede haber escrito muchos libros.
    # 'Author' es un string, en vez de un objeto, porque la clase Author aún no ha sido declarada.

    descripcion = models.TextField(max_length=1000, help_text="Ingrese una breve descripción del libro")

    isbn = models.CharField('ISBN',max_length=13, help_text='13 Caracteres <a href="https://www.isbn-international.org/content/what-isbn">ISBN number</a>')

    genero = models.ManyToManyField(Genero, help_text="Seleccione un genero para este libro")
    # ManyToManyField, porque un género puede contener muchos libros y un libro puede cubrir varios géneros.
    # La clase Genre ya ha sido definida, entonces podemos especificar el objeto arriba.

    idioma = models.ForeignKey('Idioma', on_delete=models.SET_NULL, null=True)

    def mostrar_genero(self):
        """
        Crea una cadena para el Genero. Esto es requerido para mostrar el Genero en Admin.
        """
        return ', '.join([ genero.nombre for genero in self.genero.all()[:3] ])
    mostrar_genero.short_description = 'Genero'

    def __str__(self):
        """
        String que representa al objeto Book
        """
        return self.titulo


    def get_absolute_url(self):
        """
        Devuelve el URL a una instancia particular de Book
        """
        return reverse('libro_detail', args=[str(self.id)])

import uuid # Requerida para las instancias de libros únicos
from datetime import date

class PeticionesLibro(models.Model):
    """
    Modelo que representa una copia específica de un libro (i.e. que puede ser prestado por la biblioteca).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text="ID único para este libro particular en toda la biblioteca")
    libro = models.ForeignKey('Libro', on_delete=models.SET_NULL, null=True)
    editorial = models.CharField(max_length=200)
    devolucion = models.DateField(null=True, blank=True)

    LOAN_STATUS = (
        ('m', 'Mantenimiento'),
        ('p', 'Prestado'),
        ('d', 'Disponible'),
        ('r', 'Reservado'),
    )

    status = models.CharField(max_length=1, choices=LOAN_STATUS, blank=True, default='m', help_text='Disponibilidad del libro')

    prestatario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    @property
    def es_retraso(self):
        if self.devolucion and date.today() > self.devolucion:
            return True
        return False

    class Meta:
        ordering = ["devolucion"]
        permissions = (("can_mark_returned", "Establece libro como regresado"),)


    def __str__(self):
        """
        String para representar el Objeto del Modelo
        """
        return '%s (%s)' % (self.id,self.libro.titulo)

class Autor(models.Model):
    """
    Modelo que representa un autor
    """
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    fecha_de_nacimiento = models.DateField(null=True, blank=True)
    fecha_de_deceso = models.DateField('murió', null=True, blank=True)

    class Meta:
        ordering = ['apellido', 'nombre']

    def get_absolute_url(self):
        """
        Retorna la url para acceder a una instancia particular de un autor.
        """
        return reverse('autor_detail', args=[str(self.id)])


    def __str__(self):
        """
        String para representar el Objeto Modelo
        """
        return '%s, %s' % (self.apellido, self.nombre)

class Idioma(models.Model):
    """
    Modelo que representa idioma de un libro (p. ej. Ingles, Frances, Japones, etc.).
    """
    nombre = models.CharField(max_length=200, help_text="Ingrese el nombre del idioma (p. ej. Ingles, Frances, Japones, etc.)")

    def __str__(self):
        """
        Cadena que representa a la instancia particular del modelo (p. ej. en el sitio de Administración)
        """
        return self.nombre