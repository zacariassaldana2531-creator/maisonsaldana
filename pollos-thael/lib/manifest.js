/* =============================================================
   POLLOS THAEL — datos del negocio
   -------------------------------------------------------------
   Aquí SOLO están los datos que la web usa para calcular cosas
   (si está abierto ahora mismo) y para la cinta que se desliza.

   La carta, el horario que se ve en pantalla, las reseñas y los
   textos están escritos directamente en index.html, con comentarios
   que dicen dónde editar cada cosa. Así la web sigue funcionando
   aunque el navegador del cliente bloquee JavaScript.

   ⚠️ Si cambias el horario, cámbialo en LOS DOS SITIOS:
      1) aquí abajo (para el cartelito de "Abierto ahora")
      2) en la tabla de horario de index.html (lo que se ve)
   ============================================================= */
(function () {
  "use strict";

  window.__BRAND__ = {
    nombre: "Pollos Thael",
    ciudad: "Santo Domingo, República Dominicana",

    contacto: {
      telefono: "+1 849-206-7843",
      telefonoLink: "tel:+18492067843",
      direccion: "Av. Padre Castellanos, Santo Domingo, Distrito Nacional",
      instagram: "https://www.instagram.com/pollosthael_1/"
    },

    /* Horario real del negocio, en hora de Santo Domingo (UTC−4, sin
       cambio de hora). 0 = domingo … 6 = sábado. */
    horario: [
      { dia: 0, nombre: "Domingo",   abre: "07:15", cierra: "22:00" },
      { dia: 1, nombre: "Lunes",     abre: "07:00", cierra: "22:00" },
      { dia: 2, nombre: "Martes",    abre: "07:15", cierra: "22:00" },
      { dia: 3, nombre: "Miércoles", abre: "07:15", cierra: "22:00" },
      { dia: 4, nombre: "Jueves",    abre: "07:15", cierra: "22:00" },
      { dia: 5, nombre: "Viernes",   abre: "07:15", cierra: "23:00" },
      { dia: 6, nombre: "Sábado",    abre: "07:15", cierra: "22:00" }
    ],

    // Zona horaria oficial del negocio. No la toques.
    zonaHoraria: "America/Santo_Domingo",

    // Palabras de la cinta que se desliza entre secciones.
    ticker: [
      "Pollo horneado", "Pollo frito", "Mangú", "Asado", "Alitas",
      "Costillas", "Calamares", "Salmón a la parrilla",
      "Para llevar", "Abierto desde las 7 a.m."
    ]
  };
})();
