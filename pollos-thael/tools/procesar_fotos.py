#!/usr/bin/env python3
"""
Prepara las fotos de la web: recorta, corrige el color y guarda en WebP.

Este archivo es solo de trabajo — no hace falta subirlo al hosting.

    python3 tools/procesar_fotos.py

Lee de  assets/photos/source/  y escribe en  assets/img/

Las fotos vienen de Openverse (Creative Commons) y son de estudios y
fotógrafos distintos: unas frías, otras verdosas, otras lavadas. Sin
tratarlas, juntas parecen un collage. Lo que hace este script es darles
a todas el mismo tono cálido de horno, para que la página parezca un
solo reportaje y no siete fotos pegadas.

No inventa nada: recorta, ajusta color y comprime. Nada más.
"""

import os
import sys

try:
    from PIL import Image, ImageEnhance, ImageFilter
except ImportError:
    sys.exit("Falta Pillow. Instálalo con:  pip install pillow")

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORIGEN = os.path.join(RAIZ, "assets", "photos", "source")
DESTINO = os.path.join(RAIZ, "assets", "img")

# Cada entrada: de qué archivo sale ("origen"), qué trozo se queda
# ("recorte", en proporción 0–1 del original) y a qué tamaño y forma
# se guarda. Un mismo original puede dar dos imágenes distintas.
FOTOS = {
    "hero": {
        # La pared de pollos dorados en la rustidera: es la portada.
        "origen": "alitas",
        "recorte": (0.00, 0.00, 1.00, 0.72),
        "ancho": 1800, "calidad": 82, "proporcion": 21 / 9,
    },
    "casa": {
        # Banda ancha entre la portada y "La casa".
        "origen": "pollo-asado",
        "recorte": (0.00, 0.18, 1.00, 0.94),
        "ancho": 1800, "calidad": 80, "proporcion": 21 / 9,
    },
    "pollo-horneado": {
        "origen": "pollo-horneado",
        "recorte": (0.02, 0.02, 0.98, 0.98),
        "ancho": 1100, "calidad": 82, "proporcion": 4 / 3,
    },
    "pollo-frito": {
        # arriba del original hay platos y palillos sueltos
        "origen": "pollo-frito",
        "recorte": (0.02, 0.26, 0.98, 1.00),
        "ancho": 1100, "calidad": 82, "proporcion": 4 / 3,
    },
    "alitas": {
        # otro trozo del mismo original que la portada, más cerrado
        "origen": "alitas",
        "recorte": (0.00, 0.30, 0.62, 1.00),
        "ancho": 1100, "calidad": 82, "proporcion": 4 / 3,
    },
    "salmon": {
        "origen": "salmon",
        "recorte": (0.02, 0.06, 0.92, 0.98),
        "ancho": 1100, "calidad": 82, "proporcion": 4 / 3,
    },
}


def recortar(im, caja, proporcion=None):
    """Recorta por proporción y luego ajusta a la relación de aspecto pedida."""
    w, h = im.size
    x0, y0, x1, y1 = caja
    im = im.crop((int(x0 * w), int(y0 * h), int(x1 * w), int(y1 * h)))

    if proporcion:
        w, h = im.size
        actual = w / h
        if actual > proporcion:                 # sobra ancho
            nuevo = int(h * proporcion)
            izq = (w - nuevo) // 2
            im = im.crop((izq, 0, izq + nuevo, h))
        elif actual < proporcion:               # sobra alto
            nuevo = int(w / proporcion)
            arriba = int((h - nuevo) * 0.42)    # un pelín por encima del centro
            im = im.crop((0, arriba, w, arriba + nuevo))
    return im


