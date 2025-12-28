CREATE DATABASE sae302;

USE sae302;

CREATE TABLE routeurs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    router_name VARCHAR(20) UNIQUE,
    ip VARCHAR(50),
    port INT,
    public_key TEXT
);

CREATE TABLE clients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    client_name VARCHAR(20) UNIQUE,
    ip VARCHAR(50),
    port INT,
    public_key TEXT
);


