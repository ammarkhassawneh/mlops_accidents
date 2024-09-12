import os
from cryptography.fernet import Fernet # type: ignore

# Générer la clé Fernet pour le chiffrement dans Airflow
fernet_key = Fernet.generate_key().decode()

# Générer une clé secrète pour le Webserver d'Airflow
webserver_secret_key = os.urandom(24).hex()

# Définir le contenu du fichier .env
env_content = f"""FERNET_KEY={fernet_key}
WEBSERVER_SECRET_KEY={webserver_secret_key}
"""

# Sauvegarder les clés générées dans un fichier .env
with open('.env', 'w') as env_file:
    env_file.write(env_content)

print("Les clés FERNET_KEY et WEBSERVER_SECRET_KEY ont été générées et sauvegardées dans .env")
