CREATE TABLE clientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100),
    sobrenome VARCHAR(100),
    cpf VARCHAR(14) UNIQUE,
    sexo VARCHAR(10),
    telefone VARCHAR(20),
    email VARCHAR(100),
    cartao VARCHAR(20),
    rua VARCHAR(255),
    numero VARCHAR(10),
    bairro VARCHAR(100),
    cidade VARCHAR(100),
    estado VARCHAR(50),
    complemento VARCHAR(255)
);
