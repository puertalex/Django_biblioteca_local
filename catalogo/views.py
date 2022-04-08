from turtle import title
from django.shortcuts import render

from .models import Libro, Autor, PeticionesLibro, Genero

def index(request):
    """
    Función vista para la página inicio del sitio.
    """
    # Genera contadores de algunos de los objetos principales
    num_books=Libro.objects.all().count()
    num_instances=PeticionesLibro.objects.all().count()
    # Libros disponibles (status = 'd')
    num_instances_available=PeticionesLibro.objects.filter(status__exact='d').count()
    num_authors=Autor.objects.count()  # El 'all()' esta implícito por defecto.
    num_generos=Genero.objects.count() # Cuenta Generos
    filtro=Libro.objects.filter(titulo__icontains='anillo').count()

    numero_visitas = request.session.get('numero_visitas', 0)
    request.session['numero_visitas'] = numero_visitas + 1

    context = {
        'num_books':num_books,
        'num_instances':num_instances,
        'num_instances_available':num_instances_available,
        'num_authors':num_authors,
        'numero_visitas':numero_visitas,
        'num_generos':num_generos,
        'filtro':filtro
    } 

    # Renderiza la plantilla HTML index.html con los datos en la variable contexto
    return render(
        request,
        'index.html',
        context=context
    )

from django.views import generic

class LibroListView(generic.ListView):
    model = Libro
    paginate_by = 2

class DetalleLibroView(generic.DetailView):
    model = Libro

class AutorListView(generic.ListView):
    model = Autor
    paginate_by = 2

class DetalleAutorView(generic.DetailView):
    model = Autor

from django.contrib.auth.mixins import LoginRequiredMixin

class LibrosAlquiladosPorUsuarioListView(LoginRequiredMixin,generic.ListView):
    """
    Generic class-based view listing books on loan to current user.
    """
    model = PeticionesLibro
    template_name ='catalogo/lista_libros_prestados_usuario.html'
    paginate_by = 10

    def get_queryset(self):
        return PeticionesLibro.objects.filter(prestatario=self.request.user).filter(status__exact='p').order_by('devolucion')

from django.contrib.auth.mixins import PermissionRequiredMixin

class TodosLibrosPrestadosListView(PermissionRequiredMixin, generic.ListView):
    """
    Generic class-based view listing all books on loan.
    Only visible to users with can_mark_returned permission.
    """
    model = PeticionesLibro
    permission_required = 'catalogo.can_mark_returned'
    template_name = 'catalogo/lista_todos_prestamos.html'
    paginate_by = 10

    def get_queryset(self):
        return PeticionesLibro.objects.filter(status__exact='p').order_by('devolucion')

from django.contrib.auth.decorators import permission_required

from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
import datetime

from .forms import RenovarLibroForm

@permission_required('catalogo.can_mark_returned')
def renovar_libro_bibliotecario(request, pk):
    """
    View function for renewing a specific BookInstance by librarian
    """
    pet_libro=get_object_or_404(PeticionesLibro, pk = pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = RenovarLibroForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            pet_libro.devolucion = form.cleaned_data['fecha_renovacion']
            pet_libro.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('lista-prestamos') )

    # If this is a GET (or any other method) create the default form.
    else:
        fecha_renovacion_propuesta = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenovarLibroForm(initial={'fecha_renovacion': fecha_renovacion_propuesta,})

    return render(request, 'catalogo/renovar_libro_bibliotecario.html', {'form': form, 'pet_libro':pet_libro})

from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Autor

class CrearAutor(CreateView):
    model = Autor
    fields = '__all__'
    initial={'fecha_de_deceso':'05/01/2018',}

class ActualizarAutor(UpdateView):
    model = Autor
    fields = ['nombre','apellido','fecha_de_nacimiento','fecha_de_deceso']

class BorrarAutor(DeleteView):
    model = Autor
    success_url = reverse_lazy('autores')

from .models import Libro

class CrearLibro(CreateView):
    model = Libro
    fields = '__all__'

class ActualizarLibro(UpdateView):
    model = Libro
    fields = '__all__'

class BorrarLibro(DeleteView):
    model = Libro
    success_url = reverse_lazy('libros')