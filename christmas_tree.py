import math
import numpy as np
import pygame

# --- Configuración de la ventana y la cuadrícula ASCII ---
TITLE = "ASCII Christmas Tree"
CW, CH, FONT_PX = 9, 14, 15
COLS, ROWS = 88, 74
W, H = COLS * CW, ROWS * CH
MONO = "consolas,menlo,dejavusansmono,couriermonospace,monospace"
HINT = "Space pause • R restart • S screenshot • Esc menú"
DIM, ACCENT, SIGN = (96, 104, 122), (255, 196, 90), (170, 180, 196)

# --- Constantes de geometría y escena ---
TAU = 2.0 * math.pi
GROUND = 0.0
Y0 = 0.35      # Base del follaje
Y1 = 3.25      # Punta del árbol
T_STAR = 11.5  # Momento en que aparece la estrella
T_MSG = 13.0   # Momento en que aparece el mensaje
MESSAGE = "MERRY CHRISTMAS 2026"

# --- Paleta de colores ---
GREEN = np.array([38, 168, 72], dtype=np.float32)
WHITE = np.array([235, 242, 250], dtype=np.float32)
TRUNK = np.array([120, 78, 48], dtype=np.float32)
GOLD = np.array([255, 200, 60], dtype=np.float32)
TINSEL = np.array([235, 238, 245], dtype=np.float32)
RED = np.array([230, 52, 58], dtype=np.float32)
SILVER = np.array([205, 215, 228], dtype=np.float32)
GREEN_BOX = np.array([34, 155, 68], dtype=np.float32)
T_LIGHTS = np.array([
    [255, 70, 70],
    [255, 205, 65],
    [70, 185, 255],
    [255, 110, 210],
    [95, 235, 120],
], dtype=np.float32)

# Caracteres ordenados por densidad visual (luminancia)
RAMP = " .'`^\",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"


class Parts:
    def __init__(self):
        self.p = []
        self.c = []
        self.t0 = []
        self.base = []
        self.phase = []

    def add(self, pts, cols, t0, base=0.55, phase=0.0):
        n = len(pts)
        self.p.append(pts)
        self.c.append(cols)
        self.t0.append(np.full(n, t0, dtype=np.float32) if np.isscalar(t0) else t0.astype(np.float32))
        self.base.append(np.full(n, base, dtype=np.float32) if np.isscalar(base) else base.astype(np.float32))
        self.phase.append(np.full(n, phase, dtype=np.float32) if np.isscalar(phase) else phase.astype(np.float32))

    def pack(self):
        return (
            np.vstack(self.p).astype(np.float32),
            np.vstack(self.c).astype(np.float32),
            np.concatenate(self.t0),
            np.concatenate(self.base),
            np.concatenate(self.phase),
        )


def grow_time(y):
    return (T_GROW[1] - T_GROW[0]) * np.clip((y - GROUND) / (Y1 - GROUND), 0.0, 1.0) + T_GROW[0]


T_GROW = (0.4, 5.2)


def fib_sphere(n):
    i = np.arange(n, dtype=np.float32) + 0.5
    phi = np.arccos(1.0 - 2.0 * i / n)
    theta = TAU * i / ((1.0 + math.sqrt(5.0)) / 2.0)
    return np.stack([np.sin(phi) * np.cos(theta), np.cos(phi), np.sin(phi) * np.sin(theta)], axis=1)


