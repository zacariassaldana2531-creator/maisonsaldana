"""La caja a tamaño real, contra cosas cuyo tamaño ya conoces.

El problema de juzgar un empaque en una pantalla es que la pantalla
miente: un PNG de 54 mm se ve de 80 en un teléfono y de 150 en un
portátil. Aquí la caja va contra una tarjeta de crédito —85,6 × 54 mm,
igual en todo el mundo— y contra el frasco. Eso sí se puede juzgar.
"""
from PIL import Image, ImageDraw, ImageFont
import importlib.util
import sys
import os

F = "/tmp/claude-0/-home-user-maisonsaldana/ea3b086e-04ac-5a0b-b7d0-5c4540eaa5c0/scratchpad/fuentes"
JOST = f"{F}/jost-3236.ttf"
SALIDA = os.path.dirname(os.path.abspath(__file__))

spec = importlib.util.spec_from_file_location("denso", f"{SALIDA}/denso.py")
denso = importlib.util.module_from_spec(spec)
sys.modules["denso"] = denso
spec.loader.exec_module(denso)

PPM = 14
CAJA_W, CAJA_H, CAJA_F = 54, 90, 54     # ancho, alto, fondo
TARJ_W, TARJ_H = 85.6, 54               # tarjeta de crédito, medida universal
D_FRASCO, H_FRASCO = 48, 85


def mm(v):
    return int(round(v * PPM))


def ft(pt):
    return ImageFont.truetype(JOST, max(6, int(round(pt * 0.3528 * PPM))))


MG = mm(16)
W = MG * 2 + mm(TARJ_W + 14 + CAJA_W + 14 + CAJA_W * 0.42 + 20 + D_FRASCO)
H = MG * 2 + mm(CAJA_H + 26)
lam = Image.new("RGB", (int(W), int(H)), (250, 250, 249))
d = ImageDraw.Draw(lam)
f_t, f_p = ft(3.1), ft(2.3)
SUELO = MG + mm(CAJA_H)

# ---------- 1. la tarjeta de crédito ------------------------------------
tx = MG
ty = SUELO - mm(TARJ_H)
d.rounded_rectangle([tx, ty, tx + mm(TARJ_W), SUELO], radius=mm(3.2),
                    fill=(243, 241, 237), outline=(206, 201, 194), width=2)
d.text((tx + mm(5), ty + mm(5)), "TARJETA", font=f_p, fill=(170, 164, 155))
d.text((tx, SUELO + mm(5)), "Una tarjeta de crédito", font=f_t, fill=(28, 26, 22))
d.text((tx, SUELO + mm(10)), f"{TARJ_W} × {TARJ_H} mm  ·  igual en todo el mundo",
       font=f_p, fill=(140, 134, 125))

# ---------- 2. la caja cerrada, en perspectiva ligera --------------------
cx = tx + mm(TARJ_W + 14)
cy = MG
frente = denso.b_etiqueta()[0].resize((mm(CAJA_W), mm(CAJA_H)), Image.LANCZOS)
lam.paste(frente, (int(cx), int(cy)))
d.rectangle([cx, cy, cx + mm(CAJA_W), SUELO], outline=(188, 182, 174), width=2)

# el costado, escorzado, para que se lea como una caja y no como un papel
prof = mm(CAJA_F * 0.42)
sesgo = mm(CAJA_F * 0.42) * 0.34
d.polygon([(cx + mm(CAJA_W), cy), (cx + mm(CAJA_W) + prof, cy - sesgo),
           (cx + mm(CAJA_W) + prof, SUELO - sesgo), (cx + mm(CAJA_W), SUELO)],
          fill=(238, 235, 230), outline=(188, 182, 174))
d.polygon([(cx, cy), (cx + prof, cy - sesgo),
           (cx + mm(CAJA_W) + prof, cy - sesgo), (cx + mm(CAJA_W), cy)],
          fill=(248, 246, 243), outline=(188, 182, 174))
d.text((cx, SUELO + mm(5)), "La caja", font=f_t, fill=(28, 26, 22))
d.text((cx, SUELO + mm(10)), f"{CAJA_W} × {CAJA_F} × {CAJA_H} mm",
       font=f_p, fill=(140, 134, 125))

# ---------- 3. el frasco, al lado ---------------------------------------
fx = cx + mm(CAJA_W) + prof + mm(20)
H_TAPA, H_VIDRIO = D_FRASCO * 0.560, D_FRASCO * 1.212
d.rectangle([fx, SUELO - mm(H_VIDRIO), fx + mm(D_FRASCO), SUELO],
            fill=(238, 235, 229), outline=(188, 182, 174), width=2)
tapa_w = D_FRASCO * 0.368
d.rectangle([fx + mm((D_FRASCO - tapa_w) / 2), SUELO - mm(H_VIDRIO + H_TAPA),
             fx + mm((D_FRASCO + tapa_w) / 2), SUELO - mm(H_VIDRIO)],
            fill=(248, 246, 242), outline=(188, 182, 174), width=2)
d.text((fx, SUELO + mm(5)), "El frasco", font=f_t, fill=(28, 26, 22))
d.text((fx, SUELO + mm(10)), f"Ø {D_FRASCO} × {H_FRASCO} mm",
       font=f_p, fill=(140, 134, 125))

d.text((MG, MG - mm(9)),
       "Todo a escala real. Si tu pantalla miente, imprime esta lámina al 100 % y compárala con una tarjeta.",
       font=f_p, fill=(140, 134, 125))

# Recorte al contenido: la lámina salía con medio palmo de blanco
# abajo y a la derecha, que solo confunde al juzgar tamaños.
import numpy as np
ar = np.asarray(lam.convert("L"))
filas = np.nonzero((ar < 244).any(1))[0]
cols = np.nonzero((ar < 244).any(0))[0]
m = mm(10)
lam = lam.crop((max(0, cols.min() - m), max(0, filas.min() - m),
                min(lam.width, cols.max() + m), min(lam.height, filas.max() + m)))
lam.save(f"{SALIDA}/escala.png")
print("escala:", lam.size, "=", round(W / PPM), "×", round(H / PPM), "mm a escala real")
