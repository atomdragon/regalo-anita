import json
import cv2
import numpy as np
from scipy.ndimage import distance_transform_edt

VIDEO_IN = "temp_hachiware.mp4"
OUT_JS = "hachiware_frames.js"

# Resolución de la cuadrícula ASCII (9:16 o 4:3 centrado)
COLS = 96
ROWS = 64
TARGET_FPS = 15  # 15 fps mantiene el archivo ligero (~3-4 MB) y muy fluido en web
MAX_SECONDS = 25 # Duración del clip (puedes subirlo hasta 83 para toda la canción)

RAMP = " .'`^\",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"
LIGHT = np.array([-0.45, -0.55, 0.70])
LIGHT /= np.linalg.norm(LIGHT)

# Paleta exacta (R, G, B)
PALETTE = [
    (246, 246, 248),  # 0: PAPER / Fondo claro
    (244, 245, 250),  # 1: FUR / Pelaje blanco Hachiware y Chiikawa
    (108, 172, 226),  # 2: HAIR / Orejas y flequillo azul
    (246, 134, 166),  # 3: BLUSH / Rubor mejillas
    (194, 132, 68),   # 4: WOOD / Guitarra y tronco
    (118, 178, 96),   # 5: LEAF / Arbustos y césped
    (34, 30, 32),     # 6: INK / Líneas de contorno
]

def classify(rgb):
    c = rgb.astype(int)
    r, g, b = c[..., 0], c[..., 1], c[..., 2]
    lum = c.mean(-1)
    chroma = c.max(-1) - c.min(-1)

    k = np.zeros(r.shape, dtype=np.uint8)  # 0: PAPER
    k[(lum > 228) & (chroma <= 12)] = 1    # 1: FUR
    k[(g - r > 10) & (g - b > 10)] = 5     # 5: LEAF
    k[(r - b > 30) & (r > g + 8) & (lum < 215)] = 4  # 4: WOOD
    k[(b - r > 20) & (b > 105)] = 2        # 2: HAIR
    k[(r - g > 20) & (r > 180) & (b > g - 10)] = 3   # 3: BLUSH
    k[(lum < 115) | ((lum < 145) & (chroma < 32))] = 6  # 6: INK
    return k

def compute_ascii_frame(frame_bgr):
    rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
    # Recortar ligeramente los bordes si hay barras negras
    h, w, _ = rgb.shape
    small = cv2.resize(rgb, (COLS, ROWS), interpolation=cv2.INTER_AREA)

    kind = classify(small)
    solid = kind != 6

    # Relieve 3D basado en distancia a las líneas de contorno (depth + shade)
    dist = distance_transform_edt(solid)
    puff = np.clip(dist / 5.0, 0.0, 1.0)
    height = np.sqrt(puff)
    gy, gx = np.gradient(height * 6.0)
    normals = np.stack([-gx, -gy, np.ones_like(height)], axis=-1)
    norms = np.linalg.norm(normals, axis=-1, keepdims=True)
    normals /= np.maximum(norms, 1e-6)

    lit = np.clip(normals @ LIGHT, 0.0, 1.0)
    shade = np.clip(0.58 + 0.28 * lit + 0.24 * height, 0.35, 1.15)
    shade[kind == 6] = 0.95  # Tinta bien marcada
    shade[kind == 0] = 0.18  # Fondo tenue para que resalte el personaje

    chars = []
    colors = []
    ramp_len = len(RAMP)

    for y in range(ROWS):
        row_chars = []
        row_cols = []
        for x in range(COLS):
            k = kind[y, x]
            sh = shade[y, x]
            if k == 0:
                row_chars.append(".")
                row_cols.append(0)
            elif k == 6:
                row_chars.append("#")
                row_cols.append(6)
            else:
                idx = int(np.clip(sh * (ramp_len - 1) * 0.82, 2, ramp_len - 1))
                row_chars.append(RAMP[idx])
                row_cols.append(int(k))
        chars.append("".join(row_chars))
        colors.append(row_cols)

    return {"c": chars, "k": colors}

def main():
    cap = cv2.VideoCapture(VIDEO_IN)
    src_fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    step = max(1, round(src_fps / TARGET_FPS))
    max_frames = int(MAX_SECONDS * TARGET_FPS)

    frames = []
    frame_idx = 0
    while len(frames) < max_frames:
        ret, frame = cap.read()
        if not ret:
            break
        if frame_idx % step == 0:
            frames.append(compute_ascii_frame(frame))
            if len(frames) % 30 == 0:
                print(f"Procesados {len(frames)}/{max_frames} fotogramas...")
        frame_idx += 1

    cap.release()

    payload = {
        "cols": COLS,
        "rows": ROWS,
        "fps": TARGET_FPS,
        "palette": PALETTE,
        "frames": frames,
    }

    with open(OUT_JS, "w", encoding="utf-8") as f:
        f.write("window.HACHIWARE_ASCII = ")
        json.dump(payload, f, separators=(",", ":"))
        f.write(";")

    print(f"¡Listo! Archivo generado: {OUT_JS} ({len(frames)} fotogramas)")

if __name__ == "__main__":
    main()