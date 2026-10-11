"""Dibuja a escala real las tres caras frontales propuestas para la caja.

No es arte final ni una imagen generada: es un plano, dibujado con las
tipografías de la casa y con las medidas en milímetros, para poder
elegir viendo en vez de imaginando.
"""
from PIL import Image, ImageDraw, ImageFont
import os

F = "/tmp/claude-0/-home-user-maisonsaldana/ea3b086e-04ac-5a0b-b7d0-5c4540eaa5c0/scratchpad/fuentes"
BODONI = f"{F}/bodoni-1.ttf"
JOST = f"{F}/jost-3236.ttf"
SALIDA = os.path.dirname(os.path.abspath(__file__))

PPM = 12                    # píxeles por milímetro (300 ppp ≈ 11,8)
CARA_MM = 54                # ancho de la cara frontal
ALTO_MM = 90                # alto de la caja

NEGRO = (16, 14, 12)
ORO = (169, 132, 60)        # el --oro del sitio
ORO_FOIL = (186, 152, 84)   # cómo se ve un foil dorado sobre blanco, de frente
BLANCO = (255, 255, 255)
MARFIL = (246, 241, 233)    # el --papel del sitio
GRIS_SECO = (232, 228, 222)  # relieve seco: no hay tinta, solo sombra


def mm(v):
    return int(round(v * PPM))


def fuente(ruta, pt):
    # 1 pt = 0,3528 mm
    return ImageFont.truetype(ruta, max(4, int(round(pt * 0.3528 * PPM))))


def fleuron(d, cx_mm, cy_mm, alto_mm, color):
    """Una estrella de cuatro puntas, dibujada: ninguna de las dos
    tipografías de la casa trae ese glifo y salía un cuadrito."""
    cx, cy, r = mm(cx_mm), mm(cy_mm), mm(alto_mm / 2)
    c = r * 0.17                      # cintura; cuanto menor, más afilada
    d.polygon([(cx, cy - r), (cx + c, cy - c), (cx + r, cy),
               (cx + c, cy + c), (cx, cy + r), (cx - c, cy + c),
               (cx - r, cy), (cx - c, cy - c)], fill=color)


def centrado(d, y_mm, texto, f, color, tracking_mm=0.0):
    """Dibuja centrado en la cara, con tracking en mm entre letras."""
    anchos = [d.textlength(c, font=f) for c in texto]
    tr = tracking_mm * PPM
    total = sum(anchos) + tr * (len(texto) - 1)
    x = (mm(CARA_MM) - total) / 2
    for c, a in zip(texto, anchos):
        d.text((x, mm(y_mm)), c, font=f, fill=color, anchor="lt")
        x += a + tr
    return total


def cara(fondo):
    im = Image.new("RGB", (mm(CARA_MM), mm(ALTO_MM)), fondo)
    return im, ImageDraw.Draw(im)


# ---------------------------------------------------------------- A
def concepto_a():
    """NEGRO SOBRE BLANCO. Un oro mínimo, solo en el fleurón."""
    im, d = cara(BLANCO)
    centrado(d, 30.0, "MAISON", fuente(BODONI, 15), NEGRO, 0.9)
    centrado(d, 37.5, "SALDANA", fuente(BODONI, 15), NEGRO, 0.9)
    # fleurón de oro, el único acento de la cara
    fleuron(d, CARA_MM / 2, 50.2, 3.4, ORO_FOIL)
    centrado(d, 57.0, "COLLECTION D'INSPIRATIONS", fuente(JOST, 5), NEGRO, 0.52)
    centrado(d, 70.0, "EAU DE PARFUM", fuente(JOST, 4.6), NEGRO, 0.45)
    centrado(d, 75.5, "60 ML", fuente(JOST, 4.6), NEGRO, 0.45)
    return im, "A · Negro sobre blanco", "1 tinta + foil oro en el fleurón"


