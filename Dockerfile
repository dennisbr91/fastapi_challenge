# Usa una imagen base oficial de Python
FROM python:3.8-slim
LABEL authors="dennisbr"

# Establece el directorio de trabajo en el contenedor
WORKDIR /app

# Copia el archivo de requisitos y luego instala las dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código de la aplicación
COPY . .

# Expone el puerto en el que correrá la aplicación
EXPOSE 8000

# Comando para correr la aplicación usando uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]