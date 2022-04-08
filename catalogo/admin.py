from django.contrib import admin
from .models import Autor, Genero, Libro, PeticionesLibro, Idioma

# admin.site.register(Libro)
# admin.site.register(Autor)
admin.site.register(Genero)
# admin.site.register(PeticionesLibro)
admin.site.register(Idioma)

class LibroInline(admin.TabularInline):
    model = Libro

# Define la clase admin
class AutorAdmin(admin.ModelAdmin):
    list_display = ('apellido', 'nombre', 'fecha_de_nacimiento', 'fecha_de_deceso')
    fields = ['nombre', 'apellido', ('fecha_de_nacimiento', 'fecha_de_deceso')]
    inlines = [LibroInline]

# Registra la clase admin con el modelo asociado
admin.site.register(Autor, AutorAdmin)

# Registra las clases admin para Libro usando @

class PeticionesLibroInline(admin.TabularInline):
    model = PeticionesLibro

@admin.register(Libro)
class LibroAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'autor', 'mostrar_genero')
    inlines = [PeticionesLibroInline]

# Registra las clases admin para PeticionesLibro usando @

@admin.register(PeticionesLibro)
class PeticionesLibroAdmin(admin.ModelAdmin):
    list_display = ('libro', 'status', 'prestatario', 'devolucion', 'id')
    list_filter = ('status', 'devolucion')

    fieldsets = (
        (None, {
            'fields': ('libro', 'editorial', 'id')
        }),
        ('Disponibilidad', {
            'fields': ('status', 'devolucion', 'prestatario')
        }),
    )