# ---------------------------------------------------------------- B
def concepto_b():
    """TODO EN ORO. Lo que pediste como alternativa, para que lo veas."""
    im, d = cara(BLANCO)
    centrado(d, 30.0, "MAISON", fuente(BODONI, 15), ORO_FOIL, 0.9)
    centrado(d, 37.5, "SALDANA", fuente(BODONI, 15), ORO_FOIL, 0.9)
    fleuron(d, CARA_MM / 2, 50.2, 3.4, ORO_FOIL)
    centrado(d, 57.0, "COLLECTION D'INSPIRATIONS", fuente(JOST, 5), ORO_FOIL, 0.52)
    centrado(d, 70.0, "EAU DE PARFUM", fuente(JOST, 4.6), ORO_FOIL, 0.45)
    centrado(d, 75.5, "60 ML", fuente(JOST, 4.6), ORO_FOIL, 0.45)
    return im, "B · Todo en oro", "foil oro en todo el texto"


# ---------------------------------------------------------------- C
def concepto_c():
    """MARFIL, RELIEVE SECO Y UN FILETE DE ORO. El silencioso."""
    im, d = cara(MARFIL)
    # filete de oro arriba, a 14 mm
    d.rectangle([mm(16), mm(14), mm(CARA_MM - 16), mm(14) + 2], fill=ORO_FOIL)
    # Relieve seco: no lleva tinta. Lo que se ve es el canto del
    # hundido —una sombra abajo y una luz arriba—, así que se dibuja
    # dos veces desplazado y no como texto gris plano.
    for dy, col in ((0.22, (214, 208, 199)), (-0.18, (255, 254, 251))):
        for y0, txt in ((31.0, "MAISON"), (38.5, "SALDANA")):
            centrado(d, y0 + dy, txt, fuente(BODONI, 15), col, 0.9)
    centrado(d, 56.0, "COLLECTION D'INSPIRATIONS", fuente(JOST, 5), NEGRO, 0.52)
    centrado(d, 70.0, "EAU DE PARFUM", fuente(JOST, 4.6), NEGRO, 0.45)
    centrado(d, 75.5, "60 ML", fuente(JOST, 4.6), NEGRO, 0.45)
    return im, "C · Marfil y relieve seco", "1 tinta + relieve seco + filete de oro"


# ---------------------------------------------------------------- lámina
conceptos = [concepto_a(), concepto_b(), concepto_c()]

MARGEN, HUECO, PIE = mm(14), mm(16), mm(26)
W = MARGEN * 2 + mm(CARA_MM) * 3 + HUECO * 2
H = MARGEN + mm(10) + mm(ALTO_MM) + PIE
lam = Image.new("RGB", (W, H), (248, 248, 247))
d = ImageDraw.Draw(lam)
tit = ImageFont.truetype(JOST, mm(3.2))
pie = ImageFont.truetype(JOST, mm(2.5))

for i, (im, nombre, nota) in enumerate(conceptos):
    x = MARGEN + i * (mm(CARA_MM) + HUECO)
    y = MARGEN + mm(10)
    d.text((x, MARGEN + mm(1)), nombre, font=tit, fill=(30, 28, 24))
    lam.paste(im, (x, y))
    d.rectangle([x - 1, y - 1, x + mm(CARA_MM), y + mm(ALTO_MM)], outline=(205, 200, 193))
    d.text((x, y + mm(ALTO_MM) + mm(4)), nota, font=pie, fill=(120, 114, 104))
    d.text((x, y + mm(ALTO_MM) + mm(9)),
           f"cara de {CARA_MM} × {ALTO_MM} mm", font=pie, fill=(150, 144, 134))

d.text((MARGEN, H - mm(9)),
       "Plano a escala real · medidas PROPUESTAS, a confirmar midiendo el frasco",
       font=pie, fill=(150, 144, 134))

lam.save(f"{SALIDA}/tres-conceptos.png")
print("lámina:", lam.size, "px  =", round(W / PPM), "x", round(H / PPM), "mm a escala real")
