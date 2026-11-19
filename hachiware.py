import math
import numpy as np
import pygame

# --- Configuración de la ventana y cuadrícula ASCII ---
CW, CH, FONT_PX = 9, 13, 14
COLS, ROWS = 76, 54
W, H = COLS * CW, ROWS * CH
FPS = 30
RAMP = " .:-=+*#%@"

# --- Paleta de colores (R, G, B) ---
BG = (12, 14, 20)
INK = (32, 34, 42)
FUR = (242, 244, 250)
HAIR = (110, 175, 232)
BLUSH = (248, 130, 165)
WOOD = (190, 128, 65)
WOOD_DARK = (115, 72, 35)
STRINGS = (225, 215, 195)
NOTE_COL = (255, 205, 90)


class AsciiRenderer:
    def __init__(self, cw, ch, font_px):
        self.cw, self.ch = cw, ch
        font = pygame.font.SysFont("consolas,menlo,dejavusansmono,monospace", font_px, bold=True)
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


def draw_ellipse(char_b, col_b, cx, cy, rx, ry, col, ch="@", outline=True):
    y0, y1 = max(0, int(cy - ry - 2)), min(ROWS - 1, int(cy + ry + 2))
    x0, x1 = max(0, int(cx - rx - 2)), min(COLS - 1, int(cx + rx + 2))
    for r in range(y0, y1 + 1):
        for c in range(x0, x1 + 1):
            dx = (c - cx) / rx
            dy = (r - cy) / ry
            d = dx * dx + dy * dy
            if d <= 1.0:
                if outline and d > 0.78:
                    char_b[r, c] = ord("#")
                    col_b[r, c] = INK
                else:
                    # Sombreado suave 3D según distancia al centro
                    shade = max(0.65, 1.08 - 0.35 * d - 0.12 * dx - 0.12 * dy)
                    char_b[r, c] = ord(ch)
                    col_b[r, c] = np.clip(np.array(col) * shade, 0, 255)


def draw_triangle(char_b, col_b, p1, p2, p3, col, ch="%"):
    min_x = max(0, int(min(p1[0], p2[0], p3[0])))
    max_x = min(COLS - 1, int(max(p1[0], p2[0], p3[0])))
    min_y = max(0, int(min(p1[1], p2[1], p3[1])))
    max_y = min(ROWS - 1, int(max(p1[1], p2[1], p3[1])))

    def sign(a, b, c):
        return (a[0] - c[0]) * (b[1] - c[1]) - (b[0] - c[0]) * (a[1] - c[1])

    for r in range(min_y, max_y + 1):
        for c in range(min_x, max_x + 1):
            pt = (c, r)
            d1 = sign(pt, p1, p2)
            d2 = sign(pt, p2, p3)
            d3 = sign(pt, p3, p1)
            has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
            has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)
            if not (has_neg and has_pos):
                if abs(d1) < 18 or abs(d2) < 18 or abs(d3) < 18:
                    char_b[r, c] = ord("#")
                    col_b[r, c] = INK
                else:
                    char_b[r, c] = ord(ch)
                    col_b[r, c] = col


def draw_line(char_b, col_b, x0, y0, x1, y1, col, ch="=", thick=1):
    steps = int(max(abs(x1 - x0), abs(y1 - y0)) * 2) + 1
    for i in range(steps + 1):
        u = i / max(1, steps)
        cx = int(round(x0 + (x1 - x0) * u))
        cy = int(round(y0 + (y1 - y0) * u))
        for dy in range(-thick, thick + 1):
            for dx in range(-thick, thick + 1):
                r, c = cy + dy, cx + dx
                if 0 <= r < ROWS and 0 <= c < COLS:
                    char_b[r, c] = ord(ch)
                    col_b[r, c] = col


