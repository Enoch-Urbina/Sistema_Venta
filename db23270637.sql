-- Creación de la base de datos
CREATE SCHEMA IF NOT EXISTS `BodegaAurrera` DEFAULT CHARACTER SET utf8mb4;
USE `BodegaAurrera`;

-- Tabla categorias (modificada según tus datos)
CREATE TABLE IF NOT EXISTS `categorias` (
  `id_categorias` INT NOT NULL,
  `nombre` VARCHAR(50) NOT NULL,
  PRIMARY KEY (`id_categorias`)
) ENGINE=InnoDB;

-- Tabla proveedores (modificada según tus datos)
CREATE TABLE IF NOT EXISTS `proveedores` (
  `id_proveedor` INT NOT NULL,
  `nombre` VARCHAR(50) NOT NULL,
  `telefono` VARCHAR(20) NOT NULL,
  `email` VARCHAR(100),
  `direccion` VARCHAR(100),
  PRIMARY KEY (`id_proveedor`)
) ENGINE=InnoDB;

-- Tabla unidad (modificada según tus datos)
CREATE TABLE IF NOT EXISTS `unidad` (
  `id_unidad` INT NOT NULL,
  `nombre` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`id_unidad`)
) ENGINE=InnoDB;

-- Tabla articulos (modificada según tus datos)
CREATE TABLE IF NOT EXISTS `articulos` (
  `codigo` CHAR(13) NOT NULL,
  `nombre` VARCHAR(70) NOT NULL,
  `descripcion` TEXT,
  `precio` FLOAT NOT NULL,
  `costo` FLOAT NOT NULL,
  `existencias` INT NOT NULL,
  `reorden` VARCHAR(45),
  `id_categorias` INT NOT NULL,
  `id_proveedor` INT NOT NULL,
  `id_unidad` INT NOT NULL,
  PRIMARY KEY (`codigo`),
  INDEX `fk_articulos_categorias_idx` (`id_categorias`),
  INDEX `fk_articulos_proveedores1_idx` (`id_proveedor`),
  INDEX `fk_articulos_unidad1_idx` (`id_unidad`),
  CONSTRAINT `fk_articulos_categorias`
    FOREIGN KEY (`id_categorias`)
    REFERENCES `categorias` (`id_categorias`)
    ON DELETE RESTRICT
    ON UPDATE CASCADE,
  CONSTRAINT `fk_articulos_proveedores1`
    FOREIGN KEY (`id_proveedor`)
    REFERENCES `proveedores` (`id_proveedor`)
    ON DELETE RESTRICT
    ON UPDATE CASCADE,
  CONSTRAINT `fk_articulos_unidad1`
    FOREIGN KEY (`id_unidad`)
    REFERENCES `unidad` (`id_unidad`)
    ON DELETE RESTRICT
    ON UPDATE CASCADE
) ENGINE=InnoDB;

-- Tabla clientes (con email opcional)
CREATE TABLE IF NOT EXISTS `clientes` (
  `telefono` CHAR(10) NOT NULL,
  `nombre` VARCHAR(75) NOT NULL,
  `direccion` VARCHAR(100) NOT NULL,
  `rfc` VARCHAR(20),
  `email` VARCHAR(100),
  PRIMARY KEY (`telefono`)
) ENGINE=InnoDB;

-- Tabla empleado
CREATE TABLE IF NOT EXISTS `empleado` (
  `id_empleado` INT NOT NULL,
  `nombre` VARCHAR(45) NOT NULL,
  `genero` ENUM('M', 'F') NOT NULL,
  `puesto` ENUM('encargado', 'cajero', 'administrador') NOT NULL,
  PRIMARY KEY (`id_empleado`)
) ENGINE=InnoDB;

-- Tabla venta
CREATE TABLE IF NOT EXISTS `venta` (
  `id_venta` INT NOT NULL,
  `fecha` DATE NOT NULL,
  `importe` FLOAT NOT NULL,
  `telefono` VARCHAR(20) NOT NULL,
  `id_empleado` INT NOT NULL,
  `metodo_pago` VARCHAR(20) DEFAULT 'EFECTIVO',
  PRIMARY KEY (`id_venta`),
  INDEX `fk_venta_clientes1_idx` (`telefono`),
  INDEX `fk_venta_empleado1_idx` (`id_empleado`),
  CONSTRAINT `fk_venta_clientes1`
    FOREIGN KEY (`telefono`)
    REFERENCES `clientes` (`telefono`)
    ON DELETE RESTRICT
    ON UPDATE CASCADE,
  CONSTRAINT `fk_venta_empleado1`
    FOREIGN KEY (`id_empleado`)
    REFERENCES `empleado` (`id_empleado`)
    ON DELETE RESTRICT
    ON UPDATE CASCADE
) ENGINE=InnoDB;