def build():
    rng = np.random.default_rng(7)
    q = Parts()
    tips = []

    # 1. Agujas / ramas del árbol (más densas y largas en la base)
    for i, y in enumerate(np.linspace(Y0 + 0.02, Y1 - 0.06, 24)):
        u = (y - Y0) / (Y1 - Y0)
        R = (1.0 - u) ** 0.85 * 1.15 + 0.05
        nb = int(6 + 12 * (1 - u))
        for b in range(nb):
            a = TAU * (b + 0.5 * rng.random()) / nb + i * 0.77
            L = R * rng.uniform(0.85, 1.08)
            n = int(25 + 170 * L)
            s = rng.random(n) ** 0.65
            d = np.array([np.cos(a), 0.0, np.sin(a)])
            side = np.array([-np.sin(a), 0.0, np.cos(a)])
            spread = (0.025 + 0.09 * s) * rng.normal(0, 1, n)
            sl = s * L
            p = d * sl[:, None] + side * spread[:, None]
            p[:, 1] = y + 0.06 * sl - 0.28 * sl**2 + 0.012 * rng.normal(0, 1, n)
            snow = (s > 0.5) & (rng.random(n) < 0.06) & (rng.normal(0, 1, n) > 0.3)
            green = np.array([0.18, 0.48, 0.18]) + np.array([0.12, 0.28, 0.14]) * rng.random((n, 3))
            green = green * 255.0
            q.add(p, np.where(snow[:, None], WHITE, green), grow_time(p[:, 1]),
                  base=np.where(snow, 1.0, 0.6))
            t1 = 0.99 * L
            tips.append(d * t1 + np.array([0.0, y + 0.06 * t1 - 0.28 * t1**2, 0.0]))

    # 2. Cono interior oscuro (evita que la nieve trasera atraviese las ramas)
    n = 6000
    y = Y0 + (Y1 - 0.1 - Y0) * rng.random(n)
    phi = rng.random(n) * TAU
    out = np.stack([np.cos(phi), np.full(n, 0.3), np.sin(phi)], 1)
    r = 0.6 * ((1.0 - (y - Y0) / (Y1 - Y0)) ** 0.85 * 1.15)
    q.add(np.stack([r * np.cos(phi), y, r * np.sin(phi)], 1), np.zeros((n, 3)), grow_time(y), base=0.75)

    # 3. Tronco
    m = 1500
    y = GROUND + rng.random(m) * (Y0 + 0.1 - GROUND)
    phi = rng.random(m) * TAU
    bark = 0.75 + 0.25 * np.sin(10 * phi + 30 * y)
    r_tr = 0.14
    q.add(np.stack([r_tr * np.cos(phi), y, r_tr * np.sin(phi)], 1),
          TRUNK * bark[:, None], grow_time(y), base=0.65)

    # 4. Guirnalda de espumillón (espiral dorada y plateada)
    u = np.linspace(0, 1, 2600)
    turns = 3.4
    yg = Y0 + 0.15 + (Y1 - Y0 - 0.45) * u
    ag = TAU * turns * u + 0.9
    swag = -0.07 * np.abs(np.sin(ag * 2.5))
    rg = ((1.0 - u) ** 0.87) * 1.18 + 0.06
    line = np.stack([rg * np.cos(ag), yg + swag, rg * np.sin(ag)], 1)
    for _ in range(6):
        q.add(line + 0.016 * rng.normal(0, 1, line.shape),
              np.where(rng.random((len(u), 1)) < 0.7, GOLD, TINSEL),
              6.0 + 1.8 * u, base=0.95, phase=rng.random(len(u)) * TAU)

    # 5. Esferas navideñas (rojas, doradas y plateadas)
    sphere = fib_sphere(60)
    for k in range(34):
        u = (k + rng.random()) / 34
        y = Y0 + 0.08 + u * (Y1 - Y0 - 0.38)
        a = k * 2.39996 + rng.random() * 0.4
        c = np.array([np.cos(a), 0.0, np.sin(a)]) * (((1.0 - u) ** 0.85 * 1.15) * 0.92) + [0.0, y, 0.0]
        rad = 0.058 + 0.032 * (1 - u)
        col = RED if k % 2 == 0 else (GOLD if k % 4 == 1 else SILVER)
        q.add(c + sphere * rad, np.tile(col, (len(sphere), 1)), 7.2 + 1.4 * u, base=0.9)

    # 6. Luces de hadas en las puntas de las ramas
    tips = np.array(tips)
    pick = rng.choice(len(tips), size=min(170, len(tips)), replace=False)
    bulb = fib_sphere(16)
    light_t0 = 8.4 + rng.random(len(pick)) * 1.6
    for c, tm in zip(tips[pick], light_t0):
        col = T_LIGHTS[rng.integers(0, len(T_LIGHTS))]
        q.add(c + bulb * 0.03, np.tile(col, (len(bulb), 1)), tm, base=1.0, phase=rng.random() * TAU)

    # 7. Regalos en la base con lazo cruzado
    gifts = [
        (0.9, 1.12, 0.36, 0.24, 0.28, 0.4, RED, GOLD),
        (1.5, 1.18, 0.26, 0.30, 0.22, -0.3, GREEN_BOX, RED),
        (2.6, 1.10, 0.34, 0.18, 0.25, 1.0, GOLD, RED),
        (3.7, 1.18, 0.34, 0.26, 0.28, 0.2, RED, SILVER),
        (4.7, 1.12, 0.30, 0.20, 0.32, 0.8, GREEN_BOX, RED),
        (5.6, 1.22, 0.28, 0.22, 0.24, -0.5, GOLD, RED),
    ]
    for g, (a, dist, w, h, d, rot, body, rib) in enumerate(gifts):
        areas = np.array([w * d, h * d, h * w] * 2)
        m = int(5000 * areas.sum())
        face = rng.choice(6, m, p=areas / areas.sum())
        fa, fb = rng.random(m) - 0.5, rng.random(m) - 0.5
        lx = np.select([face == 0, face == 1], [0.5, -0.5], fa) * w
        ly = np.select([face == 2, face == 3], [0.5, -0.5], np.where(face < 2, fa, fb)) * h
        lz = np.select([face == 4, face == 5], [0.5, -0.5], fb) * d
        on_x = np.abs(lx) < 0.032
        on_z = np.abs(lz) < 0.032
        ribbon = np.select([face < 2, face < 4], [on_z, on_x | on_z], on_x)
        ca, sa = math.cos(rot), math.sin(rot)
        px = dist * math.cos(a) + lx * ca - lz * sa
        pz = dist * math.sin(a) + lx * sa + lz * ca
        py = GROUND + h * 0.5 + ly
        pts_g = np.stack([px, py, pz], 1)
        cols_g = np.where(ribbon[:, None], rib, body)
        q.add(pts_g, cols_g, 9.8 + g * 0.22, base=0.85)

    return q.pack()


