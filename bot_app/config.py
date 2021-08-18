import os

# token settings
TOKEN = os.getenv('TOKEN')

# database settings
DATABASE_URL = os.getenv("DATABASE_URL")

# webhook settings
WEBHOOK_HOST = os.getenv("WEBHOOK_HOST")
WEBHOOK_PORT = os.getenv("WEBHOOK_PORT")
WEBHOOK_URL_PATH = os.getenv("WEBHOOK_URL_PATH")
WEBHOOK_URL = f"https://{WEBHOOK_HOST}:{WEBHOOK_PORT}{WEBHOOK_URL_PATH}"

WEBHOOK_SSL_CERT = os.getenv("WEBHOOK_SSL_CERT")
WEBHOOK_SSL_PRIV = os.getenv("WEBHOOK_SSL_PRIV")

# webserver settings
WEBAPP_HOST = os.getenv("WEBAPP_HOST")
WEBAPP_PORT = int(os.getenv("PORT"))
