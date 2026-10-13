"""
Base de datos del Sistema Logístico en la Nube (Conector Seguro Supabase)
Tablas: usuarios, productos, movimientos
"""
import hashlib
import streamlit as st

# Conector nativo y definitivo de Streamlit para bases de datos en la nube
conn = st.connection("postgresql", type="sql")

def hash_password(password):
    """Encripta la contraseña mediante un hash SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    """Las tablas ya están creadas de forma fija en la nube."""
    pass

# ---------- USUARIOS ----------
def crear_usuario(username, password):
    try:
        # Insertamos directamente de forma segura. Si el usuario ya existe, 
        # la base de datos lanzará un error y el 'except' devolverá False.
        with conn.session as session:
            session.execute(
                "INSERT INTO usuarios (username, password) VALUES (:username, :password);",
                {"username": username, "password": hash_password(password)}
            )
            session.commit()
        return True
    except Exception:
        return False

def validar_usuario(username, password):
    try:
        query = "SELECT id FROM usuarios WHERE username = :username AND password = :password;"
        result = conn.query(query, params={"username": username, "password": hash_password(password)}, ttl=0)
        # Verificamos si devolvió filas de manera segura
        return result is not None and len(result) > 0
    except Exception:
        return False

# ---------- PRODUCTOS ----------
def agregar_producto(codigo, nombre, categoria, stock_minimo, precio):
    try:
        with conn.session as session:
            session.execute(
                """INSERT INTO productos (codigo, nombre, categoria, stock_minimo, precio)
                   VALUES (:codigo, :nombre, :categoria, :stock_minimo, :precio);""",
                {"codigo": codigo, "nombre": nombre, "categoria": categoria, "stock_minimo": int(stock_minimo), "precio": float(precio)}
            )
            session.commit()
        return True
    except Exception:
        return False

def listar_productos():
    try:
        query = "SELECT id, codigo, nombre, categoria, stock, stock_minimo, precio FROM productos ORDER BY nombre;"
        df = conn.query(query, ttl=0)
        if df is None or df.empty:
            return []
        return df.values.tolist()
    except Exception:
        return []

def registrar_movimiento(producto_id, tipo, cantidad):
    try:
        query_stock = "SELECT stock FROM productos WHERE id = :id;"
        res_df = conn.query(query_stock, params={"id": int(producto_id)}, ttl=0)
        
        if res_df is None or res_df.empty:
            return False, "Producto no encontrado"
            
        stock_actual = int(res_df.iloc[0]['stock'])
        
        if tipo == "salida" and stock_actual < int(cantidad):
            return False, f"Stock insuficiente (hay {stock_actual})"
            
        nuevo_stock = stock_actual + int(cantidad) if tipo == "entrada" else stock_actual - int(cantidad)
        
        with conn.session as session:
            session.execute(
                "INSERT INTO movimientos (producto_id, tipo, cantidad) VALUES (:producto_id, :tipo, :cantidad);",
                {"producto_id": int(producto_id), "tipo": tipo, "cantidad": int(cantidad)}
            )
            session.execute(
                "UPDATE productos SET stock = :nuevo_stock WHERE id = :id;",
                {"nuevo_stock": nuevo_stock, "id": int(producto_id)}
            )
            session.commit()
        return True, "Movimiento registrado"
    except Exception as e:
        return False, f"Error: {str(e)}"

def productos_bajo_stock():
    try:
        query = "SELECT id, codigo, nombre, categoria, stock, stock_minimo, precio FROM productos WHERE stock <= stock_minimo;"
        df = conn.query(query, ttl=0)
        if df is None or df.empty:
            return []
        return df.values.tolist()
    except Exception:
        return []

def historial_movimientos():
    try:
        query = """
            SELECT m.id, p.nombre, m.tipo, m.cantidad, m.fecha
            FROM movimientos m
            JOIN productos p ON p.id = m.producto_id
            ORDER BY m.fecha DESC
            LIMIT 50;
        """
        df = conn.query(query, ttl=0)
        if df is None or df.empty:
            return []
        return df.values.tolist()
    except Exception:
        return []