def project(pts, yaw, aspect):
    cy, sy = math.cos(yaw), math.sin(yaw)
    x = pts[:, 0] * cy - pts[:, 2] * sy
    z = pts[:, 0] * sy + pts[:, 2] * cy + 4.3
    y = pts[:, 1] - 1.55
    f = 1.65 / np.maximum(z, 0.2)
    sx = (x * f * aspect * 0.5 + 0.5) * COLS
    sy_scr = (-y * f * 0.5 + 0.5) * ROWS
    return sx, sy_scr, z


def putchar(char_buf, col_buf, r, c, ch, tint, bright=1.0):
    if 0 <= r < ROWS and 0 <= c < COLS:
        char_buf[r, c] = ord(ch) if isinstance(ch, str) else ch
        col_buf[r, c] = np.clip(tint * bright, 0, 255)


def star(char_buf, col_buf, cx, cy, size, t, power, flash=0.0):
    if power <= 0.01:
        return
    tint = np.array(GOLD) * (1.0 - flash) + np.array(WHITE) * flash
    power = power * (1.0 + 1.6 * flash)
    for k in range(8):
        ang = k * TAU / 8 + 0.18 * np.sin(t * 0.7)
        if np.sin(ang) < -0.3:
            continue
        reach = size * (1.0 if k % 2 == 0 else 0.55) * (0.92 + 0.08 * np.sin(t * 3.1 + k * 1.3))
        ch = "|/-\\"[int(round(np.degrees(ang) % 180 / 45)) % 4]
        for s in np.arange(0.15, reach, 0.35):
            y_s = int(round(cy - np.sin(ang) * s))
            x_s = int(round(cx + np.cos(ang) * s * 1.85))
            b = power * max(0.2, 1.0 - s / max(reach, 0.1))
            putchar(char_buf, col_buf, y_s, x_s, ch, tint, b)
    putchar(char_buf, col_buf, int(round(cy)), int(round(cx)), "@", WHITE, min(1.5, power * 1.3))


