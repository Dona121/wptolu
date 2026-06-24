from django.core.exceptions import ValidationError
from django.db import models


class ConfiguracionSitio(models.Model):
    """Configuración global del sitio. Singleton: solo existe una instancia."""

    nombre_sitio = models.CharField("nombre del sitio", max_length=120, default="Tolú Turismo")
    eslogan = models.CharField("eslogan", max_length=200, blank=True)
    logo_url = models.URLField("URL del logo", max_length=600, blank=True)

    telefono_whatsapp = models.CharField(
        "WhatsApp", max_length=30, blank=True,
        help_text="Número en formato internacional sin signos, ej. 573001234567.",
    )
    email = models.EmailField("email de contacto", blank=True)
    direccion = models.CharField("dirección", max_length=200, blank=True)

    hero_intervalo_segundos = models.PositiveIntegerField(
        "intervalo del hero (segundos)", default=6,
        help_text="Cada cuántos segundos rota la imagen del hero del home.",
    )

    meta_description = models.CharField(
        "meta description por defecto", max_length=300, blank=True,
        help_text="Descripción SEO usada cuando una página no define la suya.",
    )

    class Meta:
        verbose_name = "configuración del sitio"
        verbose_name_plural = "configuración del sitio"

    def __str__(self):
        return self.nombre_sitio

    def save(self, *args, **kwargs):
        self.pk = 1  # fuerza singleton
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # No se permite borrar el singleton.
        raise ValidationError("La configuración del sitio no se puede eliminar.")

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    @property
    def whatsapp_link(self):
        if not self.telefono_whatsapp:
            return ""
        numero = "".join(ch for ch in self.telefono_whatsapp if ch.isdigit())
        return f"https://wa.me/{numero}"


class RedSocial(models.Model):
    """Red social a nivel global del sitio (footer y CTAs)."""

    class Plataforma(models.TextChoices):
        WHATSAPP = "whatsapp", "WhatsApp"
        INSTAGRAM = "instagram", "Instagram"
        FACEBOOK = "facebook", "Facebook"
        TIKTOK = "tiktok", "TikTok"
        YOUTUBE = "youtube", "YouTube"
        X = "x", "X (Twitter)"

    plataforma = models.CharField("plataforma", max_length=20, choices=Plataforma.choices)
    url = models.URLField("URL", max_length=600)
    activo = models.BooleanField("activo", default=True)
    orden = models.PositiveIntegerField("orden", default=0)

    class Meta:
        verbose_name = "red social"
        verbose_name_plural = "redes sociales"
        ordering = ["orden", "id"]

    def __str__(self):
        return self.get_plataforma_display()


class HeroSlide(models.Model):
    """Imagen del hero del home que rota automáticamente. Editable desde el panel."""

    imagen_url = models.URLField("URL de la imagen", max_length=600,
                                 help_text="Foto horizontal, ≥1920px de ancho.")
    titulo = models.CharField("título", max_length=120, blank=True,
                              help_text="Texto grande sobre la imagen (opcional).")
    subtitulo = models.CharField("subtítulo", max_length=200, blank=True)
    cta_texto = models.CharField("texto del botón", max_length=40, blank=True)
    # Enlace del botón: un servicio del catálogo tiene prioridad; si no, la URL manual.
    servicio = models.ForeignKey(
        "servicios.Servicio", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="hero_slides", verbose_name="enlazar a un servicio",
        help_text="Si eliges un servicio, el botón lleva a su página de detalle.",
    )
    cta_url = models.URLField("o URL manual", max_length=600, blank=True,
                              help_text="Se usa solo si no eliges un servicio.")
    orden = models.PositiveIntegerField("orden", default=0)
    activo = models.BooleanField("activo (entra en la rotación)", default=True)

    class Meta:
        verbose_name = "imagen del hero"
        verbose_name_plural = "imágenes del hero"
        ordering = ["orden", "id"]

    def __str__(self):
        return self.titulo or f"Slide {self.pk}"

    @property
    def enlace(self):
        """URL de destino del botón: el servicio tiene prioridad sobre la URL manual."""
        if self.servicio_id:
            return self.servicio.get_absolute_url()
        return self.cta_url or ""
