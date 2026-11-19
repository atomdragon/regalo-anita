import os
import math
import subprocess
import numpy as np
import pygame

# --- Configuración de la ventana y cuadrícula ASCII de alta resolución ---
TITLE = "Hachiware ASCII - ひとりごつ (0:00 - 0:13)"
CW, CH, FONT_PX = 7, 11, 11
COLS, ROWS = 112, 78
W, H = COLS * CW, ROWS * CH
FPS = 30
ASPECT_CHAR = CW / CH
MONO = "consolas,menlo,dejavusansmono,couriermonospace,monospace"
HINT = "Space pause • R restart • S screenshot • Esc menú"

# --- Ruta de la pista de audio ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_PATH = os.path.join(
    BASE_DIR,
    "music",
    "Chiikawa canción sub español Hitorigotsu chiikawa ending #chiikawa #hachiware - EnzoInTheStars.m4a",
)

# --- Materiales ---
M_BG = 0
M_FUR = 1
M_HAIR = 2
M_BLUSH = 3
M_WOOD = 4
M_WOOD_DK = 5
M_GRASS = 6
M_STUMP = 7
M_MOUTH = 8
M_TONGUE = 9
M_EYE = 10
M_SHINE = 11
M_INK = 12
M_LEAF = 13

PALETTE = {
    M_FUR: np.array([244, 246, 252], dtype=np.float32),
    M_HAIR: np.array([105, 178, 240], dtype=np.float32),
    M_BLUSH: np.array([248, 122, 162], dtype=np.float32),
    M_WOOD: np.array([204, 142, 72], dtype=np.float32),
    M_WOOD_DK: np.array([118, 72, 36], dtype=np.float32),
    M_GRASS: np.array([145, 205, 115], dtype=np.float32),
    M_STUMP: np.array([162, 112, 68], dtype=np.float32),
    M_MOUTH: np.array([185, 65, 88], dtype=np.float32),
    M_TONGUE: np.array([246, 138, 162], dtype=np.float32),
    M_EYE: np.array([38, 42, 54], dtype=np.float32),
    M_SHINE: np.array([255, 255, 255], dtype=np.float32),
    M_INK: np.array([68, 74, 88], dtype=np.float32),
    M_LEAF: np.array([86, 168, 96], dtype=np.float32),
}

SHADE_RAMP = " .'`^\",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"
OUT_CHARS = np.frombuffer(b"#mwnuvc", dtype=np.uint8)

YY, XX = np.mgrid[0:ROWS, 0:COLS].astype(np.float32)


