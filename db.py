import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


def get_db_connection():
    """Retorna una conexión a la base de datos moral_compass."""
    try:
        conn = psycopg2.connect(DATABASE_URL + "moral_compass")
        return conn
    except psycopg2.Error as e:
        print(f"Error al conectar a la base de datos: {e}")
        raise
