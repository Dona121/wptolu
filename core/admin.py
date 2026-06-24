from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin

from .models import ConfiguracionSitio, HeroSlide, RedSocial


@admin.register(RedSocial)
class RedSocialAdmin(ModelAdmin):
    list_display = ("plataforma", "url", "activo", "orden")
    list_filter = ("plataforma", "activo")
    list_editable = ("activo", "orden")


@admin.register(HeroSlide)
class HeroSlideAdmin(ModelAdmin):
    list_display = ("preview", "titulo", "destino", "orden", "activo")
    list_display_links = ("preview", "titulo")
    list_editable = ("orden", "activo")
    list_filter = ("activo",)
    autocomplete_fields = ("servicio",)
    fieldsets = (
        ("Imagen", {"fields": ("imagen_url", "titulo", "subtitulo")}),
        ("Botón (opcional)", {"fields": ("cta_texto", "servicio", "cta_url")}),
        ("Rotación", {"fields": ("orden", "activo")}),
    )

    @admin.display(description="Vista previa")
    def preview(self, obj):
        if obj and obj.imagen_url:
            return format_html(
                '<img src="{}" style="height:48px;width:84px;border-radius:8px;object-fit:cover;" alt="">',
                obj.imagen_url,
            )
        return "—"

    @admin.display(description="Enlaza a")
    def destino(self, obj):
        if obj.servicio_id:
            return obj.servicio.nombre
        return obj.cta_url or "—"


@admin.register(ConfiguracionSitio)
class ConfiguracionSitioAdmin(ModelAdmin):
    fieldsets = (
        ("Identidad", {"fields": ("nombre_sitio", "eslogan", "logo_url")}),
        ("Contacto", {"fields": ("telefono_whatsapp", "email", "direccion")}),
        ("Hero del home", {"fields": ("hero_intervalo_segundos",)}),
        ("SEO", {"fields": ("meta_description",)}),
    )

    def has_add_permission(self, request):
        # Singleton: no se permite crear una segunda instancia.
        return not ConfiguracionSitio.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
