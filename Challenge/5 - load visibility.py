import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Variables de entorno para la conexión a la base de datos
DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')

# Verificar si las variables de entorno están cargadas correctamente
if not all([DB_HOST, DB_USER, DB_PASSWORD, DB_NAME]):
    raise ValueError("Faltan variables de entorno necesarias para la conexión a la base de datos.")

# Crear la conexión utilizando SQLAlchemy
connection_string = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

# Manejo de excepciones para la conexión a la base de datos
try:
    engine = create_engine(connection_string)
    # Intenta hacer una conexión inicial para asegurarse de que la base de datos es accesible
    with engine.connect() as connection:
        print("Conexión a la base de datos exitosa.")
except Exception as e:
    print(f"Error al conectar a la base de datos: {e}")
    exit(1)

# Consulta SQL para obtener solo el campo 'ID' y 'visibility', con TRIM() para eliminar espacios
query = """
SELECT ID, TRIM(visibility) as visibility
FROM drive_files
LIMIT 1000
"""

# Manejo de excepciones para la ejecución de la consulta
try:
    visibility_df = pd.read_sql(query, engine)
    # Imprimir las primeras filas del DataFrame para verificar los resultados
    print(visibility_df.head())
except Exception as e:
    print(f"Error al ejecutar la consulta: {e}")
    exit(1)

# Inspeccionar las columnas del DataFrame
print("Columnas en el DataFrame:", visibility_df.columns)
