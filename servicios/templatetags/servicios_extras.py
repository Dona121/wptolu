from urllib.parse import urlencode

from django import template

register = template.Library()


@register.filter
def pesos(valor):
    """Formatea un valor como pesos colombianos: 180000 -> $180.000."""
    try:
        entero = int(round(float(valor)))
    except (TypeError, ValueError):
        return valor
    return "$" + f"{entero:,}".replace(",", ".")


@register.simple_tag(takes_context=True)
def querystring_sin(context, *claves):
    """Devuelve el querystring actual quitando las claves indicadas.

    Útil para construir enlaces de filtros conservando el resto del estado.
    """
    params = context["request"].GET.copy()
    for clave in claves:
        params.pop(clave, None)
    datos = {k: v for k, v in params.items() if v}
    return urlencode(datos)
