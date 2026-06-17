# ============================================================
# ms-notifications — Flask (envio de email via Gmail API)
# ============================================================
FROM python:3.11-slim
WORKDIR /app

# Instalamos dependencias. gunicorn (servidor WSGI de produccion) se
# agrega aparte porque el archivo de requisitos no lo incluye; el
# servidor de desarrollo de Flask no es apto para "produccion".
COPY requeriments.txt .
RUN pip install --no-cache-dir -r requeriments.txt gunicorn

COPY . .

EXPOSE 5000

# Escuchamos en 0.0.0.0 (no 127.0.0.1) para ser accesibles desde otros
# contenedores de la red de compose.
# IMPORTANTE: las credenciales de Gmail (carpeta confidencial/) NO se
# copian a la imagen; se montan como volumen en docker-compose. El
# token.pickle debe estar pre-generado (el flujo OAuth interactivo no
# funciona dentro de un contenedor sin navegador).
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
