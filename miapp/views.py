
# Mercado Pago
import mercadopago
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

# Vista para iniciar pago Mercado Pago
from django.utils.decorators import method_decorator
@csrf_exempt
@login_required
def iniciar_pago_mp(request):
  carrito = request.session.get('carrito', {})
  preference_items = []
  total = 0
  for key, cantidad in carrito.items():
    if key.startswith('patron_'):
      from .models import PatronDescargable
      patron_id = key.replace('patron_', '')
      patron = PatronDescargable.objects.filter(id=patron_id).first()
      if patron:
        price = int(getattr(patron, 'precio', 0))
        preference_items.append({
          "title": patron.nombre,
          "quantity": int(cantidad),
          "unit_price": price,
          "currency_id": "CLP"
        })
        total += price * int(cantidad)
    elif '_' in key:
      producto_id, numero_crochet_id = key.split('_')
      producto = Hilado.objects.filter(id=producto_id).first()
      numero = NumeroCrochet.objects.filter(id=numero_crochet_id).first()
      if numero:
        price = int(numero.precio)
        preference_items.append({
          "title": f"{producto.nombre} (N° {numero.numero})",
          "quantity": int(cantidad),
          "unit_price": price,
          "currency_id": "CLP"
        })
        total += price * int(cantidad)
    else:
      producto = Hilado.objects.filter(id=key).first()
      if producto:
        price = int(producto.precio)
        preference_items.append({
          "title": producto.nombre,
          "quantity": int(cantidad),
          "unit_price": price,
          "currency_id": "CLP"
        })
        total += price * int(cantidad)
  sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)
  preference_data = {
    "items": preference_items,
    "back_urls": {
      "success": request.build_absolute_uri('/pago-exitoso/'),
      "failure": request.build_absolute_uri('/pago-fallido/'),
      "pending": request.build_absolute_uri('/pago-pendiente/')
    },
    "auto_return": "approved"
  }
  preference_response = sdk.preference().create(preference_data)
  preference = preference_response["response"]
  return JsonResponse({"init_point": preference["init_point"]})

# Callback de éxito
@login_required
def pago_exitoso(request):
  # Aquí podrías marcar la compra como pagada y liberar los descargables
  return render(request, 'miapp/pago_exitoso.html')

# Callback de fallo
@login_required
def pago_fallido(request):
  return render(request, 'miapp/pago_fallido.html')

# Callback de pendiente
@login_required
def pago_pendiente(request):
  return render(request, 'miapp/pago_pendiente.html')
# Agregar patrón descargable al carrito
from django.shortcuts import get_object_or_404, redirect

def agregar_patron_al_carrito(request, patron_id):
  patron = get_object_or_404(PatronDescargable, id=patron_id)
  carrito = request.session.get('carrito', {})
  key = f"patron_{patron_id}"
  cantidad_actual = carrito.get(key, 0)
  carrito[key] = cantidad_actual + 1
  request.session['carrito'] = carrito
  return render(request, 'miapp/producto_agregado.html', {'producto': patron})
# Vista para catálogo de patrones descargables
from .models import PatronDescargable

def patrones(request):
  patrones = PatronDescargable.objects.all().order_by('-fecha')
  return render(request, 'miapp/patrones.html', {'patrones': patrones})
# Importaciones necesarias
from django.contrib.auth.decorators import login_required
from .models import Compra, DetalleCompra, Hilado, NumeroCrochet

# Vista para patrones descargables del usuario
@login_required
def mis_descargables(request):
  patrones = request.user.patrones_descargables.all().order_by('-fecha')
  return render(request, 'miapp/mis_descargables.html', {'patrones': patrones})

# Vista para historial de compras del usuario
@login_required
def historial_compras(request):
  compras = request.user.compras.all().order_by('-fecha')
  return render(request, 'miapp/historial_compras.html', {'compras': compras})
