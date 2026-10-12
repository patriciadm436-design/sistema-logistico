"""
Base de datos del Sistema Logístico en la Nube (PostgreSQL / Supabase)
Tablas: usuarios, productos, movimientos
"""
import psycopg2
import hashlib
import streamlit as st

# Obtenemos la dirección secreta de la base de datos que guardamos en Streamlit Secrets
DB_URL = st.secrets["DB_URL"]

def get_connection():
    """Establece la conexión con la base de datos fija en Supabase."""
    return psycopg2.connect(DB_URL)


def hash_password(password):
    """Encripta la contraseña mediante un hash SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


def init_db():
    """Las tablas ya fueron creadas en el panel de Supabase."""
    pass


# ---------- USUARIOS ----------
def crear_usuario(username, password):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute(
            "INSERT INTO usuarios (username, password) VALUES (%s, %s)",
            (username, hash_password(password)),
        )
        conn.commit()
        return True
    except Exception:
        return False  # El usuario ya existe o hubo un error
    finally:
        c.close()
        conn.close()


def validar_usuario(username, password):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "SELECT id FROM usuarios WHERE username = %s AND password = %s",
        (username, hash_password(password)),
    )
    row = c.fetchone()
    c.close()
    conn.close()
    return row is not None


# ---------- PRODUCTOS ----------
def agregar_producto(codigo, nombre, categoria, stock_minimo, precio):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute(
            """INSERT INTO productos (codigo, nombre, categoria, stock_minimo, precio)
               VALUES (%s, %s, %s, %s, %s)""",
            (codigo, nombre, categoria, stock_minimo, precio),
        )
        conn.commit()
        return True
    except Exception:
        return False  # Código duplicado o error
    finally:
        c.close()
        conn.close()


def listar_productos():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, codigo, nombre, categoria, stock, stock_minimo, precio FROM productos ORDER BY nombre")
    data = c.fetchall()
    c.close()
    conn.close()
    return data


def registrar_movimiento(producto_id, tipo, cantidad):
    """Registra entrada/salida y actualiza el stock."""
    conn = get_connection()
    c = conn.cursor()
    
    c.execute("SELECT stock FROM productos WHERE id = %s", (producto_id,))
    row = c.fetchone()
    if row is None:
        c.close()
        conn.close()
        return False, "Producto no encontrado"

    stock_actual = row[0]
    if tipo == "salida" and stock_actual < cantidad:
        c.close()
        conn.close()
        return False, f"Stock insuficiente (hay {stock_actual})"

    nuevo_stock = stock_actual + cantidad if tipo == "entrada" else stock_actual - cantidad

    c.execute(
        "INSERT INTO movimientos (producto_id, tipo, cantidad) VALUES (%s, %s, %s)",
        (producto_id, tipo, cantidad),
    )
    c.execute("UPDATE productos SET stock = %s WHERE id = %s", (nuevo_stock, producto_id))
    conn.commit()
    c.close()
    conn.close()
    return True, "Movimiento registrado"


def productos_bajo_stock():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, codigo, nombre, categoria, stock, stock_minimo, precio FROM productos WHERE stock <= stock_minimo")
    data = c.fetchall()
    c.close()
    conn.close()
    return data


def historial_movimientos():
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT m.id, p.nombre, m.tipo, m.cantidad, m.fecha
        FROM movimientos m
        JOIN productos p ON p.id = m.producto_id
        ORDER BY m.fecha DESC
        LIMIT 50
    """)
    data = c.fetchall()
    c.close()
    conn.close()
    return data

