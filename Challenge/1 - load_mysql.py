import os
import pickle
import mysql.connector
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from dotenv import load_dotenv  # Importar dotenv para manejar el archivo .env

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Variables de entorno
DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')
SERVICE_ACCOUNT_FILE_1 = os.getenv('SERVICE_ACCOUNT_FILE_1')
SERVICE_ACCOUNT_FILE_2 = os.getenv('SERVICE_ACCOUNT_FILE_2')

# Ruta absoluta para los archivos de credenciales
script_dir = os.path.dirname(os.path.abspath(__file__))
service_account_path_1 = os.path.join(script_dir, SERVICE_ACCOUNT_FILE_1)
service_account_path_2 = os.path.join(script_dir, SERVICE_ACCOUNT_FILE_2)

# Configuración de las credenciales OAuth2
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']

# El flujo de OAuth2
def authenticate(service_account_path):
    creds = None
    # El archivo token.pickle almacena las credenciales de usuario
    token_path = os.path.join(script_dir, 'token.pickle')
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
    # Si no existen credenciales válidas, pedir autorización al usuario.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(service_account_path, SCOPES)
            creds = flow.run_local_server(port=0)
        # Guardar las credenciales para la próxima vez que se ejecute el script.
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)
    return creds

# Conectar a la base de datos MySQL
db = mysql.connector.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME
)
cursor = db.cursor()

# Crear tabla si no existe
cursor.execute("""
CREATE TABLE IF NOT EXISTS drive_files (
    id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255),
    extension VARCHAR(50),
    owner VARCHAR(255),
    visibility VARCHAR(50),
    mimeType VARCHAR(100)
)
""")

# Autenticación con las credenciales de servicio 1 (o 2, dependiendo de lo que necesites)
creds = authenticate(service_account_path_1)  # Aquí puedes cambiar a service_account_path_2 si es necesario

# Construir el servicio de la API de Google Drive
service = build('drive', 'v3', credentials=creds)

# Obtener archivos de Google Drive
def fetch_files():
    results = service.files().list(fields="files(id, name, mimeType, owners, permissions)").execute()
    files = results.get('files', [])
    
    for file in files:
        name = file['name']
        extension = name.split('.')[-1] if '.' in name else 'Unknown'
        owner = file['owners'][0]['emailAddress'] if file.get('owners') else 'Unknown'
        visibility = 'public' if any(p['type'] == 'anyone' for p in file.get('permissions', [])) else 'private'
        mimeType = file['mimeType']

        cursor.execute("""
        REPLACE INTO drive_files (id, name, extension, owner, visibility, mimeType) 
        VALUES (%s, %s, %s, %s, %s, %s)
        """, (file['id'], name, extension, owner, visibility, mimeType))

    db.commit()

# Ejecutar la función de extracción
fetch_files()

# Cerrar la conexión a la base de datos
cursor.close()
db.close()
