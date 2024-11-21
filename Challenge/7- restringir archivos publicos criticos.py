import os
import pandas as pd
from googleapiclient.discovery import build
from google.oauth2 import service_account
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Ruta base donde está el script
base_path = os.path.dirname(os.path.abspath(__file__))

# Variables de entorno
SERVICE_ACCOUNT_FILE = os.path.join(base_path, os.getenv('SERVICE_ACCOUNT_FILE_2'))  # Ruta absoluta al JSON de la cuenta de servicio
PUBLIC_FILES_CSV = os.path.join(base_path, os.getenv('PUBLIC_FILES_CSV'))  # Ruta absoluta al archivo CSV de entrada

# 1. Configurar el acceso a la API
SCOPES = ['https://www.googleapis.com/auth/drive']

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

service = build('drive', 'v3', credentials=credentials)

# 2. Cargar el CSV con los archivos públicos
data = pd.read_csv(PUBLIC_FILES_CSV)

# Filtrar solo archivos públicos y con clasificación "Crítico" o "Alto"
public_files = data[(data['visibility'] == 'public') & (data['Clasificación Final'].isin(['Crítico', 'Alto']))]

# 3. Crear una lista para almacenar los resultados
change_status = []

# Cambiar la visibilidad de los archivos
for _, row in public_files.iterrows():
    file_id = row['ID']
    owner_email = row['owner']  # Suponiendo que el correo del propietario está en esta columna
    try:
        # Quitar permisos públicos (cualquier usuario con enlace)
        permissions = service.permissions().list(fileId=file_id).execute()
        for permission in permissions.get('permissions', []):
            if permission['type'] == 'anyone':
                service.permissions().delete(fileId=file_id, permissionId=permission['id']).execute()
                print(f'Permiso público eliminado del archivo {file_id}')
        
        # Agregar un estado de éxito en la lista de cambio de permisos
        change_status.append({'file_id': file_id, 'owner': owner_email, 'status': True})

    except Exception as e:
        # Si ocurre un error, agregar el estado como False
        print(f'Error al procesar el archivo {file_id}: {e}')
        change_status.append({'file_id': file_id, 'owner': owner_email, 'status': False})

# Guardar el estado de los cambios en un archivo CSV con el correo del propietario
status_df = pd.DataFrame(change_status)
status_df.to_csv(os.path.join(base_path, 'change_status.csv'), index=False)

print("Proceso finalizado.")
