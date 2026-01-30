import sqlite3

NOMBRE_DB = "agenda_final.db"

def conectar():
    return sqlite3.connect(NOMBRE_DB)

def crear_tablas():
    conn = conectar()
    cursor = conn.cursor()
    
    # 1. Clientes
    cursor.execute('''CREATE TABLE IF NOT EXISTS clientes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nombre TEXT NOT NULL,
                        telefono TEXT,
                        telefono_alt TEXT,
                        direccion TEXT)''')
    
    # 2. Servicios (NUEVA TABLA)
    cursor.execute('''CREATE TABLE IF NOT EXISTS servicios (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nombre TEXT NOT NULL)''')

    # 3. Turnos (MODIFICADA: Ahora incluye 'servicio')
    cursor.execute('''CREATE TABLE IF NOT EXISTS turnos (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        cliente_nombre TEXT,
                        servicio TEXT,
                        fecha TEXT,
                        hora TEXT,
                        detalle TEXT)''')
    
    conn.commit()
    conn.close()