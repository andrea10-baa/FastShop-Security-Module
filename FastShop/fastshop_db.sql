-- ============================================
-- SCRIPT DE CREACIÓN DE BASE DE DATOS
-- Fast Shop Guatemala
-- Sistema de Gestión de Tienda de Natación
-- ============================================

-- Seleccionar la base de datos
USE fastshop_db;

-- ============================================
-- TABLA: roles
-- ============================================
CREATE TABLE roles (
    id_rol INT AUTO_INCREMENT PRIMARY KEY,
    nombre_rol VARCHAR(50) NOT NULL UNIQUE,
    descripcion TEXT,
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- ============================================
-- TABLA: usuarios
-- ============================================
CREATE TABLE usuarios (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    usuario VARCHAR(50) NOT NULL UNIQUE,
    contrasena VARCHAR(255) NOT NULL,
    nombre_completo VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE,
    estado BOOLEAN DEFAULT TRUE,
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    id_rol INT NOT NULL,
    FOREIGN KEY (id_rol) REFERENCES roles(id_rol) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- ============================================
-- TABLA: permisos
-- ============================================
CREATE TABLE permisos (
    id_permiso INT AUTO_INCREMENT PRIMARY KEY,
    id_rol INT NOT NULL,
    modulo VARCHAR(50) NOT NULL,
    puede_crear BOOLEAN DEFAULT FALSE,
    puede_leer BOOLEAN DEFAULT TRUE,
    puede_actualizar BOOLEAN DEFAULT FALSE,
    puede_eliminar BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (id_rol) REFERENCES roles(id_rol) ON DELETE CASCADE ON UPDATE CASCADE,
    UNIQUE KEY unique_rol_modulo (id_rol, modulo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- ============================================
-- TABLA: clientes
-- ============================================
CREATE TABLE clientes (
    id_cliente INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    nit VARCHAR(20),
    telefono VARCHAR(20),
    email VARCHAR(100),
    direccion TEXT,
    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
    estado BOOLEAN DEFAULT TRUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- ============================================
-- TABLA: productos
-- ============================================
CREATE TABLE productos (
    id_producto INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    categoria VARCHAR(50),
    precio DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    stock INT NOT NULL DEFAULT 0,
    marca VARCHAR(50),
    talla VARCHAR(20),
    color VARCHAR(30),
    estado BOOLEAN DEFAULT TRUE,
    fecha_ingreso DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- ============================================
-- INSERTAR DATOS INICIALES
-- ============================================

-- Insertar roles predefinidos
INSERT INTO roles (nombre_rol, descripcion) VALUES
('Administrador', 'Acceso total al sistema, puede crear usuarios y asignar permisos'),
('Contable', 'Gestiona clientes y reportes financieros'),
('Técnico de Inventario', 'Gestiona productos y control de stock');

-- Insertar permisos para Administrador (ID: 1)
INSERT INTO permisos (id_rol, modulo, puede_crear, puede_leer, puede_actualizar, puede_eliminar) VALUES
(1, 'usuarios', TRUE, TRUE, TRUE, TRUE),
(1, 'roles', TRUE, TRUE, TRUE, TRUE),
(1, 'clientes', TRUE, TRUE, TRUE, TRUE),
(1, 'productos', TRUE, TRUE, TRUE, TRUE),
(1, 'reportes', TRUE, TRUE, TRUE, TRUE);

-- Insertar permisos para Contable (ID: 2)
INSERT INTO permisos (id_rol, modulo, puede_crear, puede_leer, puede_actualizar, puede_eliminar) VALUES
(2, 'clientes', TRUE, TRUE, TRUE, FALSE),
(2, 'reportes', FALSE, TRUE, FALSE, FALSE),
(2, 'productos', FALSE, TRUE, FALSE, FALSE);

-- Insertar permisos para Técnico de Inventario (ID: 3)
INSERT INTO permisos (id_rol, modulo, puede_crear, puede_leer, puede_actualizar, puede_eliminar) VALUES
(3, 'productos', TRUE, TRUE, TRUE, TRUE),
(3, 'clientes', FALSE, TRUE, FALSE, FALSE);

-- Insertar usuario administrador inicial
-- Usuario: admin
-- Contraseña: admin123 (sin encriptar por ahora, se encriptará desde Python)
INSERT INTO usuarios (usuario, contrasena, nombre_completo, email, estado, id_rol) VALUES
('admin', 'admin123', 'Administrador del Sistema', 'admin@fastshop.gt', TRUE, 1);

-- ============================================
-- INSERTAR DATOS DE EJEMPLO
-- ============================================

-- Clientes de ejemplo
INSERT INTO clientes (nombre, nit, telefono, email, direccion) VALUES
('Juan Pérez', '12345678-9', '5551-1234', 'juan.perez@email.com', 'Zona 10, Ciudad de Guatemala'),
('María González', '98765432-1', '5552-5678', 'maria.gonzalez@email.com', 'Zona 1, Ciudad de Guatemala'),
('Carlos López', 'CF', '5553-9012', 'carlos.lopez@email.com', 'Antigua Guatemala');

-- Productos de ejemplo
INSERT INTO productos (nombre, descripcion, categoria, precio, stock, marca, talla, color) VALUES
('Traje de Baño Speedo Competencia', 'Traje de baño profesional para competencia', 'Traje', 450.00, 15, 'Speedo', 'M', 'Negro'),
('Goggle Arena Cobra Ultra', 'Lentes de natación profesionales anti-empañante', 'Goggle', 250.00, 30, 'Arena', 'Única', 'Azul'),
('Gorro de Silicona TYR', 'Gorro de silicona para entrenamiento', 'Gorro', 75.00, 50, 'TYR', 'Única', 'Rojo'),
('Aletas Finis Z2', 'Aletas de entrenamiento para mejorar patada', 'Aleta', 380.00, 20, 'Finis', 'L', 'Amarillo'),
('Tabla de Flotación Speedo', 'Tabla kickboard para entrenamiento de piernas', 'Tabla', 120.00, 25, 'Speedo', 'Única', 'Verde'),
('Snorkel Frontal Finis', 'Snorkel de entrenamiento para técnica de brazada', 'Accesorio', 280.00, 12, 'Finis', 'Única', 'Negro'),
('Traje Arena Powerskin', 'Traje de alta compresión para competencias', 'Traje', 650.00, 8, 'Arena', 'L', 'Rojo'),
('Goggle MP Michael Phelps', 'Lentes panorámicos para entrenamiento', 'Goggle', 320.00, 18, 'MP', 'Única', 'Transparente');

-- ============================================
-- CONSULTAS DE VERIFICACIÓN
-- ============================================

-- Ver todos los roles
SELECT * FROM roles;

-- Ver todos los usuarios
SELECT u.usuario, u.nombre_completo, u.email, r.nombre_rol 
FROM usuarios u 
JOIN roles r ON u.id_rol = r.id_rol;

-- Ver permisos por rol
SELECT r.nombre_rol, p.modulo, p.puede_crear, p.puede_leer, p.puede_actualizar, p.puede_eliminar
FROM permisos p
JOIN roles r ON p.id_rol = r.id_rol
ORDER BY r.nombre_rol, p.modulo;

-- Ver todos los clientes
SELECT * FROM clientes;

-- Ver todos los productos
SELECT * FROM productos ORDER BY categoria, nombre;

-- ============================================
-- FIN DEL SCRIPT
-- ============================================
