"""Cuatro caras frontales minimalistas, a escala real.

La idea de las cuatro es la misma: una cara no tiene que cargar con todo.
La caja tiene cinco caras visibles; el frente solo lleva lo que identifica
la casa y el resto se reparte. Lo que las diferencia es cuánto queda y
dónde.
"""
from PIL import Image, ImageDraw, ImageFont
import os

F = "/tmp/claude-0/-home-user-maisonsaldana/ea3b086e-04ac-5a0b-b7d0-5c4540eaa5c0/scratchpad/fuentes"
BODONI, JOST = f"{F}/bodoni-1.ttf", f"{F}/jost-3236.ttf"
SALIDA = os.path.dirname(os.path.abspath(__file__))

PPM = 14
W_MM, H_MM = 54, 90

NEGRO = (16, 14, 12)
ORO = (178, 143, 74)        # foil dorado visto de frente sobre blanco
BLANCO = (255, 255, 255)


def mm(v):
    return int(round(v * PPM))


def ft(ruta, pt):
    return ImageFont.truetype(ruta, max(5, int(round(pt * 0.3528 * PPM))))


def linea(d, y_mm, texto, f, color, track_mm=0.0, x_centro=None):
    """Una línea centrada, con tracking real en milímetros."""
    anchos = [d.textlength(c, font=f) for c in texto]
    tr = track_mm * PPM
    total = sum(anchos) + tr * (len(texto) - 1)
    cx = mm(W_MM / 2 if x_centro is None else x_centro)
    x = cx - total / 2
    for c, a in zip(texto, anchos):
        d.text((x, mm(y_mm) + f.getmetrics()[0]), c, font=f, fill=color, anchor="ls")
        x += a + tr
    return total


def filete(d, y_mm, ancho_mm, color, grosor=1.6):
    x0 = mm((W_MM - ancho_mm) / 2)
    d.rectangle([x0, mm(y_mm), x0 + mm(ancho_mm), mm(y_mm) + grosor], fill=color)


def fleuron(d, cx_mm, cy_mm, alto_mm, color):
    cx, cy, r = mm(cx_mm), mm(cy_mm), mm(alto_mm / 2)
    c = r * 0.17
    d.polygon([(cx, cy - r), (cx + c, cy - c), (cx + r, cy), (cx + c, cy + c),
               (cx, cy + r), (cx - c, cy + c), (cx - r, cy), (cx - c, cy - c)],
              fill=color)


def cara():
    im = Image.new("RGB", (mm(W_MM), mm(H_MM)), BLANCO)
    return im, ImageDraw.Draw(im)


# ======================================================== 1 · EL SILENCIO
def uno():
    im, d = cara()
    linea(d, 31.5, "MAISON", ft(BODONI, 13), NEGRO, 1.05)
    linea(d, 38.5, "SALDANA", ft(BODONI, 13), NEGRO, 1.05)
    return im, "1 · El silencio", [
        "Solo el nombre. Nada más en el frente.",
        "Todo lo demás pasa a los costados y al dorso.",
        "1 tinta. Sin foil."]


# ====================================================== 2 · EL MONOGRAMA
def dos():
    im, d = cara()
    linea(d, 32.0, "MS", ft(BODONI, 29), ORO, 1.2)
    linea(d, 62.0, "MAISON SALDANA", ft(JOST, 4.4), NEGRO, 0.5)
    return im, "2 · El monograma", [
        "La MS que ya usas de icono en la web,",
        "grande y en oro. El nombre, susurrado abajo.",
        "1 tinta + foil oro en el monograma."]


# ===================================================== 3 · LA LÍNEA DE ORO
def tres():
    im, d = cara()
    filete(d, 23.0, 20.0, ORO, 1.8)
    linea(d, 63.0, "MAISON", ft(BODONI, 13), NEGRO, 1.05)
    linea(d, 70.0, "SALDANA", ft(BODONI, 13), NEGRO, 1.05)
    return im, "3 · La línea", [
        "El nombre baja al tercio inferior y arriba",
        "queda el aire, cortado por un filete de oro.",
        "1 tinta + foil oro en el filete."]


# ============================================================ 4 · EL SELLO
def cuatro():
    im, d = cara()
    linea(d, 37.0, "MAISON SALDANA", ft(BODONI, 7.4), NEGRO, 0.5)
    fleuron(d, W_MM / 2, 44.2, 2.1, ORO)
    linea(d, 47.6, "COLLECTION D'INSPIRATIONS", ft(JOST, 3.1), NEGRO, 0.26)
    return im, "4 · El sello", [
        "Todo en un bloque diminuto en el centro,",
        "ahogado en blanco. Letra pequeña, caja grande.",
        "1 tinta + foil oro en el fleurón."]


# ================================================================= lámina
op = [uno(), dos(), tres(), cuatro()]
MG, HU, PIE = mm(16), mm(18), mm(30)
Wl = MG * 2 + mm(W_MM) * 4 + HU * 3
Hl = MG + mm(9) + mm(H_MM) + PIE
lam = Image.new("RGB", (Wl, Hl), (249, 249, 248))
d = ImageDraw.Draw(lam)
f_t = ImageFont.truetype(JOST, mm(3.1))
f_p = ImageFont.truetype(JOST, mm(2.3))

for i, (im, nombre, notas) in enumerate(op):
    x = MG + i * (mm(W_MM) + HU)
    y = MG + mm(9)
    d.text((x, MG), nombre, font=f_t, fill=(28, 26, 22))
    lam.paste(im, (x, y))
    d.rectangle([x - 1, y - 1, x + mm(W_MM), y + mm(H_MM)], outline=(206, 201, 194))
    for k, n in enumerate(notas):
        d.text((x, y + mm(H_MM) + mm(4.5 + k * 3.6)), n, font=f_p,
               fill=(110, 104, 96) if k < 2 else (160, 153, 144))

d.text((MG, Hl - mm(7)),
       f"Cara frontal de {W_MM} × {H_MM} mm, a escala real  ·  Bodoni Moda y Jost, las de la casa",
       font=f_p, fill=(160, 153, 144))
lam.save(f"{SALIDA}/minimal.png")
print("lámina:", lam.size, "=", round(Wl / PPM), "×", round(Hl / PPM), "mm")
