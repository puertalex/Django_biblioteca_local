from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('libros/', views.LibroListView.as_view(), name='libros'),
    path('libros/<pk>', views.DetalleLibroView.as_view(), name='libro_detail'),
    path('autores/', views.AutorListView.as_view(), name='autores'),
    path('autores/<pk>', views.DetalleAutorView.as_view(), name='autor_detail'),
]

urlpatterns += [
    path('mislibros/', views.LibrosAlquiladosPorUsuarioListView.as_view(), name='mis-prestamos'),
    path('prestamos/', views.TodosLibrosPrestadosListView.as_view(), name='lista-prestamos'),
]

urlpatterns += [
    path('libro/<pk>/renovar/', views.renovar_libro_bibliotecario, name='renovar-libro-bibliotecario'),
]

urlpatterns += [
    path('autor/crear/', views.CrearAutor.as_view(), name='crear_autor'),
    path('autor/<pk>/actualizar/', views.ActualizarAutor.as_view(), name='actualizar_autor'),
    path('autor/<pk>/eliminar/', views.BorrarAutor.as_view(), name='eliminar_autor'),
]

urlpatterns += [
    path('libro/crear/', views.CrearLibro.as_view(), name='crear_libro'),
    path('libro/<pk>/actualizar/', views.ActualizarLibro.as_view(), name='actualizar_libro'),
    path('libro/<pk>/eliminar/', views.BorrarLibro.as_view(), name='eliminar_libro'),
]