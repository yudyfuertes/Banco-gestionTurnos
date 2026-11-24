CREATE DATABASE IF NOT EXISTS asesores_db;
USE asesores_db;

CREATE TABLE IF NOT EXISTS asesores (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL,
  ventanilla INT NOT NULL,
  estado VARCHAR(20) NOT NULL DEFAULT 'disponible'
);

INSERT INTO asesores (nombre, ventanilla) VALUES
  ('Valeria', 1),
  ('Alix', 2);
