# FastShop Security Module - Swimming Products Management System

![Python](https://img.shields.io/badge/Python-3.x-blue)
![Flask](https://img.shields.io/badge/Flask-Framework-lightgrey)
![MySQL](https://img.shields.io/badge/MySQL-Database-orange)
![HTML](https://img.shields.io/badge/HTML-CSS-red)

Proyecto universitario del curso **Base de Datos 1** — Universidad Mesoamericana.  
Sistema web desarrollado en Python/Flask con MySQL para la gestión de una tienda de 
productos de natación, con un módulo de seguridad y control de accesos por roles.

---

## 🧩 Módulos del sistema

### 🖥️ Frontend
- **Acerca de la empresa** — Información general de FastShop
- **Crear usuario y contraseña** — Registro de nuevos usuarios
- **Mantenimientos**
  - Clientes
  - Productos
- **Reportes**
  - Reporte de Clientes
  - Reporte de Productos
- **Procesos / Movimientos**
  - Facturación

### ⚙️ Backend
- **Asignación de accesos por rol**
  - Administrador
  - Contable
  - Técnico

---

## 🛠️ Tecnologías utilizadas

- Python 3
- Flask
- MySQL
- HTML5 & CSS3
- JavaScript
- Jinja2 Templates

---

## ⚙️ Instalación y configuración

1. Clonar el repositorio
   git clone https://github.com/andrea10-baa/FastShop-Security-Module.git

2. Instalar dependencias
   pip install -r requirements.txt

3. Configurar la base de datos en config.py con tus credenciales MySQL

4. Importar la base de datos
   mysql -u root -p < FastShop/fastshop_db.sql

5. Ejecutar el proyecto
   python FastShop/app.py

---

## 👩‍💻 Autora

**Rosa Torres**  
Estudiante de Ingeniería en Sistemas — Universidad Mesoamericana  
Curso: Base de Datos 1 | Catedrático: Ing. Magno Orozco
