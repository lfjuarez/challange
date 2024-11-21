import os
import mysql.connector
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv  # Importar dotenv para manejar el archivo .env

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Variables de entorno
DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')
EMAIL_USER = os.getenv('EMAIL_USER')  # Correo electrónico del remitente
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')  # Contraseña de la aplicación de correo
EMAIL_SMTP_SERVER = os.getenv('EMAIL_SMTP_SERVER', 'smtp.gmail.com')  # Servidor SMTP (por defecto Gmail)
EMAIL_SMTP_PORT = int(os.getenv('EMAIL_SMTP_PORT', 587))  # Puerto SMTP (por defecto 587 para TLS)

# Conectar a la base de datos MySQL
db = mysql.connector.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME
)

cursor = db.cursor()

# Consulta SQL para obtener archivos públicos
query = """
SELECT id, name, visibility, owner 
FROM drive_files 
WHERE visibility = 'public' and owner = 'challangemeli@gmail.com'
"""

cursor.execute(query)

# Función para enviar correo
def send_email(to, subject, body):
    # Crear el objeto mensaje
    message = MIMEMultipart()
    message['To'] = to
    message['From'] = EMAIL_USER
    message['Subject'] = subject

    # Agregar cuerpo del correo
    message.attach(MIMEText(body, 'plain'))

    # Utilizar el servicio SMTP con la contraseña de la aplicación
    try:
        with smtplib.SMTP(EMAIL_SMTP_SERVER, EMAIL_SMTP_PORT) as server:
            server.starttls()  # Inicia la conexión segura
            server.login(EMAIL_USER, EMAIL_PASSWORD)  # Autenticación con el correo y contraseña
            text = message.as_string()
            server.sendmail(message['From'], to, text)
            print(f"Correo enviado a {to}")
    except Exception as e:
        print(f"Error al enviar el correo: {e}")

# Recorrer los resultados y enviar correos
for (id, name, visibility, owner) in cursor.fetchall():
    subject = f"Cuestionario criticidad archivo compartido: \"{name}\""
    body = (f"Buenas tardes estimado/a, nos comunicamos desde el área de ciberseguridad, con motivo de la visibilidad "
            f"pública del archivo llamado \"{name}\", cuyo id es \"{id}\", a fin de pedirle que complete el siguiente "
            f"cuestionario para clasificar su criticidad: https://docs.google.com/forms/d/e/1FAIpQLSf_JYr_W5umqTKWS9VpiZLYrPGl6PVuWlu2paWNseZG1neO8Q/viewform")
    send_email(owner, subject, body)

# Cerrar la conexión a la base de datos
cursor.close()
db.close()
