from django.test import TestCase
from django.urls import reverse

from catalogo.models import Autor

class TestAutorListView(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create 13 authors for pagination tests
        numero_autores = 13

        for autor_id in range(numero_autores):
            Autor.objects.create(
                nombre=f'Cristian {autor_id}',
                apellido=f'Apellido {autor_id}',
            )

    def test_view_url_existe_en_esa_localizacion(self):
        response = self.client.get('/catalogo/autores/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accesible_por_nombre(self):
        response = self.client.get(reverse('autores'))
        self.assertEqual(response.status_code, 200)

    def test_view_usa_la_plantilla_correcta(self):
        response = self.client.get(reverse('autores'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalogo/autor_list.html')

    def test_paginacion_es_diez(self):
        response = self.client.get(reverse('autores'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'] == True)
        self.assertEqual(len(response.context['autor_list']), 2)

    def test_listas_todos_los_autores(self):
        # Get second page and confirm it has (exactly) remaining 3 items
        response = self.client.get(reverse('autores')+'?page=7')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'] == True)
        self.assertEqual(len(response.context['autor_list']), 1)

import datetime

from django.utils import timezone
from django.contrib.auth.models import User # Required to assign User as a borrower

from catalogo.models import PeticionesLibro, Libro, Genero, Idioma

class TestPeticionLibroPorUsuarioListViewTest(TestCase):
    def setUp(self):
        # Create two users
        test_usuario1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_usuario2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD')

        test_usuario1.save()
        test_usuario2.save()

        # Create a book
        test_autor = Autor.objects.create(nombre='John', apellido='Smith')
        test_genero = Genero.objects.create(nombre='Fantasia')
        test_idioma = Idioma.objects.create(nombre='Ingles')
        test_libro = Libro.objects.create(
            titulo='Book Title',
            descripcion='My book summary',
            isbn='ABCDEFG',
            autor=test_autor,
            idioma=test_idioma,
        )

        # Create genre as a post-step
        objeto_genero_para_libro = Genero.objects.all()
        test_libro.genero.set(objeto_genero_para_libro) # Direct assignment of many-to-many types not allowed.
        test_libro.save()

        # Create 30 BookInstance objects
        numero_de_copias_de_libro = 30
        for copia_libro in range(numero_de_copias_de_libro):
            fecha_entrega = timezone.localtime() + datetime.timedelta(days=copia_libro%5)
            el_prestatario = test_usuario1 if copia_libro % 2 else test_usuario2
            status = 'm'
            PeticionesLibro.objects.create(
                libro=test_libro,
                editorial='Unlikely Imprint, 2016',
                devolucion=fecha_entrega,
                prestatario=el_prestatario,
                status=status,
            )

    def test_redirrecion_sin_logueo(self):
        respuesta = self.client.get(reverse('mis-prestamos'))
        self.assertRedirects(respuesta, '/accounts/login/?next=/catalogo/mislibros/')

    def test_logueo_usa_plantilla_correcta(self):
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('mis-prestamos'))

        # Check our user is logged in
        self.assertEqual(str(response.context['user']), 'testuser1')
        # Check that we got a response "success"
        self.assertEqual(response.status_code, 200)

        # Check we used correct template
        self.assertTemplateUsed(response, 'catalogo/lista_libros_prestados_usuario.html')

    def test_solo_libros_prestados_en_lista(self):
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        respuesta = self.client.get(reverse('mis-prestamos'))

        # Check our user is logged in
        self.assertEqual(str(respuesta.context['user']), 'testuser1')
        # Check that we got a response "success"
        self.assertEqual(respuesta.status_code, 200)

        # Check that initially we don't have any books in list (none on loan)
        self.assertTrue('peticioneslibro_list' in respuesta.context)
        self.assertEqual(len(respuesta.context['peticioneslibro_list']), 0)

        # Now change all books to be on loan
        libros = PeticionesLibro.objects.all()[:10]

        for libro in libros:
            libro.status = 'p'
            libro.save()

        # Check that now we have borrowed books in the list
        respuesta = self.client.get(reverse('mis-prestamos'))
        # Check our user is logged in
        self.assertEqual(str(respuesta.context['user']), 'testuser1')
        # Check that we got a response "success"
        self.assertEqual(respuesta.status_code, 200)

        self.assertTrue('peticioneslibro_list' in respuesta.context)

        # Confirm all books belong to testuser1 and are on loan
        for itemlibro in respuesta.context['peticioneslibro_list']:
            self.assertEqual(respuesta.context['user'], itemlibro.prestatario)
            self.assertEqual(itemlibro.status, 'p')

    def test_paginas_ordenadas_por_fecha_retorno(self):
        # Change all books to be on loan
        for libro in PeticionesLibro.objects.all():
            libro.status='p'
            libro.save()

        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        respuesta = self.client.get(reverse('mis-prestamos'))

        # Check our user is logged in
        self.assertEqual(str(respuesta.context['user']), 'testuser1')
        # Check that we got a response "success"
        self.assertEqual(respuesta.status_code, 200)

        # Confirm that of the items, only 10 are displayed due to pagination.
        self.assertEqual(len(respuesta.context['peticioneslibro_list']), 10)

        ultima_fecha = 0
        for libro in respuesta.context['peticioneslibro_list']:
            if ultima_fecha == 0:
                ultima_fecha = libro.devolucion
            else:
                self.assertTrue(ultima_fecha <= libro.devolucion)
                ultima_fecha = libro.devolucion
    
from django.contrib.auth.models import Permission # Required to grant the permission needed to set a book as returned.

class TestRenovarPeticionesDeLibrosView(TestCase):

    def setUp(self):
        #Create a user
        test_user1 = User.objects.create_user(username='testuser1', password='12345')
        test_user1.save()

        test_user2 = User.objects.create_user(username='testuser2', password='12345')
        test_user2.save()
        permission = Permission.objects.get(name='Establece libro como regresado')
        test_user2.user_permissions.add(permission)
        test_user2.save()

        #Create a book
        test_autor = Autor.objects.create(nombre='John', apellido='Smith')
        test_genero = Genero.objects.create(nombre='Fantasia')
        test_idioma = Idioma.objects.create(nombre='Ingles')
        test_libro = Libro.objects.create(titulo='Titulo del Libro', descripcion = 'Resumen de mi libro', isbn='ABCDEFG', autor=test_autor, idioma=test_idioma,)
        # Create genre as a post-step
        objeto_genero_para_libro = Genero.objects.all()
        test_libro.genero.set(objeto_genero_para_libro) # Direct assignment of many-to-many types not allowed.
        test_libro.save()

        #Create a BookInstance object for test_user1
        fecha_retorno = datetime.date.today() + datetime.timedelta(days=5)
        self.test_peticionlibro1=PeticionesLibro.objects.create(libro=test_libro,editorial='Unlikely Imprint, 2016', devolucion=fecha_retorno, prestatario=test_user1, status='p')

        #Create a BookInstance object for test_user2
        fecha_retorno= datetime.date.today() + datetime.timedelta(days=5)
        self.test_peticionlibro2=PeticionesLibro.objects.create(libro=test_libro,editorial='Unlikely Imprint, 2016', devolucion=fecha_retorno, prestatario=test_user2, status='p')
    
    def test_redirecciona_si_no_esta_logueado(self):
        resp = self.client.get(reverse('renovar-libro-bibliotecario', kwargs={'pk':self.test_peticionlibro1.pk,}) )
        
        #Manually check redirect (Can't use assertRedirect, because the redirect URL is unpredictable)
        self.assertEqual( resp.status_code,302)
        self.assertTrue( resp.url.startswith('/accounts/login/') )

    def test_redirecciona_si_esta_loguedo_pero_no_tiene_permisos(self):
        login = self.client.login(username='testuser1', password='12345')
        resp = self.client.get(reverse('renovar-libro-bibliotecario', kwargs={'pk':self.test_peticionlibro1.pk,}) )

        #Manually check redirect (Can't use assertRedirect, because the redirect URL is unpredictable)
        self.assertEqual( resp.status_code,302)
        self.assertTrue( resp.url.startswith('/accounts/login/') )

    def test_logueado_con_permisos_libros_prestados(self):
        login = self.client.login(username='testuser2', password='12345')
        resp = self.client.get(reverse('renovar-libro-bibliotecario', kwargs={'pk':self.test_peticionlibro2.pk,}) )

        #Check that it lets us login - this is our book and we have the right permissions.
        self.assertEqual( resp.status_code,200)

    def test_logueado_con_permisos_libros_prestados_otro_usuario(self):
        login = self.client.login(username='testuser2', password='12345')
        resp = self.client.get(reverse('renovar-libro-bibliotecario', kwargs={'pk':self.test_peticionlibro1.pk,}) )

        #Check that it lets us login. We're a librarian, so we can view any users book
        self.assertEqual( resp.status_code,200)

    def test_HTTP404_para_libro_invalido_logueado(self):
        import uuid
        test_uid = uuid.uuid4() #unlikely UID to match our bookinstance!
        login = self.client.login(username='testuser2', password='12345')
        resp = self.client.get(reverse('renovar-libro-bibliotecario', kwargs={'pk':test_uid,}) )
        self.assertEqual( resp.status_code,404)

    def test_Usa_plantilla_correcta(self):
        login = self.client.login(username='testuser2', password='12345')
        resp = self.client.get(reverse('renovar-libro-bibliotecario', kwargs={'pk':self.test_peticionlibro1.pk,}) )
        self.assertEqual( resp.status_code,200)

        #Check we used correct template
        self.assertTemplateUsed(resp, 'catalogo/renovar_libro_bibliotecario.html')
    
    def test_form_fecha_renovacion_inicialmente_tiene_tres_semanas_en_el_futuro(self):
        login = self.client.login(username='testuser2', password='12345')
        resp = self.client.get(reverse('renovar-libro-bibliotecario', kwargs={'pk':self.test_peticionlibro1.pk,}) )
        self.assertEqual( resp.status_code,200)

        fecha_tres_semanas_en_el_futuro = datetime.date.today() + datetime.timedelta(weeks=3)
        self.assertEqual(resp.context['form'].initial['fecha_renovacion'], fecha_tres_semanas_en_el_futuro )
    
    def test_redirecciona_a_la_lista_todos_los_libros_prestados_correctamente(self):
        login = self.client.login(username='testuser2', password='12345')
        fecha_valida_en_el_futuro = datetime.date.today() + datetime.timedelta(weeks=2)
        resp = self.client.post(reverse('renovar-libro-bibliotecario', kwargs={'pk':self.test_peticionlibro1.pk,}), {'fecha_renovacion':fecha_valida_en_el_futuro} )
        self.assertRedirects(resp, reverse('lista-prestamos') )
    
    def test_form_fecha_renovacion_invalida_en_el_pasado(self):
        login = self.client.login(username='testuser2', password='12345')
        fecha_en_el_pasado = datetime.date.today() - datetime.timedelta(weeks=1)
        resp = self.client.post(reverse('renovar-libro-bibliotecario', kwargs={'pk':self.test_peticionlibro1.pk,}), {'fecha_renovacion':fecha_en_el_pasado} )
        self.assertEqual( resp.status_code,200)
        self.assertFormError(resp, 'form', 'fecha_renovacion', 'Fecha invalida - renovación en el pasado')

    def test_form_fecha_renovacion_invalida_en_el_futuro(self):
        login = self.client.login(username='testuser2', password='12345')
        fecha_invalida_en_el_futuro = datetime.date.today() + datetime.timedelta(weeks=5)
        resp = self.client.post(reverse('renovar-libro-bibliotecario', kwargs={'pk':self.test_peticionlibro1.pk,}), {'fecha_renovacion':fecha_invalida_en_el_futuro} )
        self.assertEqual( resp.status_code,200)
        self.assertFormError(resp, 'form', 'fecha_renovacion', 'Fecha invalida - renovación mayor a 4 semanas')