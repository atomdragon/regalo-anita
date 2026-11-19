import os
import sys
import time
import subprocess
import pygame

# --- Configuración de Ventana y Pantalla ---
TITLE = "ASCII Hachiware - ひとりごつ (Chiikawa)"
VIDEO_PATH = os.path.join(os.path.dirname(__file__), "video", "hachiware.mp4")
MUSIC_OGG = os.path.join(os.path.dirname(__file__), "music", "hitorigotsu.ogg")
MUSIC_MP3 = os.path.join(os.path.dirname(__file__), "music", "hitorigotsu.mp3")

BASE_W, BASE_H = 540, 960  # Resolución nativa proporcional (9:16)
FPS = 30

# Colores HUD
ACCENT = (255, 196, 90)
DIM = (96, 104, 122)
GREEN_DOT = (80, 220, 120)
TEXT_WHITE = (235, 240, 250)


class VideoStream:
    def __init__(self, filepath, width, height, fps=30):
        self.filepath = filepath
        self.w = width
        self.h = height
        self.fps = fps
        self.proc = None
        self.frame_bytes = width * height * 3
        self.start()

    def start(self):
        self.close()
        cmd = [
            "ffmpeg",
            "-re",
            "-i", self.filepath,
            "-f", "rawvideo",
            "-pix_fmt", "rgb24",
            "-s", f"{self.w}x{self.h}",
            "-r", str(self.fps),
            "-"
        ]
        self.proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            bufsize=self.frame_bytes * 5
        )

    def read_frame(self):
        if not self.proc or not self.proc.stdout:
            return None
        buf = self.proc.stdout.read(self.frame_bytes)
        if not buf or len(buf) != self.frame_bytes:
            return None
        return pygame.image.frombuffer(buf, (self.w, self.h), "RGB")

    def close(self):
        if self.proc:
            try:
                self.proc.terminate()
                self.proc.wait(timeout=0.5)
            except Exception:
                try:
                    self.proc.kill()
                except Exception:
                    pass
            self.proc = None


def run_hachiware(standalone=True):
    pygame.init()
    pygame.mixer.init()

    # Intentar cargar música
    music_loaded = False
    for mpath in [MUSIC_OGG, MUSIC_MP3]:
        if os.path.exists(mpath):
            try:
                pygame.mixer.music.load(mpath)
                music_loaded = True
                break
            except Exception as e:
                print(f"No se pudo cargar {mpath}: {e}")

    # Ventana escalable
    screen = pygame.display.set_mode((BASE_W, BASE_H), pygame.RESIZABLE)
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()

    hud_font = pygame.font.SysFont("consolas,menlo,dejavusansmono,monospace", 14)

    # Iniciar stream de video
    stream = VideoStream(VIDEO_PATH, BASE_W, BASE_H, FPS)

    if music_loaded:
        pygame.mixer.music.play()

    paused = False
    running = True
    last_surface = None
    t0 = time.time()
    elapsed = 0.0

    while running:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    paused = not paused
                    if music_loaded:
                        if paused:
                            pygame.mixer.music.pause()
                        else:
                            pygame.mixer.music.unpause()
                elif event.key == pygame.K_r:
                    # Reiniciar
                    stream.start()
                    if music_loaded:
                        pygame.mixer.music.play()
                    t0 = time.time()
                    elapsed = 0.0
                elif event.key == pygame.K_s:
                    fname = f"screenshot_hachiware_{int(time.time())}.png"
                    pygame.image.save(screen, fname)
                    print(f"Captura guardada: {fname}")

        if not paused:
            elapsed += dt
            frame_surf = stream.read_frame()
            if frame_surf is not None:
                last_surface = frame_surf
            else:
                # Loop video
                stream.start()
                frame_surf = stream.read_frame()
                if frame_surf is not None:
                    last_surface = frame_surf

        # Renderizar en pantalla
        screen.fill((10, 12, 18))
        if last_surface:
            # Escalar si la ventana cambió de tamaño
            cur_w, cur_h = screen.get_size()
            if cur_w != BASE_W or cur_h != BASE_H:
                # Mantener relación de aspecto
                scale = min(cur_w / BASE_W, cur_h / BASE_H)
                draw_w, draw_h = int(BASE_W * scale), int(BASE_H * scale)
                scaled = pygame.transform.smoothscale(last_surface, (draw_w, draw_h))
                off_x = (cur_w - draw_w) // 2
                off_y = (cur_h - draw_h) // 2
                screen.blit(scaled, (off_x, off_y))
            else:
                screen.blit(last_surface, (0, 0))

        # HUD Overlay de Controles
        help_txt = hud_font.render("Space: Pausa • R: Reiniciar • S: Captura • Esc: Volver al Menú", True, DIM)
        screen.blit(help_txt, (14, screen.get_height() - 24))

        if paused:
            pause_badge = hud_font.render("[ PAUSADO ]", True, ACCENT)
            screen.blit(pause_badge, (screen.get_width() // 2 - pause_badge.get_width() // 2, 40))

        pygame.display.flip()

    stream.close()
    if music_loaded:
        pygame.mixer.music.stop()

    if standalone:
        pygame.quit()


if __name__ == "__main__":
    run_hachiware(standalone=True)
