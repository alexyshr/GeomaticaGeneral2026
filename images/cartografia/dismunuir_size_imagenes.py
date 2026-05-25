# testenv 3.11.14
# conda install pillow -y
# conda list pillow

import os
from PIL import Image

def optimizar_desde_directorio_actual(tamano_max_mb=1.0, ancho_maximo=1600):
    """
    Evalúa de forma recursiva las imágenes en el directorio de ejecución.
    Aplica compresión y redimensionamiento proporcional solo a archivos > 1 MB.
    """
    # Determinar la ruta donde se encuentra guardado el script
    ruta_actual = os.path.dirname(os.path.abspath(__file__))
    bytes_maximos = tamano_max_mb * 1024 * 1024
    formatos_soportados = ('.png', '.jpg', '.jpeg', '.tiff')
    
    modificadas = 0
    omitidas = 0

    print(f"Directorio de análisis: {ruta_actual}")
    print(f"Umbral de activación: > {tamano_max_mb} MB\n")

    for raiz, _, archivos in os.walk(ruta_actual):
        for archivo in archivos:
            # Evitar que el script se procese a sí mismo
            if archivo == os.path.basename(__file__):
                continue
                
            if archivo.lower().endswith(formatos_soportados):
                ruta_completa = os.path.join(raiz, archivo)
                tamano_archivo = os.path.getsize(ruta_completa)
                
                # Condición de activación por peso del archivo
                if tamano_archivo > bytes_maximos:
                    try:
                        with Image.open(ruta_completa) as img:
                            ancho, alto = img.size
                            formato_original = img.format
                            
                            # Redimensionamiento proporcional (mantiene la relación de aspecto)
                            if ancho > ancho_maximo:
                                factor_escala = ancho_maximo / float(ancho)
                                nuevo_alto = int(float(alto) * float(factor_escala))
                                img_procesada = img.resize((ancho_maximo, nuevo_alto), Image.Resampling.LANCZOS)
                                dimensiones_texto = f"{ancho}x{alto}px -> {ancho_maximo}x{nuevo_alto}px"
                            else:
                                # Si las dimensiones son aceptables, solo se procesa para compresión
                                img_procesada = img.copy()
                                dimensiones_texto = f"{ancho}x{alto}px (Dimensiones originales preservadas)"
                            
                            # Guardado optimizado sobrescribiendo el archivo original
                            if formato_original == 'PNG':
                                img_procesada.save(ruta_completa, format=formato_original, optimize=True)
                            else:
                                img_procesada.save(ruta_completa, format=formato_original, quality=80, optimize=True)
                                
                        nuevo_tamano = os.path.getsize(ruta_completa)
                        print(f"[MODIFICADA] {os.path.relpath(ruta_completa, ruta_actual)}")
                        print(f"  - Geometría: {dimensiones_texto}")
                        print(f"  - Peso: {tamano_archivo/1024/1024:.2f} MB -> {nuevo_tamano/1024/1024:.2f} MB")
                        modificadas += 1
                        
                    except Exception as e:
                        print(f"[ERROR] No se pudo procesar {archivo}: {str(e)}")
                else:
                    # Archivos que ya cumplen con el límite de peso
                    omitidas += 1

    print("\n--- Resumen de procesamiento ---")
    print(f"Imágenes optimizadas: {modificadas}")
    print(f"Imágenes omitidas (cumplen el peso): {omitidas}")

if __name__ == "__main__":
    optimizar_desde_directorio_actual(tamano_max_mb=1.0, ancho_maximo=1920)