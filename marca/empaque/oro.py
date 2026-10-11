"""La estría en oro: foil y relieve a la vez, y cuánto oro es demasiado.

Pedir la estría dorada no es pedir otro color: es cambiar de técnica.
El relieve seco no lleva nada encima; el oro es una lámina que se
estampa en caliente. Las dos cosas juntas se hacen con un TROQUEL
COMBINADO, que estampa y hunde en la misma pasada.

Aquí se dibujan tres repartos de oro para poder elegir con los ojos,
y las dos calidades de lámina —mate y brillante— que es la decisión
que de verdad cambia si la caja parece una casa de perfume o un papel
de regalo.
"""
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import importlib.util
import sys
import os

F = "/tmp/claude-0/-home-user-maisonsaldana/ea3b086e-04ac-5a0b-b7d0-5c4540eaa5c0/scratchpad/fuentes"
BODONI, JOST = f"{F}/bodoni-1.ttf", f"{F}/jost-3236.ttf"
SALIDA = os.path.dirname(os.path.abspath(__file__))

spec = importlib.util.spec_from_file_location("denso", f"{SALIDA}/denso.py")
denso = importlib.util.module_from_spec(spec)
sys.modules["denso"] = denso
spec.loader.exec_module(denso)

PPM = 20
W, H = 54, 90
PASO, CRESTA = 2.2, 1.0
VENTANA = (4.0, 25.0, W - 4.0, 63.0)

# Un foil no es un color plano: es metal, y lo que se ve es el reflejo
# cruzando la cresta. Por eso cada estría se pinta con un degradado,
# no con un relleno.
ORO_MATE = ((198, 170, 112), (146, 117, 64), (176, 146, 92))   # luz, sombra, medio
ORO_BRILLO = ((248, 232, 176), (134, 98, 36), (214, 178, 96))


def mm(v):
    return int(round(v * PPM))


def ft(r, pt):
    return ImageFont.truetype(r, max(5, int(round(pt * 0.3528 * PPM))))


def cara(paleta=ORO_MATE, oro=True, ventana=True):
    luz, sombra, medio = paleta
    alto, ancho = mm(H), mm(W)
    lienzo = np.full((alto, ancho, 3), 255.0)

    x = 0.0
    while x < W:
        c0, c1 = mm(x), min(mm(x + CRESTA), ancho)
        if c1 > c0:
            t = np.linspace(0, 1, c1 - c0)
            if oro:
                # reflejo metálico cruzando la cresta: claro donde pega la
                # luz, oscuro en el canto opuesto
                mezcla = np.empty((c1 - c0, 3))
                for k in range(3):
                    mezcla[:, k] = np.interp(t, [0, 0.28, 0.62, 1.0],
                                             [sombra[k], luz[k], medio[k], sombra[k]])
                lienzo[:, c0:c1] = mezcla[None, :, :]
            else:
                lienzo[:, c0:c1] = 255.0
        # el valle: papel blanco con la sombra del canto
        v0, v1 = mm(x + CRESTA), min(mm(x + PASO), ancho)
        if v1 > v0:
            t = np.linspace(0, 1, v1 - v0)
            lienzo[:, v0:v1] -= (np.exp(-((t - 0.2) ** 2) / 0.05) * 22)[None, :, None]
        x += PASO

    if ventana:
        x0, y0, x1, y1 = (mm(VENTANA[0]), mm(VENTANA[1]), mm(VENTANA[2]), mm(VENTANA[3]))
        lienzo[y0:y1, x0:x1] = 255.0

    im = Image.fromarray(np.clip(lienzo, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(im)
    guarda = denso.PPM
    denso.PPM = PPM
    denso.pila(d, 29.0)
    denso.PPM = guarda
    return im


def media_cara(paleta):
    """Oro solo en el tercio de arriba y el de abajo; el centro, en blanco."""
    im = cara(paleta)
    blanco = cara(paleta, oro=False)
    a, b = np.asarray(im).astype(float), np.asarray(blanco).astype(float)
    a[mm(22):mm(66)] = b[mm(22):mm(66)]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def detalle(im, x_mm=6, y_mm=70, lado=10, aum=5):
    c = im.crop((mm(x_mm), mm(y_mm), mm(x_mm + lado), mm(y_mm + lado)))
    return c.resize((mm(lado * aum), mm(lado * aum)), Image.LANCZOS)


# ================================================================= lámina
op = [
    (cara(ORO_MATE), "1 · Oro mate, estría completa",
     ["Lo que pediste. Troquel combinado: estampa y hunde",
      "en la misma pasada, así que el oro cae clavado en la cresta.",
      "46 % de la cara cubierta de lámina."]),
    (cara(ORO_BRILLO), "2 · Oro brillante",
     ["La misma estría con lámina brillante en vez de mate.",
      "Mírala al lado de la otra: aquí está la decisión.",
      "Mismo coste, resultado muy distinto."]),
    (media_cara(ORO_MATE), "3 · Oro mate, solo arriba y abajo",
     ["El oro enmarca y el centro respira.",
      "La mitad de lámina y la mitad de riesgo.",
      "23 % de la cara cubierta."]),
]

MG, HU = mm(14), mm(16)
LADO, AUM = 10, 5
Wl = MG * 2 + mm(W) * 3 + HU * 2 + mm(LADO * AUM) + HU
Hl = MG * 2 + mm(H) + mm(22)
lam = Image.new("RGB", (Wl, Hl), (250, 250, 249))
d = ImageDraw.Draw(lam)
f_t = ImageFont.truetype(JOST, mm(2.9))
f_p = ImageFont.truetype(JOST, mm(2.1))

for i, (im, tit, notas) in enumerate(op):
    x = MG + i * (mm(W) + HU)
    y = MG + mm(7)
    d.text((x, MG), tit, font=f_t, fill=(28, 26, 22))
    lam.paste(im, (x, y))
    d.rectangle([x - 1, y - 1, x + mm(W), y + mm(H)], outline=(208, 203, 196))
    for k, n in enumerate(notas):
        d.text((x, y + mm(H) + mm(4 + k * 3.4)), n, font=f_p,
               fill=(108, 102, 94) if k < 2 else (158, 151, 142))

cx = MG + 3 * (mm(W) + HU)
d.text((cx, MG), f"Mate y brillante, × {AUM}", font=f_t, fill=(28, 26, 22))
lam.paste(detalle(op[0][0], lado=LADO, aum=AUM), (cx, MG + mm(7)))
d.text((cx, MG + mm(7) + mm(LADO * AUM) + mm(3)), "mate", font=f_p, fill=(108, 102, 94))
y2 = MG + mm(7) + mm(LADO * AUM) + mm(9)
lam.paste(detalle(op[1][0], lado=LADO, aum=AUM), (cx, y2))
d.text((cx, y2 + mm(LADO * AUM) + mm(3)), "brillante", font=f_p, fill=(108, 102, 94))

lam.save(f"{SALIDA}/oro.png")
cara(ORO_MATE).save(f"{SALIDA}/frente-a-estria-oro.png")
media_cara(ORO_MATE).save(f"{SALIDA}/frente-a-estria-oro-marco.png")

cobertura = (CRESTA / PASO) * 100
print("oro:", lam.size, "=", round(Wl / PPM), "×", round(Hl / PPM), "mm")
print(f"cobertura de lámina en la cara: {cobertura:.0f} %")
area = 3 * W * H * cobertura / 100
print(f"foil por caja (frente + 2 costados): {area:.0f} mm² = {area/100:.0f} cm²")
