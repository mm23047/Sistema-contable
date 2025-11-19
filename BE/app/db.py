"""
Configuración de base de datos y gestión de sesiones para el proyecto contable.
Maneja la conexión a PostgreSQL con variables de entorno.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Cargar variables de entorno desde archivo .env
load_dotenv()

# Detectar modo test
TESTING = os.getenv("TESTING", "false").lower() == "true"

if TESTING:
    # En modo test, usar SQLite en memoria
    DATABASE_URL = "sqlite:///./test.db"
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    # En producción, usar PostgreSQL
    POSTGRES_USER = os.getenv("POSTGRES_USER", "contable")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "contable123")
    POSTGRES_HOST = os.getenv("POSTGRES_HOST", "contable_db17")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_DB = os.getenv("POSTGRES_DB", "contable_db")
    
    # Construir URL de base de datos para PostgreSQL
    DATABASE_URL = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """
    Dependencia para FastAPI para obtener sesiones de base de datos.
    Cada request obtiene su propia sesión de base de datos.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """
    Crear todas las tablas de la base de datos.
    # TODO: En producción usar Alembic para migraciones
    """
    Base.metadata.create_all(bind=engine)