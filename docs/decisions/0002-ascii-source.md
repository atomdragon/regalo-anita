# 0002 — Conservar la animación ASCII original

**Estado:** Aceptada
**Afecta:** js/hachiware.js, index.html

## Contexto
El video local ya contiene arte ASCII y un editor en la parte inferior. Volver a clasificar sus caracteres como imágenes genera una trama densa que dificulta reconocer al personaje en móvil.

## Decisión
Decodificar el MP4 silenciado y dibujar su área de animación (720×800 desde y=24) en Canvas 2D, manteniendo el audio como reloj y los subtítulos bilingües. Mostrar una proporción fija y tamaño limitado por la pantalla. Esto reemplaza únicamente la caché de cuadros regenerados de la decisión 0001.

## Alternativas
Regenerar ASCII desde el ASCII original degrada los contornos. Mostrar el MP4 entero incluye el editor y ocupa demasiada altura.

## Consecuencias
No se descarga hachiware_frames.js al reproducir. Los archivos del generador permanecen disponibles para uso independiente. El audio del MP4 está silenciado para evitar duplicación.

## Validación
Revisión móvil y escritorio, búsquedas, pausa, repetición a 25 s y karaoke.