def animate_hachiware(t, char_b, col_b):
    char_b.fill(32)
    col_b[:] = BG

    # Movimiento rítmico al cantar y tocar
    bounce = math.sin(t * 7.5) * 1.3
    sway = math.sin(t * 3.75) * 1.8
    strum = math.sin(t * 15.0) * 2.2
    cx = COLS / 2 + sway
    cy = 23 + bounce

    # 1. Orejas azules
    draw_triangle(char_b, col_b, (cx - 17, cy - 5), (cx - 13, cy - 18), (cx - 4, cy - 8), HAIR, "%")
    draw_triangle(char_b, col_b, (cx + 17, cy - 5), (cx + 13, cy - 18), (cx + 4, cy - 8), HAIR, "%")

    # 2. Cuerpo blanco
    draw_ellipse(char_b, col_b, cx, cy + 16, 13, 10, FUR, "+", outline=True)

    # 3. Cabeza y flequillo azul estilo Hachiware
    draw_ellipse(char_b, col_b, cx, cy, 18, 11.5, FUR, "@", outline=True)
    # Flequillo partido en el centro
    draw_triangle(char_b, col_b, (cx - 16, cy - 4), (cx - 8, cy - 11), (cx, cy - 4), HAIR, "%")
    draw_triangle(char_b, col_b, (cx + 16, cy - 4), (cx + 8, cy - 11), (cx, cy - 4), HAIR, "%")

    # 4. Ojos, brillo, mejillas y boca cantando
    blink = (int(t * 1.2) % 5 == 0) and ((t * 1.2) % 1.0 < 0.12)
    if blink:
        draw_line(char_b, col_b, cx - 9, cy - 1, cx - 5, cy - 1, INK, "-", thick=0)
        draw_line(char_b, col_b, cx + 5, cy - 1, cx + 9, cy - 1, INK, "-", thick=0)
    else:
        draw_ellipse(char_b, col_b, cx - 7, cy - 1, 2.3, 1.7, INK, "@", outline=False)
        draw_ellipse(char_b, col_b, cx + 7, cy - 1, 2.3, 1.7, INK, "@", outline=False)
        # Brillo en los ojos
        char_b[int(cy - 2), int(cx - 8)] = ord("*")
        col_b[int(cy - 2), int(cx - 8)] = FUR
        char_b[int(cy - 2), int(cx + 6)] = ord("*")
        col_b[int(cy - 2), int(cx + 6)] = FUR

    # Rubor en mejillas
    draw_ellipse(char_b, col_b, cx - 12, cy + 2.5, 3.0, 1.4, BLUSH, ":", outline=False)
    draw_ellipse(char_b, col_b, cx + 12, cy + 2.5, 3.0, 1.4, BLUSH, ":", outline=False)

    # Boca (cambia según el ritmo de la canción)
    mouth_open = 1.6 + 1.1 * abs(math.sin(t * 9.0))
    draw_ellipse(char_b, col_b, cx, cy + 4.2, 2.6, mouth_open, (225, 95, 115), "o", outline=True)

    # 5. Guitarra acústica
    gx, gy = cx - 2, cy + 16
    draw_line(char_b, col_b, gx + 7, gy - 2, gx + 23, gy - 8, WOOD_DARK, "=", thick=1)
    draw_ellipse(char_b, col_b, gx, gy, 9.5, 6.2, WOOD, "#", outline=True)
    draw_ellipse(char_b, col_b, gx + 2, gy - 0.5, 2.8, 1.8, WOOD_DARK, ".", outline=False)
    draw_line(char_b, col_b, gx - 4, gy + 1, gx + 22, gy - 8, STRINGS, "-", thick=0)

    # 6. Brazos (uno sosteniendo el mástil, otro rasgueando)
    draw_ellipse(char_b, col_b, gx + 14, gy - 3, 3.2, 2.2, FUR, "+", outline=True)
    draw_ellipse(char_b, col_b, gx - 1, gy - 1 + strum * 0.6, 3.5, 2.3, FUR, "+", outline=True)

    # 7. Notas musicales flotando
    notes = ["♪", "♫", "♩"]
    for i in range(3):
        nt = (t * 0.9 + i * 0.33) % 1.0
        nx = int(cx + 16 + math.sin(nt * 6 + i) * 4 + nt * 8)
        ny = int(cy - 6 - nt * 16)
        if 1 <= ny < ROWS - 1 and 1 <= nx < COLS - 1:
            char_b[ny, nx] = ord("*") if i == 2 else ord("d")
            col_b[ny, nx] = NOTE_COL


def main():
    pygame.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Hachiware ASCII")
    clock = pygame.time.Clock()
    renderer = AsciiRenderer(CW, CH, FONT_PX)

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

        if not paused:
            t += dt

        animate_hachiware(t, char_buf, col_buf)
        renderer.render(screen, char_buf, col_buf)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()