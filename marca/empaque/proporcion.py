"""El frasco dentro de la caja propuesta, a escala real.

Las medidas del frasco salen de su propia foto: midiendo el diámetro y
la altura en píxeles y suponiendo 48 mm de diámetro, que es el valor
que devuelve 61 ml de volumen interno —el que vende la casa—. Es una
PROPUESTA: hay que confirmarla con una regla.
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np
import os

FOTO = "/home/user/maisonsaldana/originales/frasco-maison-saldana.webp"
JOST = "/tmp/claude-0/-home-user-maisonsaldana/ea3b086e-04ac-5a0b-b7d0-5c4540eaa5c0/scratchpad/fuentes/jost-3236.ttf"
SALIDA = os.path.dirname(os.path.abspath(__file__))

PPM = 10
D_MM = 48.0                 # diámetro supuesto del frasco
CAJA_W, CAJA_H = 54, 90     # caja propuesta
HOLGURA = (CAJA_W - D_MM) / 2

# --- recorte del frasco en la foto, sin la sombra -----------------------
im = Image.open(FOTO).convert("RGB")
a = np.asarray(im).astype(int)
fondo = np.median(a[:40, :40].reshape(-1, 3), axis=0)
obj = np.abs(a - fondo).sum(2) > 34
anchos = np.array([(np.nonzero(obj[y])[0].max() - np.nonzero(obj[y])[0].min() + 1)
                   if obj[y].any() else 0 for y in range(a.shape[0])])
y0 = next(y for y in range(len(anchos)) if anchos[y] > 0)
yc = next(y for y in range(len(anchos)) if anchos[y] > 400)
y1 = next(y for y in range(yc, len(anchos)) if anchos[y] > 520) - 1
fila = np.nonzero(obj[(yc + y1) // 2])[0]
x0, x1 = fila.min(), fila.max()
D_PX = x1 - x0 + 1

frasco = im.crop((x0, y0, x1 + 1, y1 + 1))
escala = (D_MM * PPM) / D_PX
frasco = frasco.resize((int(frasco.width * escala), int(frasco.height * escala)), Image.LANCZOS)
ALTO_FRASCO_MM = frasco.height / PPM

# --- lámina -------------------------------------------------------------
M = 22 * PPM
W = M * 2 + (CAJA_W + 30 + CAJA_W) * PPM
H = M * 2 + (CAJA_H + 22) * PPM
lam = Image.new("RGB", (int(W), int(H)), (250, 250, 249))
d = ImageDraw.Draw(lam)
f_t = ImageFont.truetype(JOST, int(3.4 * PPM))
f_p = ImageFont.truetype(JOST, int(2.6 * PPM))

# 1) el frasco solo
xf = M
yf = M + int((CAJA_H - ALTO_FRASCO_MM) * PPM)
lam.paste(frasco, (int(xf), int(yf)))
d.text((xf, M - int(5 * PPM)), "El frasco", font=f_t, fill=(30, 28, 24))
d.text((xf, M + int((CAJA_H + 4) * PPM)),
       f"Ø {D_MM:.0f} mm  ·  alto {ALTO_FRASCO_MM:.0f} mm con tapa", font=f_p, fill=(120, 114, 104))
d.text((xf, M + int((CAJA_H + 8.5) * PPM)),
       "PROPUESTO — deducido de la foto", font=f_p, fill=(175, 168, 158))

# 2) la caja con el frasco dentro
xc = M + int((CAJA_W + 30) * PPM)
yc2 = M
d.rectangle([xc, yc2, xc + CAJA_W * PPM, yc2 + CAJA_H * PPM],
            fill=(255, 255, 255), outline=(190, 184, 176), width=2)
# el frasco, centrado dentro
fx = xc + int(HOLGURA * PPM)
fy = yc2 + int((CAJA_H - ALTO_FRASCO_MM) * PPM / 2)
# El frasco dentro va como dibujo técnico, no como foto recortada:
# el vidrio es casi del color del fondo y cualquier silueta sacada de
# la foto sale sucia. Las proporciones son las medidas arriba.
D_PROP = D_MM
H_TAPA = D_MM * 0.560
H_VIDRIO = D_MM * 1.212
cx = xc + CAJA_W * PPM / 2
base = fy + ALTO_FRASCO_MM * PPM
GRIS, CANTO = (222, 218, 211), (176, 170, 161)
d.rectangle([cx - D_PROP * PPM / 2, base - H_VIDRIO * PPM,
             cx + D_PROP * PPM / 2, base], fill=GRIS, outline=CANTO, width=2)
d.rectangle([cx - D_PROP * 0.184 * PPM, base - (H_VIDRIO + H_TAPA) * PPM,
             cx + D_PROP * 0.184 * PPM, base - H_VIDRIO * PPM],
            fill=(238, 235, 230), outline=CANTO, width=2)
# cotas
d.line([xc, yc2 - int(2.5 * PPM), xc + CAJA_W * PPM, yc2 - int(2.5 * PPM)],
       fill=(170, 164, 154), width=2)
d.text((xc + CAJA_W * PPM / 2, yc2 - int(6.5 * PPM)), f"{CAJA_W} mm",
       font=f_p, fill=(120, 114, 104), anchor="mt")
d.line([xc + (CAJA_W + 3) * PPM, yc2, xc + (CAJA_W + 3) * PPM, yc2 + CAJA_H * PPM],
       fill=(170, 164, 154), width=2)
d.text((xc + (CAJA_W + 5) * PPM, yc2 + CAJA_H * PPM / 2), f"{CAJA_H} mm",
       font=f_p, fill=(120, 114, 104), anchor="lm")
d.text((xc, M - int(5 * PPM)), "Dentro de la caja propuesta", font=f_t, fill=(30, 28, 24))
d.text((xc, M + int((CAJA_H + 4) * PPM)),
       f"{HOLGURA:.0f} mm de holgura a cada lado: lo que ocupa la cuna de cartón",
       font=f_p, fill=(120, 114, 104))
d.text((xc, M + int((CAJA_H + 8.5) * PPM)),
       f"{CAJA_H - ALTO_FRASCO_MM:.0f} mm de aire arriba y abajo repartidos",
       font=f_p, fill=(120, 114, 104))

lam.save(f"{SALIDA}/proporcion.png")
print(f"frasco deducido: Ø {D_MM:.0f} mm × {ALTO_FRASCO_MM:.1f} mm de alto con tapa")
print(f"caja propuesta : {CAJA_W} × {CAJA_W} × {CAJA_H} mm internos")
print("lámina:", lam.size)
