# RAISE-512: Dark/light mode switch solo aplica a bloques de código

WHAT:      El toggle de tema en raiseframework.ai/docs solo cambia los bloques de código;
           el fondo, texto, sidebar, headers y navegación no responden al cambio.
WHEN:      Al activar light mode (o viceversa) desde el toggle de Starlight en la barra de navegación
WHERE:     docs/src/styles/starlight.css
EXPECTED:  Toda la UI actualiza colores al cambiar el tema (fondo, texto, sidebar, nav, código)
Done when: Al activar light mode, la página completa cambia a tema claro;
           al activar dark mode, vuelve al tema oscuro. Bloques de código mantienen coherencia.