-- Tabla facturas (con todos los campos obligatorios)
CREATE TABLE IF NOT EXISTS `facturas` (
  `id_factura` INT AUTO_INCREMENT PRIMARY KEY,
  `id_venta` INT NOT NULL,
  `rfc` VARCHAR(13) NOT NULL,
  `razon_social` VARCHAR(100) NOT NULL,
  `direccion_fiscal` TEXT NOT NULL,
  `email` VARCHAR(100) NOT NULL,
  FOREIGN KEY (`id_venta`) REFERENCES `venta`(`id_venta`)
) ENGINE=InnoDB;

-- Tabla ventas_pausadas
CREATE TABLE IF NOT EXISTS `ventas_pausadas` (
  `id_pausa` INT AUTO_INCREMENT PRIMARY KEY,
  `telefono_cliente` VARCHAR(10),
  `cliente_info` TEXT,
  `productos` TEXT,
  `id_empleado` INT,
  `fecha_pausa` DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- =============================================
-- INSERCIÓN DE DATOS SEGÚN TUS REQUERIMIENTOS
-- =============================================

-- Insertar unidades
INSERT INTO `unidad` (id_unidad, nombre) VALUES 
(1, 'pieza'),
(2, 'litro'),
(3, 'gramo'),
(4, 'kilogramo'),
(5, 'mililitro'),
(6, 'sobre'),
(7, 'unidad');

-- Insertar categorias
INSERT INTO `categorias` (id_categorias, nombre) VALUES
(1, 'Lacteos'),
(2, 'Salsas y Aderezos'),
(3, 'Bebidas'),
(4, 'Panaderia y Pasteleria'),
(5, 'Cafe y Te'),
(6, 'Harinas y Cereales'),
(7, 'Snacks y Dulces'),
(8, 'Suplementos Alimenticios'),
(9, 'Condimentos'),
(10, 'Galletas y Snacks');

-- Insertar proveedor generico
INSERT INTO `proveedores` (id_proveedor, nombre, telefono, email, direccion)
VALUES (1, 'Proveedor Generico', '5551234567', 'contacto@proveedor.com', 'Calle Falsa 123');

-- Insertar articulos con descripcion, precio y stock
INSERT INTO `articulos` (codigo, nombre, descripcion, precio, costo, existencias, reorden, id_categorias, id_proveedor, id_unidad) VALUES
('7501020565959', 'Leche semidescremada Lala 1 lt', 'Leche semidescremada marca Lala presentacion 1 litro', 22.50, 18.00, 50, '20', 1, 1, 2),
('7501052472195', 'Catsup Clemente Jacques 220g', 'Catsup de la marca Clemente Jacques en presentacion de 220 gramos', 18.00, 12.50, 100, '30', 2, 1, 3),
('7501040090028', 'Yoghurt Yoplait Batido Natural 1Kg', 'Yoghurt natural batido marca Yoplait en presentacion de 1 kilogramo', 35.00, 28.00, 60, '15', 1, 1, 4),
('7501032398477', 'Vitalinea sin azucar sabor Manzana Verde - Danone', 'Yoghurt Vitalinea sin azucar con sabor manzana verde marca Danone', 24.00, 20.00, 40, '10', 1, 1, 3),
('7501000630363', 'Mini Mamut Gamesa 12 g', 'Mini galletas Mamut de la marca Gamesa en presentacion de 12 gramos', 6.00, 4.00, 120, '40', 7, 1, 3),
('7501125149221', 'Electrolit sabor Fresa/Kiwi 625 ml', 'Bebida rehidratante Electrolit sabor fresa y kiwi presentacion 625 mililitros', 28.00, 22.00, 80, '25', 3, 1, 5),
('7506495020224', 'Media crema 252gr', 'Media crema en presentacion de 252 gramos', 26.00, 20.00, 70, '20', 1, 1, 3),
('7501079016235', 'Italpasta pasta tallarin largo 200 gr', 'Pasta tipo tallarin largo marca Italpasta en presentacion de 200 gramos', 14.00, 11.00, 90, '30', 6, 1, 3),
('7501005110242', 'Harina Maizena Natural 95Gr', 'Harina de maiz Maizena natural en presentacion de 95 gramos', 16.00, 12.00, 75, '25', 6, 1, 3),
('7501052474076', 'Mermelada Clemente Jacques Fresa 470g', 'Mermelada de fresa marca Clemente Jacques en presentacion de 470 gramos', 38.00, 30.00, 55, '15', 2, 1, 3),
('7501001604103', 'Jugo Sazonador Maggi 1 Botella de 100ml', 'Jugo sazonador Maggi en botella de 100 mililitros', 10.00, 8.00, 110, '40', 9, 1, 5),
('7501052417509', 'Cafe Oro Soluble 24 Kilates 160g', 'Cafe soluble Oro 24 Kilates presentacion de 160 gramos', 55.00, 45.00, 50, '15', 5, 1, 3),
('7501077400050', 'Harina de Maiz Nixtamalizado Maseca 1 kg', 'Harina de maiz nixtamalizado marca Maseca en presentacion de 1 kilogramo', 20.00, 16.00, 80, '20', 6, 1, 4),
('7500326818271', 'Proteina Vegetal Chai Falcon 1.170Kg', 'Proteina vegetal marca Chai Falcon presentacion 1.170 kilogramos', 150.00, 120.00, 35, '10', 8, 1, 4),
('7506495017668', 'Te zacate de limon Great Value 18 sobres - 27 g', 'Te de zacate de limon marca Great Value con 18 sobres, peso 27 gramos', 25.00, 20.00, 60, '20', 5, 1, 6),
('7506495017675', 'Te manzanilla Great Value 18 Uds - 21.6 g', 'Te de manzanilla marca Great Value con 18 unidades, peso 21.6 gramos', 25.00, 20.00, 60, '20', 5, 1, 6),
('7502254496262', 'Te Doblett Verde con Frambuesa 19.2g', 'Te Doblett sabor verde con frambuesa presentacion 19.2 gramos', 28.00, 22.00, 70, '25', 5, 1, 3),
('7500533002951', 'Members Mark Te & Infusiones 200 Uds 240g', 'Te e infusiones Members Mark 200 unidades, peso 240 gramos', 90.00, 75.00, 40, '10', 5, 1, 3),
('7500478018406', 'Galletas Marias 720 g', 'Galletas Maria presentacion 720 gramos', 30.00, 25.00, 100, '30', 10, 1, 3),
('7501952966398', 'Chile Miguelito el original en polvo - 250 g', 'Chile Miguelito en polvo presentacion 250 gramos', 18.00, 15.00, 120, '40', 9, 1, 3),
('7501069213811', 'Harina para Hot Cakes Tradicionales 800g', 'Harina para hot cakes tradicional en presentacion de 800 gramos', 22.00, 18.00, 85, '25', 6, 1, 3);

-- Cliente general (requerido para el sistema)
INSERT INTO `clientes` (telefono, nombre, direccion, rfc, email) 
VALUES ('0000000000', 'CLIENTE GENERAL', 'SIN DIRECCIÓN', 'XAXX010101000', 'general@tienda.com');

-- Datos de ejemplo para clientes
INSERT INTO `clientes` (telefono, nombre, direccion, rfc, email) VALUES 
('5512345678', 'Juan Pérez', 'Calle Falsa 123', 'PERJ800101ABC', 'juan.perez@email.com'),
('5567890123', 'María López', 'Avenida Siempre Viva 456', 'LOML850202DEF', 'maria.lopez@email.com'),
('5545678901', 'Carlos Sánchez', 'Boulevard Los Ángeles 789', 'SACC900303GHI', 'carlos.sanchez@email.com');

-- Datos de ejemplo para empleados
INSERT INTO `empleado` (id_empleado, nombre, genero, puesto) VALUES 
(1, 'Ana García', 'F', 'administrador'),
(2, 'Pedro Martínez', 'M', 'encargado'),
(3, 'Luisa Rodríguez', 'F', 'cajero');