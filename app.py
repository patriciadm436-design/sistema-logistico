"""
Sistema Logístico en la Nube - Gestión de Inventario
Para correrlo localmente:  streamlit run app.py
"""
import streamlit as st
import pandas as pd
from database import (
    init_db, crear_usuario, validar_usuario,
    agregar_producto, listar_productos, registrar_movimiento,
    productos_bajo_stock, historial_movimientos,
)

st.set_page_config(page_title="Sistema Logístico", page_icon="📦")

# Inicializar la base de datos
init_db()

# Estado de sesión (para recordar quién está logueado)
if "logueado" not in st.session_state:
    st.session_state.logueado = False
    st.session_state.usuario = ""


# ==================== PANTALLA DE LOGIN / REGISTRO ====================
def pantalla_login():
    st.title("📦 Sistema Logístico en la Nube")
    tab1, tab2 = st.tabs(["Iniciar sesión", "Registrarse"])

    with tab1:
        user = st.text_input("Usuario", key="login_user")
        pwd = st.text_input("Contraseña", type="password", key="login_pwd")
        if st.button("Entrar"):
            if validar_usuario(user, pwd):
                st.session_state.logueado = True
                st.session_state.usuario = user
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos")

    with tab2:
        new_user = st.text_input("Nuevo usuario", key="reg_user")
        new_pwd = st.text_input("Contraseña", type="password", key="reg_pwd")
        if st.button("Crear cuenta"):
            if crear_usuario(new_user, new_pwd):
                st.success("Cuenta creada, ahora inicia sesión")
            else:
                st.error("Ese usuario ya existe")


# ==================== SISTEMA (con usuario logueado) ====================
def pantalla_sistema():
    st.sidebar.title(f"👤 {st.session_state.usuario}")
    if st.sidebar.button("Cerrar sesión"):
        st.session_state.logueado = False
        st.rerun()

    menu = st.sidebar.radio(
        "Menú",
        ["📊 Dashboard", "📦 Inventario", "🔄 Entradas / Salidas", "⚠️ Alertas de stock", "📜 Historial"],
    )

    # ---------- DASHBOARD ----------
    if menu == "📊 Dashboard":
        st.title("📊 Dashboard")
        productos = listar_productos()
        if productos:
            df = pd.DataFrame(
                productos,
                columns=["ID", "Código", "Nombre", "Categoría", "Stock", "Stock mínimo", "Precio"],
            )
            valor_total = (df["Stock"] * df["Precio"]).sum()
            c1, c2, c3 = st.columns(3)
            c1.metric("Productos registrados", len(df))
            c2.metric("Valor del inventario", f"S/ {valor_total:,.2f}")
            c3.metric("Bajo stock", len(productos_bajo_stock()))
            st.subheader("Stock por producto")
            st.bar_chart(df.set_index("Nombre")["Stock"])
        else:
            st.info("Aún no hay productos registrados. Ve a 'Inventario' para agregar.")

    # ---------- INVENTARIO ----------
    elif menu == "📦 Inventario":
        st.title("📦 Inventario")
        with st.expander("➕ Agregar nuevo producto"):
            with st.form("form_producto"):
                col1, col2 = st.columns(2)
                codigo = col1.text_input("Código")
                nombre = col2.text_input("Nombre")
                categoria = col1.text_input("Categoría")
                stock_min = col2.number_input("Stock mínimo", min_value=0, value=5)
                precio = col1.number_input("Precio (S/)", min_value=0.0, value=0.0)
                if st.form_submit_button("Guardar producto"):
                    if agregar_producto(codigo, nombre, categoria, stock_min, precio):
                        st.success(f"Producto '{nombre}' registrado")
                    else:
                        st.error("Ese código ya existe")

        productos = listar_productos()
        if productos:
            df = pd.DataFrame(
                productos,
                columns=["ID", "Código", "Nombre", "Categoría", "Stock", "Stock mínimo", "Precio"],
            )
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No hay productos aún.")

    # ---------- MOVIMIENTOS ----------
    elif menu == "🔄 Entradas / Salidas":
        st.title("🔄 Registrar movimiento")
        productos = listar_productos()
        if productos:
            nombres = {f"{p[0]} - {p[2]} ({p[4]} uds)": p[0] for p in productos}
            seleccion = st.selectbox("Producto", list(nombres.keys()))
            tipo = st.radio("Tipo de movimiento", ["entrada", "salida"], horizontal=True)
            cantidad = st.number_input("Cantidad", min_value=1, value=1)
            if st.button("Registrar"):
                ok, msg = registrar_movimiento(nombres[seleccion], tipo, cantidad)
                if ok:
                    st.success(msg)
                else:
                    st.error(msg)
        else:
            st.info("Primero registra productos en el Inventario.")

    # ---------- ALERTAS ----------
    elif menu == "⚠️ Alertas de stock":
        st.title("⚠️ Productos con stock bajo")
        alertas = productos_bajo_stock()
        if alertas:
            df = pd.DataFrame(
                alertas,
                columns=["ID", "Código", "Nombre", "Categoría", "Stock", "Stock mínimo", "Precio"],
            )
            st.warning(f"Hay {len(df)} productos que necesitan reposición")
            st.dataframe(df, use_container_width=True)
        else:
            st.success("Todo el inventario está por encima del stock mínimo 🎉")

    # ---------- HISTORIAL ----------
    elif menu == "📜 Historial":
        st.title("📜 Últimos movimientos")
        movs = historial_movimientos()
        if movs:
            df = pd.DataFrame(movs, columns=["ID", "Producto", "Tipo", "Cantidad", "Fecha"])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No hay movimientos registrados.")


# ==================== PUNTO DE ENTRADA ====================
if st.session_state.logueado:
    pantalla_sistema()
else:
    pantalla_login()
