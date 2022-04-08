from django.test import TestCase

from catalogo.models import Autor

class TestModeloAutor(TestCase):

    @classmethod
    def setUpTestData(cls):
        Autor.objects.create(nombre='Bob', apellido='El Grande')

    def test_label_nombre(self):
        autor=Autor.objects.get(id=1)
        campo_label = autor._meta.get_field('nombre').verbose_name
        self.assertEquals(campo_label,'nombre')

    def test_label_fecha_de_deceso(self):
        autor=Autor.objects.get(id=1)
        campo_label = autor._meta.get_field('fecha_de_deceso').verbose_name
        self.assertEquals(campo_label,'murió')

    def test_longitud_maxima_nombre(self):
        autor=Autor.objects.get(id=1)
        longitud_maxima = autor._meta.get_field('nombre').max_length
        self.assertEquals(longitud_maxima,100)

    def test_nombre_objeto_es_apellido_coma_nombre(self):
        autor=Autor.objects.get(id=1)
        nombre_objeto_esperado = f'{autor.apellido}, {autor.nombre}'#'%s, %s' % (autor.apellido, autor.nombre)
        self.assertEquals(nombre_objeto_esperado,str(autor))

    def test_get_absolute_url(self):
        autor=Autor.objects.get(id=1)
        #This will also fail if the urlconf is not defined.
        self.assertEquals(autor.get_absolute_url(),'/catalogo/autores/1')