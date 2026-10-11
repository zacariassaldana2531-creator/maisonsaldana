"""Cuatro frentes con cuerpo, y una tira de escala para juzgar el tamaño.

Lo anterior se quedó corto: minimalista y vacío están a un pelo y me
pasé. Aquí la cara se llena, pero no con adorno —nada de marcos
victorianos, coronas ni filigranas— sino con estructura: la pila de
texto de la propia etiqueta del frasco, un filete, y la estría del
vidrio llevada al cartón.

Y la letra baja un 15 % respecto de la ronda anterior: en una caja de
54 mm, lo de antes se leía enorme.
"""
from PIL import Image, ImageDraw, ImageFont
import os

F = "/tmp/claude-0/-home-user-maisonsaldana/ea3b086e-04ac-5a0b-b7d0-5c4540eaa5c0/scratchpad/fuentes"
BODONI, JOST = f"{F}/bodoni-1.ttf", f"{F}/jost-3236.ttf"
SALIDA = os.path.dirname(os.path.abspath(__file__))

PPM = 16
W, H = 54, 90

NEGRO = (16, 14, 12)
ORO = (178, 143, 74)
BLANCO = (255, 255, 255)
ESTRIA = (238, 236, 232)       # la estría va en relieve seco: casi no hay tinta
HILO = (120, 114, 104)


def mm(v):
    return int(round(v * PPM))


def ft(r, pt):
    return ImageFont.truetype(r, max(5, int(round(pt * 0.3528 * PPM))))


def linea(d, y, txt, f, color, track=0.0, ancho=W, x0=0):
    an = [d.textlength(c, font=f) for c in txt]
    tr = track * PPM
    total = sum(an) + tr * (len(txt) - 1)
    x = mm(x0) + mm(ancho) / 2 - total / 2
    asc = f.getmetrics()[0]
    for c, a in zip(txt, an):
        d.text((x, mm(y) + asc), c, font=f, fill=color, anchor="ls")
        x += a + tr
    return total


def filete(d, y, largo, color=NEGRO, g=1.2, cx=W / 2):
    d.rectangle([mm(cx - largo / 2), mm(y), mm(cx + largo / 2), mm(y) + g * PPM / 5],
                fill=color)


def fleuron(d, cx, cy, alto, color):
    X, Y, r = mm(cx), mm(cy), mm(alto / 2)
    c = r * 0.17
    d.polygon([(X, Y - r), (X + c, Y - c), (X + r, Y), (X + c, Y + c),
               (X, Y + r), (X - c, Y + c), (X - r, Y), (X - c, Y - c)], fill=color)


def pila(d, y0, ancho=W, x0=0, esc=1.0):
    """La pila de la etiqueta del frasco: nombre, fleurón, colección,
    concentración y volumen. Es lo que ya lleva el frasco; repetirla en
    la caja hace que las dos piezas se lean como una sola."""
    linea(d, y0, "MAISON SALDANA", ft(BODONI, 8.2 * esc), NEGRO, 0.40 * esc, ancho, x0)
    y = y0 + 7.6 * esc
    cx = x0 + ancho / 2
    # Dos tramos con un hueco en medio para el fleurón. Estaban los dos
    # tramos Y un filete entero por detrás, y el filete entero cruzaba
    # el fleurón de lado a lado.
    for a, b in ((-13, -4.2), (4.2, 13)):
        d.rectangle([mm(cx + a * esc), mm(y),
                     mm(cx + b * esc), mm(y) + 2], fill=HILO)
    fleuron(d, cx, y, 2.1 * esc, ORO)
    linea(d, y0 + 11.0 * esc, "COLLECTION D'INSPIRATIONS",
          ft(JOST, 2.9 * esc), NEGRO, 0.22 * esc, ancho, x0)
    filete(d, y0 + 16.6 * esc, 16 * esc, HILO, cx=x0 + ancho / 2)
    linea(d, y0 + 19.0 * esc, "EAU DE PARFUM", ft(JOST, 3.1 * esc), NEGRO, 0.26 * esc, ancho, x0)
    filete(d, y0 + 24.6 * esc, 16 * esc, HILO, cx=x0 + ancho / 2)
    linea(d, y0 + 27.0 * esc, "60 ML", ft(BODONI, 4.6 * esc), NEGRO, 0.24 * esc, ancho, x0)
    return y0 + 31.5 * esc


def cara():
    im = Image.new("RGB", (mm(W), mm(H)), BLANCO)
    return im, ImageDraw.Draw(im)


