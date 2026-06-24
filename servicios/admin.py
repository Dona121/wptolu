from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin, TabularInline

from .models import ImagenServicio, Servicio, VideoServicio


class ImagenServicioInline(TabularInline):
    model = ImagenServicio
    extra = 1
    fields = ("preview", "url", "titulo", "es_portada", "orden")
    readonly_fields = ("preview",)
    ordering = ("orden",)

    @admin.display(description="Vista previa")
    def preview(self, obj):
        if obj and obj.url:
            return format_html(
                '<img src="{}" style="height:54px;border-radius:8px;object-fit:cover;" alt="">',
                obj.url,
            )
        return "—"


class VideoServicioInline(TabularInline):
    model = VideoServicio
    extra = 0
    fields = ("url", "titulo", "orden")
    ordering = ("orden",)


@admin.register(Servicio)
class ServicioAdmin(ModelAdmin):
    list_display = ("nombre", "tipo", "precio_fmt", "lugar", "destacado", "activo")
    list_filter = ("tipo", "activo", "destacado", "unidad_precio")
    list_editable = ("destacado", "activo")
    search_fields = ("nombre", "lugar", "descripcion_corta", "descripcion")
    inlines = (ImagenServicioInline, VideoServicioInline)
    list_per_page = 30
    # El slug se genera solo a partir del nombre (ver Servicio.save); no se
    # muestra en el formulario para no confundir a quien administra.
    fieldsets = (
        ("Información principal", {
            "fields": ("nombre", "tipo", "descripcion_corta", "descripcion"),
        }),
        ("Precio y capacidad", {
            "fields": ("precio", "unidad_precio", "capacidad"),
        }),
        ("Ubicación", {
            "fields": ("lugar", ("latitud", "longitud")),
        }),
        ("Publicación", {
            "fields": (("destacado", "activo"),),
        }),
    )

    @admin.display(description="Precio", ordering="precio")
    def precio_fmt(self, obj):
        return f"${obj.precio:,.0f} {obj.get_unidad_precio_display()}"
