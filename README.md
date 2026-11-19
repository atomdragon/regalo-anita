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