# Vista para finalizar compra y guardar el carrito
@login_required
def finalizar_compra(request):
  carrito = request.session.get('carrito', {})
  if not carrito:
    return redirect('ver_carrito')
  compra = Compra.objects.create(usuario=request.user)
  from .models import PatronDescargable
  for key, cantidad in carrito.items():
    if key.startswith('patron_'):
      patron_id = key.replace('patron_', '')
      patron = PatronDescargable.objects.filter(id=patron_id).first()
      if patron:
        patron.usuarios.add(request.user)
    elif '_' in key:
      producto_id, numero_crochet_id = key.split('_')
      producto = Hilado.objects.filter(id=producto_id).first()
      numero = NumeroCrochet.objects.filter(id=numero_crochet_id).first()
      DetalleCompra.objects.create(compra=compra, producto=producto, numero_crochet=numero, cantidad=cantidad)
    else:
      producto = Hilado.objects.filter(id=key).first()
      DetalleCompra.objects.create(compra=compra, producto=producto, cantidad=cantidad)
  # Limpiar carrito
  request.session['carrito'] = {}
  return render(request, 'miapp/compra_exitosa.html', {'compra': compra})
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import RegistroForm

# Vista de registro
def registro(request):
  if request.method == 'POST':
    form = RegistroForm(request.POST)
    if form.is_valid():
      user = form.save()
      login(request, user)
      return redirect('index')
  else:
    form = RegistroForm()
  return render(request, 'miapp/registro.html', {'form': form})

# Vista de login
def login_view(request):
  if request.method == 'POST':
    form = AuthenticationForm(request, data=request.POST)
    if form.is_valid():
      user = form.get_user()
      login(request, user)
      return redirect('index')
  else:
    form = AuthenticationForm()
  return render(request, 'miapp/login.html', {'form': form})

# Vista de logout
def logout_view(request):
  logout(request)
  return redirect('index')
# Carrito de compras básico
from django.shortcuts import get_object_or_404

def agregar_al_carrito(request, producto_id):
  from .models import StockCrochet
  producto = get_object_or_404(Hilado, id=producto_id)
  numero_crochet_id = request.POST.get('numero_crochet')
  key = str(producto_id)
  carrito = request.session.get('carrito', {})
  exito = False
  error = ''
  if numero_crochet_id:
    key = f"{producto_id}_{numero_crochet_id}"
    stock_crochet = StockCrochet.objects.filter(accesorio=producto, numero_crochet_id=numero_crochet_id).first()
    cantidad_actual = carrito.get(key, 0)
    if stock_crochet and stock_crochet.stock > cantidad_actual:
      carrito[key] = cantidad_actual + 1
      stock_crochet.stock -= 1
      stock_crochet.save()
      request.session['carrito'] = carrito
      exito = True
    else:
      error = 'No hay suficiente stock disponible para este número de crochet.'
  else:
    # Para productos sin número de crochet (ej: hilados)
    cantidad_actual = carrito.get(key, 0)
    if producto.stock > cantidad_actual:
      carrito[key] = cantidad_actual + 1
      producto.stock -= 1
      producto.save()
      request.session['carrito'] = carrito
      exito = True
    else:
      error = 'No hay suficiente stock disponible para este producto.'
  if exito:
    return render(request, 'miapp/producto_agregado.html', {'producto': producto})
  else:
    # Si hay error, redirigir a accesorios con mensaje de error
    request.session['carrito_error'] = error
    return redirect('accesorios')

