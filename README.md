# Tolú Turismo

Plataforma web para ofertar **hoteles** y **lanchas/tours** en Santiago de Tolú
(Golfo de Morrosquillo, Sucre — Colombia). Catálogo público con filtros, detalle
con galería y video, y contacto directo por WhatsApp. Todo el contenido se
administra desde el panel (django-unfold) sin tocar código.

## Stack

- **Python / entorno:** `uv`
- **Backend:** Django 6
- **Admin:** django-unfold
- **CSS:** Tailwind CSS v4 (CLI standalone, sin Node)
- **Interactividad:** Alpine.js (menú móvil, lightbox, filtros) + htmx (carga
  parcial de la grilla de resultados, sin recargar la página)
- **Base de datos:** SQLite en desarrollo; PostgreSQL listo para producción

### Decisiones técnicas

- **Tailwind standalone CLI:** se eligió el binario único (`tailwindcss.exe`)
  para no acoplar la toolchain de Node a un proyecto Python con `uv`. El CSS
  compilado vive en `static/css/tolu.css`; la fuente con los tokens de diseño en
  `static/css/input.css`.
- **htmx:** se introdujo solo para el listado. Al cambiar un filtro o el orden,
  htmx pide la vista y reemplaza únicamente `#resultados` (parcial
  `servicios/_grilla.html`), actualizando la URL. Sin JS también funciona: el
  mismo formulario hace un GET normal.
- **Redes sociales:** se manejan a nivel **global** del sitio (`RedSocial` +
  `ConfiguracionSitio`). No se duplican por servicio porque el negocio es un
  único operador local; el CTA de WhatsApp por servicio reutiliza el número
  global con un mensaje prellenado según el servicio.
- **Imágenes y videos por enlace** (`URLField`), no archivos subidos: simplifica
  la etapa de pruebas (se referencian recursos de un CDN/S3). Por eso Pillow no
  es necesario.

### Sistema de diseño (skill `frontend-design`)

- **Color:** `mar` #0A4A5C, `turquesa` #15A0A6, `sol` #FF7A3D (atardecer de Tolú,
  color firma), `concha` #F3E2C7, `arena` #FBF7F0, `carbon` #0E2A30.
- **Tipografía:** *Bricolage Grotesque* (display), *Hanken Grotesk* (cuerpo),
  *Space Mono* (datos: precios y coordenadas náuticas).
- **Elemento firma:** hero fotográfico a sangre completa con efecto **Ken Burns**
  (zoom lento) y cross-fade entre imágenes administrables (`HeroSlide`), rematado
  por un divisor de olas que funde la foto con la sección oscura. Las etiquetas de
  lugar usan formato de coordenada náutica en mono. La audacia se concentra ahí;
  el resto queda disciplinado.

## Requisitos

- [uv](https://docs.astral.sh/uv/) instalado
- Python 3.13 (uv lo gestiona)

## Cómo correrlo

```bash
# 1. Dependencias y entorno (uv crea el .venv automáticamente)
uv sync

# 2. Migraciones
uv run python manage.py migrate

# 3. Datos de prueba (config del sitio, redes y 6 servicios con fotos/videos)
uv run python manage.py seed          # usa --reset para recargar desde cero

# 4. Superusuario para el admin
uv run python manage.py createsuperuser

# 5. Servidor
uv run python manage.py runserver
```

Sitio: http://127.0.0.1:8000/ · Admin: http://127.0.0.1:8000/admin/

> Si corriste el `seed` de este repo, ya existe un admin de ejemplo:
> usuario `admin` / contraseña `tolu12345` (cámbiala en producción).

### Compilar Tailwind

El CSS ya viene compilado en `static/css/tolu.css`. Para regenerarlo tras editar
clases o tokens, descarga el binario standalone y ejecútalo:

```bash
# Descargar una vez (Windows x64) — ver releases para tu plataforma:
#   https://github.com/tailwindlabs/tailwindcss/releases/latest
# tailwindcss-windows-x64.exe  ->  renómbralo a tailwindcss.exe

# Compilar
./tailwindcss.exe -i static/css/input.css -o static/css/tolu.css --minify

# Modo observador durante el desarrollo
./tailwindcss.exe -i static/css/input.css -o static/css/tolu.css --watch
```

## Administrar contenido desde el panel

Todo es parametrizable sin tocar código:

- **Servicios** (`Servicios`): crea un hotel o lancha con nombre, tipo, precio y
  unidad, lugar, descripción, capacidad y coordenadas. En la misma pantalla,
  mediante *inlines*, agregas varias **imágenes** (por URL, marca una como
  portada) y **videos** (pega el enlace de YouTube/Vimeo; se normaliza a embed).
  - `destacado` → aparece en el home. `activo` → controla la visibilidad pública.
- **Imágenes del hero** (`Imágenes del hero`): las fotos a pantalla completa que
  rotan en el home. Cada slide tiene imagen, título/subtítulo opcionales y un
  botón que puede enlazar a un servicio del catálogo **o** a una URL manual (el
  servicio tiene prioridad). Controla la rotación con `orden` y `activo`. Si solo
  hay un slide activo se muestra fijo; si no hay ninguno, se usa un degradado de
  respaldo. El intervalo de rotación se ajusta en *Configuración del sitio*.
- **Redes sociales** (`Redes sociales`): agrega WhatsApp, Instagram, etc.; se
  reflejan en el footer y los CTAs.
- **Configuración del sitio** (`Configuración del sitio`): nombre, eslogan, logo,
  WhatsApp, email, dirección, **intervalo del hero (segundos)** y meta description
  SEO. Es un *singleton* (una sola instancia).

Cualquier cambio guardado se ve de inmediato en el front.

## Migrar a PostgreSQL (producción)

Solo se cambia `DATABASES` en `config/settings.py` — los modelos y vistas no se
tocan. En el archivo está el bloque comentado listo para usar:

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("DB_NAME", "tolu_turismo"),
        "USER": os.environ.get("DB_USER", "tolu"),
        "PASSWORD": os.environ.get("DB_PASSWORD", ""),
        "HOST": os.environ.get("DB_HOST", "localhost"),
        "PORT": os.environ.get("DB_PORT", "5432"),
    }
}
```

Luego: `uv add psycopg[binary]` y `uv run python manage.py migrate`.

> Para producción recuerda además: `DEBUG = False`, `ALLOWED_HOSTS` con tu
> dominio, `SECRET_KEY` desde variable de entorno, y `collectstatic`.

## Estructura

```
config/        settings, urls, wsgi/asgi
core/          ConfiguracionSitio, RedSocial, páginas estáticas, context processor
servicios/     Servicio + ImagenServicio + VideoServicio, vistas, admin, sitemap, seed
templates/     base.html, home.html, servicios/, core/, partials/
static/css/    input.css (tokens) + tolu.css (compilado)
```
