# Pollos Thael — la web

Una sola página, sin programas raros ni cuotas mensuales. Se copian los
archivos a un hosting y ya funciona.

Para verla ahora mismo: abre `index.html` con doble clic. Funciona igual
desde el escritorio que desde internet.

---

## 1. Lo primero: los precios

Los precios están **vacíos a propósito**. No inventé ninguno. Donde falta
un precio, la web pone un guion discreto (—) en vez de un número falso.

Para poner uno, abre `index.html` con el Bloc de notas y busca la línea del
plato. Verás algo así:

```html
<span class="plato-precio"></span>
```

Escribe el precio entre las comillas del final:

```html
<span class="plato-precio">RD$ 450</span>
```

Guarda y listo. Repite con cada plato.

---

## 2. Lo segundo: revisar la carta

La carta la armé con lo que aparece publicado del negocio en Google y en
Restaurant Guru. **Hay que revisarla antes de enseñarla a nadie.**

**Confirmados** (salen en tu ficha pública): pollo horneado, pollo frito,
asado, hornado, mangú, alitas, costillas baby back, salmón a la parrilla,
calamares fritos, rape y fish and chips.

**Que me inventé porque son lo normal en la casa, y hay que confirmar:**
medio pollo, cuarto de pollo, arroz blanco, habichuelas, papas fritas,
tostones, ensalada verde y refrescos.

En `index.html`, la sección de la carta está marcada con un comentario que
dice `EDITA AQUÍ la carta entera`. Para quitar un plato, borra su bloque
`<li class="plato"> … </li>` completo. Para añadir uno, copia un bloque
entero y cambia el nombre y la descripción.

---

## 3. Las fotos

**Léelo entero, es lo más importante de este archivo.**

Las fotos que tiene ahora la web **no son de Pollos Thael**. Son
fotografías de archivo con licencia Creative Commons, buscadas en
Openverse, elegidas a mano entre unas sesenta y retocadas todas con el
mismo tono cálido para que parezcan un solo reportaje.

Están ahí para que la web no se vea vacía mientras se hacen las fotos de
verdad. No son el pollo de la casa, y por eso:

- La página `creditos.html` lo dice con todas las letras y da el autor y
  la licencia de cada una. **Ese enlace del pie no se puede quitar**: las
  licencias CC BY y CC BY-SA obligan a dar crédito.
- En cuanto haya fotos reales, se sustituyen y esa página desaparece.

### Cómo poner fotos reales (lo mejor que le puedes hacer a esta web)

1. Haz las fotos con el móvil, **de día y cerca de una ventana o de la
   puerta**. Nada de flash: la luz del flash aplana la comida y le quita
   el brillo. Un pollo recién sacado del horno, con vapor, junto a una
   ventana, gana a cualquier foto de archivo.
2. Guárdalas en `assets/photos/source/` con estos nombres exactos, en
   `.jpg`:

   | Nombre del archivo | Qué foto va ahí |
   |---|---|
   | `hero.jpg` | El fondo de la portada — la rustidera llena, un plano abierto |
   | `casa.jpg` | La banda ancha — el horno, la parrilla, las manos trabajando |
   | `pollo-horneado.jpg` | Un pollo entero horneado |
   | `pollo-frito.jpg` | Las presas de pollo frito |
   | `alitas.jpg` | Las alitas |
   | `salmon.jpg` | El salmón |

3. Ejecuta una vez:

   ```
   python3 tools/procesar_fotos.py
   ```

   Recorta, corrige el color, comprime a `.webp` y las deja en
   `assets/img/`. La web las coge sola: no hay que tocar el HTML.

4. Borra la línea de los créditos del pie de `index.html` y el archivo
   `creditos.html`, que ya no hacen falta.

Si alguna foto queda mal encuadrada, en `tools/procesar_fotos.py` hay una
tabla al principio con el recorte de cada una, y comentarios que explican
qué significa cada número.

### Añadir fotos a otros platos

Busca la línea del plato en `index.html` y cámbiala así:

