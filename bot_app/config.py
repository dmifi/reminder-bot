import os

TOKEN = os.getenv('TOKEN')

# fix database settings heroku
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# # webhook settings
# WEBHOOK_HOST = os.getenv("WEBHOOK_HOST")
# WEBHOOK_PATH = os.getenv("WEBHOOK_PATH")
# WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"
#
# # webserver settings
# WEBAPP_HOST = os.getenv("WEBAPP_HOST")
# WEBAPP_PORT = int(os.getenv("PORT"))
