# 📦 Sistema Logístico en la Nube

## 👩‍💻 Autora

**Patricia Delgado Moreno**

## 📌 Descripción

Sistema web para la gestión y control de inventario de una organización.

El sistema permite registrar productos, controlar entradas y salidas, consultar el historial de movimientos y detectar productos que necesitan reposición.

## 🎯 Objetivo

Desarrollar un sistema logístico accesible mediante Internet que facilite la administración y control del inventario.

## ⚙️ Funcionalidades

- 🔐 Registro e inicio de sesión de usuarios.
- 📦 Registro de productos.
- ➕ Registro de entradas de productos.
- ➖ Registro de salidas de productos.
- 📊 Actualización automática del stock.
- ⚠️ Alertas de productos con stock bajo.
- 📜 Historial de movimientos.
- 📈 Dashboard con información del inventario.

## 🛠️ Tecnologías utilizadas

- Python
- Streamlit
- SQLite
- Pandas
- GitHub
- Streamlit Community Cloud

## ☁️ Arquitectura

El sistema funciona mediante una aplicación web desplegada en la nube.

**Usuario → Internet → Streamlit Cloud → Aplicación Python → Base de datos**

## 🌐 Aplicación

**Enlace:**  
https://sistema-logistico-6v5l74vg4htaxfzv6wx9kn.streamlit.app/

## 📂 Estructura del proyecto

```text
sistema-logistico/
├── app.py
├── database.py
├── requirements.txt
├── .devcontainer/
└── README.md
