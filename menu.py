#!/usr/bin/env python3
"""
Menu Principal - Animaciones ASCII
Permite seleccionar y reproducir tanto el Árbol de Navidad ASCII como la animación de Hachiware (Chiikawa),
así como lanzar la versión Web interactiva o ver el video original.
"""
import os
import sys
import webbrowser
import subprocess

def show_terminal_menu():
    while True:
        os.system('clear' if os.name == 'posix' else 'cls')
        print(r"""
============================================================
       ✨ STUDIO DE ANIMACIONES ASCII INTERACTIVAS ✨
============================================================
  1. 🎄 Árbol de Navidad 3D ASCII (christmas_tree.py)
  2. 🐱 Hachiware - ひとりごつ / Chiikawa (hachiware.py)
  3. 🌐 Abrir Menú Web Completo en Navegador (index.html)
  4. 🎬 Ver Video Original de Hachiware (MP4)
  5. 🚪 Salir
============================================================
""")
        choice = input("Selecciona una opción [1-5]: ").strip()

        if choice == "1":
            print("\nIniciando Árbol de Navidad ASCII... (Presiona Esc dentro de la ventana para volver al menú)")
            try:
                import christmas_tree
                christmas_tree.main(standalone=False)
            except Exception as e:
                print(f"Error al ejecutar Árbol de Navidad: {e}")
                input("Presiona Enter para continuar...")
        elif choice == "2":
            print("\nIniciando Hachiware ASCII con Música... (Presiona Esc dentro de la ventana para volver al menú)")
            try:
                import hachiware
                hachiware.run_hachiware(standalone=False)
            except Exception as e:
                print(f"Error al ejecutar Hachiware: {e}")
                input("Presiona Enter para continuar...")
        elif choice == "3":
            print("\nIniciando servidor local y abriendo versión Web interactiva...")
            import threading
            import http.server
            import socketserver

            port = 8080
            # Intentar lanzar servidor web local
            def start_srv():
                try:
                    handler = http.server.SimpleHTTPRequestHandler
                    with socketserver.TCPServer(("", port), handler) as srv:
                        srv.serve_forever()
                except Exception:
                    pass

            t = threading.Thread(target=start_srv, daemon=True)
            t.start()
            
            web_url = f"http://localhost:{port}/index.html"
            print(f"Abriendo: {web_url}")
            webbrowser.open(web_url)
            input("Presiona Enter para volver al menú...")
        elif choice == "4":
            video_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "video", "hachiware.mp4"))
            print(f"\nAbriendo video original: {video_path}")
            try:
                # Intentar abrir con el reproductor del sistema
                if sys.platform.startswith('linux'):
                    subprocess.Popen(['xdg-open', video_path])
                elif sys.platform == 'darwin':
                    subprocess.Popen(['open', video_path])
                elif sys.platform.startswith('win'):
                    os.startfile(video_path)
            except Exception as e:
                # Fallback al navegador
                webbrowser.open(f"file://{video_path}")
            input("Presiona Enter para continuar...")
        elif choice == "5":
            print("\n¡Hasta pronto!")
            sys.exit(0)
        else:
            print("Opción inválida. Intenta nuevamente.")
            input("Presiona Enter para continuar...")


if __name__ == "__main__":
    show_terminal_menu()
