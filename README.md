# 🎄 Studio de Animaciones ASCII 🐱

Proyecto interactivo que integra animaciones en arte ASCII con música sincronizada y visor de código en tiempo real, disponible tanto en **Python (Pygame)** como en **Web (HTML5 Canvas + Video + Audio)**.

---

## 🌟 Animaciones Incluidas

1. **🎄 Árbol de Navidad 3D (`christmas_tree.py` / Vista Web)**:
   - Motor 3D de puntos con proyección z-buffer y algoritmo de sombreado de pintor.
   - Nieve en caída dinámica con oscilación sinusoidal.
   - Esferas doradas, rojas y plateadas generadas con la esfera de Fibonacci.
   - Luces titilantes y espiral de guirnalda.
   - Estrella brillante en la cima y mensaje festivo inferior animado.

2. **🐱 Hachiware ASCII - ひとりごつ / Chiikawa (`hachiware.py` / Vista Web)**:
   - Recreación fiel del video: Hachiware cantando y tocando la guitarra en arte ASCII coloreado.
   - Sincronización con la canción provista en la carpeta `music/` (*Hitorigotsu*).
   - HUD superior con contador de tomas (`shot 01/25`), título en japonés, cantidad de caracteres ASCII y cronómetro en vivo.
   - Visor de código Python inferior con resaltado de sintaxis y auto-scroll sincronizado.
   - Letra karaoke en Japonés con traducción en Español.

3. **🎬 Reproductor del Video Original**:
   - Visor integrado de alta definición para ver directamente el video original en formato vertical.

---

## 🚀 Cómo Ejecutar

### Opción 1: Menú General (Python)
Ejecuta el menú interactivo para acceder a cualquiera de las animaciones o lanzar la versión web:

```bash
./venv/bin/python menu.py
# o
python3 menu.py
```

### Opción 2: Versión Web Interactiva (Navegador)
Inicia el servidor local y abre la interfaz web con un solo comando:

```bash
./venv/bin/python serve.py
# o
python3 serve.py
```
Luego abre tu navegador en: [http://localhost:8080/index.html](http://localhost:8080/index.html)

### Opción 3: Ejecución Individual de Animaciones en Python
- **Árbol de Navidad:**
  ```bash
  ./venv/bin/python christmas_tree.py
  ```
- **Hachiware (Chiikawa):**
  ```bash
  ./venv/bin/python hachiware.py
  ```

---

## ⌨️ Atajos de Teclado (Versión Web)

| Tecla | Acción |
|---|---|
| `1` | Cambiar a Árbol de Navidad 3D |
| `2` | Cambiar a Animación de Hachiware (Chiikawa) |
| `3` | Ver Video Original |
| `M` | Abrir / Cerrar Menú Selector Visual |
| `Espacio` | Pausar / Reanudar animación |
| `F` | Pantalla Completa |


## Escenas web celestes

Ejecutar `python3 serve.py` y abrir `http://localhost:8080/index.html`.

El árbol web usa Three.js 0.181.2 y sus complementos oficiales, incluidos localmente bajo `vendor/three` con licencia MIT. No necesita red al ejecutarse. La implementación está separada en `js/app.js`, `js/tree.js` y `js/hachiware.js`.

Hachiware conserva el ASCII original de `video/hachiware.mp4` y lo dibuja en un lienzo de 720×800, excluyendo el editor inferior. El video está silenciado: la canción completa gobierna el tiempo y la animación se repite cada 25 segundos. Ya no se descarga ni se vuelve a renderizar `hachiware_frames.js`. El generador independiente permanece disponible en `scripts/build_ascii_web.py`.

Los subtítulos de `subtitles/hitorigotsu.vtt` cubren las frases cantadas del audio local hasta 01:25.280, con silencios sin texto. Se obtuvieron mediante faster-whisper small (CPU int8) y se corrigieron errores ortográficos del reconocimiento; la traducción al español se elaboró a partir de esa transcripción. Los tiempos son automáticos y no equivalen a una revisión humana de precisión. Referencia localizada de la canción: https://utaten.com/lyric/mi22062929/ . La letra no se importó de esa página.

El reproductor usa toda la frecuencia de cuadros disponible, sin controles técnicos de calidad ni avisos de repetición en la interfaz.

Validación realizada: sintaxis JS y Python, integridad de 750 cuadros / 25 segundos, navegación y atajos, reproducción/pausa/búsqueda, idiomas y limpieza de subtítulos fuera de intervalo, anchos 360/768/1440 y consola del navegador. Movimiento reducido y fallo WebGL tienen tratamiento implementado, sin simulación manual en esta revisión.


### Karaoke y volumen del teléfono
La letra está abierta y utiliza `subtitles/hitorigotsu-karaoke.json`: intervalos de caracteres derivados de los tiempos de palabras de faster-whisper sobre el audio local. La división interna de cada palabra es interpolada; no es alineación fonética manual. El japonés cantado se resalta progresivamente y el español también se resalta por carácter con tiempos aproximados distribuidos sobre la actividad vocal de cada frase. El panel sigue la frase activa sin desplazar la página.

Se eliminó la atenuación propia y el deslizador de volumen: el audio pasa al nivel multimedia del dispositivo, controlado con sus botones. El navegador no lee ni modifica el volumen global del teléfono; Silenciar continúa siendo independiente. La comprobación fue en navegador de escritorio, no en un teléfono físico.


La pestaña del árbol reproduce el archivo local `music/last-christmas.mp3`, generado a partir de `music/Last Christmas - Wham!.flac` conservando el original. Se omiten los primeros 17.8 segundos: la primera voz se detectó en 17.96 s con faster-whisper small. Al entrar comienza desde esa frase y continúa; al salir se pausa y se prepara para volver al inicio. Los controles nativos permiten iniciar la canción si el navegador bloquea el inicio automático. No requiere YouTube ni conexión.

Regeneración: `ffmpeg -ss 17.8 -i 'music/Last Christmas - Wham!.flac' -codec:a libmp3lame -q:a 2 music/last-christmas.mp3`.


Corrección móvil: el lienzo mantiene proporción 9:10 y un tamaño limitado por el ancho y alto de la pantalla. El árbol gira directamente sobre su eje a 0.32 rad/s desde su aparición; el control «Girar árbol / Detener giro» permite cambiarlo. Movimiento reducido desactiva el giro inicial, pero el control permite iniciarlo explícitamente. Pausar detiene también la rotación.
