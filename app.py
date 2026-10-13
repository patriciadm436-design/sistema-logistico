"""Sistema Logístico en la Nube - Gestión de Inventario."""

import streamlit as st
import pandas as pd

from database import (
    init_db,
    crear_usuario,
    validar_usuario,
    agregar_producto,
    listar_productos,
    registrar_movimiento,
    productos_bajo_stock,
    historial_movimientos,
)

st.set_page_config(
    page_title="Sistema Logístico",
    page_icon="📦",
    layout="wide",
)

# Inicializar la base de datos
try:
    init_db()
except Exception:
    st.error(
        "No se pudo conectar con la base de datos. "
        "Revisa los Secrets de Streamlit y los registros de la aplicación."
    )
    st.stop()


# Estado de sesión
if "logueado" not in st.session_state:
    st.session_state.logueado = False
    st.session_state.usuario = ""


# ==================== LOGIN Y REGISTRO ====================

def pantalla_login():
    st.title("📦 Sistema Logístico en la Nube")
    st.caption("Gestión de inventario, movimientos y alertas")

    tab1, tab2 = st.tabs(["Iniciar sesión", "Registrarse"])

    with tab1:
        with st.form("form_login"):
            usuario = st.text_input("Usuario")
            password = st.text_input("Contraseña", type="password")
            entrar = st.form_submit_button("Entrar", use_container_width=True)

        if entrar:
            if not usuario.strip() or not password:
                st.warning("Completa el usuario y la contraseña.")
            elif validar_usuario(usuario, password):
                st.session_state.logueado = True
                st.session_state.usuario = usuario.strip()
                st.rerun()
            else:
                st.error(
                    "Usuario o contraseña incorrectos. "
                    "Si el problema continúa, revisa los registros de la aplicación."
                )

    with tab2:
        with st.form("form_registro"):
            nuevo_usuario = st.text_input("Nuevo usuario")
            nueva_password = st.text_input(
                "Nueva contraseña",
                type="password",
            )
            confirmar = st.text_input(
                "Confirmar contraseña",
                type="password",
            )
            registrar = st.form_submit_button(
                "Crear cuenta",
                use_container_width=True,
            )

        if registrar:
            if not nuevo_usuario.strip() or not nueva_password:
                st.warning("Completa todos los campos.")
            elif nueva_password != confirmar:
                st.error("Las contraseñas no coinciden.")
            else:
                ok, mensaje = crear_usuario(nuevo_usuario, nueva_password)

                if ok:
                    st.success(mensaje)
                else:
                    st.error(mensaje)


# ==================== SISTEMA PRINCIPAL ====================

def pantalla_sistema():
    st.sidebar.title("📦 Sistema Logístico")
    st.sidebar.write(f"Usuario: **{st.session_state.usuario}**")

    if st.sidebar.button("Cerrar sesión", use_container_width=True):
        st.session_state.logueado = False
        st.session_state.usuario = ""
        st.rerun()

    menu = st.sidebar.radio(
        "Menú principal",
        [
            "📊 Dashboard",
            "📦 Inventario",
            "🔄 Entradas / Salidas",
            "⚠️ Alertas de stock",
            "📜 Historial",
        ],
    )

    # ---------- DASHBOARD ----------

    if menu == "📊 Dashboard":
        st.title("📊 Dashboard")

        productos = listar_productos()

        if productos:
            df = pd.DataFrame(productos)

            valor_total = sum(
                float(p["stock"]) * float(p["precio"])
                for p in productos
            )

            bajo_stock = productos_bajo_stock()

            c1, c2, c3 = st.columns(3)
            c1.metric("Productos registrados", len(productos))
            c2.metric("Valor del inventario", f"S/ {valor_total:,.2f}")
            c3.metric("Productos con stock bajo", len(bajo_stock))

            st.subheader("Stock por producto")
            st.bar_chart(df.set_index("nombre")["stock"])

            st.subheader("Resumen del inventario")
            st.dataframe(df, use_container_width=True, hide_index=True)

        else:
            st.info("Todavía no hay productos registrados.")

    # ---------- INVENTARIO ----------

    elif menu == "📦 Inventario":
        st.title("📦 Inventario")

        with st.expander("➕ Agregar nuevo producto", expanded=False):
            with st.form("form_producto"):
                codigo = st.text_input("Código del producto")
                nombre = st.text_input("Nombre del producto")
                categoria = st.text_input("Categoría")
                col1, col2 = st.columns(2)

                stock_minimo = col1.number_input(
                    "Stock mínimo",
                    min_value=0,
                    value=5,
                    step=1,
                )

                precio = col2.number_input(
                    "Precio (S/)",
                    min_value=0.0,
                    value=0.0,
                    step=1.0,
                )

                guardar = st.form_submit_button("Guardar producto")

            if guardar:
                if not codigo.strip() or not nombre.strip():
                    st.warning("El código y el nombre son obligatorios.")
                else:
                    ok, mensaje = agregar_producto(
                        codigo,
                        nombre,
                        categoria,
                        int(stock_minimo),
                        float(precio),
                    )

                    if ok:
                        st.success(mensaje)
                        st.rerun()
                    else:
                        st.error(mensaje)

        productos = listar_productos()

        if productos:
            st.subheader("Productos registrados")
            st.dataframe(
                pd.DataFrame(productos),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No hay productos todavía.")

    # ---------- ENTRADAS Y SALIDAS ----------

    elif menu == "🔄 Entradas / Salidas":
        st.title("🔄 Registrar movimiento")

        productos = listar_productos()

        if not productos:
            st.info("Primero registra un producto en Inventario.")
        else:
            opciones = {
                f'{p["codigo"]} - {p["nombre"]} (stock: {p["stock"]})': p["id"]
                for p in productos
            }

            with st.form("form_movimiento"):
                seleccion = st.selectbox(
                    "Producto",
                    list(opciones.keys()),
                )

                tipo = st.radio(
                    "Tipo de movimiento",
                    ["entrada", "salida"],
                    horizontal=True,
                )

                cantidad = st.number_input(
                    "Cantidad",
                    min_value=1,
                    value=1,
                    step=1,
                )

                registrar = st.form_submit_button("Registrar movimiento")

            if registrar:
                ok, mensaje = registrar_movimiento(
                    opciones[seleccion],
                    tipo,
                    int(cantidad),
                )

                if ok:
                    st.success(mensaje)
                    st.rerun()
                else:
                    st.error(mensaje)

    # ---------- ALERTAS DE STOCK ----------

    elif menu == "⚠️ Alertas de stock":
        st.title("⚠️ Productos con stock bajo")

        alertas = productos_bajo_stock()

        if alertas:
            st.warning(
                f"Hay {len(alertas)} producto(s) que necesitan reposición."
            )
            st.dataframe(
                pd.DataFrame(alertas),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.success("Todos los productos están por encima del stock mínimo.")

    # ---------- HISTORIAL ----------

    elif menu == "📜 Historial":
        st.title("📜 Últimos movimientos")

        movimientos = historial_movimientos()

        if movimientos:
            st.dataframe(
                pd.DataFrame(movimientos),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("Todavía no hay movimientos registrados.")


# ==================== PUNTO DE ENTRADA ====================

if st.session_state.logueado:
    pantalla_sistema()
else:
    pantalla_login()
