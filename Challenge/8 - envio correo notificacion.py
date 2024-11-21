import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Variables de entorno
EMAIL_USER = os.getenv('EMAIL_USER')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
EMAIL_SMTP_SERVER = os.getenv('EMAIL_SMTP_SERVER')
EMAIL_SMTP_PORT = os.getenv('EMAIL_SMTP_PORT')

# Obtener la ruta relativa del archivo desde el .env
csv_input_file = os.getenv('CSV_INPUT_FILE_1')

# Asegurarse de que la ruta sea correcta, utilizando el directorio donde se ejecuta el script
file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), csv_input_file)

# Verificar si el archivo existe
if os.path.exists(file_path):
    print(f"El archivo {file_path} existe. Cargando...")
    change_status = pd.read_csv(file_path)  # Cargar el archivo CSV con la ruta correcta
else:
    print(f"El archivo {file_path} no se encuentra en el directorio actual.")
    exit()

# Recorrer el archivo de cambios de permisos y enviar correo al propietario
for index, row in change_status.iterrows():
    owner_email = row['owner']  # Cambié 'owner_email' por 'owner'
    status = row['status']  # Asumiendo que tienes una columna de 'status' que indica si se pudo cambiar el permiso
    file_id = row['file_id']  # Se asume que tienes una columna 'file_id' que contiene el ID del archivo

    # Crear el cuerpo del mensaje
    if status == 'success':
        subject = f'Notificación de cambio de permisos del archivo {file_id}: Éxito'
        body = f"Estimado/a,\n\nPor políticas de seguridad de la información, la visibilidad del archivo {file_id} fue cambiada de pública a privada, por haber sido calificado como crítico.\n\nSaludos."
    else:
        subject = f'Notificación de cambio de permisos del archivo {file_id}: Error'
        body = f"Estimado/a,\n\nPor políticas de seguridad de la información, la visibilidad del archivo {file_id} debe ser cambiada de pública a privada, por haber sido calificado como crítico. Por favor, realice el cambio solicitado y envíe las evidencias correspondientes.\n\nSaludos."

    # Configuración del mensaje
    msg = MIMEMultipart()
    msg['From'] = EMAIL_USER
    msg['To'] = owner_email
    msg['Subject'] = subject

    # Cuerpo del mensaje
    msg.attach(MIMEText(body, 'plain'))

    # Conectar y enviar el correo
    try:
        with smtplib.SMTP(EMAIL_SMTP_SERVER, EMAIL_SMTP_PORT) as server:
            server.starttls()  # Inicia TLS para mayor seguridad
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            text = msg.as_string()
            server.sendmail(EMAIL_USER, owner_email, text)
            print(f'Correo enviado correctamente a {owner_email}')
    except Exception as e:
        print(f'Error al enviar correo a {owner_email}: {e}')
