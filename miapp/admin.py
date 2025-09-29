
from django.contrib import admin
# Registro de PatronDescargable para subir PDFs
from .models import PatronDescargable

@admin.register(PatronDescargable)
class PatronDescargableAdmin(admin.ModelAdmin):
	list_display = ("nombre", "fecha", "imagen_tag")

	def imagen_tag(self, obj):
		if obj.imagen:
			return f'<img src="{obj.imagen.url}" style="height:40px;max-width:60px;object-fit:contain;" />'
		return ""
	imagen_tag.allow_tags = True
	imagen_tag.short_description = "Imagen"

from .models import Contacto, Hilado, NumeroCrochet, StockCrochet, Compra, DetalleCompra
class DetalleCompraInline(admin.TabularInline):
	model = DetalleCompra
	extra = 0

@admin.register(Compra)
class CompraAdmin(admin.ModelAdmin):
	list_display = ("id", "usuario", "fecha", "estado")
	list_filter = ("estado", "fecha", "usuario")
	inlines = [DetalleCompraInline]

admin.site.register(DetalleCompra)

class StockCrochetInline(admin.TabularInline):
	model = StockCrochet
	extra = 1

@admin.register(Hilado)
class HiladoAdmin(admin.ModelAdmin):
	inlines = [StockCrochetInline]
	list_display = ("nombre", "categoria", "stock", "precio")

admin.site.register(Contacto)
@admin.register(NumeroCrochet)
class NumeroCrochetAdmin(admin.ModelAdmin):
	list_display = ("numero", "precio")
admin.site.register(StockCrochet)

# Register your models here.
