"""La estría, gofrada de verdad: geometría viable y cómo se ve.

Lo dibujado antes iba a 1,9 mm de paso con cresta de 0,34 mm. Eso se
imprime pero NO se gofra: por debajo de 0,8 mm el latón del troquel no
sostiene la cresta y la fibra del cartón se parte. La geometría que sí
aguanta es 2,2 de paso con 1,0 de cresta: 25 estrías en la cara, que es
prácticamente lo mismo que se veía.

Una estría gofrada en cartulina blanca no se ve por su color —no lleva
tinta— sino por la sombra del canto. Por eso aquí se dibuja la sombra
del valle y no una raya gris.
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
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
PASO, CRESTA, HONDO = 2.2, 1.0, 0.18      # mm, mm, mm
VENTANA = (4.0, 25.0, W - 4.0, 63.0)      # zona plana donde va el texto


def mm(v):
    return int(round(v * PPM))


def ft(r, pt):
    return ImageFont.truetype(r, max(5, int(round(pt * 0.3528 * PPM))))


def cara_gofrada():
    """La cara con la estría en relieve seco, iluminada desde la izquierda."""
    alto, ancho = mm(H), mm(W)
    luz = np.full((alto, ancho), 255.0)

    # Cada paso lleva una cresta y un valle. Lo que se ve en papel blanco
    # sin tinta es el canto: la pared que da la espalda a la luz se
    # oscurece, la que la recibe se queda en blanco del papel.
    x = 0.0
    while x < W:
        v0, v1 = x + CRESTA, x + PASO            # el valle
        c0, c1 = mm(v0), min(mm(v1), ancho)   # el último valle se sale de la cara
        if c1 > c0:
            tira = np.linspace(0, 1, c1 - c0)
            # sombra fuerte pegada a la pared de la izquierda del valle,
            # que es la que queda a contraluz, y se desvanece hacia la otra
            sombra = np.exp(-((tira - 0.18) ** 2) / 0.055) * 26
            luz[:, c0:c1] -= sombra[None, :]
            # un filo claro en la arista de la cresta, donde pega la luz
            a0 = max(0, c0 - max(1, int(0.12 * PPM)))
            luz[:, a0:c0] += 6
        x += PASO

    # La ventana plana: ahí el troquel no toca, para que el texto se
    # imprima sobre liso y se lea. Un canto suave la separa.
    x0, y0, x1, y1 = (mm(VENTANA[0]), mm(VENTANA[1]), mm(VENTANA[2]), mm(VENTANA[3]))
    plano = np.full_like(luz, 255.0)
    mascara = np.zeros_like(luz)
    mascara[y0:y1, x0:x1] = 1.0
    mascara = np.asarray(
        Image.fromarray((mascara * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(mm(0.5)))
    ) / 255.0
    luz = luz * (1 - mascara) + plano * mascara

    im = Image.fromarray(np.clip(luz, 0, 255).astype(np.uint8)).convert("RGB")
    d = ImageDraw.Draw(im)

    # la pila, con los helpers de denso.py reescalados a este PPM
    guarda = denso.PPM
    denso.PPM = PPM
    denso.pila(d, 29.0)
    denso.PPM = guarda
    return im


def cara_dibujada():
    """La misma, con la estría impresa en gris: lo que había antes."""
    im = Image.new("RGB", (mm(W), mm(H)), (255, 255, 255))
    d = ImageDraw.Draw(im)
    x = PASO / 2
    while x < W:
        d.rectangle([mm(x), 0, mm(x) + max(1, int(0.34 * PPM)), mm(H)], fill=(238, 236, 232))
        x += PASO
    d.rectangle([mm(VENTANA[0]), mm(VENTANA[1]), mm(VENTANA[2]), mm(VENTANA[3])],
                fill=(255, 255, 255))
    guarda = denso.PPM
    denso.PPM = PPM
    denso.pila(d, 29.0)
    denso.PPM = guarda
    return im


def seccion(ancho_mm=70, alto_mm=26):
    """Corte transversal del cartón, ampliado nueve veces."""
    ESC = 9
    an, al = mm(ancho_mm), mm(alto_mm)
    im = Image.new("RGB", (an, al), (250, 250, 249))
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype(JOST, mm(2.0))

    base = al - mm(9)
    calibre = 0.42 * ESC
    prof = HONDO * ESC
    techo = base - mm(calibre)

    pts, x = [], 6.0
    while x < ancho_mm - 1:
        for xx, yy in ((x, 0), (x + CRESTA * ESC / 3, 0),
                       (x + CRESTA * ESC / 3 + 0.9, prof),
                       (x + PASO * ESC / 3 - 0.9, prof),
                       (x + PASO * ESC / 3, 0)):
            pts.append((mm(xx), techo + mm(yy)))
        x += PASO * ESC / 3
    d.line(pts, fill=(70, 66, 60), width=3, joint="curve")
    d.line([(mm(6), base), (mm(ancho_mm - 1), base)], fill=(70, 66, 60), width=3)

    # cota del paso, sobre las dos primeras crestas
    p = PASO * ESC / 3
    d.line([(mm(6), techo - mm(4)), (mm(6 + p), techo - mm(4))], fill=(196, 150, 150), width=2)
    for xa in (6, 6 + p):
        d.line([(mm(xa), techo - mm(5)), (mm(xa), techo - mm(3))], fill=(196, 150, 150), width=2)
    d.text((mm(6 + p / 2), techo - mm(6)), f"paso {PASO} mm", font=f,
           fill=(150, 144, 134), anchor="mb")

    d.text((mm(ancho_mm - 1), base + mm(2)),
           f"calibre 0,42 mm  ·  cresta {CRESTA} mm  ·  valle {round(PASO - CRESTA, 1)} mm"
           f"  ·  hondo {HONDO} mm", font=f, fill=(150, 144, 134), anchor="rt")
    d.text((mm(1.5), base + mm(2)), "× 9", font=f, fill=(150, 144, 134))
    return im


def detalle(im, x_mm, y_mm, lado_mm=11, aumento=4):
    """Un trozo de la cara, ampliado, que es donde se nota la diferencia."""
    c = im.crop((mm(x_mm), mm(y_mm), mm(x_mm + lado_mm), mm(y_mm + lado_mm)))
    return c.resize((mm(lado_mm * aumento), mm(lado_mm * aumento)), Image.LANCZOS)


# ================================================================= lámina
gof, dib = cara_gofrada(), cara_dibujada()
sec = seccion()
LADO, AUM = 11, 4
det_d, det_g = detalle(dib, 6, 68, LADO, AUM), detalle(gof, 6, 68, LADO, AUM)

MG, HU = mm(14), mm(15)
col2 = MG + mm(W) * 2 + HU * 2
Wl = col2 + mm(LADO * AUM) * 2 + HU + MG
Hl = MG * 2 + mm(H) + mm(26)
lam = Image.new("RGB", (Wl, Hl), (250, 250, 249))
d = ImageDraw.Draw(lam)
f_t = ImageFont.truetype(JOST, mm(2.9))
f_p = ImageFont.truetype(JOST, mm(2.1))

for i, (im, tit, nota) in enumerate((
        (dib, "Dibujada", "Una raya gris impresa. Se ve, no se siente."),
        (gof, "Gofrada", "Sin tinta. Lo que se ve es la sombra del canto."))):
    x = MG + i * (mm(W) + HU)
    y = MG + mm(7)
    d.text((x, MG), tit, font=f_t, fill=(28, 26, 22))
    lam.paste(im, (x, y))
    d.rectangle([x - 1, y - 1, x + mm(W), y + mm(H)], outline=(208, 203, 196))
    d.text((x, y + mm(H) + mm(4)), nota, font=f_p, fill=(108, 102, 94))

d.text((col2, MG), f"El mismo trozo, × {AUM}", font=f_t, fill=(28, 26, 22))
for i, (im, tit) in enumerate(((det_d, "dibujada"), (det_g, "gofrada"))):
    x = col2 + i * (mm(LADO * AUM) + HU)
    lam.paste(im, (x, MG + mm(7)))
    d.rectangle([x - 1, MG + mm(7) - 1, x + mm(LADO * AUM), MG + mm(7) + mm(LADO * AUM)],
                outline=(208, 203, 196))
    d.text((x, MG + mm(7) + mm(LADO * AUM) + mm(3)), tit, font=f_p, fill=(108, 102, 94))

ys = MG + mm(7) + mm(LADO * AUM) + mm(11)
lam.paste(sec, (col2, ys))

for k2, txt in enumerate([
        "Relieve seco (gofrado) con troquel de latón. Sin tinta y",
        "sin barniz: el relieve es el propio cartón empujado.",
        "",
        f"{PASO} mm de paso = 25 estrías en la cara de 54 mm.",
        "A 1,9 mm NO se puede: por debajo de 0,8 mm de cresta",
        "el latón no aguanta y la fibra del cartón se parte.",
        "",
        "La ventana del texto va PLANA. El troquel no la toca,",
        "para que la letra se imprima sobre liso y se lea."]):
    d.text((col2, ys + mm(30 + k2 * 3.8)), txt, font=f_p, fill=(108, 102, 94))

lam.save(f"{SALIDA}/relieve.png")
gof.save(f"{SALIDA}/frente-a-estria-gofrada.png")
print("relieve:", lam.size, "=", round(Wl / PPM), "×", round(Hl / PPM), "mm")
print(f"geometría: paso {PASO} · cresta {CRESTA} · valle {round(PASO-CRESTA,1)} · hondo {HONDO} mm")
print(f"estrías en la cara: {54/PASO:.0f}")