def ver_carrito(request):
  from .models import StockCrochet, NumeroCrochet
  carrito = request.session.get('carrito', {})
  productos = []
  total = 0
  from .models import PatronDescargable
  for key, cantidad in carrito.items():
    if key.startswith('patron_'):
      patron_id = key.replace('patron_', '')
      patron = PatronDescargable.objects.filter(id=patron_id).first()
      if patron:
        precio_unitario = float(getattr(patron, 'precio', 0))
        productos.append({'producto': patron, 'cantidad': cantidad, 'numero_crochet': None, 'stock_crochet': None, 'precio_unitario': precio_unitario, 'subtotal': precio_unitario * cantidad, 'es_patron': True})
        total += precio_unitario * cantidad
    elif '_' in key:
      producto_id, numero_crochet_id = key.split('_')
      producto = Hilado.objects.filter(id=producto_id).first()
      numero = None
      stock_crochet = None
      precio_unitario = 0
      if producto:
        numero = NumeroCrochet.objects.filter(id=numero_crochet_id).first()
        stock_crochet = StockCrochet.objects.filter(accesorio=producto, numero_crochet_id=numero_crochet_id).first()
        if numero:
          precio_unitario = float(numero.precio)
        productos.append({'producto': producto, 'cantidad': cantidad, 'numero_crochet': numero, 'stock_crochet': stock_crochet, 'precio_unitario': precio_unitario, 'subtotal': precio_unitario * cantidad, 'es_patron': False})
        total += precio_unitario * cantidad
    else:
      producto = Hilado.objects.filter(id=key).first()
      precio_unitario = 0
      if producto:
        precio_unitario = float(producto.precio)
        productos.append({'producto': producto, 'cantidad': cantidad, 'numero_crochet': None, 'stock_crochet': None, 'precio_unitario': precio_unitario, 'subtotal': precio_unitario * cantidad, 'es_patron': False})
        total += precio_unitario * cantidad
  return render(request, 'miapp/carrito.html', {'productos': productos, 'total': total})

def eliminar_del_carrito(request, producto_id):
  from .models import StockCrochet, NumeroCrochet, Hilado
  carrito = request.session.get('carrito', {})
  # Buscar claves que correspondan a este producto (puede ser con o sin crochet)
  keys_to_remove = [key for key in carrito.keys() if key == str(producto_id) or key.startswith(f"{producto_id}_")]
  for key in keys_to_remove:
    cantidad = carrito[key]
    if '_' in key:
      _, numero_crochet_id = key.split('_')
      accesorio = Hilado.objects.filter(id=producto_id).first()
      stock_crochet = StockCrochet.objects.filter(accesorio=accesorio, numero_crochet_id=numero_crochet_id).first()
      if stock_crochet:
        stock_crochet.stock += cantidad
        stock_crochet.save()
    else:
      producto = Hilado.objects.filter(id=producto_id).first()
      if producto:
        producto.stock += cantidad
        producto.save()
    del carrito[key]
  request.session['carrito'] = carrito
  return redirect('ver_carrito')
# Vista para accesorios
def accesorios(request):
  from .models import StockCrochet, NumeroCrochet
  accesorios = Hilado.objects.filter(categoria__iexact='Accesorios')
  accesorios_data = []
  for accesorio in accesorios:
    stock_crochet = StockCrochet.objects.filter(accesorio=accesorio)
    crochet_options = []
    for sc in stock_crochet:
      crochet_options.append({
        'id': sc.numero_crochet.id,
        'numero': sc.numero_crochet.numero,
        'stock': sc.stock
      })
    accesorios_data.append({
      'accesorio': accesorio,
      'crochet_options': crochet_options
    })
  error = request.session.pop('carrito_error', '')
  return render(request, 'miapp/accesorios.html', {'accesorios_data': accesorios_data, 'carrito_error': error})
from django.shortcuts import render, redirect

from .forms import ContactoForm
from .models import Contacto, Hilado

# Create your views here.
def index(request):
  return render(request, 'miapp/index.html')


def contacto(request):
  if request.method == 'POST':
    form = ContactoForm(request.POST)
    if form.is_valid():
      form.save()
      return render(request, 'miapp/contacto.html', {'form': ContactoForm(), 'exito': True})
  else:
    form = ContactoForm()
  return render(request, 'miapp/contacto.html', {'form': form})

def hiladoRoma(request):
  hilados_roma = Hilado.objects.filter(categoria__iexact='Roma')
  hilados_chenille = Hilado.objects.filter(categoria__iexact='Chenille')
  return render(request, 'miapp/hiladoRoma.html', {
      'hilados_roma': hilados_roma,
      'hilados_chenille': hilados_chenille
  })


# Nueva vista para mostrar los contactos registrados
def lista_contactos(request):
    contactos = Contacto.objects.all().order_by('-fecha')
    return render(request, 'miapp/lista_contactos.html', {'contactos': contactos})