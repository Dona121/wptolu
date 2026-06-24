import re
from urllib.parse import parse_qs, urlparse

from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Servicio(models.Model):
    """Un hotel o una lancha/tour ofertado en Tolú."""

    class Tipo(models.TextChoices):
        HOTEL = "hotel", "Hotel"
        LANCHA = "lancha", "Lancha / Tour"

    class Unidad(models.TextChoices):
        POR_NOCHE = "por_noche", "por noche"
        POR_PERSONA = "por_persona", "por persona"
        POR_RECORRIDO = "por_recorrido", "por recorrido"
        POR_DIA = "por_dia", "por día"

    nombre = models.CharField("nombre", max_length=140)
    slug = models.SlugField("slug", max_length=160, unique=True, blank=True)
    tipo = models.CharField("tipo", max_length=10, choices=Tipo.choices, db_index=True)
    descripcion_corta = models.CharField(
        "descripción corta", max_length=180,
        help_text="Texto breve para las tarjetas del catálogo.",
    )
    descripcion = models.TextField("descripción")
    precio = models.DecimalField(
        "precio", max_digits=12, decimal_places=2, blank=True, null=True,
        help_text="Déjalo vacío si el precio es variable: el sitio invitará a "
                  "consultar por WhatsApp.",
    )
    unidad_precio = models.CharField(
        "unidad de precio", max_length=15,
        choices=Unidad.choices, default=Unidad.POR_NOCHE,
        null=False,
        blank=True
    )
    lugar = models.CharField(
        "lugar / ubicación", max_length=140,
        help_text="Zona de Tolú o destino del tour (ej. Playa El Francés, Islas de San Bernardo).",
    )
    latitud = models.FloatField("latitud", null=True, blank=True)
    longitud = models.FloatField("longitud", null=True, blank=True)
    capacidad = models.PositiveIntegerField("capacidad", null=True, blank=True)
    destacado = models.BooleanField("destacado en el home", default=False)
    activo = models.BooleanField("visible en el sitio", default=True, db_index=True)
    creado = models.DateTimeField("creado", auto_now_add=True)
    actualizado = models.DateTimeField("actualizado", auto_now=True)

    class Meta:
        verbose_name = "servicio"
        verbose_name_plural = "servicios"
        ordering = ["-destacado", "-creado"]
        indexes = [models.Index(fields=["tipo", "activo"])]

    def __str__(self):
        return f"{self.get_tipo_display()} · {self.nombre}"

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.nombre)[:150] or "servicio"
            slug = base
            n = 2
            while Servicio.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{n}"
                n += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("servicios:detalle", kwargs={"slug": self.slug})

    @property
    def precio_a_consultar(self):
        """True cuando no se fijó precio (tarifa variable: se consulta)."""
        return self.precio is None

    @property
    def portada(self):
        """Imagen marcada como portada, o la primera disponible."""
        return (
            self.imagenes.filter(es_portada=True).first()
            or self.imagenes.first()
        )

    @property
    def coordenadas(self):
        """Etiqueta tipo carta náutica para latitud/longitud, o None."""
        if self.latitud is None or self.longitud is None:
            return None
        ns = "N" if self.latitud >= 0 else "S"
        ew = "E" if self.longitud >= 0 else "O"
        return f"{abs(self.latitud):.4f}°{ns}  {abs(self.longitud):.4f}°{ew}"


class ImagenServicio(models.Model):
    """Imagen referenciada por enlace (URLField), no archivo subido."""

    servicio = models.ForeignKey(
        Servicio, on_delete=models.CASCADE, related_name="imagenes"
    )
    url = models.URLField("URL de la imagen", max_length=600)
    titulo = models.CharField(
        "título / texto alternativo", max_length=160,
        help_text="Describe la imagen (accesibilidad y SEO).",
    )
    es_portada = models.BooleanField("usar como portada", default=False)
    orden = models.PositiveIntegerField("orden", default=0)

    class Meta:
        verbose_name = "imagen"
        verbose_name_plural = "imágenes"
        ordering = ["orden", "id"]

    def __str__(self):
        return self.titulo or self.url


class VideoServicio(models.Model):
    """Video por enlace (YouTube/Vimeo). Se normaliza a URL de embed."""

    servicio = models.ForeignKey(
        Servicio, on_delete=models.CASCADE, related_name="videos"
    )
    url = models.URLField("URL del video", max_length=600,
                          help_text="Enlace de YouTube o Vimeo.")
    titulo = models.CharField("título", max_length=160, blank=True)
    orden = models.PositiveIntegerField("orden", default=0)

    class Meta:
        verbose_name = "video"
        verbose_name_plural = "videos"
        ordering = ["orden", "id"]

    def __str__(self):
        return self.titulo or self.url

    @property
    def embed_url(self):
        """Convierte enlaces de YouTube/Vimeo a su formato embebible."""
        url = self.url.strip()
        host = urlparse(url).netloc.lower()

        # YouTube: youtu.be/ID, watch?v=ID, /embed/ID, /shorts/ID
        if "youtu" in host:
            yt_id = None
            if "youtu.be" in host:
                yt_id = urlparse(url).path.lstrip("/")
            elif "/embed/" in url:
                yt_id = url.split("/embed/")[1].split("?")[0]
            elif "/shorts/" in url:
                yt_id = url.split("/shorts/")[1].split("?")[0]
            else:
                qs = parse_qs(urlparse(url).query)
                yt_id = (qs.get("v") or [None])[0]
            if yt_id:
                # Dominio sin cookies: reduce bloqueos de incrustación (error 153)
                # por consentimiento/cookies. rel=0 limita los videos sugeridos.
                return f"https://www.youtube-nocookie.com/embed/{yt_id}?rel=0"

        # Vimeo: vimeo.com/ID
        if "vimeo.com" in host:
            m = re.search(r"vimeo\.com/(?:video/)?(\d+)", url)
            if m:
                return f"https://player.vimeo.com/video/{m.group(1)}"

        return url
