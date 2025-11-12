# Imagen base de Python
FROM python:3.10-slim

# Carpeta de trabajo dentro del contenedor
WORKDIR /app

# Copiar todos los archivos al contenedor
COPY . .

# Instalar dependencias necesarias para conectarse a Postgres y manejar datos
RUN pip install psycopg2-binary pandas numpy sqlalchemy

# Comando por defecto que se ejecuta al iniciar el contenedor
CMD ["python", "build_obt.py"]
