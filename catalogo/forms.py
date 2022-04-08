from django.core.exceptions import ValidationError
#from django.utils.translation import ugettext_lazy as _
import datetime #for checking renewal date range.

from django import forms

class RenovarLibroForm(forms.Form):
    fecha_renovacion = forms.DateField(help_text="Ingresa una fecha entre hoy y 4 semanas (3 predetermindo).")

    def clean_fecha_renovacion(self):
        data = self.cleaned_data['fecha_renovacion']

        #Check date is not in past.
        if data < datetime.date.today():
            raise ValidationError('Fecha invalida - renovación en el pasado')

        #Check date is in range librarian allowed to change (+4 weeks).
        if data > datetime.date.today() + datetime.timedelta(weeks=4):
            raise ValidationError('Fecha invalida - renovación mayor a 4 semanas')

        # Remember to always return the cleaned data.
        return data