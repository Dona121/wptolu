"""Carga datos de prueba: configuración, redes y varios servicios.

Uso:  uv run python manage.py seed
      uv run python manage.py seed --reset   (borra servicios antes de cargar)
"""
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from core.models import ConfiguracionSitio, HeroSlide, RedSocial
from servicios.models import ImagenServicio, Servicio, VideoServicio

# Imágenes públicas (Unsplash) usadas solo como datos de ejemplo.
IMG = {
    "playa": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=1200&q=80",
    "hotel1": "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=1200&q=80",
    "hotel2": "https://images.unsplash.com/photo-1571896349842-33c89424de2d?w=1200&q=80",
    "piscina": "https://images.unsplash.com/photo-1571003123894-1f0594d2b5d9?w=1200&q=80",
    "habitacion": "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?w=1200&q=80",
    "lancha": "https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=1200&q=80",
    "isla": "https://images.unsplash.com/photo-1559128010-7c1ad6e1b6a5?w=1200&q=80",
    "mar": "https://images.unsplash.com/photo-1505228395891-9a51e7e86bf6?w=1200&q=80",
    "snorkel": "https://images.unsplash.com/photo-1544550581-5f7ceaf7f992?w=1200&q=80",
    "atardecer": "https://images.unsplash.com/photo-1518837695005-2083093ee35b?w=1200&q=80",
    "cabana": "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?w=1200&q=80",
    "muelle": "https://images.unsplash.com/photo-1473116763249-2faaef81ccda?w=1200&q=80",
}

