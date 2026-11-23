#!/usr/bin/env python3
"""
Menu Principal - Animaciones ASCII (Edición Celeste Hachiware)
Permite seleccionar y reproducir tanto el Árbol de Navidad ASCII como la animación de Hachiware (Chiikawa),
así como lanzar la versión Web interactiva.
"""
import os
import sys
import webbrowser

# Colores ANSI (celeste / azul suave)
SKY_BOLD = "\033[1;96m"      # Celeste brillante en negrita
SKY = "\033[0;96m"           # Celeste claro
BLUE_SOFT = "\033[0;94m"     # Azul pastel/suave
CYAN_DIM = "\033[2;36m"      # Celeste tenue para detalles
GREEN_SOFT = "\033[0;92m"    # Verde suave para mensajes de éxito/inicio
WARN_SOFT = "\033[0;93m"     # Amarillo suave para avisos
RESET = "\033[0m"


def enable_ansi_on_windows():
    """Habilita secuencias de escape ANSI en consolas de Windows."""
    if os.name == "nt":
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        except Exception:
            pass


def clear_screen():
    os.system("clear" if os.name == "posix" else "cls")


def show_terminal_menu():
    enable_ansi_on_windows()

    while True:
        clear_screen()
        print(f"""{SKY_BOLD}
   /\\_/\\   ╭────────────────────────────────────────────────────╮
  ( o.o )  │  ✦  HACHIWARE STUDIO · ANIMACIONES ASCII  ✦        │
   > ^ <   │      "¡Nanka chiisakute kawaii yatsu!" ~♪        │
  /  |  \\  ╰────────────────────────────────────────────────────╯{RESET}
{SKY}  ============================================================{RESET}
   {SKY_BOLD}[1]{RESET} 🎄  Árbol de Navidad 3D ASCII  {CYAN_DIM}(christmas_tree.py){RESET}
   {SKY_BOLD}[2]{RESET} 🐱  Hachiware - ひとりごつ      {CYAN_DIM}(hachiware.py){RESET}
   {SKY_BOLD}[3]{RESET} 🌐  Abrir Menú Web en Navegador  {CYAN_DIM}(index.html · :8080){RESET}
   {SKY_BOLD}[4]{RESET} 🐾  Salir del estudio
{SKY}  ============================================================{RESET}
{BLUE_SOFT}   Consejo: dentro de las animaciones, presiona [Esc] para volver.{RESET}
""")
        choice = input(f"{SKY_BOLD}   Elige una opción [1-4]: {RESET}").strip()

        if choice == "1":
            print(f"\n{GREEN_SOFT}   🎄 ¡Vamos! Iniciando Árbol de Navidad ASCII...{RESET}")
            try:
                import christmas_tree
                christmas_tree.main(standalone=False)
            except Exception as e:
                print(f"\n{WARN_SOFT}   Ups, ocurrió un error al ejecutar Árbol de Navidad: {e}{RESET}")
                input(f"{SKY}   Presiona Enter para volver al menú...{RESET}")

        elif choice == "2":
            print(f"\n{GREEN_SOFT}   🐱 ¡Nanka ii kanji! Iniciando Hachiware ASCII con Música...{RESET}")
            try:
                import hachiware
                hachiware.run_hachiware(standalone=False)
            except Exception as e:
                print(f"\n{WARN_SOFT}   Ups, ocurrió un error al ejecutar Hachiware: {e}{RESET}")
                input(f"{SKY}   Presiona Enter para volver al menú...{RESET}")

        elif choice == "3":
            print(f"\n{SKY_BOLD}   🌐 Levantando servidor local y abriendo versión Web...{RESET}")
            import threading
            import http.server
            import socketserver
            import functools

            port = 8080
            base_dir = os.path.dirname(os.path.abspath(__file__))

            def start_srv():
                try:
                    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=base_dir)
                    socketserver.TCPServer.allow_reuse_address = True
                    with socketserver.TCPServer(("", port), handler) as srv:
                        srv.serve_forever()
                except Exception as e:
                    print(f"\n{WARN_SOFT}   [Servidor en segundo plano]: {e}{RESET}")

            t = threading.Thread(target=start_srv, daemon=True)
            t.start()

            web_url = f"http://localhost:{port}/index.html"
            print(f"{SKY}   Abriendo:{RESET} {web_url}")
            webbrowser.open(web_url)
            input(f"\n{SKY}   Servidor activo. Presiona Enter para volver al menú...{RESET}")

        elif choice == "4":
            print(f"\n{SKY_BOLD}   /\\_/\\  ¡Hasta pronto! Cuídate mucho~ 🐾{RESET}")
            print(f"{SKY}  ( ^.^) {RESET}\n")
            sys.exit(0)

        else:
            print(f"\n{WARN_SOFT}   ( •_•)? Esa opción no existe. Intenta con un número del 1 al 4.{RESET}")
            input(f"{SKY}   Presiona Enter para continuar...{RESET}")


if __name__ == "__main__":
    show_terminal_menu()
