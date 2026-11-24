CREATE DATABASE IF NOT EXISTS clientes_db;
USE clientes_db;

CREATE TABLE IF NOT EXISTS clientes (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL,
  documento VARCHAR(20) NOT NULL UNIQUE,
  telefono VARCHAR(20)
);

INSERT INTO clientes (nombre, documento, telefono) VALUES
  ('Fernando', '1001', '3001112233'),
  ('Elizabeth', '1002', '3004445566');
