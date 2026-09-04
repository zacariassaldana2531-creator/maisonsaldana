/* =============================================================
   POLLOS THAEL — comportamiento
   -------------------------------------------------------------
   Todo lo que hay aquí es un añadido: si este archivo no cargara,
   la web sigue mostrando la carta, el horario y los teléfonos.
   ============================================================= */
(function () {
  "use strict";

  var data = window.__BRAND__ || {};
  var doc = document;

  /* ---------- Ayudas ---------- */
  function $(sel, ctx) { return (ctx || doc).querySelector(sel); }
  function $$(sel, ctx) { return Array.prototype.slice.call((ctx || doc).querySelectorAll(sel)); }
  function safe(fn, nombre) {
    try { fn(); } catch (e) { console.warn("[" + nombre + "]", e); }
  }

  var punteroFino = matchMedia("(hover: hover) and (pointer: fine)").matches;

  /* =============================================================
     Splash — con doble red de seguridad (aquí y en el CSS)
     ============================================================= */
  function initSplash() {
    var splash = $("[data-splash]");
    if (!splash) return;
    var fuera = function () { splash.classList.add("is-out"); };

    if (doc.readyState === "complete") setTimeout(fuera, 500);
    else window.addEventListener("load", function () { setTimeout(fuera, 400); });

    setTimeout(fuera, 3800);   // seguridad extra
  }

  /* =============================================================
     Nav — se vuelve sólida al bajar
     ============================================================= */
  function initNav() {
    var nav = $("[data-nav]");
    if (!nav) return;
    var ultimo = -1;

    function pinta() {
      var solida = window.scrollY > 24;
      if (solida !== ultimo) {
        nav.classList.toggle("is-solid", solida);
        ultimo = solida;
      }
    }
    pinta();
    window.addEventListener("scroll", pinta, { passive: true });
  }

  /* =============================================================
     Barra de móvil — se esconde mientras se ve la portada, porque
     ahí ya están los dos botones. Si este código no corriera, la
     barra se queda visible siempre, que es el fallo bueno.
     ============================================================= */
  function initBarraMovil() {
    var barra = $(".barra-movil");
    var hero = $(".hero");
    if (!barra || !hero) return;

    var pendiente = false;
    function decide() {
      pendiente = false;
      barra.classList.toggle("is-fuera", window.scrollY < hero.offsetHeight * 0.72);
    }
    function alScroll() {
      if (pendiente) return;
      pendiente = true;
      requestAnimationFrame(decide);
    }
    decide();
    window.addEventListener("scroll", alScroll, { passive: true });
    window.addEventListener("resize", alScroll, { passive: true });
  }

  /* =============================================================
     ¿Abierto ahora? — se calcula en hora de Santo Domingo,
     da igual desde dónde mire el visitante.
     ============================================================= */
  var DIAS_CORTOS = { Sun: 0, Mon: 1, Tue: 2, Wed: 3, Thu: 4, Fri: 5, Sat: 6 };

  function minutos(hhmm) {
    var p = String(hhmm).split(":");
    return (parseInt(p[0], 10) * 60) + parseInt(p[1] || "0", 10);
  }

  function aHoraBonita(hhmm) {
    var p = String(hhmm).split(":");
    var h = parseInt(p[0], 10);
    var m = p[1] || "00";
    return h + ":" + m;
  }

  // Devuelve { dia: 0-6, min: minutos desde medianoche } en la zona del negocio.
  function ahoraLocalDelNegocio(zona) {
    try {
      var partes = new Intl.DateTimeFormat("en-US", {
        timeZone: zona,
        weekday: "short",
        hour: "2-digit",
        minute: "2-digit",
        hour12: false
      }).formatToParts(new Date());

      var mapa = {};
      partes.forEach(function (p) { mapa[p.type] = p.value; });

      var dia = DIAS_CORTOS[mapa.weekday];
      var h = parseInt(mapa.hour, 10) % 24;
      var m = parseInt(mapa.minute, 10);
      if (dia === undefined || isNaN(h) || isNaN(m)) throw new Error("sin datos");
      return { dia: dia, min: h * 60 + m };
    } catch (e) {
      var d = new Date();   // último recurso: la hora del visitante
      return { dia: d.getDay(), min: d.getHours() * 60 + d.getMinutes() };
    }
  }

  function tramoDe(dia) {
    var lista = data.horario || [];
    for (var i = 0; i < lista.length; i++) {
      if (lista[i].dia === dia) return lista[i];
    }
    return null;
  }

  function calculaEstado() {
    if (!data.horario || !data.horario.length) return null;

    var ahora = ahoraLocalDelNegocio(data.zonaHoraria || "America/Santo_Domingo");
    var hoy = tramoDe(ahora.dia);

    if (hoy) {
      var abre = minutos(hoy.abre);
      var cierra = minutos(hoy.cierra);

      if (ahora.min >= abre && ahora.min < cierra) {
        var faltan = cierra - ahora.min;
        return {
          abierto: true,
          texto: faltan <= 45
            ? "Abierto · cierra en " + faltan + " min"
            : "Abierto ahora · hasta las " + aHoraBonita(hoy.cierra)
        };
      }
      if (ahora.min < abre) {
        return { abierto: false, texto: "Cerrado · abre hoy a las " + aHoraBonita(hoy.abre) };
      }
    }

    // Ya cerró: busca el próximo día con horario.
    for (var s = 1; s <= 7; s++) {
      var t = tramoDe((ahora.dia + s) % 7);
      if (!t) continue;
      var cuando = (s === 1) ? "mañana" : "el " + t.nombre.toLowerCase();
      return { abierto: false, texto: "Cerrado · abre " + cuando + " a las " + aHoraBonita(t.abre) };
    }
    return null;
  }

  function initEstado() {
    var chips = $$("[data-estado]");
    if (!chips.length) return;

    function pinta() {
      var e = calculaEstado();
      if (!e) return;
      chips.forEach(function (chip) {
        chip.hidden = false;
        chip.classList.toggle("is-abierto", e.abierto);
        chip.classList.toggle("is-cerrado", !e.abierto);
        var t = $("[data-estado-texto]", chip);
        if (t) t.textContent = e.texto;
      });
    }

    pinta();
    setInterval(pinta, 60000);   // se refresca solo cada minuto
  }

  /* =============================================================
     Marca el día de hoy en la tabla de horario
     ============================================================= */
  function initHoy() {
    var filas = $$(".horario tr[data-dia]");
    if (!filas.length) return;
    var ahora = ahoraLocalDelNegocio(data.zonaHoraria || "America/Santo_Domingo");
    filas.forEach(function (fila) {
      if (parseInt(fila.getAttribute("data-dia"), 10) === ahora.dia) {
        fila.classList.add("is-hoy");
      }
    });
  }

  /* =============================================================
     Cinta — se duplica el contenido para que el bucle no dé saltos
     ============================================================= */
  function initTicker() {
    var track = $("[data-ticker]");
    if (!track || track.getAttribute("data-listo")) return;
    track.innerHTML = track.innerHTML + track.innerHTML;
    track.setAttribute("data-listo", "1");
  }

  /* =============================================================
     Filtros de la carta — se construyen a partir de lo que ya
     está en el HTML, así nunca se descuadran al editar la carta.
     ============================================================= */
  function initTabs() {
    var barra = $("[data-tabs]");
    var cats = $$(".cat");
    if (!barra || cats.length < 2) return;

    var botones = [];

    function muestra(clave) {
      cats.forEach(function (cat) {
        cat.hidden = !(clave === "todo" || cat.id === clave);
      });
      botones.forEach(function (b) {
        var on = b.getAttribute("data-para") === clave;
        b.classList.toggle("is-on", on);
        b.setAttribute("aria-pressed", on ? "true" : "false");
      });
      if (window.ScrollTrigger) { try { ScrollTrigger.refresh(); } catch (_) {} }
    }

    function creaBoton(clave, etiqueta) {
      var b = doc.createElement("button");
      b.type = "button";
      b.className = "tab";
      b.textContent = etiqueta;
      b.setAttribute("data-para", clave);
            b.addEventListener("click", function () { muestra(clave); });
      barra.appendChild(b);
      botones.push(b);
    }

    creaBoton("todo", "Toda la carta");
    cats.forEach(function (cat) {
      creaBoton(cat.id, cat.getAttribute("data-cat") || cat.id);
    });

    muestra("todo");
  }

  /* =============================================================
     Apariciones al bajar — umbral bajísimo y red de seguridad,
     para que ninguna tarjeta se quede invisible nunca.
     ============================================================= */
  function initReveals() {
    var objetivos = $$("[data-reveal]");
    if (!objetivos.length) return;

    if (!("IntersectionObserver" in window)) {
      objetivos.forEach(function (el) { el.classList.add("is-revealed"); });
      return;
    }

    var io = new IntersectionObserver(function (entradas) {
      entradas.forEach(function (e) {
        if (!e.isIntersecting) return;
        e.target.classList.add("is-revealed");
        io.unobserve(e.target);
      });
    }, { threshold: 0.01, rootMargin: "0px 0px -2% 0px" });

    objetivos.forEach(function (el, i) {
      el.style.transitionDelay = Math.min(i % 6, 5) * 55 + "ms";
      io.observe(el);
    });

    /* Barrido de respaldo. El observador se puede saltar un elemento si
       el visitante baja de golpe (rueda rápida, barra lateral, teclado):
       en ese caso el elemento entra y sale en el mismo fotograma y nunca
       se marca. Esto lo recoge. */
    var pendiente = false;
    function barre() {
      pendiente = false;
      var quedan = $$("[data-reveal]:not(.is-revealed)");
      quedan.forEach(function (el) {
        if (el.getBoundingClientRect().top < window.innerHeight * 0.98) {
          el.classList.add("is-revealed");
          io.unobserve(el);
        }
      });
      if (!quedan.length) window.removeEventListener("scroll", alScroll);
    }
    function alScroll() {
      if (pendiente) return;
      pendiente = true;
      requestAnimationFrame(barre);
    }
    window.addEventListener("scroll", alScroll, { passive: true });
    window.addEventListener("resize", alScroll, { passive: true });

    // Red de seguridad final: a los 6 s no puede quedar nada escondido.
    setTimeout(function () {
      $$("[data-reveal]:not(.is-revealed)").forEach(function (el) {
        if (el.getBoundingClientRect().top < window.innerHeight * 1.6) {
          el.classList.add("is-revealed");
        }
      });
    }, 6000);
  }

  /* =============================================================
     El sello de la casa: la brasa que sigue al cursor
     ============================================================= */
  function initBrasa() {
    if (!punteroFino) return;
    $$("[data-brasa]").forEach(function (card) {
      card.addEventListener("mousemove", function (ev) {
        var r = card.getBoundingClientRect();
        card.style.setProperty("--mx", ((ev.clientX - r.left) / r.width * 100) + "%");
        card.style.setProperty("--my", ((ev.clientY - r.top) / r.height * 100) + "%");
      });
      card.addEventListener("mouseleave", function () {
        card.style.setProperty("--mx", "50%");
        card.style.setProperty("--my", "50%");
      });
    });
  }

  /* =============================================================
     Números que suben (la nota y las reseñas)
     ============================================================= */
  function initContadores() {
    var nums = $$("[data-count-to]");
    if (!nums.length || !("IntersectionObserver" in window)) return;

    var io = new IntersectionObserver(function (entradas) {
      entradas.forEach(function (e) {
        if (!e.isIntersecting) return;
        anima(e.target);
        io.unobserve(e.target);
      });
    }, { threshold: 0.05 });

    nums.forEach(function (n) { io.observe(n); });

    function anima(el) {
      var fin = parseFloat(el.getAttribute("data-count-to"));
      var dec = parseInt(el.getAttribute("data-decimals") || "0", 10);
      if (isNaN(fin)) return;
      var t0 = null, dur = 1100;

      function paso(t) {
        if (t0 === null) t0 = t;
        var p = Math.min((t - t0) / dur, 1);
        var suave = 1 - Math.pow(1 - p, 3);
        var v = (fin * suave).toFixed(dec);
        el.textContent = dec > 0 ? v.replace(".", ",") : v;
        if (p < 1) requestAnimationFrame(paso);
      }
      requestAnimationFrame(paso);
    }
  }

  /* =============================================================
     Año del pie
     ============================================================= */
  function initAnio() {
    var el = $("[data-anio]");
    if (el) el.textContent = new Date().getFullYear();
  }

  /* =============================================================
     Parallax suave del halo del hero (solo si GSAP cargó)
     ============================================================= */
  function initHeroParallax() {
    var plate = $(".hero-plate");
    if (!plate) return;

    gsap.to(plate, {
      yPercent: 14,
      scale: 1.08,
      ease: "none",
      scrollTrigger: {
        trigger: ".hero",
        start: "top top",
        end: "bottom top",
        scrub: 0.6
      }
    });

    gsap.to(".hero-inner", {
      yPercent: 7,
      opacity: 0.35,
      ease: "none",
      scrollTrigger: {
        trigger: ".hero",
        start: "top top",
        end: "bottom top",
        scrub: 0.6
      }
    });
  }

  /* =============================================================
     Arranque
     ============================================================= */
  function boot() {
    doc.documentElement.classList.add("js");

    safe(initSplash, "splash");
    safe(initNav, "nav");
    safe(initBarraMovil, "barraMovil");
    safe(initEstado, "estado");
    safe(initHoy, "hoy");
    safe(initTicker, "ticker");
    safe(initTabs, "tabs");
    safe(initReveals, "reveals");
    safe(initBrasa, "brasa");
    safe(initContadores, "contadores");
    safe(initAnio, "anio");

    if (window.gsap && window.ScrollTrigger) {
      try { gsap.registerPlugin(ScrollTrigger); } catch (_) {}
      safe(initHeroParallax, "heroParallax");
    }

    doc.documentElement.classList.add("is-ready");
  }

  if (doc.readyState === "loading") {
    doc.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
