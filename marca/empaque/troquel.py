"""Plano de troquel de la caja, a escala, con el arte repartido.

Estuche plegadizo de solapas metidas (tuck-end), que es lo que hace
cualquier imprenta de Santo Domingo en tirada corta. Línea continua =
corte. Línea de puntos = hendido, por donde dobla.

Esto es un PLANO para decidir y para enseñárselo al impresor. El arte
final se reconstruye en vectorial.
"""
from PIL import Image, ImageDraw, ImageFont
import os

F = "/tmp/claude-0/-home-user-maisonsaldana/ea3b086e-04ac-5a0b-b7d0-5c4540eaa5c0/scratchpad/fuentes"
BODONI, JOST = f"{F}/bodoni-1.ttf", f"{F}/jost-3236.ttf"
QR = "/home/user/maisonsaldana/marca/qr-maison-saldana.png"
SALIDA = os.path.dirname(os.path.abspath(__file__))

PPM = 9
A, H = 54, 90              # ancho de cara, alto del cuerpo
SOLAPA = 32                # solapa de cierre
PESTANA = 12               # pestaña de pegado
OREJA = 22                 # orejetas antipolvo

NEGRO, ORO = (16, 14, 12), (178, 143, 74)
CORTE, HENDIDO = (120, 114, 106), (196, 150, 150)
COTA = (150, 144, 134)


def mm(v):
    return int(round(v * PPM))


def ft(r, pt):
    return ImageFont.truetype(r, max(4, int(round(pt * 0.3528 * PPM))))


MG = mm(26)
ANCHO = MG * 2 + mm(A * 4 + PESTANA)
ALTO = MG * 2 + mm(SOLAPA * 2 + H) + mm(14)
lam = Image.new("RGB", (ANCHO, ALTO), (250, 250, 249))
d = ImageDraw.Draw(lam)

X0, Y0 = MG, MG + mm(8)
YC0, YC1 = Y0 + mm(SOLAPA), Y0 + mm(SOLAPA + H)      # cuerpo
paneles = [("FRENTE", A), ("COSTADO", A), ("DORSO", A), ("COSTADO", A)]


def punteada(p0, p1, color=HENDIDO, paso=7):
    x0, y0 = p0
    x1, y1 = p1
    n = max(1, int(((x1 - x0) ** 2 + (y1 - y0) ** 2) ** .5 / paso))
    for i in range(n):
        if i % 2:
            continue
        a0 = (x0 + (x1 - x0) * i / n, y0 + (y1 - y0) * i / n)
        a1 = (x0 + (x1 - x0) * (i + 1) / n, y0 + (y1 - y0) * (i + 1) / n)
        d.line([a0, a1], fill=color, width=2)


def centrado(y_mm, texto, f, color, track_mm, panel_x, panel_w=A):
    anchos = [d.textlength(c, font=f) for c in texto]
    tr = track_mm * PPM
    total = sum(anchos) + tr * (len(texto) - 1)
    x = panel_x + mm(panel_w) / 2 - total / 2
    for c, a in zip(texto, anchos):
        d.text((x, YC0 + mm(y_mm) + f.getmetrics()[0]), c, font=f, fill=color, anchor="ls")
        x += a + tr


def fleuron(cx, cy_mm, alto_mm, color):
    cy, r = YC0 + mm(cy_mm), mm(alto_mm / 2)
    c = r * 0.17
    d.polygon([(cx, cy - r), (cx + c, cy - c), (cx + r, cy), (cx + c, cy + c),
               (cx, cy + r), (cx - c, cy + c), (cx - r, cy), (cx - c, cy - c)], fill=color)


# ---------- cuerpo: cuatro paneles + pestaña ---------------------------
x = X0
bordes = []
for nombre, w in paneles:
    bordes.append(x)
    d.rectangle([x, YC0, x + mm(w), YC1], fill=(255, 255, 255), outline=None)
    x += mm(w)
bordes.append(x)
d.rectangle([x, YC0 + mm(4), x + mm(PESTANA), YC1 - mm(4)], fill=(252, 250, 247))

# ---------- solapas y orejetas -----------------------------------------
for i, (nombre, w) in enumerate(paneles):
    bx = bordes[i]
    if i in (0, 2):                                   # solapas de cierre
        for yy, sg in ((YC0, -1), (YC1, 1)):
            d.polygon([(bx + mm(2), yy), (bx + mm(w - 2), yy),
                       (bx + mm(w - 6), yy + sg * mm(SOLAPA)),
                       (bx + mm(6), yy + sg * mm(SOLAPA))], fill=(252, 250, 247))
    else:                                             # orejetas antipolvo
        for yy, sg in ((YC0, -1), (YC1, 1)):
            d.polygon([(bx + mm(1.5), yy), (bx + mm(w - 1.5), yy),
                       (bx + mm(w - 1.5), yy + sg * mm(OREJA - 4)),
                       (bx + mm(w - 5), yy + sg * mm(OREJA)),
                       (bx + mm(5), yy + sg * mm(OREJA))], fill=(252, 250, 247))

