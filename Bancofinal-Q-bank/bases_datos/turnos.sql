CREATE DATABASE IF NOT EXISTS turnos_db;
USE turnos_db;

CREATE TABLE IF NOT EXISTS turnos (
  id INT AUTO_INCREMENT PRIMARY KEY,
  codigo VARCHAR(10),
  cliente_id INT NOT NULL,
  asesor_id INT,
  tramite VARCHAR(50) NOT NULL DEFAULT 'general',
  estado VARCHAR(20) NOT NULL DEFAULT 'en_espera',
  creado TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO turnos (codigo, cliente_id, tramite) VALUES
  ('T-1', 1, 'general'),
  ('T-2', 2, 'credito');