```html
<li class="plato plato--destacado" data-reveal data-brasa>
  <div class="plato-marco"><img class="plato-foto" src="assets/img/tostones.webp" alt="Tostones recién fritos" loading="lazy" decoding="async" /></div>
  <div class="plato-texto">
  ...
```

Lo que cambia respecto a un plato normal es `plato--destacado` en la
primera línea y el bloque `plato-marco` con la foto.

El mangú se quedó sin foto a propósito: no encontré ninguna de archivo que
fuera mangú de verdad (las que hay son mofongo, que es otra cosa), y
prefiero dejarlo sin foto antes que poner un plato que no es.

---

## 4. El cartelito de "Abierto ahora"

Arriba a la derecha y en la portada aparece un cartelito verde que dice si
el negocio está abierto en este momento, y a qué hora cierra. Lo calcula
solo, en hora de Santo Domingo, aunque el que mire la web esté en Nueva
York o en Madrid.

**Si cambias el horario, hay que cambiarlo en dos sitios:**

1. `lib/manifest.js` — es lo que usa el cartelito para calcular.
2. La tabla de horario en `index.html` — es lo que se ve en pantalla.

Los dos están marcados con comentarios que lo explican.

---

## 5. Lo que hay que revisar antes de publicar

- [ ] **El teléfono.** Puse el +1 849-206-7843, que es el que aparece
      publicado. Si el bueno es otro, hay que cambiarlo en varios sitios de
      `index.html`: busca `18492067843` y cámbialos todos (aparece 6 veces), y cambia también el `+1-849-206-7843` del bloque de datos para Google, al final del archivo.
- [ ] **¿Ese número tiene WhatsApp?** No lo sé, así que todos los botones
      llaman por teléfono. Si tiene WhatsApp, se cambia y mejora mucho.
- [ ] **El horario** — que siga siendo el correcto.
- [ ] **El enlace de Uber Eats** — que sea la tienda correcta.
- [ ] **Los precios y la carta** (pasos 1 y 2).

---

## 6. Detalles que ya están resueltos

- **Funciona sin internet rápido y sin JavaScript.** Si el navegador del
  cliente falla, la carta, el horario, la dirección y el teléfono se ven
  igual. Nada del contenido depende de que todo cargue bien.
- **Móvil primero.** Abajo hay una barra fija con "Llamar y pedir" que
  aparece en cuanto se baja de la portada.
- **Las reseñas son reales**, copiadas de Google tal como las escribió la
  gente. No hay ninguna inventada.
- **Ficha para Google.** La web lleva dentro los datos del negocio en el
  formato que Google entiende (dirección, teléfono, horario, valoración),
  para que salga mejor en las búsquedas.
- **Sin cookies, sin rastreadores, sin formularios** que guarden datos de
  nadie. No hay nada legal que gestionar.

---

## 7. Qué archivo es cada cosa

| Archivo | Qué es |
|---|---|
| `index.html` | Toda la página: textos, carta, horario, teléfonos |
| `styles.css` | Los colores, las tipografías y la maquetación |
| `main.js` | Los detalles que se mueven (cartelito de abierto, filtros de la carta) |
| `lib/manifest.js` | El horario que usa el cartelito de "Abierto ahora" |
| `lib/gsap.min.js`, `lib/ScrollTrigger.min.js` | Librerías de animación |
| `creditos.html` | Autoría de las fotos de archivo (obligatorio mientras se usen) |
| `assets/img/` | Las fotos ya listas para la web |
| `assets/photos/source/` | Las fotos originales, antes de procesar |
| `tools/` | Solo de trabajo: no hace falta subirlo al hosting |
| `.htaccess` | Le dice al hosting que no guarde versiones viejas en caché |

---

## 8. Para publicarla

Los archivos se suben tal cual a la carpeta pública del hosting
(`public_html` en Hostinger). No hay que compilar ni instalar nada.

Cuando cambies algo y lo vuelvas a subir, cambia también la fecha en estas
dos líneas de `index.html` para que a los clientes les llegue la versión
nueva y no la vieja guardada en su navegador:

```html
<link rel="stylesheet" href="styles.css?v=20260904" />
<script defer src="main.js?v=20260904"></script>
```

Pon la fecha del día (`?v=20261120`, por ejemplo).
