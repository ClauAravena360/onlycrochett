# Importaciones necesarias
from django.db import models
from django.contrib.auth.models import User

# Modelo para patrones descargables (PDF)


class PatronDescargable(models.Model):
    nombre = models.CharField(max_length=200)
    imagen = models.ImageField(upload_to='patrones/imagenes/', blank=True, null=True, help_text='Imagen de portada para el patrón')
    archivo = models.FileField(upload_to='patrones/')
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    usuarios = models.ManyToManyField(User, blank=True, related_name='patrones_descargables', help_text='Usuarios que pueden descargar este patrón')
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre
# Modelo de compra y detalle de compra
class Compra(models.Model):
    ESTADOS = [
        ("pendiente", "Pendiente"),
        ("pagado", "Pagado"),
        ("enviado", "Enviado"),
        ("entregado", "Entregado"),
        ("cancelado", "Cancelado"),
    ]
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="compras")
    fecha = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default="pendiente")

    def __str__(self):
        return f"Compra #{self.id} - {self.usuario.username} - {self.estado}"

class DetalleCompra(models.Model):
    compra = models.ForeignKey(Compra, on_delete=models.CASCADE, related_name="detalles")
    producto = models.ForeignKey('Hilado', on_delete=models.SET_NULL, null=True, blank=True)
    numero_crochet = models.ForeignKey('NumeroCrochet', on_delete=models.SET_NULL, null=True, blank=True)
    cantidad = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.producto} x{self.cantidad} (Compra #{self.compra.id})"

## Modelo para números de crochet (solo para accesorios)
class NumeroCrochet(models.Model):
    numero = models.CharField(max_length=10)
    precio = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    def __str__(self):
        return self.numero

# Modelo para productos Hilado


class Hilado(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    imagen = models.ImageField(upload_to='hilados/')
    categoria = models.CharField(max_length=50, default='Roma')
    # Solo para accesorios: imagen alternativa para hover
    imagen_hover = models.ImageField(upload_to='hilados/', blank=True, null=True, help_text='Solo para accesorios: imagen al pasar el mouse')
    # El stock general solo para hilados, no para accesorios
    stock = models.PositiveIntegerField(default=0)
    precio = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.nombre

# Modelo intermedio para stock por accesorio y número de crochet
class StockCrochet(models.Model):
    accesorio = models.ForeignKey(Hilado, on_delete=models.CASCADE, related_name='stock_crochet')
    numero_crochet = models.ForeignKey(NumeroCrochet, on_delete=models.CASCADE)
    stock = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('accesorio', 'numero_crochet')

    def __str__(self):
        return f"{self.accesorio.nombre} - {self.numero_crochet.numero}: {self.stock} disponibles"

# Create your models here.
class Contacto(models.Model):
    nombre = models.CharField(max_length=100)
    email = models.EmailField()
    mensaje = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} - {self.email}"


