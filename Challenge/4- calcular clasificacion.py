import os
import pandas as pd
from dotenv import load_dotenv  # Para manejar el archivo .env

# Cargar variables de entorno desde .env
load_dotenv()

# Obtener las rutas de los archivos CSV desde el archivo .env
# Usamos la ruta relativa para evitar problemas con ubicaciones de archivos
CSV_INPUT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.getenv('CSV_INPUT_FILE'))  # Tomamos la ruta relativa al script

# Obtener la ruta absoluta del directorio actual
current_directory = os.path.dirname(os.path.realpath(__file__))

# Crear la ruta completa para el archivo de salida en el mismo directorio
CSV_OUTPUT_FILE = os.path.join(current_directory, os.getenv('CSV_OUTPUT_FILE'))  # Tomamos la ruta desde el .env para el archivo de salida

# Cargar datos desde el archivo CSV original
df = pd.read_csv(CSV_INPUT_FILE, header=None)

# Asignar nombres de columnas según las preguntas
df.columns = [
    'Timestamp',
    'ID',
    '¿Contiene información sensible?',
    '¿Incluye información regulada?',
    'Impacto exposición pública',
    '¿Afecta a clientes/empleados?',
    '¿Requiere acceso externo?',
    '¿Puede recrearse fácilmente?',
    'Clasificación por usuario'
]

# Conversión de respuestas a valores numéricos
conversion = {
    '¿Contiene información sensible?': {'Si': 3, 'No': 1},
    '¿Incluye información regulada?': {'Si': 3, 'No': 1},
    'Impacto exposición pública': {'Bajo': 1, 'Medio': 2, 'Alto': 4, 'Critico': 5},
    '¿Afecta a clientes/empleados?': {'Si': 3, 'No': 1},
    '¿Requiere acceso externo?': {'Si': 3, 'No': 1},
    '¿Puede recrearse fácilmente?': {'Si': 3, 'No': 1},
    'Clasificación por usuario': {'Bajo': 1, 'Medio': 2, 'Alto': 4, 'Critico': 5}
}

# Aplicar la conversión a cada columna
for col, mapping in conversion.items():
    df[f'Puntaje {col.split("?")[0].strip()}'] = df[col].map(mapping)

# Calcular el puntaje total
df['Puntaje Total'] = (
    df['Puntaje ¿Contiene información sensible'] +
    df['Puntaje ¿Incluye información regulada'] +
    df['Puntaje Impacto exposición pública'] +
    df['Puntaje ¿Afecta a clientes/empleados'] +
    df['Puntaje ¿Requiere acceso externo'] +
    df['Puntaje ¿Puede recrearse fácilmente'] +
    df['Puntaje Clasificación por usuario']
)

# Determinar la clasificación final basada en el puntaje total
def determinar_clasificacion(puntaje):
    if puntaje >= 19:
        return 'Crítico'
    elif puntaje >= 15:
        return 'Alto'
    elif puntaje >= 10:
        return 'Medio'
    else:
        return 'Bajo'

df['Clasificación Final'] = df['Puntaje Total'].apply(determinar_clasificacion)

# Guardar datos actualizados en un nuevo archivo CSV en el mismo directorio
df.to_csv(CSV_OUTPUT_FILE, index=False)

print("Datos procesados y guardados en:", CSV_OUTPUT_FILE)

