from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse


def nosotros(request):
    return render(request, "core/nosotros.html", {
        "meta_title": "Sobre nosotros",
    })


def robots(request):
    sitemap_url = request.build_absolute_uri(reverse(
        "django.contrib.sitemaps.views.sitemap"
    ))
    lines = ["User-agent: *", "Allow: /", f"Sitemap: {sitemap_url}"]
    return HttpResponse("\n".join(lines), content_type="text/plain")