class Renderer:
    def __init__(self, self_cw, self_ch, font_px):
        self.cw, self.ch = self_cw, self_ch
        font = pygame.font.SysFont(MONO, font_px)
        self.atlas = []
        for code in range(32, 127):
            g = font.render(chr(code), True, (255, 255, 255))
            s = pygame.Surface((self.cw, self.ch))
            s.fill((0, 0, 0))
            s.blit(g, ((self.cw - g.get_width()) // 2, (self.ch - g.get_height()) // 2))
            self.atlas.append(pygame.surfarray.array3d(s).transpose(1, 0, 2))
        self.atlas = np.array(self.atlas, dtype=np.uint16)

    def draw(self, screen, char_buf, col_buf):
        idx = np.clip(char_buf - 32, 0, len(self.atlas) - 1)
        glyphs = self.atlas[idx]  # (ROWS, COLS, CH, CW, 3)
        colored = (glyphs * col_buf[:, :, None, None, :].astype(np.uint16)) >> 8
        img = colored.transpose(0, 2, 1, 3, 4).reshape(ROWS * self.ch, COLS * self.cw, 3).astype(np.uint8)
        pygame.surfarray.blit_array(screen, img.transpose(1, 0, 2))


def main(standalone=True):
    pygame.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()
    renderer = Renderer(CW, CH, FONT_PX)
    hud_font = pygame.font.SysFont(MONO, 13)

    pts, cols, t0, base, phase = build()
    rng_snow = np.random.default_rng(42)
    snow_x = rng_snow.uniform(0, COLS, 240)
    snow_y = rng_snow.uniform(0, ROWS, 240)
    snow_v = rng_snow.uniform(2.2, 6.5, 240)
    snow_c = np.where(snow_v > 4.5, ord("*"), ord("."))

    t = 0.0
    paused = False
    aspect = (COLS * CW) / (ROWS * CH)

    running = True
    while running:
        dt = clock.tick(30) / 1000.0
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    running = False
                elif ev.key == pygame.K_SPACE:
                    paused = not paused
                elif ev.key == pygame.K_r:
                    t = 0.0
                elif ev.key == pygame.K_s:
                    pygame.image.save(screen, f"christmas_tree_{int(t)}.png")

        if not paused:
            t += dt
            snow_y = (snow_y + snow_v * dt) % ROWS
            snow_x = (snow_x + np.sin(t * 0.8 + snow_v) * 1.4 * dt) % COLS

        char_buf = np.full((ROWS, COLS), 32, dtype=np.int32)
        col_buf = np.zeros((ROWS, COLS, 3), dtype=np.float32)

        # Nieve de fondo
        for sx, sy, sc in zip(snow_x.astype(int), snow_y.astype(int), snow_c):
            putchar(char_buf, col_buf, sy, sx, chr(sc), WHITE, 0.55)

        # Proyección 3D y Z-buffer
        yaw = t * 0.52
        sx, sy, z = project(pts, yaw, aspect)
        vis = (t >= t0) & (sx >= 0) & (sx < COLS) & (sy >= 0) & (sy < ROWS)
        vi = np.nonzero(vis)[0]
        order = vi[np.argsort(-z[vi])]  # De atrás hacia adelante (painter's algorithm)

        twinkle = 0.78 + 0.22 * np.sin(t * 4.5 + phase[order])
        bright = base[order] * twinkle * np.clip(4.6 / np.maximum(z[order], 1.5), 0.45, 1.25)
        r_idx = sy[order].astype(np.int32)
        c_idx = sx[order].astype(np.int32)
        ramp_i = np.clip((bright * (len(RAMP) - 1) * 0.78).astype(np.int32), 1, len(RAMP) - 1)
        chars_arr = np.frombuffer(RAMP.encode("ascii"), dtype=np.uint8)[ramp_i]

        char_buf[r_idx, c_idx] = chars_arr
        col_buf[r_idx, c_idx] = np.clip(cols[order] * bright[:, None], 0, 255)

        # Estrella en la cima
        if t >= T_STAR:
            flash = float(np.clip(1.0 - (t - T_STAR) / 1.0, 0.0, 1.0) ** 2)
            tx, ty, _ = project(np.array([[0.0, Y1 + 0.09, 0.0]]), yaw, aspect)
            star(char_buf, col_buf, float(tx[0]), float(ty[0]), 4.2, t,
                 min(1.0, (t - T_STAR) / 0.8), flash=flash)

        # Mensaje inferior
        if t >= T_MSG:
            row_id = ROWS - 9
            col0 = (COLS - len(MESSAGE)) // 2
            shown = min(len(MESSAGE), int((t - T_MSG) * 18))
            char_buf[row_id - 1:row_id + 2, max(0, col0 - 3):col0 + shown + 3] = 32
            for i, ch in enumerate(MESSAGE[:shown]):
                tint = (RED, GOLD, GREEN_BOX)[(i // 2 + int(t * 1.5)) % 3]
                putchar(char_buf, col_buf, row_id, col0 + i, ch, tint, 0.85 + 0.25 * np.sin(t * 5 + i))

        screen.fill((10, 12, 18))
        renderer.draw(screen, char_buf, col_buf)

        # HUD superior e inferior
        fps_surf = hud_font.render(f"• t {t:05.2f}s  • {int(clock.get_fps())} fps", True, ACCENT)
        screen.blit(fps_surf, (W - fps_surf.get_width() - 14, 10))
        info_surf = hud_font.render(f"@decmimh.ascii  |  rotation {math.degrees(yaw) % 360:05.1f}°  |  {HINT}", True, DIM)
        screen.blit(info_surf, (14, H - 22))

        pygame.display.flip()

    if standalone:
        pygame.quit()


if __name__ == "__main__":
    main(standalone=True)