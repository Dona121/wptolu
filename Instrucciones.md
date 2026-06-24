# Prompt: Plataforma de oferta de hoteles y lanchas en Tolú (Sucre)

## Rol

Actúa como desarrollador full-stack senior especializado en Django y diseño web moderno. Vas a construir, de forma incremental y autónoma, un sitio web para ofertar **hoteles** y **lanchas/tours** en el municipio de **Santiago de Tolú, Sucre (Colombia)**. Trabaja con criterio técnico: cuando una decisión tenga alternativas relevantes, elige la más adecuada y deja una nota breve del porqué.

> **Usa la habilidad (skill) `frontend-design`.** Antes de diseñar cualquier UI, carga y aplica la skill `frontend-design` disponible en `.claude/skills/frontend-design/SKILL.md`. Sigue su proceso (brainstorm → plan de tokens de color/tipografía/layout → crítica → build → crítica de nuevo) y su exigencia de un diseño con identidad propia, no plantillero. Si la skill no está disponible en tu entorno, indícalo explícitamente y aplica de todas formas sus principios resumidos en la sección de diseño de este prompt.

## Objetivo del proyecto

Una página pública, moderna y responsive donde los visitantes puedan:

- Ver un catálogo de hoteles y de lanchas/tours.
- Filtrar por tipo de servicio (hotel / lancha), precio y ubicación.
- Entrar al detalle de cada servicio con galería de imágenes, video, descripción, precio y ubicación.
- Contactar fácilmente (CTA de WhatsApp y redes sociales son críticos para turismo local).

Todo el contenido debe ser **100% parametrizable desde el panel de administración**, sin tocar código: enlaces de imágenes y videos, redes sociales, e información básica del servicio (precio, lugar, descripción).

## Contexto de negocio

Tolú está en el Golfo de Morrosquillo; su turismo gira en torno a playas, hospedaje y paseos en lancha a las Islas de San Bernardo, el Islote de Santa Cruz y zonas cercanas. El diseño y el copy deben reflejar un tono costero, cálido y confiable. Prioriza la conversión hacia contacto directo (no es necesario un motor de reservas/pagos en esta etapa).

## Stack tecnológico (obligatorio)

- **Gestor de entorno y dependencias:** `uv` (el entorno ya se inicializa desde Python con uv).
- **Framework backend:** Django (versión estable actual).
- **Base de datos:** SQLite por defecto (etapa de pruebas). Deja la configuración lista para migrar a PostgreSQL en producción cambiando solo `DATABASES`.
- **Admin:** `django-unfold` (panel moderno sobre el admin de Django).
- **CSS:** Tailwind CSS (versión actual), enfoque mobile-first.
- **Interactividad:** JavaScript ligero. Usa **Alpine.js** para interacciones de cliente (menú móvil, lightbox de galería, carrusel, filtros) y, opcionalmente, **htmx** si algún listado se beneficia de carga parcial sin recargar la página. Justifica si introduces htmx.

### Dependencias mínimas a instalar

```bash
uv add django django-unfold
# Pillow solo si finalmente usas algún ImageField; con enlaces (URLField) no es indispensable.
```

### Decisión sobre Tailwind (elige y documenta)

- **Opción recomendada (sin Node):** Tailwind CSS standalone CLI (binario único) para compilar el CSS. Evita acoplar la toolchain de Node a un proyecto Python con uv.
- **Opción rápida de prototipo:** Tailwind por CDN (solo para arranque; no para "producción").
- Evita `django-tailwind` salvo que ya quieras la dependencia de Node; menciónalo como alternativa.

## Estructura del proyecto sugerida

```
tolu_turismo/            # proyecto Django
  config/                # settings, urls, wsgi/asgi
  servicios/             # app principal (modelos, vistas, admin)
  core/                  # configuración del sitio, páginas estáticas
  templates/
    base.html
    home.html
    servicios/lista.html
    servicios/detalle.html
  static/
    css/                 # output de Tailwind
    js/                  # alpine, scripts propios
  manage.py
```

## Modelos de datos

Diseña los modelos para que **toda** la información editable viva en la base de datos y sea administrable desde Unfold. Los enlaces de imágenes y videos son **URLField** (se referencian recursos externos, p. ej. S3 o un CDN), no archivos subidos, para simplificar la etapa de pruebas.

### `Servicio`
- `nombre` (CharField)
- `slug` (SlugField, único, autogenerado)
- `tipo` (choices: `hotel`, `lancha`)
- `descripcion_corta` (CharField, para tarjetas)
- `descripcion` (TextField)
- `precio` (DecimalField)
- `unidad_precio` (choices: `por_noche`, `por_persona`, `por_recorrido`, `por_dia`)
- `lugar` / `ubicacion` (CharField; ej. zona de Tolú o destino del tour)
- `latitud`, `longitud` (FloatField, opcionales, para mapa futuro)
- `capacidad` (PositiveIntegerField, opcional)
- `destacado` (BooleanField, para home)
- `activo` (BooleanField; controla visibilidad pública)
- `creado`, `actualizado` (timestamps)