class AsciiRenderer:
    def __init__(self, cw, ch, font_px):
        self.cw, self.ch = cw, ch
        font = pygame.font.SysFont(MONO, font_px, bold=True)
        self.atlas = []
        for code in range(32, 127):
            g = font.render(chr(code), True, (255, 255, 255))
            surf = pygame.Surface((cw, ch))
            surf.fill((0, 0, 0))
            surf.blit(g, ((cw - g.get_width()) // 2, (ch - g.get_height()) // 2))
            self.atlas.append(pygame.surfarray.array3d(surf).transpose(1, 0, 2))
        self.atlas = np.array(self.atlas, dtype=np.uint16)

    def render(self, screen, char_buf, col_buf):
        idx = np.clip(char_buf - 32, 0, len(self.atlas) - 1)
        glyphs = self.atlas[idx]
        colored = (glyphs * col_buf[:, :, None, None, :].astype(np.uint16)) >> 8
        img = colored.transpose(0, 2, 1, 3, 4).reshape(ROWS * self.ch, COLS * self.cw, 3).astype(np.uint8)
        pygame.surfarray.blit_array(screen, img.transpose(1, 0, 2))


# --- Primitivas vectorizadas con corrección de proporción visual ---
def fill_oval(mat_b, puff_b, cx, cy, rx, ry, mat, tilt=0.0):
    ct, st = math.cos(tilt), math.sin(tilt)
    ox = XX - cx
    oy = (YY - cy) / ASPECT_CHAR
    dx = (ox * ct + oy * st) / rx
    dy = (-ox * st + oy * ct) / ry
    d = dx * dx + dy * dy
    inside = d <= 1.0
    mat_b[inside] = mat
    puff_b[inside] = np.sqrt(np.maximum(0.0, 1.0 - d[inside]))


def fill_tri(mat_b, puff_b, p1, p2, p3, mat):
    q1 = (p1[0], p1[1] / ASPECT_CHAR)
    q2 = (p2[0], p2[1] / ASPECT_CHAR)
    q3 = (p3[0], p3[1] / ASPECT_CHAR)
    px, py = XX, YY / ASPECT_CHAR

    def sign(a, b):
        return (px - b[0]) * (a[1] - b[1]) - (a[0] - b[0]) * (py - b[1])

    d1 = sign(q1, q2)
    d2 = sign(q2, q3)
    d3 = sign(q3, q1)
    inside = ~(((d1 < 0) | (d2 < 0) | (d3 < 0)) & ((d1 > 0) | (d2 > 0) | (d3 > 0)))
    area = abs((q1[0] - q3[0]) * (q2[1] - q3[1]) - (q2[0] - q3[0]) * (q1[1] - q3[1])) + 1e-5
    edge = np.minimum(np.minimum(np.abs(d1), np.abs(d2)), np.abs(d3)) / math.sqrt(area)
    mat_b[inside] = mat
    puff_b[inside] = np.minimum(1.0, edge[inside] * 0.22)


def stroke_line(mat_b, puff_b, x0, y0, x1, y1, mat, thick=0.65):
    vx = x1 - x0
    vy = (y1 - y0) / ASPECT_CHAR
    l2 = vx * vx + vy * vy + 1e-6
    ox = XX - x0
    oy = (YY - y0) / ASPECT_CHAR
    t = np.clip((ox * vx + oy * vy) / l2, 0.0, 1.0)
    dist = np.hypot(ox - t * vx, oy - t * vy)
    mask = dist <= thick
    mat_b[mask] = mat
    puff_b[mask] = 0.65


def apply_thin_outline(mat_b, target_mats):
    """Traza un contorno fino de 1 carácter alrededor de los materiales indicados."""
    in_set = np.isin(mat_b, target_mats)
    up = np.roll(in_set, -1, axis=0)
    dn = np.roll(in_set, 1, axis=0)
    lf = np.roll(in_set, -1, axis=1)
    rt = np.roll(in_set, 1, axis=1)
    edge = in_set & ~(up & dn & lf & rt)
    edge[:5, :] = False
    edge[-1:, :] = False
    edge[:, :1] = False
    edge[:, -1:] = False
    mat_b[edge] = M_INK


def draw_blush(mat_b, puff_b, cx, cy, rx, ry):
    fill_oval(mat_b, puff_b, cx, cy, rx, ry, M_BLUSH)
    for off in (-rx * 0.45, 0.0, rx * 0.45):
        stroke_line(
            mat_b,
            puff_b,
            cx + off - 0.8,
            cy + ry * 0.45 * ASPECT_CHAR,
            cx + off + 0.8,
            cy - ry * 0.45 * ASPECT_CHAR,
            M_INK,
            thick=0.45,
        )


# ==============================================================================
# ESCENA 1 (00:00 - 00:05): Hachiware sentado sobre el tocón tocando guitarra
# ==============================================================================
def shot_01_stump_guitar(mat_b, puff_b, t, singing):
    sp = 1.0 if singing else 0.15
    bounce = math.sin(t * 7.2 * sp) * 1.0
    sway = math.sin(t * 3.6 * sp) * 1.6
    strum = math.sin(t * 15.0 * sp) * 2.2

    cx = COLS * 0.50 + sway
    cy = 27.0 + bounce

    # 1. Césped ovalado en la base
    fill_oval(mat_b, puff_b, COLS * 0.50, 67.0, 46.0, 9.0, M_GRASS)
    for gx_b in range(18, 94, 9):
        gy_b = 65 + (gx_b % 3)
        stroke_line(mat_b, puff_b, gx_b, gy_b, gx_b - 0.8, gy_b - 1.5, M_INK, 0.4)
        stroke_line(mat_b, puff_b, gx_b + 1.5, gy_b, gx_b + 2.2, gy_b - 1.5, M_INK, 0.4)

    # 2. Tocón de árbol marrón debajo de Hachiware
    tx, ty = COLS * 0.50, 56.0
    fill_oval(mat_b, puff_b, tx, ty + 6.0, 22.0, 6.5, M_STUMP)
    fill_oval(mat_b, puff_b, tx, ty - 1.0, 18.5, 9.5, M_STUMP)
    apply_thin_outline(mat_b, [M_STUMP])
    for wx in (-10, -4, 3, 9):
        stroke_line(mat_b, puff_b, tx + wx, ty - 3, tx + wx * 1.15, ty + 7, M_INK, 0.45)

    # 3. Patitas inferiores asomando bajo la guitarra
    fill_oval(mat_b, puff_b, cx - 3.5, cy + 25.0, 3.8, 3.2, M_FUR)
    fill_oval(mat_b, puff_b, cx + 3.5, cy + 25.0, 3.8, 3.2, M_FUR)
    apply_thin_outline(mat_b, [M_FUR])

    # 4. Cuerpo blanco gordito
    fill_oval(mat_b, puff_b, cx, cy + 17.5, 17.5, 13.0, M_FUR)
    apply_thin_outline(mat_b, [M_FUR])

    # 5. Orejas azules
    fill_tri(mat_b, puff_b, (cx - 24, cy - 5), (cx - 19, cy - 23), (cx - 6, cy - 11), M_HAIR)
    fill_tri(mat_b, puff_b, (cx + 24, cy - 5), (cx + 19, cy - 23), (cx + 6, cy - 11), M_HAIR)

    # 6. Cabeza redonda y flequillo partido de Hachiware
    fill_oval(mat_b, puff_b, cx, cy, 25.5, 19.5, M_FUR)
    fill_tri(mat_b, puff_b, (cx - 23.5, cy - 3.5), (cx - 11, cy - 17.5), (cx, cy - 5.0), M_HAIR)
    fill_tri(mat_b, puff_b, (cx + 23.5, cy - 3.5), (cx + 11, cy - 17.5), (cx, cy - 5.0), M_HAIR)
    apply_thin_outline(mat_b, [M_FUR, M_HAIR])

    # 7. Cejas y ojos expresivos con reflejo blanco
    stroke_line(mat_b, puff_b, cx - 12, cy - 6.0, cx - 9.5, cy - 6.0, M_INK, 0.45)
    stroke_line(mat_b, puff_b, cx + 9.5, cy - 6.0, cx + 12, cy - 6.0, M_INK, 0.45)

    fill_oval(mat_b, puff_b, cx - 10.8, cy - 1.2, 3.4, 3.4, M_EYE)
    fill_oval(mat_b, puff_b, cx + 10.8, cy - 1.2, 3.4, 3.4, M_EYE)
    fill_oval(mat_b, puff_b, cx - 11.8, cy - 2.3, 1.3, 1.3, M_SHINE)
    fill_oval(mat_b, puff_b, cx + 9.8, cy - 2.3, 1.3, 1.3, M_SHINE)

    # 8. Mejillas rosadas
    draw_blush(mat_b, puff_b, cx - 17.5, cy + 3.0, 4.2, 2.3)
    draw_blush(mat_b, puff_b, cx + 17.5, cy + 3.0, 4.2, 2.3)

    # 9. Boca de gatito cantando con lengüita
    syl = (abs(math.sin(t * 8.5)) * 0.7 + abs(math.cos(t * 13.5)) * 0.3) if singing else 0.1
    stroke_line(mat_b, puff_b, cx - 3.2, cy + 3.8, cx - 1.0, cy + 4.8, M_INK, 0.55)
    stroke_line(mat_b, puff_b, cx - 1.0, cy + 4.8, cx, cy + 3.6, M_INK, 0.55)
    stroke_line(mat_b, puff_b, cx, cy + 3.6, cx + 1.0, cy + 4.8, M_INK, 0.55)
    stroke_line(mat_b, puff_b, cx + 1.0, cy + 4.8, cx + 3.2, cy + 3.8, M_INK, 0.55)
    if syl > 0.2:
        fill_oval(mat_b, puff_b, cx, cy + 6.2, 2.7, 1.3 + syl * 2.2, M_MOUTH)
        fill_oval(mat_b, puff_b, cx, cy + 7.0, 1.8, 0.9 + syl * 1.1, M_TONGUE)
        apply_thin_outline(mat_b, [M_MOUTH, M_TONGUE])

    # 10. Guitarra acústica
    gx, gy = cx - 2.5, cy + 17.5
    stroke_line(mat_b, puff_b, gx + 9, gy - 2.5, gx + 31, gy - 10.5, M_WOOD, 1.5)
    stroke_line(mat_b, puff_b, gx + 28, gy - 9.5, gx + 33, gy - 11.5, M_INK, 1.8)
    fill_oval(mat_b, puff_b, gx, gy, 14.0, 9.5, M_WOOD, -0.15)
    apply_thin_outline(mat_b, [M_WOOD])
    fill_oval(mat_b, puff_b, gx + 3.2, gy - 0.7, 3.6, 2.8, M_WOOD_DK)
    stroke_line(mat_b, puff_b, gx - 5.5, gy + 1.0, gx + 30, gy - 10.5, M_SHINE, 0.4)

    # 11. Manitas blancas tocando
    fill_oval(mat_b, puff_b, gx + 19, gy - 4.2, 4.2, 3.3, M_FUR)
    fill_oval(mat_b, puff_b, gx - 1, gy - 0.8 + strum * 0.65, 4.4, 3.5, M_FUR)
    apply_thin_outline(mat_b, [M_FUR])


# ==============================================================================
# ESCENA 2 (00:05 - 00:09): Primer plano inclinado "hitorigotsu..."
# ==============================================================================
def shot_02_closeup_tilt(mat_b, puff_b, t, singing):
    cx = COLS * 0.54 + math.sin(t * 2.8) * 1.5
    cy = 44.0 + math.sin(t * 6.5) * 1.0

    # Arbusto verde en la esquina inferior izquierda
    fill_oval(mat_b, puff_b, 14.0, 68.0, 18.0, 14.0, M_LEAF)
    fill_oval(mat_b, puff_b, 26.0, 73.0, 15.0, 11.0, M_LEAF)
    apply_thin_outline(mat_b, [M_LEAF])

    # Gran oreja azul izquierda y cabeza inclinada
    fill_tri(mat_b, puff_b, (cx - 46, cy - 16), (cx - 32, cy - 42), (cx - 10, cy - 22), M_HAIR)
    fill_oval(mat_b, puff_b, cx, cy + 4, 48.0, 38.0, M_FUR, tilt=-0.18)
    fill_tri(mat_b, puff_b, (cx - 44, cy - 12), (cx - 20, cy - 34), (cx - 2, cy - 14), M_HAIR)
    apply_thin_outline(mat_b, [M_FUR, M_HAIR])

    # Ojos grandes con brillo y cejas
    stroke_line(mat_b, puff_b, cx - 22, cy - 14, cx - 17, cy - 15, M_INK, 0.7)
    stroke_line(mat_b, puff_b, cx + 16, cy - 20, cx + 21, cy - 21, M_INK, 0.7)

    fill_oval(mat_b, puff_b, cx - 19, cy - 4, 6.2, 6.2, M_EYE)
    fill_oval(mat_b, puff_b, cx + 19, cy - 10, 6.2, 6.2, M_EYE)
    fill_oval(mat_b, puff_b, cx - 21, cy - 6, 2.3, 2.3, M_SHINE)
    fill_oval(mat_b, puff_b, cx + 17, cy - 12, 2.3, 2.3, M_SHINE)

    # Mejillas rayadas
    draw_blush(mat_b, puff_b, cx - 31, cy + 5, 7.5, 4.0)
    draw_blush(mat_b, puff_b, cx + 31, cy - 4, 7.5, 4.0)

    # Boca cantando con colmillitos y lengüita rosada
    syl = abs(math.sin(t * 8.0)) if singing else 0.2
    stroke_line(mat_b, puff_b, cx - 6.5, cy + 3.5, cx - 2.0, cy + 5.2, M_INK, 0.8)
    stroke_line(mat_b, puff_b, cx - 2.0, cy + 5.2, cx, cy + 3.0, M_INK, 0.8)
    stroke_line(mat_b, puff_b, cx, cy + 3.0, cx + 2.5, cy + 4.8, M_INK, 0.8)
    stroke_line(mat_b, puff_b, cx + 2.5, cy + 4.8, cx + 6.5, cy + 2.2, M_INK, 0.8)

    fill_oval(mat_b, puff_b, cx + 0.5, cy + 8.5, 5.2, 3.0 + syl * 3.0, M_MOUTH)
    fill_oval(mat_b, puff_b, cx + 1.0, cy + 10.0, 3.6, 1.8 + syl * 1.5, M_TONGUE)
    apply_thin_outline(mat_b, [M_MOUTH, M_TONGUE])


# ==============================================================================
# ESCENA 3 (00:09 - 00:13): Plano abierto con Chiikawa al fondo izquierdo
# ==============================================================================
def shot_03_with_chiikawa(mat_b, puff_b, t, singing):
    bounce = math.sin(t * 7.5) * 0.9
    cX, cY = 34.0, 34.0 - bounce * 0.6
    hX, hY = 92.0, 48.0 + bounce

    # Prado verde amplio al fondo
    fill_oval(mat_b, puff_b, COLS * 0.50, 44.0, 62.0, 26.0, M_GRASS)
    for gx_b in range(14, 98, 11):
        gy_b = 26 + (gx_b % 18)
        stroke_line(mat_b, puff_b, gx_b, gy_b, gx_b - 0.6, gy_b - 1.2, M_INK, 0.35)
        stroke_line(mat_b, puff_b, gx_b + 1.2, gy_b, gx_b + 1.8, gy_b - 1.2, M_INK, 0.35)

    # Chiikawa sentado en el pasto (izquierda)
    fill_oval(mat_b, puff_b, cX - 10, cY - 12, 3.6, 3.6, M_FUR)
    fill_oval(mat_b, puff_b, cX + 10, cY - 12, 3.6, 3.6, M_FUR)
    fill_oval(mat_b, puff_b, cX, cY + 13, 12.5, 9.5, M_FUR)
    fill_oval(mat_b, puff_b, cX, cY, 17.0, 13.5, M_FUR)
    apply_thin_outline(mat_b, [M_FUR])

    fill_oval(mat_b, puff_b, cX - 6.0, cY - 1.0, 2.2, 2.2, M_EYE)
    fill_oval(mat_b, puff_b, cX + 6.0, cY - 1.0, 2.2, 2.2, M_EYE)
    fill_oval(mat_b, puff_b, cX - 6.7, cY - 1.7, 0.8, 0.8, M_SHINE)
    fill_oval(mat_b, puff_b, cX + 5.3, cY - 1.7, 0.8, 0.8, M_SHINE)
    draw_blush(mat_b, puff_b, cX - 10.5, cY + 2.2, 2.8, 1.6)
    draw_blush(mat_b, puff_b, cX + 10.5, cY + 2.2, 2.8, 1.6)
    stroke_line(mat_b, puff_b, cX - 2.0, cY + 3.0, cX, cY + 4.0, M_INK, 0.45)
    stroke_line(mat_b, puff_b, cX, cY + 4.0, cX + 2.0, cY + 3.0, M_INK, 0.45)

    # Hachiware en primer plano derecho mirando hacia Chiikawa
    fill_tri(mat_b, puff_b, (hX - 28, hY - 8), (hX - 22, hY - 30), (hX - 7, hY - 14), M_HAIR)
    fill_tri(mat_b, puff_b, (hX + 24, hY - 8), (hX + 22, hY - 30), (hX + 6, hY - 14), M_HAIR)
    fill_oval(mat_b, puff_b, hX, hY + 4, 30.0, 24.0, M_FUR)
    fill_tri(mat_b, puff_b, (hX - 27, hY - 6), (hX - 14, hY - 21), (hX - 4, hY - 7), M_HAIR)
    fill_tri(mat_b, puff_b, (hX + 25, hY - 6), (hX + 12, hY - 21), (hX - 4, hY - 7), M_HAIR)
    apply_thin_outline(mat_b, [M_FUR, M_HAIR])

    # Ojo izquierdo y mejilla mirando a Chiikawa
    fill_oval(mat_b, puff_b, hX - 19, hY - 1, 3.6, 3.6, M_EYE)
    fill_oval(mat_b, puff_b, hX - 20.2, hY - 2.2, 1.3, 1.3, M_SHINE)
    draw_blush(mat_b, puff_b, hX - 11, hY + 5, 5.2, 2.8)
    syl = abs(math.sin(t * 8.5)) if singing else 0.1
    fill_oval(mat_b, puff_b, hX - 25, hY + 6, 2.4, 1.2 + syl * 2.0, M_MOUTH)
    apply_thin_outline(mat_b, [M_MOUTH])


def render_frame_buffers(t, singing, char_buf, col_buf):
    mat_b = np.full((ROWS, COLS), M_BG, dtype=np.uint8)
    puff_b = np.zeros((ROWS, COLS), dtype=np.float32)

    # Ciclo exacto de los primeros 13 segundos del video
    cycle = t % 13.0
    use_letterbox = False

    if cycle < 5.0:
        shot_idx = 1 + int(cycle)
        shot_01_stump_guitar(mat_b, puff_b, t, singing)
    elif cycle < 9.0:
        shot_idx = 6 + int(cycle - 5.0)
        shot_02_closeup_tilt(mat_b, puff_b, t, singing)
    else:
        shot_idx = 10 + int(cycle - 9.0)
        use_letterbox = True
        shot_03_with_chiikawa(mat_b, puff_b, t, singing)

    # Sombreado 3D direccional superior-izquierda
    gy, gx = np.gradient(puff_b * 5.0)
    lit = np.clip((gx * 0.45 + gy * 0.55 + 0.70) / 1.15, 0.0, 1.0)
    shade = np.clip(0.62 + 0.25 * lit + 0.22 * puff_b, 0.55, 1.12)

    ramp_arr = np.frombuffer(SHADE_RAMP.encode("ascii"), dtype=np.uint8)
    char_buf.fill(32)
    col_buf.fill(0)

    for mat, base_col in PALETTE.items():
        m = mat_b == mat
        if not np.any(m):
            continue
        if mat == M_INK:
            char_buf[m] = OUT_CHARS[(YY[m].astype(np.int32) * 7 + XX[m].astype(np.int32) * 13) % len(OUT_CHARS)]
            col_buf[m] = base_col
        elif mat == M_EYE:
            char_buf[m] = ord("@")
            col_buf[m] = base_col
        elif mat == M_SHINE:
            char_buf[m] = ord("*")
            col_buf[m] = base_col
        else:
            s_vals = shade[m]
            idx = np.clip((s_vals * (len(ramp_arr) - 1) * 0.85).astype(np.int32), 12, len(ramp_arr) - 1)
            char_buf[m] = ramp_arr[idx]
            col_buf[m] = np.clip(base_col * s_vals[:, None], 0, 255)

    # Barras letterbox superiores e inferiores en el plano 3 (00:09 - 00:13)
    if use_letterbox:
        char_buf[:12, :] = 32
        col_buf[:12, :] = 0
        char_buf[ROWS - 12 :, :] = 32
        col_buf[ROWS - 12 :, :] = 0
    else:
        char_buf[:5, :] = 32
        col_buf[:5, :] = 0

    letters_count = int(np.count_nonzero(char_buf != 32))
    return shot_idx, letters_count


def start_audio():
    if not os.path.exists(AUDIO_PATH):
        return False
    try:
        pygame.mixer.init()
        pygame.mixer.music.load(AUDIO_PATH)
        pygame.mixer.music.play(-1)
        return True
    except Exception:
        try:
            tmp_wav = "/tmp/hachiware_hitorigotsu.wav"
            if not os.path.exists(tmp_wav):
                subprocess.run(
                    ["ffmpeg", "-y", "-i", AUDIO_PATH, tmp_wav],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    check=True,
                )
            pygame.mixer.init()
            pygame.mixer.music.load(tmp_wav)
            pygame.mixer.music.play(-1)
            return True
        except Exception:
            return False


def run_hachiware(standalone=True):
    pygame.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()
    renderer = AsciiRenderer(CW, CH, FONT_PX)
    hud_font = pygame.font.SysFont(MONO, 13, bold=True)

    audio_loaded = start_audio()

    char_buf = np.full((ROWS, COLS), 32, dtype=np.int32)
    col_buf = np.zeros((ROWS, COLS, 3), dtype=np.float32)

    t = 0.0
    paused = False
    running = True

    while running:
        dt = clock.tick(FPS) / 1000.0
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    running = False
                elif ev.key == pygame.K_SPACE:
                    paused = not paused
                    if audio_loaded:
                        if paused:
                            pygame.mixer.music.pause()
                        else:
                            pygame.mixer.music.unpause()
                elif ev.key == pygame.K_r:
                    t = 0.0
                    if audio_loaded:
                        pygame.mixer.music.play(-1)
                        if paused:
                            pygame.mixer.music.pause()
                elif ev.key == pygame.K_s:
                    pygame.image.save(screen, f"hachiware_13s_{int(t)}.png")

        if not paused:
            t += dt

        shot_idx, letters_count = render_frame_buffers(t, not paused, char_buf, col_buf)
        renderer.render(screen, char_buf, col_buf)

        # HUD superior limpio
        s1 = hud_font.render("hachiware.py · ascii", True, (240, 244, 250))
        s2 = hud_font.render(f"shot {shot_idx:02d}/13  ♪ ひとりごつ", True, (215, 220, 230))
        s3 = hud_font.render(f"letters {letters_count:,}", True, (185, 192, 205))
        s_time = hud_font.render(f"• t {t % 13.0:05.2f}s / 13.00s", True, (255, 196, 90))
        s_hint = hud_font.render(HINT, True, (140, 148, 165))

        screen.blit(s1, (12, 8))
        screen.blit(s2, (12, 24))
        screen.blit(s3, (12, 40))
        screen.blit(s_time, (W - s_time.get_width() - 12, 8))
        screen.blit(s_hint, (12, H - 20))

        pygame.display.flip()

    if audio_loaded:
        pygame.mixer.music.stop()
    if standalone:
        pygame.quit()


def main():
    run_hachiware(standalone=True)


if __name__ == "__main__":
    main()