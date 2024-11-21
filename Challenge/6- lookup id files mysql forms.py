import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Variables de entorno para la base de datos y rutas de archivos
DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')

# Verificar si las variables de entorno necesarias están presentes
if not all([DB_HOST, DB_USER, DB_PASSWORD, DB_NAME]):
    raise ValueError("Faltan variables de entorno necesarias para la conexión a la base de datos.")

# Obtener la ruta del directorio donde está el script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Construir la ruta completa al archivo CSV
MERGE_INPUT_FILE = os.path.join(script_dir, os.getenv('MERGE_INPUT_FILE'))  # archivo CSV de entrada
MERGE_OUTPUT_FILE = os.path.join(script_dir, os.getenv('MERGE_OUTPUT_FILE'))  # archivo CSV de salida

# Verificar si el archivo de entrada existe
if not os.path.exists(MERGE_INPUT_FILE):
    raise FileNotFoundError(f"El archivo de entrada no se encuentra: {MERGE_INPUT_FILE}")

# 1. Cargar el archivo CSV
df = pd.read_csv(MERGE_INPUT_FILE)

# Crear la conexión utilizando SQLAlchemy para MySQL
connection_string = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

# Manejo de excepciones para la conexión a la base de datos
try:
    engine = create_engine(connection_string)
    # Verificar si la conexión es exitosa
    with engine.connect() as connection:
        print("Conexión a la base de datos exitosa.")
except Exception as e:
    print(f"Error al conectar a la base de datos: {e}")
    exit(1)

# 3. Consulta SQL para obtener 'ID', 'visibility' y 'owner' de la base de datos
query = "SELECT ID, visibility, owner FROM drive_files LIMIT 1000"

# Manejo de excepciones para la ejecución de la consulta
try:
    visibility_df = pd.read_sql(query, engine)
except Exception as e:
    print(f"Error al ejecutar la consulta SQL: {e}")
    exit(1)

# 4. Realizar un 'merge' entre ambos DataFrames usando la columna 'ID' como clave
merged_df = pd.merge(df, visibility_df, on='ID', how='left')

# 5. Mostrar el DataFrame final con las columnas 'visibility' y 'owner' agregadas
print(merged_df[['Timestamp', 'ID', 'Clasificación Final', 'visibility', 'owner']])

# Filtrar el DataFrame por Clasificación Final 'Alto' o 'Crítico' y visibility 'public'
filtered_df = merged_df[(merged_df['Clasificación Final'].isin(['Alto', 'Crítico'])) & (merged_df['visibility'] == 'public')]

# Mostrar los resultados filtrados
print(filtered_df)

# Verificar si el directorio de salida existe, si no, crearlo
if not os.path.exists(os.path.dirname(MERGE_OUTPUT_FILE)):
    os.makedirs(os.path.dirname(MERGE_OUTPUT_FILE))

# Guardar el DataFrame filtrado como un archivo CSV
filtered_df.to_csv(MERGE_OUTPUT_FILE, index=False)

print(f"Datos filtrados guardados en: {MERGE_OUTPUT_FILE}")
