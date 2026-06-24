from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import Servicio


class ServicioSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return Servicio.objects.filter(activo=True)

    def lastmod(self, obj):
        return obj.actualizado


class EstaticasSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.9

    def items(self):
        return ["home", "servicios:lista"]

    def location(self, item):
        return reverse(item)
