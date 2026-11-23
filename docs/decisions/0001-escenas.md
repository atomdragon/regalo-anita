# 0001 — Escenas locales y reloj de audio

**Estado:** Aceptada; la caché de cuadros se sustituye por [0002](0002-ascii-source.md).
**Afecta:** js/tree.js, js/hachiware.js, js/app.js

## Contexto
La aplicación estática conserva su servidor Python. La caché de cientos de lienzos aumenta memoria; los cuadros duran 25 s frente a 87 s del audio.

## Decisión
Three.js 0.181.2 local con WebGL y complementos oficiales para el árbol. Canvas 2D para ASCII, caché LRU de 12 cuadros y un único HTMLAudioElement como reloj. La animación se repite, los subtítulos no. Carga diferida al abrir cada escena.

## Alternativas
Un framework y un reproductor externo añaden complejidad sin necesidad. Pre-renderizar todos los cuadros consume demasiada memoria. WebGPU reduciría compatibilidad.

## Consecuencias
Sin dependencias de red al ejecutar; recursos 3D y reproducción se suspenden al salir. Hay que revisar subtítulos contra el audio, sin inventar tiempos ni repetir las frases con la imagen.

## Validación
Navegación, búsquedas, fin del audio, caché acotada, ausencia de render oculto y fallback WebGL.