SERVICIOS = [
    {
        "nombre": "Hotel Brisas del Golfo",
        "tipo": "hotel", "precio": "240000", "unidad": "por_noche",
        "lugar": "Avenida de la Playa, Tolú", "capacidad": 4,
        "destacado": True, "lat": 9.5240, "lng": -75.5830,
        "corta": "Frente al mar, con piscina y desayuno típico incluido.",
        "desc": "A pocos pasos de la arena, el Hotel Brisas del Golfo ofrece habitaciones amplias con aire acondicionado y balcón con vista al Golfo de Morrosquillo.\n\nIncluye desayuno costeño, piscina al aire libre y parqueadero. El punto perfecto para salir temprano a los paseos en lancha.",
        "imgs": [("playa", "Vista al mar desde el hotel", True), ("hotel1", "Fachada del hotel"), ("piscina", "Piscina al aire libre"), ("habitacion", "Habitación doble")],
        "videos": [("https://www.youtube.com/watch?v=aqz-KE-bpKQ", "Recorrido por el hotel")],
    },
    {
        "nombre": "Posada Mar Azul",
        "tipo": "hotel", "precio": "150000", "unidad": "por_noche",
        "lugar": "Centro, Tolú", "capacidad": 3,
        "destacado": True, "lat": 9.5260, "lng": -75.5810,
        "corta": "Posada familiar a dos cuadras del muelle turístico.",
        "desc": "Posada acogedora de estilo costero, ideal para familias. Habitaciones ventiladas, hamacas en el patio y bicicletas disponibles para recorrer el malecón.",
        "imgs": [("hotel2", "Entrada de la posada", True), ("cabana", "Zona de hamacas"), ("habitacion", "Habitación familiar")],
        "videos": [],
    },
    {
        "nombre": "Cabañas Manglar Tolú",
        "tipo": "hotel", "precio": "320000", "unidad": "por_noche",
        "lugar": "Sector El Francés, Tolú", "capacidad": 6,
        "destacado": False, "lat": 9.5050, "lng": -75.5900,
        "corta": "Cabañas privadas entre manglar y playa, para grupos.",
        "desc": "Cabañas independientes rodeadas de manglar, con cocina equipada y terraza propia. Perfectas para grupos que buscan tranquilidad cerca de la naturaleza.",
        "imgs": [("cabana", "Cabaña entre el manglar", True), ("playa", "Playa cercana"), ("atardecer", "Atardecer desde la terraza")],
        "videos": [],
    },
    {
        "nombre": "Tour Islas de San Bernardo",
        "tipo": "lancha", "precio": "85000", "unidad": "por_persona",
        "lugar": "Islas de San Bernardo", "capacidad": 25,
        "destacado": True, "lat": 9.7833, "lng": -75.8500,
        "corta": "Paseo full day a las islas con almuerzo y snorkel.",
        "desc": "Salida desde el muelle de Tolú hacia el archipiélago de San Bernardo. Visitamos Isla Múcura, Isla Tintipán y el famoso Islote de Santa Cruz.\n\nIncluye chaleco salvavidas, guía, parada para snorkel y tiempo libre en playa. Almuerzo típico opcional.",
        "imgs": [("isla", "Islas de San Bernardo", True), ("lancha", "Nuestra lancha"), ("snorkel", "Parada de snorkel"), ("mar", "Aguas cristalinas")],
        "videos": [("https://www.youtube.com/watch?v=aqz-KE-bpKQ", "Un día en las islas")],
    },
    {
        "nombre": "Paseo al Islote de Santa Cruz",
        "tipo": "lancha", "precio": "70000", "unidad": "por_persona",
        "lugar": "Islote de Santa Cruz", "capacidad": 20,
        "destacado": True, "lat": 9.7700, "lng": -75.8650,
        "corta": "Conoce la isla más densamente poblada del mundo.",
        "desc": "Recorrido guiado por el Islote de Santa Cruz, una pequeña isla artificial habitada por pescadores. Conoce su historia, su gente y el acuario natural cercano.",
        "imgs": [("muelle", "Salida del muelle", True), ("isla", "Islote de Santa Cruz"), ("mar", "En altamar")],
        "videos": [],
    },
    {
        "nombre": "Atardecer en lancha por el Golfo",
        "tipo": "lancha", "precio": "180000", "unidad": "por_recorrido",
        "lugar": "Golfo de Morrosquillo", "capacidad": 8,
        "destacado": False, "lat": 9.5300, "lng": -75.6000,
        "corta": "Recorrido privado al atardecer, ideal para parejas.",
        "desc": "Navega el Golfo de Morrosquillo a la hora dorada. Recorrido privado de hora y media con bebidas a bordo y la mejor vista del atardecer caribeño.",
        "imgs": [("atardecer", "Atardecer en el golfo", True), ("lancha", "Lancha privada"), ("mar", "Navegando")],
        "videos": [],
    },
]

REDES = [
    ("whatsapp", "https://wa.me/573001234567"),
    ("instagram", "https://instagram.com/toluturismo"),
    ("facebook", "https://facebook.com/toluturismo"),
    ("tiktok", "https://tiktok.com/@toluturismo"),
]

# HeroSlides: fotos horizontales de licencia libre (Unsplash) con temática
# costera/caribeña. Se cargan con ancho 1920 para el hero a sangre completa.
# El administrador las reemplaza luego por fotos definitivas de Tolú.
HERO = [
    {
        "img": "https://images.unsplash.com/photo-1559128010-7c1ad6e1b6a5?w=1920&q=80",
        "titulo": "Donde el Golfo se vuelve plan",
        "subtitulo": "Hoteles frente al mar y paseos en lancha en Santiago de Tolú.",
        "cta_texto": "Ver el catálogo", "servicio": None, "cta_url": "",
    },
    {
        "img": "https://images.unsplash.com/photo-1505228395891-9a51e7e86bf6?w=1920&q=80",
        "titulo": "Islas de San Bernardo, todo el día",
        "subtitulo": "Snorkel, playa y el Islote de Santa Cruz en una sola salida.",
        "cta_texto": "Reservar tour", "servicio": "Tour Islas de San Bernardo", "cta_url": "",
    },
    {
        "img": "https://images.unsplash.com/photo-1518837695005-2083093ee35b?w=1920&q=80",
        "titulo": "Atardeceres del Caribe colombiano",
        "subtitulo": "Navega el Golfo de Morrosquillo a la hora dorada.",
        "cta_texto": "Ver paseo al atardecer", "servicio": "Atardecer en lancha por el Golfo", "cta_url": "",
    },
    {
        "img": "https://images.unsplash.com/photo-1473116763249-2faaef81ccda?w=1920&q=80",
        "titulo": "Tu base frente a la playa",
        "subtitulo": "Hoteles y cabañas a pocos pasos de la arena.",
        "cta_texto": "Ver hoteles", "servicio": None,
        "cta_url": "/servicios/?tipo=hotel",
    },
]


