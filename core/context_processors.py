from .models import ConfiguracionSitio, RedSocial


def sitio(request):
    """Inyecta la configuración del sitio y las redes activas en cada plantilla.

    Decisión de alcance: las redes sociales se manejan a nivel GLOBAL del sitio
    (modelo RedSocial + ConfiguracionSitio). No se duplican por servicio porque
    el negocio es un único operador local; el CTA de WhatsApp por servicio usa
    el número global con un mensaje prellenado según el servicio.
    """
    return {
        "sitio": ConfiguracionSitio.load(),
        "redes": RedSocial.objects.filter(activo=True),
    }