### `ImagenServicio`
- `servicio` (FK a Servicio, `related_name="imagenes"`)
- `url` (URLField)
- `titulo` / `alt` (CharField, accesibilidad/SEO)
- `es_portada` (BooleanField)
- `orden` (PositiveIntegerField)

### `VideoServicio`
- `servicio` (FK a Servicio, `related_name="videos"`)
- `url` (URLField; soporta enlaces de YouTube/Vimeo, normaliza a formato embed)
- `titulo` (CharField)
- `orden` (PositiveIntegerField)

### `RedSocial`
- `plataforma` (choices: `whatsapp`, `instagram`, `facebook`, `tiktok`, `youtube`, `x`, ...)
- `url` (URLField)
- `activo` (BooleanField)
- `orden` (PositiveIntegerField)
- Decisión: maneja redes a nivel global (en `ConfiguracionSitio`) y, si aporta, también por servicio. Documenta el alcance que implementes.

### `ConfiguracionSitio` (singleton)
- `nombre_sitio`, `eslogan`
- `logo_url` (URLField)
- `telefono_whatsapp`, `email`, `direccion`
- `hero_intervalo_segundos` (PositiveIntegerField, default 6; controla cada cuánto rota el hero)
- Datos de contacto y SEO básicos (meta description por defecto)
- Garantiza una sola instancia editable desde el admin.

### `HeroSlide`
Imágenes del hero del home que rotan automáticamente. Administrables desde el panel.
- `imagen_url` (URLField)
- `titulo` (CharField, opcional; texto sobre la imagen)
- `subtitulo` (CharField, opcional)
- `cta_texto` (CharField, opcional; texto del botón)
- `cta_url` (URLField o FK opcional a `Servicio`, para enlazar el slide a un servicio)
- `orden` (PositiveIntegerField)
- `activo` (BooleanField; controla si entra en la rotación)

> Requisito de parametrización (no negociable): un administrador debe poder crear/editar un servicio, agregar varias imágenes y videos por enlace, definir precio, lugar y descripción, y configurar redes sociales del sitio, **todo desde el panel**, viéndose reflejado de inmediato en el front.

## Panel de administración (Unfold)

- Configura `django-unfold` correctamente (apps en `INSTALLED_APPS` en el orden que exige Unfold, sus settings y la `UNFOLD` config dict).
- `ServicioAdmin` con `TabularInline`/`StackedInline` para `ImagenServicio` y `VideoServicio` (editar el servicio y sus medios en una sola pantalla).
- `list_display`, `list_filter` (por `tipo`, `activo`, `destacado`), `search_fields`, `prepopulated_fields` para el slug.
- Admin para `RedSocial` y `ConfiguracionSitio`.
- Aplica branding de Unfold (colores costeros, nombre del sitio) para que el panel se vea acorde.

## Frontend y diseño

> Aplica la skill `frontend-design`. En la práctica esto significa: define primero un **sistema de tokens** (4–6 colores con hex nombrados, una tipografía display con carácter usada con moderación + una tipografía de cuerpo + una utilitaria para datos/captions, y un concepto de layout), elige **un elemento "firma"** memorable que represente a Tolú (el mar, las lanchas, el Golfo de Morrosquillo) y mantén todo lo demás disciplinado. Evita los clichés de diseño generado por IA (fondo crema + serif de alto contraste + acento terracota; fondo casi negro con un acento verde ácido; layout tipo periódico con reglas finas). El brief manda: tono costero, cálido y confiable.

### Referencias y principios
Inspírate en patrones de UX de plataformas de hospedaje/tours bien valoradas (Booking, Airbnb, Hotels.com) **sin copiar marcas**: hero con buscador/filtros, grilla de tarjetas con imagen destacada y precio, galería con lightbox en el detalle, CTA de contacto siempre visible, navegación sticky.

### Buenas prácticas web actuales
- **Mobile-first** y totalmente responsive.
- HTML **semántico** y accesible (a11y: `alt`, foco, contraste, roles ARIA donde aplique).
- **SEO técnico:** títulos/meta dinámicos por servicio, URLs limpias con slug, Open Graph, sitemap básico.
- **Rendimiento:** `loading="lazy"` en imágenes, evitar layout shift (CLS), apuntar a buen puntaje Lighthouse (LCP/CLS/TBT).
- Micro-interacciones sobrias, estados hover/focus, skeleton o placeholders al cargar.
- Modo claro consistente; modo oscuro opcional.