class Command(BaseCommand):
    help = "Carga datos de prueba (configuración, redes y servicios)."

    def add_arguments(self, parser):
        parser.add_argument("--reset", action="store_true",
                            help="Elimina servicios y redes antes de cargar.")

    @transaction.atomic
    def handle(self, *args, **options):
        if options["reset"]:
            Servicio.objects.all().delete()
            RedSocial.objects.all().delete()
            HeroSlide.objects.all().delete()
            self.stdout.write(self.style.WARNING("Servicios, redes y hero eliminados."))

        # Configuración del sitio (singleton)
        cfg = ConfiguracionSitio.load()
        cfg.nombre_sitio = "Tolú Turismo"
        cfg.eslogan = "Hoteles y lanchas en el Golfo de Morrosquillo."
        cfg.telefono_whatsapp = "573001234567"
        cfg.email = "reservas@toluturismo.co"
        cfg.direccion = "Muelle turístico, Santiago de Tolú, Sucre"
        cfg.meta_description = (
            "Reserva hoteles frente al mar y paseos en lancha a las Islas de "
            "San Bernardo desde Santiago de Tolú, Golfo de Morrosquillo."
        )
        cfg.save()

        # Redes
        for orden, (plat, url) in enumerate(REDES):
            RedSocial.objects.update_or_create(
                plataforma=plat, defaults={"url": url, "activo": True, "orden": orden}
            )

        # Servicios
        creados = 0
        for data in SERVICIOS:
            servicio, nuevo = Servicio.objects.update_or_create(
                nombre=data["nombre"],
                defaults={
                    "tipo": data["tipo"],
                    "descripcion_corta": data["corta"],
                    "descripcion": data["desc"],
                    "precio": Decimal(data["precio"]),
                    "unidad_precio": data["unidad"],
                    "lugar": data["lugar"],
                    "latitud": data["lat"],
                    "longitud": data["lng"],
                    "capacidad": data["capacidad"],
                    "destacado": data["destacado"],
                    "activo": True,
                },
            )
            servicio.imagenes.all().delete()
            for orden, item in enumerate(data["imgs"]):
                clave, titulo = item[0], item[1]
                portada = len(item) > 2 and item[2]
                ImagenServicio.objects.create(
                    servicio=servicio, url=IMG[clave], titulo=titulo,
                    es_portada=portada, orden=orden,
                )
            servicio.videos.all().delete()
            for orden, (url, titulo) in enumerate(data["videos"]):
                VideoServicio.objects.create(
                    servicio=servicio, url=url, titulo=titulo, orden=orden,
                )
            creados += 1

        # HeroSlides (se enlazan a un servicio por nombre cuando aplica)
        HeroSlide.objects.all().delete()
        for orden, h in enumerate(HERO):
            servicio = None
            if h["servicio"]:
                servicio = Servicio.objects.filter(nombre=h["servicio"]).first()
            HeroSlide.objects.create(
                imagen_url=h["img"], titulo=h["titulo"], subtitulo=h["subtitulo"],
                cta_texto=h["cta_texto"], servicio=servicio, cta_url=h["cta_url"],
                orden=orden, activo=True,
            )

        self.stdout.write(self.style.SUCCESS(
            f"Listo: {creados} servicios, {len(REDES)} redes, {len(HERO)} hero slides y configuración."
        ))
