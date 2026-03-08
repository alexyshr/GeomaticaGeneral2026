# 1. IMPORTACIÓN DE LIBRERÍAS
import ee
import datetime
import arcpy # Necesario para interactuar con la interfaz de ArcGIS Pro

# 2. INICIALIZACIÓN (Siguiendo instrucciones del Toolbox)
# Reemplaza 'ee-giswqg' con tu ID de proyecto si es diferente
ee.Initialize(project='ee-giswqg')

# Opcional: Etiqueta de carga de trabajo
ee.data.setWorkloadTag("arcgis-ee-connector")

# 3. DEFINICIÓN DEL PUNTO GEOGRÁFICO
# UNAL Bogotá [Longitud, Latitud]
punto_unal = ee.Geometry.Point([-74.084, 4.638])

# 4. EXPLORAR Y FILTRAR COLECCIÓN
coleccion_l9 = (ee.ImageCollection("LANDSAT/LC09/C02/T1_TOA") 
    .filterBounds(punto_unal) 
    .filterDate('2023-01-01', '2023-12-31') 
    .sort('CLOUD_COVER'))

# 5. DIAGNÓSTICO: EXTRAER EL TOP 3 DE IMÁGENES
ids = coleccion_l9.aggregate_array('system:id').getInfo()
nubes = coleccion_l9.aggregate_array('CLOUD_COVER').getInfo()
fechas = coleccion_l9.aggregate_array('system:time_start').getInfo()

print("--- TOP 3 IMÁGENES CON MENOS NUBES EN EL AÑO 2023 ---")
for i in range(min(3, len(ids))):
    fecha_legible = datetime.datetime.fromtimestamp(fechas[i] / 1000.0, datetime.UTC).strftime('%Y-%m-%d')
    print(f"Opción {i+1} | Nubes: {nubes[i]:.2f}% | Fecha: {fecha_legible}")
print("----------------------------------------------------------------")

# 6. SELECCIÓN DE LA IMAGEN
l9_filtrado = coleccion_l9.first()
fecha_capa = datetime.datetime.fromtimestamp(l9_filtrado.get('system:time_start').getInfo() / 1000.0, datetime.UTC).strftime('%Y-%m-%d')

# 7. PARÁMETROS DE VISUALIZACIÓN
vis_params = {'bands': ['B4', 'B3', 'B2'], 'min': 0.0, 'max': 0.3}

# 8. ENVIAR LA CAPA AL MAPA DE ARCGIS PRO
# En el toolbox de ArcGIS, el método estándar para visualizar es usar 'addLayer'
# proporcionado por la integración del plugin.
try:
    # Intentamos añadir la capa al mapa activo
    # Nota: Algunos toolboxes requieren pasar el objeto ee y vis_params directamente
    arcpy.AddMessage(f"Añadiendo a ArcGIS: Landsat 9 RGB - {fecha_capa}")
    
    # Esta función depende de que el toolbox esté correctamente cargado en el entorno
    # Si 'geemap' está instalado en el entorno de ArcGIS Pro, podrías usar geemap.arcgis_layers
    import geemap
    Map = geemap.Map()
    Map.addLayer(l9_filtrado, vis_params, f'Landsat 9 RGB - {fecha_capa}')
    
    print(f"\n✅ CAPA ENVIADA AL MAPA: Landsat 9 RGB - {fecha_capa}")
except Exception as e:
    print(f"\n❌ Error al intentar visualizar en el mapa: {e}")
    print("El procesamiento en GEE terminó, pero no se pudo renderizar en el mapa.")

# 9. FINALIZACIÓN (Evita que la consola se cierre)
input("Presione Enter para salir...")