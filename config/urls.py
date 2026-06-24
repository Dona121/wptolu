"""URL configuration for config project."""
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path

from core import views as core_views
from servicios import views as servicios_views
from servicios.sitemaps import EstaticasSitemap, ServicioSitemap

sitemaps = {
    "servicios": ServicioSitemap,
    "estaticas": EstaticasSitemap,
}

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", servicios_views.home, name="home"),
    path("nosotros/", core_views.nosotros, name="nosotros"),
    path("servicios/", include("servicios.urls")),
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    path("robots.txt", core_views.robots, name="robots"),
]
