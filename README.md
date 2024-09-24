# **Características**

FastAPI: 
Utiliza FastAPI para construir la API.
SQLAlchemy: ORM para interactuar con la base de datos.
Alembic: Herramienta de migración de bases de datos.
Pytest: Framework de pruebas para asegurar la calidad del código.

# **Requisitos**

1. Python 3.8+
2. FastAPI
3. SQLAlchemy
4. Alembic
5. Pytest

## **Instalación**

Clona el repositorio:
git clone https://github.com/dennisbr91/fastapi_challenge.git
cd fastapi_challenge

Crea un entorno virtual y actívalo:
python -m venv env
source env/bin/activate  # En Windows usa `env\Scripts\activate`

Instala las dependencias:
pip install -r requirements.txt

Configura la base de datos:
alembic upgrade head

Uso
Para iniciar la aplicación, ejecuta:

uvicorn main:app --reload

La aplicación estará disponible en http://127.0.0.1:8000.