def tono_horno(im):
    """
    El tono de la casa: cálido, con cuerpo, sin quemar las luces.

    1. Baja el azul y sube ligeramente el rojo — quita el frío de las
       cocinas con fluorescente y los fondos verdes.
    2. Contraste y saturación medidos: apetitoso, no de anuncio chillón.
    3. Viñeta suave para que la mirada caiga en la comida.
    """
    im = im.convert("RGB")
    r, g, b = im.split()

    # curva cálida por canal
    r = r.point(lambda v: min(255, int(v * 1.045 + 4)))
    g = g.point(lambda v: min(255, int(v * 1.005 + 1)))
    b = b.point(lambda v: max(0, int(v * 0.935 - 2)))
    im = Image.merge("RGB", (r, g, b))

    im = ImageEnhance.Color(im).enhance(0.94)      # baja el verde chillón
    im = ImageEnhance.Contrast(im).enhance(1.10)
    im = ImageEnhance.Brightness(im).enhance(1.02)

    # viñeta
    w, h = im.size
    mascara = Image.new("L", (w, h), 0)
    borde = Image.new("L", (int(w * 0.86), int(h * 0.86)), 255)
    mascara.paste(borde, (int(w * 0.07), int(h * 0.07)))
    mascara = mascara.filter(ImageFilter.GaussianBlur(radius=max(w, h) // 9))
    oscura = ImageEnhance.Brightness(im).enhance(0.80)
    im = Image.composite(im, oscura, mascara)

    im = im.filter(ImageFilter.UnsharpMask(radius=1.4, percent=52, threshold=3))
    return im


def main():
    if not os.path.isdir(ORIGEN):
        sys.exit(f"No existe {ORIGEN}")
    os.makedirs(DESTINO, exist_ok=True)

    total = 0
    for nombre, cfg in FOTOS.items():
        origen = None
        base = cfg.get("origen", nombre)
        for ext in ("jpg", "jpeg", "png", "webp"):
            p = os.path.join(ORIGEN, f"{base}.{ext}")
            if os.path.exists(p):
                origen = p
                break
        if not origen:
            print(f"  {nombre:<16} SIN ORIGEN — se salta")
            continue

        im = Image.open(origen)
        antes = im.size
        im = recortar(im, cfg["recorte"], cfg.get("proporcion"))

        if im.width > cfg["ancho"]:
            alto = int(im.height * cfg["ancho"] / im.width)
            im = im.resize((cfg["ancho"], alto), Image.LANCZOS)

        im = tono_horno(im)

        destino = os.path.join(DESTINO, f"{nombre}.webp")
        im.save(destino, "WEBP", quality=cfg["calidad"], method=6)
        kb = os.path.getsize(destino) // 1024
        total += kb
        print(f"  {nombre:<16} {antes[0]}x{antes[1]} → {im.width}x{im.height}  {kb} KB")

    print(f"\n  Total en assets/img/: {total} KB")
    escribir_creditos()


def _arrancar():
    main()


# ---------------------------------------------------------------------------
# Créditos: se escriben directamente dentro de creditos.html.
#
# Se podría cargar assets/credits.json con JavaScript, pero entonces la
# página de créditos saldría vacía al abrirla con doble clic (el navegador
# bloquea la lectura de archivos locales) y la licencia obliga a que la
# atribución se vea siempre. Así que se escribe el HTML tal cual.
# ---------------------------------------------------------------------------

import html as _html
import json as _json
import re as _re

LICENCIAS = {
    "by": "CC BY", "by-sa": "CC BY-SA", "cc0": "CC0", "pdm": "Dominio público",
}


def escribir_creditos():
    ruta_json = os.path.join(RAIZ, "assets", "credits.json")
    ruta_html = os.path.join(RAIZ, "creditos.html")
    if not (os.path.exists(ruta_json) and os.path.exists(ruta_html)):
        print("  (sin créditos que escribir)")
        return

    with open(ruta_json, encoding="utf-8") as f:
        creditos = _json.load(f)

    def e(v):
        return _html.escape(str(v)) if v else ""

    filas = []
    for slot, c in creditos.items():
        nombre = LICENCIAS.get(c.get("license", ""), (c.get("license") or "").upper())
        version = c.get("license_version") or ""
        autor = e(c.get("creator") or "Autor no indicado")
        if c.get("creator_url"):
            autor = f'<a href="{e(c["creator_url"])}" target="_blank" rel="noopener">{autor}</a>'
        licencia = f"{nombre} {version}".strip()
        if c.get("license_url"):
            licencia = f'<a href="{e(c["license_url"])}" target="_blank" rel="noopener">{e(licencia)}</a>'
        else:
            licencia = e(licencia)
        original = ""
        if c.get("foreign_landing_url"):
            original = (f' · <a href="{e(c["foreign_landing_url"])}" target="_blank"'
                        f' rel="noopener">Ver la original ↗</a>')

        filas.append(
            f'      <li class="credito">\n'
            f'        <img class="credito-mini" src="{e(c["src"])}" alt="" loading="lazy" />\n'
            f'        <div>\n'
            f'          <p class="credito-titulo">{e(c.get("title") or slot)}</p>\n'
            f'          <p class="credito-meta">\n'
            f'            {autor} · {licencia} · vía {e(c.get("source") or "Openverse")}{original}\n'
            f'          </p>\n'
            f'        </div>\n'
            f'      </li>'
        )

    with open(ruta_html, encoding="utf-8") as f:
        pagina = f.read()

    bloque = ('<ul class="creditos-lista" data-creditos>\n'
              + "\n".join(filas) + "\n    </ul>")
    pagina = _re.sub(r'<ul class="creditos-lista" data-creditos>.*?</ul>',
                     bloque, pagina, flags=_re.S)

    with open(ruta_html, "w", encoding="utf-8") as f:
        f.write(pagina)
    print(f"  creditos.html: {len(filas)} fotografías atribuidas")


if __name__ == "__main__":
    _arrancar()
