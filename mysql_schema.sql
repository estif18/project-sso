-- Crea la base de datos y las tablas necesarias para empresas y trabajadores en MySQL
CREATE DATABASE IF NOT EXISTS gestion_empresas CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE gestion_empresas;

CREATE TABLE IF NOT EXISTS company (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS worker (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    company_id INT NOT NULL,
    FOREIGN KEY (company_id) REFERENCES company(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS submission (
    id INT AUTO_INCREMENT PRIMARY KEY,
    company_id INT NOT NULL,
    worker_id INT NOT NULL,
    asset_id INT NOT NULL,
    checklist_data LONGTEXT,
    tools_check_data LONGTEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES company(id) ON DELETE CASCADE,
    FOREIGN KEY (worker_id) REFERENCES worker(id) ON DELETE CASCADE,
    FOREIGN KEY (asset_id) REFERENCES asset(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS asset (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(100) NOT NULL,
    code VARCHAR(100) NOT NULL,
    company_id INT NOT NULL,
    FOREIGN KEY (company_id) REFERENCES company(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS daily_checklist_response (
    id INT AUTO_INCREMENT PRIMARY KEY,
    submission_id INT NOT NULL,
    item_key VARCHAR(50) NOT NULL,
    item_value VARCHAR(255) NOT NULL,
    FOREIGN KEY (submission_id) REFERENCES submission(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS tools_check_response (
    id INT AUTO_INCREMENT PRIMARY KEY,
    submission_id INT NOT NULL,
    item_key VARCHAR(50) NOT NULL,
    item_value VARCHAR(255) NOT NULL,
    FOREIGN KEY (submission_id) REFERENCES submission(id) ON DELETE CASCADE
);

-- Tabla de códigos de preguntas del checklist diario de equipos
CREATE TABLE IF NOT EXISTS checklist_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    item_key VARCHAR(50) NOT NULL UNIQUE,
    item_label VARCHAR(255) NOT NULL
);

-- Eliminar datos previos para evitar duplicados
DELETE FROM checklist_items;

-- Insertar descripciones de los ítems del checklist diario
INSERT INTO checklist_items (item_key, item_label) VALUES
('item0', 'CHEQUEO EL STICKER SI LLEGA AL KILOMETRAJE DE MANTTO LLEVE AL TALLER'),
('item1', 'CHEQUEE SI LA UNIDAD TIENE ALGÚN ROCE, ABOLLADURA, ETC.'),
('item2', 'VERIFIQUE QUE NO EXISTAN FUGAS DE ACEITE, AGUA, COMBUSTIBLE*'),
('item3', 'PURGAR EL AGUA DEL FILTRO DE PETRÓLEO*'),
('item4', 'REVISE EL NIVEL DE ACEITE DE MOTOR*'),
('item5', 'REVISE EL NIVEL DE ACEITE HIDRÁULICO'),
('item6', 'REVISE EL NIVEL DE LÍQUIDO DE FRENO*'),
('item7', 'REVISE EL NIVEL DE LÍQUIDO DE EMBRAGUE*'),
('item8', 'REVISE EL NIVEL DE AGUA DEL LIMPIAPARABRISAS'),
('item9', 'REVISE CONEXIONES DE BATERÍA Y NIVEL DE ELECTROLITO*'),
('item10', 'REVISE TENSIÓN DE LAS FAJAS DE ALTERNADOR*'),
('item11', 'VERIFIQUE EL AJUSTE DE TUERCAS DE LAS RUEDAS*'),
('item12', 'REVISE ESPEJOS RETROVISORES *'),
('item13', 'CINTURÓN DE SEGURIDAD *'),
('item14', 'COMPROBAR ALARMA DE RETROCESO *'),
('item15', 'COMPROBAR NIVEL DEL REFRIGERANTE'),
('item16', 'TAPA DE TANQUE DE COMBUSTIBLE'),
('item17', 'VERIFIQUE PROFUNDIDAD DE NEUMÁTICOS'),
('item18', 'COMPUERTAS TRASERAS EN CASO DE FURGÓN *'),
('item19', 'CABLE PARA PASAR CORRIENTE DE BATERÍA'),
('item100', 'VERIFIQUE QUE NO EXISTAN FUGAS DE ACEITE, AGUA, COMBUSTIBLE O LIQUIDO DE FRENO QUE MOJE LOS NEUMÁTICOS*'),
('item101', 'REVISE LUCES ( BAJA Y ALTA - RUTA ) *'),
('item102', 'VERIFIQUE FUNCIONAMIENTO NORMAL DEL TABLERO DE INSTRUMENTOS'),
('item103', 'NIVEL DE COMBUSTIBLE MAYOR DE 1/4 DE TANQUE'),
('item104', 'COMPROBAR FUNCIONAMIENTO DE CLAXON *'),
('item105', 'FRENO DE MANO Y PARQUEO *'),
('item106', 'PRESIÓN DE ACEITE DE MOTOR'),
('item107', 'CARGA DE ALTERNADOR'),
('item108', 'TABLERO DE CONTROL'),
('item200', 'NIVEL DE ACEITE DE TRANSMISIÓN Y HIDRÁULICO'),
('item201', 'UÑAS Y CADENA DE LEVANTE'),
('item202', 'BRAZO DE SOPORTE'),
('item203', 'AJUSTE DE CADENAS Y ESTADO DEL TEMPLADOR'),
('item204', 'ESTADO DE RUEDA GUÍA Y SPROCKET'),
('item205', 'ESTADO DE CONTROL DE MANDOS '),
('item300', 'ESTADO DE ROLA'),
('item301', 'LAS GOMAS DE LA ROLA'),
('item400', 'TOLDERA '),
('item401', 'CINTA REFLECTIVA VISIBLE'),
('item402', 'GANCHOS DE COMPUERTA TRASERA'),
('item403', 'TEMPLADORES DE LA COMPUERTA'),
('item404', 'REVISIÓN DE LA TOLVA (BASE, PINES DE COMPUERTA)'),
('item405', 'FUGAS DE ACEITE DE PISTÓN DE LEVANTE Y TANQUE HIDRÁULICO'),
('item500', 'ACCESORIOS DE LA PLUMA Y PLATAFORMA'),
('item501', 'ACCESORIOS DE IZAJE'),
('item600', 'TANQUE - CONTOMETRO Y PISTOLA SURTIDORA AUTOMÁTICA'),
('item601', 'BOMBA DE AGUA ');

-- Tabla de códigos de preguntas del checklist de herramientas y seguridad
CREATE TABLE IF NOT EXISTS tools_check_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    item_key VARCHAR(50) NOT NULL UNIQUE,
    item_label VARCHAR(255) NOT NULL
);

-- Eliminar datos previos para evitar duplicados
DELETE FROM tools_check_items;

-- Insertar descripciones de los ítems del checklist de herramientas
INSERT INTO tools_check_items (item_key, item_label) VALUES
('herr_item1', 'GATA Y LLAVE DE RUEDAS*'),
('herr_item2', 'CINTA REFLECTIVA'),
('herr_item3', 'LLANTA DE REPUESTO*'),
('herr_extintor_fecha', 'EXTINTOR - FECHA VENCIMIENTO'),
('herr_item4', 'EXTINTOR'),
('herr_item5', 'TRIANGULO DE SEGURIDAD / CONOS DE SEGURIDAD'),
('herr_item6', 'BOTIQUIN'),
('herr_item7', 'PAÑO ABSORVENTE'),
('herr_item8', 'TACO VIAL DE SEGURIDAD PARA VEHÍCULOS (2 UND)*'),
('kit_panos', 'PAÑOS ABSORBENTES DE HIDROCARBUROS'),
('kit_pico', 'PICO'),
('kit_lampa', 'LAMPA'),
('kit_costales', 'COSTALES (PARA RECOGER LA TIERRA CONTAMINADA)'),
('kit_salchicha', 'SALCHICHA ABSORBENTE GRANDE'),
('kit_bandeja', 'BANDEJA ANTIDERRAME'),
('kit_tacos', 'TACOS O TARUGOS DE MADERA'),
('kit_trajes', 'TRAJES TYBEK'),
('kit_guantes', 'PAR DE GUANTES'),
('otros_soat', 'SOAT'),
('otros_soat_fecha', 'SOAT - FECHA VENCIMIENTO'),
('otros_propiedad', 'Tarjeta de propiedad'),
('otros_circulacion', 'Tarjeta de circulación'),
('otros_licencia', 'Licencia de conducir');