# =========================================================== A · LA ESTRÍA
def a_estria():
    im, d = cara()
    paso, grosor = 1.9, 0.34
    x = paso / 2
    while x < W:
        d.rectangle([mm(x), 0, mm(x) + max(1, int(grosor * PPM)), mm(H)], fill=ESTRIA)
        x += paso
    # ventana limpia donde se apoya el texto, como el vidrio liso bajo la etiqueta
    d.rectangle([mm(4), mm(25), mm(W - 4), mm(63)], fill=BLANCO)
    pila(d, 29.0)
    return im, "A · La estría", [
        "La estría del vidrio llevada al cartón, en relieve seco.",
        "Llena la cara entera sin una gota de tinta de más.",
        "1 tinta + relieve seco + foil en el fleurón."]


# ========================================================= B · LA ETIQUETA
def b_etiqueta():
    im, d = cara()
    x0, x1, y0, y1 = 7.5, W - 7.5, 22.0, 68.0
    d.rectangle([mm(x0), mm(y0), mm(x1), mm(y1)], outline=NEGRO, width=max(2, int(0.5 * PPM)))
    d.rectangle([mm(x0 + 1.6), mm(y0 + 1.6), mm(x1 - 1.6), mm(y1 - 1.6)],
                outline=NEGRO, width=max(1, int(0.18 * PPM)))
    pila(d, 31.0, ancho=x1 - x0, x0=x0, esc=0.92)
    return im, "B · La etiqueta", [
        "La misma etiqueta del frasco, ampliada en la caja.",
        "Frasco y caja se leen como una sola pieza.",
        "1 tinta + foil en el fleurón."]


# ============================================================ C · EL MARCO
def c_marco():
    im, d = cara()
    # A 4,5 mm del canto se metía dentro del margen de seguridad,
    # que en esta caja es de 4 mm. Se aparta a 6,5.
    d.rectangle([mm(6.5), mm(6.5), mm(W - 6.5), mm(H - 6.5)],
                outline=NEGRO, width=max(1, int(0.22 * PPM)))
    pila(d, 29.0, esc=0.96)
    linea(d, 78.0, "SANTO DOMINGO", ft(JOST, 2.5), HILO, 0.2)
    return im, "C · El marco", [
        "Un hilo negro recorre el canto y encierra la pila.",
        "Lo que llena no es adorno: es el borde y el aire medido.",
        "1 tinta + foil en el fleurón."]


# =========================================================== D · EL BLOQUE
def d_bloque():
    im, d = cara()
    d.rectangle([0, mm(14), mm(W), mm(15.1)], fill=NEGRO)
    pila(d, 24.0, esc=1.04)
    d.rectangle([0, mm(68), mm(W), mm(69.1)], fill=NEGRO)
    linea(d, 74.0, "SANTO DOMINGO", ft(JOST, 2.6), HILO, 0.22)
    return im, "D · El bloque", [
        "Dos barras cierran la composición arriba y abajo.",
        "Todo el peso en el centro, sin aire sobrante.",
        "1 tinta + foil en el fleurón."]


# ================================================================== lámina
op = [a_estria(), b_etiqueta(), c_marco(), d_bloque()]
MG, HU, PIE = mm(15), mm(17), mm(26)
Wl = MG * 2 + mm(W) * 4 + HU * 3
Hl = MG + mm(8) + mm(H) + PIE
lam = Image.new("RGB", (Wl, Hl), (250, 250, 249))
dd = ImageDraw.Draw(lam)
f_t = ImageFont.truetype(JOST, mm(2.9))
f_p = ImageFont.truetype(JOST, mm(2.1))

for i, (im, nombre, notas) in enumerate(op):
    x = MG + i * (mm(W) + HU)
    y = MG + mm(8)
    dd.text((x, MG), nombre, font=f_t, fill=(28, 26, 22))
    lam.paste(im, (x, y))
    dd.rectangle([x - 1, y - 1, x + mm(W), y + mm(H)], outline=(208, 203, 196))
    for k, n in enumerate(notas):
        dd.text((x, y + mm(H) + mm(4 + k * 3.2)), n, font=f_p,
                fill=(108, 102, 94) if k < 2 else (158, 151, 142))

dd.text((MG, Hl - mm(6)),
        f"Cara de {W} × {H} mm, a escala real  ·  la letra baja un 15 % respecto de la ronda anterior",
        font=f_p, fill=(158, 151, 142))
lam.save(f"{SALIDA}/denso.png")
for fn, slug in ((a_estria, "a-la-estria"), (b_etiqueta, "b-la-etiqueta"),
                 (c_marco, "c-el-marco"), (d_bloque, "d-el-bloque")):
    fn()[0].save(f"{SALIDA}/frente-{slug}.png")
print("lámina:", lam.size, "=", round(Wl / PPM), "×", round(Hl / PPM), "mm")
