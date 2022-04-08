import datetime

from django.test import TestCase
from django.utils import timezone

from catalogo.forms import RenovarLibroForm

class TestFechaRenovacion(TestCase):
    def test_label_form_fecha_renovacion(self):
        form = RenovarLibroForm()
        self.assertTrue(form.fields['fecha_renovacion'].label is None or form.fields['fecha_renovacion'].label == 'fecha renovacion')

    def test_campo_form_help_text_fecha_renovacion(self):
        form = RenovarLibroForm()
        self.assertEqual(form.fields['fecha_renovacion'].help_text, 'Ingresa una fecha entre hoy y 4 semanas (3 predetermindo).')

    def test_form_fecha_renovacion_en_el_pasado(self):
        date = datetime.date.today() - datetime.timedelta(days=1)
        form = RenovarLibroForm(data={'fecha_renovacion': date})
        self.assertFalse(form.is_valid())

    def test_form_fecha_renovacion_muy_lejos_en_el_futuro(self):
        date = datetime.date.today() + datetime.timedelta(weeks=4) + datetime.timedelta(days=1)
        form = RenovarLibroForm(data={'fecha_renovacion': date})
        self.assertFalse(form.is_valid())

    def test_form_fecha_renovacion_hoy(self):
        date = datetime.date.today()
        form = RenovarLibroForm(data={'fecha_renovacion': date})
        self.assertTrue(form.is_valid())

    def test_form_fecha_renovacion_max(self):
        date = timezone.localtime() + datetime.timedelta(weeks=4)
        form = RenovarLibroForm(data={'fecha_renovacion': date})
        self.assertTrue(form.is_valid())