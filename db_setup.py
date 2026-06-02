"""
Script de configuración de la base de datos.
Crea la base de datos 'moral_compass' y las tablas necesarias.
"""

import os
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


def crear_base_de_datos():
    """Crea la base de datos moral_compass si no existe."""
    try:
        # Conectar a la base de datos por defecto 'postgres'
        conn = psycopg2.connect(DATABASE_URL + "postgres")
        conn.autocommit = True
        cur = conn.cursor()

        # Verificar si la base de datos ya existe
        cur.execute("SELECT 1 FROM pg_database WHERE datname = 'moral_compass'")
        exists = cur.fetchone()

        if not exists:
            cur.execute(sql.SQL("CREATE DATABASE {}").format(
                sql.Identifier("moral_compass")
            ))
            print("✅ Base de datos 'moral_compass' creada exitosamente.")
        else:
            print("ℹ️  La base de datos 'moral_compass' ya existe.")

        cur.close()
        conn.close()
    except psycopg2.Error as e:
        print(f"❌ Error al crear la base de datos: {e}")
        raise


def crear_tablas():
    """Crea las tablas necesarias en la base de datos moral_compass."""
    try:
        conn = psycopg2.connect(DATABASE_URL + "moral_compass")
        cur = conn.cursor()

        # Tabla de usuarios
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(120) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                onboarding_complete BOOLEAN DEFAULT FALSE,
                grocery_cooking_important BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # Tabla de disponibilidad del usuario
        cur.execute("""
            CREATE TABLE IF NOT EXISTS user_availability (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                day_of_week VARCHAR(15) NOT NULL,
                start_time NUMERIC(4,2) NOT NULL,
                end_time NUMERIC(4,2) NOT NULL,
                UNIQUE(user_id, day_of_week, start_time, end_time)
            );
        """)

        # Tabla de actividades de enfoque del usuario
        cur.execute("""
            CREATE TABLE IF NOT EXISTS user_focus_activities (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                activity_name VARCHAR(100) NOT NULL,
                priority INTEGER CHECK (priority BETWEEN 1 AND 10),
                UNIQUE(user_id, activity_name)
            );
        """)

        conn.commit()
        cur.close()
        conn.close()
        print("✅ Tablas creadas exitosamente.")
    except psycopg2.Error as e:
        print(f"❌ Error al crear las tablas: {e}")
        raise


if __name__ == "__main__":
    print("🔧 Configurando la base de datos de Moral Compass...")
    crear_base_de_datos()
    crear_tablas()
    print("🎉 Configuración completada.")