# ---------- arte ---------------------------------------------------------
# FRENTE: el sello
fx = bordes[0]
centrado(37.0, "MAISON SALDANA", ft(BODONI, 7.4), NEGRO, 0.5, fx)
fleuron(fx + mm(A) / 2, 44.2, 2.1, ORO)
centrado(47.6, "COLLECTION D'INSPIRATIONS", ft(JOST, 3.1), NEGRO, 0.26, fx)

# COSTADO 1: concentración y volumen
cx1 = bordes[1]
centrado(42.0, "EAU DE PARFUM", ft(JOST, 3.2), NEGRO, 0.3, cx1)
centrado(48.0, "60 ML  ·  2 FL OZ", ft(JOST, 3.2), NEGRO, 0.3, cx1)

# DORSO: QR, web y procedencia. La caja es universal: la misma para
# las 373 fragancias, así que aquí no va el nombre de ninguna. Al
# quitar el recuadro que lo reservaba quedaba un hueco en medio, así
# que el bloque del QR sube al centro óptico y la procedencia baja a
# apoyarse en el pie.
dx = bordes[2]
QR_ARRIBA = 29
try:
    # El archivo trae fondo marfil; sobre una caja blanca ese cuadrado
    # se vería. Se pasa a blanco puro antes de colocarlo.
    qr = Image.open(QR).convert("L").point(lambda v: 0 if v < 128 else 255)
    qr = qr.resize((mm(15), mm(15)), Image.NEAREST).convert("RGB")
    lam.paste(qr, (int(dx + mm((A - 15) / 2)), int(YC0 + mm(QR_ARRIBA))))
except Exception:
    d.rectangle([dx + mm((A - 15) / 2), YC0 + mm(QR_ARRIBA),
                 dx + mm((A + 15) / 2), YC0 + mm(QR_ARRIBA + 15)],
                outline=NEGRO, width=2)
centrado(QR_ARRIBA + 19.0, "MAISONSALDANA.COM", ft(JOST, 2.9), NEGRO, 0.22, dx)
centrado(72.0, "HECHO EN REPÚBLICA DOMINICANA", ft(JOST, 2.5), NEGRO, 0.16, dx)
centrado(76.5, "SANTO DOMINGO  ·  809 439 4509", ft(JOST, 2.5), NEGRO, 0.16, dx)

# COSTADO 2: la firma
cx2 = bordes[3]
centrado(45.0, "MAISON SALDANA", ft(JOST, 3.0), NEGRO, 0.28, cx2)

# ---------- líneas de corte y de hendido --------------------------------
d.line([X0, YC0, bordes[4] + mm(PESTANA), YC0], fill=HENDIDO, width=2)
punteada((X0, YC0), (bordes[4] + mm(PESTANA), YC0))
punteada((X0, YC1), (bordes[4] + mm(PESTANA), YC1))
for b in bordes[1:]:
    punteada((b, YC0 - mm(SOLAPA)), (b, YC1 + mm(SOLAPA)))
d.rectangle([X0, YC0, bordes[4], YC1], outline=CORTE, width=2)
for i, (nombre, w) in enumerate(paneles):
    bx = bordes[i]
    alto = SOLAPA if i in (0, 2) else OREJA
    for yy, sg in ((YC0, -1), (YC1, 1)):
        d.line([(bx, yy), (bx, yy + sg * mm(alto))], fill=CORTE, width=2)
        d.line([(bx + mm(w), yy), (bx + mm(w), yy + sg * mm(alto))], fill=CORTE, width=2)
        d.line([(bx, yy + sg * mm(alto)), (bx + mm(w), yy + sg * mm(alto))],
               fill=CORTE, width=2)
d.rectangle([bordes[4], YC0 + mm(4), bordes[4] + mm(PESTANA), YC1 - mm(4)],
            outline=CORTE, width=2)

# ---------- rótulos y cotas ---------------------------------------------
f_t = ImageFont.truetype(JOST, mm(3.4))
f_p = ImageFont.truetype(JOST, mm(2.5))
for i, (nombre, w) in enumerate(paneles):
    d.text((bordes[i] + mm(w) / 2, YC1 + mm(OREJA if i in (1, 3) else SOLAPA) + mm(5)),
           nombre, font=f_p, fill=COTA, anchor="mt")
d.text((bordes[4] + mm(PESTANA) / 2, YC1 + mm(5)), "PEGA", font=f_p, fill=COTA, anchor="mt")

d.text((MG, MG - mm(2)), "Plano de troquel · estuche plegadizo de solapas metidas",
       font=f_t, fill=(28, 26, 22))
d.text((MG, ALTO - mm(13)),
       f"Interior {A} × {A} × {H} mm  ·  desarrollo {A*4+PESTANA} × {H+SOLAPA*2} mm  ·  "
       f"sangrado 3 mm por fuera del corte  ·  escala real",
       font=f_p, fill=COTA)
d.text((MG, ALTO - mm(8)),
       "Línea continua = corte   ·   línea de puntos = hendido, por donde dobla",
       font=f_p, fill=COTA)

lam.save(f"{SALIDA}/troquel.png")
print("troquel:", lam.size, "=", round(ANCHO / PPM), "×", round(ALTO / PPM), "mm")
print(f"desarrollo del cartón: {A*4+PESTANA} × {H+SOLAPA*2} mm")
