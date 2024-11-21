import os
import csv
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from dotenv import load_dotenv  # Para manejar el archivo .env

# Cargar variables de entorno desde .env
load_dotenv()

# Variables de entorno
# Usamos la ruta relativa al script para evitar problemas de ruta en diferentes PCs
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))  # Directorio del script
SERVICE_ACCOUNT_FILE = os.path.join(SCRIPT_DIR, 'client_secret_oauth.json')  # Ruta al archivo client_secret.json
SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')  # ID del Google Sheet
TOKEN_FILE = os.path.join(SCRIPT_DIR, 'token.json')  # Ruta al archivo token.json generado automáticamente
CSV_OUTPUT_FILE = os.path.join(SCRIPT_DIR, 'datos_google_sheets.csv')  # Ruta al archivo CSV de salida

# Alcances requeridos
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly', 
          'https://www.googleapis.com/auth/drive.readonly']

def authenticate():
    """Autenticación con el archivo client_secret.json y generación del token.json"""
    creds = None

    # Si ya existe un archivo token.json, se cargan las credenciales de él.
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    
    # Si no hay credenciales (token.json) válidas, solicita autenticación
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(SERVICE_ACCOUNT_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Guardar las credenciales para la próxima ejecución
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    
    return creds

def fetch_data():
    """Función para obtener datos del Google Sheets"""
    creds = authenticate()
    service = build('sheets', 'v4', credentials=creds)

    # ID del archivo de Google Sheets y rango a leer
    RANGE_NAME = 'Respuestas de formulario 1!A2:I50'  # Rango de celdas

    # Obtener los datos de la hoja
    result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
    rows = result.get('values', [])
    
    if not rows:
        print('No se encontraron datos.')
    else:
        print('Datos recuperados:')
        for row in rows:
            print(row)

        # Guardar los datos en CSV
        save_to_csv(rows)

def save_to_csv(rows):
    """Guardar los datos en un archivo CSV"""
    with open(CSV_OUTPUT_FILE, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(rows)

# Llamada a la función
fetch_data()
