from django.contrib import admin
from django.urls import path
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('index/', RedirectView.as_view(url='/', permanent=True)),
    path('contacto/', views.contacto, name='contacto'),
    path('admin/', admin.site.urls),
    path('hiladoRoma/', views.hiladoRoma, name='hiladoRoma'),
    path('accesorios/', views.accesorios, name='accesorios'),
    path('lista_contactos/', views.lista_contactos, name='lista_contactos'),
    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('carrito/agregar/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/agregar-patron/<int:patron_id>/', views.agregar_patron_al_carrito, name='agregar_patron_al_carrito'),
    path('carrito/eliminar/<int:producto_id>/', views.eliminar_del_carrito, name='eliminar_del_carrito'),
    path('carrito/finalizar/', views.finalizar_compra, name='finalizar_compra'),
    path('mis-compras/', views.historial_compras, name='historial_compras'),
    path('mis-descargables/', views.mis_descargables, name='mis_descargables'),
    path('patrones/', views.patrones, name='patrones'),
    path('registro/', views.registro, name='registro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('pago-mercadopago/', views.iniciar_pago_mp, name='pago_mercadopago'),
    path('pago-exitoso/', views.pago_exitoso, name='pago_exitoso'),
    path('pago-fallido/', views.pago_fallido, name='pago_fallido'),
    path('pago-pendiente/', views.pago_pendiente, name='pago_pendiente'),
]