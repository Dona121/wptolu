from decimal import Decimal, InvalidOperation

from django.db.models import Max, Min
from django.shortcuts import get_object_or_404, render

from core.models import HeroSlide

from .models import Servicio


def home(request):
    activos = Servicio.objects.filter(activo=True).prefetch_related("imagenes")
    destacados = activos.filter(destacado=True)[:6]
    if not destacados:
        destacados = activos[:6]
    context = {
        "hero_slides": HeroSlide.objects.filter(activo=True).select_related("servicio"),
        "destacados": destacados,
        "hoteles": activos.filter(tipo=Servicio.Tipo.HOTEL)[:3],
        "lanchas": activos.filter(tipo=Servicio.Tipo.LANCHA)[:3],
        "total_hoteles": activos.filter(tipo=Servicio.Tipo.HOTEL).count(),
        "total_lanchas": activos.filter(tipo=Servicio.Tipo.LANCHA).count(),
        "meta_title": None,  # usa el título por defecto
    }
    return render(request, "home.html", context)


def _to_decimal(value):
    try:
        return Decimal(value)
    except (InvalidOperation, TypeError, ValueError):
        return None


def lista(request):
    qs = Servicio.objects.filter(activo=True).prefetch_related("imagenes")

    tipo = request.GET.get("tipo") or ""
    lugar = request.GET.get("lugar") or ""
    precio = request.GET.get("precio") or ""  # "consultar" = solo sin precio
    precio_min = _to_decimal(request.GET.get("precio_min"))
    precio_max = _to_decimal(request.GET.get("precio_max"))
    orden = request.GET.get("orden") or "-destacado"

    if tipo in {Servicio.Tipo.HOTEL, Servicio.Tipo.LANCHA}:
        qs = qs.filter(tipo=tipo)
    if lugar:
        qs = qs.filter(lugar=lugar)
    if precio == "consultar":
        # Solo servicios con tarifa variable (sin precio fijo).
        qs = qs.filter(precio__isnull=True)
    else:
        if precio_min is not None:
            qs = qs.filter(precio__gte=precio_min)
        if precio_max is not None:
            qs = qs.filter(precio__lte=precio_max)

    ordenes_validos = {"precio", "-precio", "nombre", "-destacado", "-creado"}
    if orden in ordenes_validos:
        if orden == "-destacado":
            qs = qs.order_by("-destacado", "-creado")
        else:
            qs = qs.order_by(orden)

    base = Servicio.objects.filter(activo=True)
    # ¿El filtro de precio tiene sentido? Solo si algún servicio tiene precio fijo.
    # Si todos están "a consultar", se oculta por completo el filtro de precio.
    hay_con_precio = base.filter(precio__isnull=False).exists()
    hay_sin_precio = base.filter(precio__isnull=True).exists()
    rango = base.aggregate(min=Min("precio"), max=Max("precio"))
    lugares = (
        base.order_by("lugar").values_list("lugar", flat=True).distinct()
    )

    context = {
        "servicios": qs,
        "total": qs.count(),
        "tipos": Servicio.Tipo.choices,
        "lugares": lugares,
        "rango": rango,
        "hay_con_precio": hay_con_precio,
        "hay_sin_precio": hay_sin_precio,
        "filtros": {
            "tipo": tipo,
            "lugar": lugar,
            "precio": precio,
            "precio_min": request.GET.get("precio_min", ""),
            "precio_max": request.GET.get("precio_max", ""),
            "orden": orden,
        },
        "meta_title": "Catálogo de hoteles y lanchas en Tolú",
    }
    # Carga parcial con htmx: solo la grilla de resultados (sin recargar la página).
    if request.headers.get("HX-Request"):
        return render(request, "servicios/_grilla.html", context)
    return render(request, "servicios/lista.html", context)


def detalle(request, slug):
    servicio = get_object_or_404(
        Servicio.objects.prefetch_related("imagenes", "videos"),
        slug=slug,
        activo=True,
    )
    relacionados = (
        Servicio.objects.filter(activo=True, tipo=servicio.tipo)
        .exclude(pk=servicio.pk)
        .prefetch_related("imagenes")[:3]
    )
    context = {
        "servicio": servicio,
        "relacionados": relacionados,
        "meta_title": f"{servicio.nombre} · {servicio.lugar}",
        "meta_description": servicio.descripcion_corta,
        "og_image": servicio.portada.url if servicio.portada else None,
    }
    return render(request, "servicios/detalle.html", context)
