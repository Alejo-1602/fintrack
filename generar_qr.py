"""
Script para generar el código QR de acceso a FinTrack
Permite a cualquier persona escanearlo con la cámara del celular
y acceder directamente a la aplicación web desplegada en la nube.

Uso:
    python generar_qr.py https://fintrack.onrender.com
o simplemente:
    python generar_qr.py
"""

import sys
import os

try:
    import qrcode
    from PIL import Image
except ImportError:
    print("\n[ERROR] Falta instalar la librería 'qrcode' o 'Pillow'.")
    print("Ejecuta en tu terminal: pip install qrcode[pil]\n")
    sys.exit(1)


def generar_codigo_qr(url_destino: str, nombre_salida: str = "fintrack_qr.png"):
    """
    Genera una imagen PNG con el código QR que apunta a la URL especificada.
    """
    url_limpia = url_destino.strip()
    if not url_limpia:
        print("[ERROR] La URL no puede estar vacía.")
        return False

    # Agregar esquema si el usuario olvidó https://
    if not (url_limpia.startswith("http://") or url_limpia.startswith("https://")):
        url_limpia = "https://" + url_limpia

    print(f"\n[+] Generando código QR para: {url_limpia}")

    # Configuración de alta calidad para el QR
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # Alta tolerancia a errores (30%)
        box_size=12,  # Tamaño de cada módulo de píxeles
        border=4,     # Grosor del margen blanco
    )

    qr.add_data(url_limpia)
    qr.make(fit=True)

    # Crear imagen con colores de marca FinTrack (azul marino elegante y fondo blanco)
    imagen_qr = qr.make_image(fill_color="#1e3a8a", back_color="#ffffff")

    # Guardar en la misma carpeta del script
    directorio_actual = os.path.dirname(os.path.abspath(__file__))
    ruta_guardado = os.path.join(directorio_actual, nombre_salida)

    imagen_qr.save(ruta_guardado)
    print(f"[OK] Código QR generado con éxito:")
    print(f"     -> Archivo: {nombre_salida}")
    print(f"     -> Ubicación: {ruta_guardado}")
    print("     -> Ya puedes escanearlo con la cámara de tu teléfono móvil.\n")
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("      FinTrack - Generador de Código QR de Despliegue")
    print("=" * 60)

    # Si se pasa como argumento por consola: python generar_qr.py https://...
    if len(sys.argv) > 1:
        url_input = sys.argv[1]
    else:
        try:
            url_input = input("\nIngresa la URL pública de FinTrack (ej: https://fintrack.onrender.com): ")
        except (KeyboardInterrupt, EOFError):
            print("\nOperación cancelada.")
            sys.exit(0)

    generar_codigo_qr(url_input)
