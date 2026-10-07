"""
Base de datos del Sistema Logístico (SQLite)
Tablas: usuarios, productos, movimientos
"""
import sqlite3
import hashlib

DB_NAME = "logistica.db"


def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)


def hash_password(password):
    """Encripta la contraseña (nunca guardamos contraseñas en texto plano)."""
    return hashlib.sha256(password.encode()).hexdigest()


def init_db():
    """Crea las tablas si no existen."""
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT UNIQUE NOT NULL,
            nombre TEXT NOT NULL,
            categoria TEXT,
            stock INTEGER DEFAULT 0,
            stock_minimo INTEGER DEFAULT 5,
            precio REAL DEFAULT 0
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS movimientos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            producto_id INTEGER NOT NULL,
            tipo TEXT NOT NULL,               -- 'entrada' o 'salida'
            cantidad INTEGER NOT NULL,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (producto_id) REFERENCES productos(id)
        )
    """)

    conn.commit()
    conn.close()


# ---------- USUARIOS ----------
def crear_usuario(username, password):
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO usuarios (username, password) VALUES (?, ?)",
            (username, hash_password(password)),
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # el usuario ya existe
    finally:
        conn.close()


def validar_usuario(username, password):
    conn = get_connection()
    c = conn.execute(
        "SELECT id FROM usuarios WHERE username = ? AND password = ?",
        (username, hash_password(password)),
    )
    row = c.fetchone()
    conn.close()
    return row is not None


# ---------- PRODUCTOS ----------
def agregar_producto(codigo, nombre, categoria, stock_minimo, precio):
    conn = get_connection()
    try:
        conn.execute(
            """INSERT INTO productos (codigo, nombre, categoria, stock_minimo, precio)
               VALUES (?, ?, ?, ?, ?)""",
            (codigo, nombre, categoria, stock_minimo, precio),
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # código duplicado
    finally:
        conn.close()


def listar_productos():
    conn = get_connection()
    c = conn.execute("SELECT * FROM productos ORDER BY nombre")
    data = c.fetchall()
    conn.close()
    return data


def registrar_movimiento(producto_id, tipo, cantidad):
    """Registra entrada/salida y actualiza el stock."""
    conn = get_connection()
    c = conn.execute("SELECT stock FROM productos WHERE id = ?", (producto_id,))
    row = c.fetchone()
    if row is None:
        conn.close()
        return False, "Producto no encontrado"

    stock_actual = row[0]
    if tipo == "salida" and stock_actual < cantidad:
        conn.close()
        return False, f"Stock insuficiente (hay {stock_actual})"

    nuevo_stock = stock_actual + cantidad if tipo == "entrada" else stock_actual - cantidad

    conn.execute(
        "INSERT INTO movimientos (producto_id, tipo, cantidad) VALUES (?, ?, ?)",
        (producto_id, tipo, cantidad),
    )
    conn.execute("UPDATE productos SET stock = ? WHERE id = ?", (nuevo_stock, producto_id))
    conn.commit()
    conn.close()
    return True, "Movimiento registrado"


def productos_bajo_stock():
    conn = get_connection()
    c = conn.execute("SELECT * FROM productos WHERE stock <= stock_minimo")
    data = c.fetchall()
    conn.close()
    return data


def historial_movimientos():
    conn = get_connection()
    c = conn.execute("""
        SELECT m.id, p.nombre, m.tipo, m.cantidad, m.fecha
        FROM movimientos m
        JOIN productos p ON p.id = m.producto_id
        ORDER BY m.fecha DESC
        LIMIT 50
    """)
    data = c.fetchall()
    conn.close()
    return data