### Páginas
1. **Home:** hero fotográfico a pantalla completa con propuesta de valor de Tolú + buscador/filtros, sección de destacados (hoteles y lanchas), bloque "por qué reservar con nosotros", footer con redes y contacto.
   - **Hero fotográfico rotativo (por defecto):** el hero es una imagen real a sangre completa (`object-cover`, altura `min-h-[80vh]`) que cambia automáticamente al entrar y cada cierto tiempo. Las imágenes provienen del modelo `HeroSlide` (administrables desde el panel), ordenadas por `orden`. Si no hay ningún `HeroSlide` activo, usa un degradado costero de respaldo.
   - **Comportamiento:** cross-fade (transición de opacidad) entre slides con Alpine.js, usando el intervalo de `ConfiguracionSitio.hero_intervalo_segundos`. Pausa al pasar el cursor. Respeta `prefers-reduced-motion` (sin auto-rotación si el usuario lo pide). Si solo hay un `HeroSlide` activo, muéstralo estático sin rotación.
   - **Firma de diseño:** aplica un efecto **Ken Burns** sutil (zoom lento) sobre cada foto durante su turno, para que no se sienta un slider plantillero. Mantén la firma solo aquí y todo lo demás disciplinado.
   - **Legibilidad:** como el fondo es una foto, aplica un scrim (degradado oscuro, p. ej. de `slate-900/70` abajo a transparente arriba) y usa titular y subtítulo en color claro (blanco/crema), con el eyebrow en un acento legible. La tarjeta de búsqueda (fondo blanco) se mantiene sobre cualquier imagen.
   - **Rendimiento:** primer slide con `loading="eager"` y `fetchpriority="high"`; el resto `loading="lazy"`. Reserva la altura del hero para evitar CLS.
   - **Accesibilidad:** indicadores (bullets) con `aria-label` y navegables por teclado; sin flechas grandes salvo que aporten.
   - **Selección de imágenes:** busca y elige fotos reales que mejor se adapten al hero, de fuentes de **licencia libre** (Unsplash, Pexels, Wikimedia Commons), con temática de Tolú y su entorno: playas del Golfo de Morrosquillo, mar, lanchas/paseos, Islas de San Bernardo, atardeceres costeros. Criterios: orientación horizontal, alta resolución (≥ 1920 px de ancho), composición que conserve un área despejada donde caen el titular y el buscador (evita imágenes con el sujeto muy al centro), y coherencia cromática con la paleta costera. Respeta las licencias y, si la fuente lo exige, incluye la atribución. Las definitivas las cargará el administrador desde el panel; estas son la base inicial.
   - **Términos de búsqueda sugeridos** (combina español e inglés para mejores resultados):
     - `Tolú Sucre playa`, `Santiago de Tolú Colombia`, `Tolú Colombia beach`
     - `Golfo de Morrosquillo`, `Gulf of Morrosquillo Colombia`
     - `Islas de San Bernardo`, `San Bernardo Islands Colombia`, `Islote de Santa Cruz`
     - `Coveñas playa`, `Caribbean beach Colombia boat`, `lancha tour Caribe Colombia`
     - `Colombia Caribbean coast aerial`, `tropical beach turquoise water boat`, `Caribbean sunset sea pier`
   - Conserva el divisor de olas inferior.
2. **Listado:** grilla de tarjetas con filtro por tipo, precio y lugar (filtros con Alpine; opcional htmx para resultados sin recarga).
3. **Detalle:** galería de imágenes (lightbox), video embebido, descripción, precio + unidad, ubicación, capacidad, y CTA de WhatsApp con mensaje prellenado.

### Interactividad (Alpine.js)
- Hero fotográfico rotativo del home (cross-fade automático con intervalo configurable, efecto Ken Burns sutil, pausa al hover, respeta `prefers-reduced-motion`).
- Menú móvil, lightbox/carrusel de galería, filtros reactivos, botón flotante de WhatsApp.
- Mantén el JS propio mínimo y en `static/js/`.

## Plan de implementación por fases

1. Inicializar proyecto con `uv`, instalar dependencias, crear proyecto y apps Django.
2. Configurar `settings` (Unfold, apps, static, templates, SQLite) y `urls`.
3. Definir modelos + migraciones.
4. Configurar admin Unfold con inlines y branding.
5. Integrar Tailwind (CLI standalone) y `base.html`.
6. Construir templates: home, listado, detalle.
7. Añadir Alpine.js para interacciones.
8. Crear superusuario y datos de prueba (varios hoteles y lanchas con imágenes/videos de ejemplo, y 3–4 `HeroSlide` cuyas imágenes sean fotos de Tolú / Golfo de Morrosquillo de licencia libre, seleccionadas según los criterios del hero).
9. Revisar responsive, accesibilidad y Lighthouse; ajustar.

## Criterios de aceptación

- El sitio corre con `uv run python manage.py runserver` sin errores.
- Crear un servicio en el admin (con imágenes, video, precio, lugar y descripción) lo publica en el front automáticamente.
- Las redes sociales configuradas aparecen en el footer y CTAs.
- El catálogo filtra por tipo, precio y lugar.
- Diseño responsive correcto en móvil y escritorio.
- Migrar a PostgreSQL requiere solo cambiar `DATABASES` (sin tocar modelos ni vistas).

## Comandos de arranque esperados

```bash
uv add django django-unfold
uv run django-admin startproject config .
uv run python manage.py startapp servicios
# ...modelos, migraciones...
uv run python manage.py makemigrations
uv run python manage.py migrate
uv run python manage.py createsuperuser
uv run python manage.py runserver
```

## Entrega

Implementa el proyecto completo y funcional, con datos de prueba (fixtures o script de seed) y un `README.md` con: requisitos, cómo correrlo con uv, cómo administrar contenido desde el panel, y cómo migrar a PostgreSQL.