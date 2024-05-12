# Utiliza una imagen oficial de Python como padre
FROM python:3.10-slim

# Establece el directorio de trabajo
WORKDIR /app

# Copia el archivo de requisitos primero para aprovechar la caché de Docker
COPY requirements.txt .

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código de la aplicación
COPY . .

# Haz que el puerto 8000 esté disponible fuera de este contenedor
EXPOSE 8000

# Define el comando para correr la aplicación
CMD ["flask", "run", "--host=0.0.0.0", "--port=8000"]
