
CREATE TABLE dVeiculos_R (
    id INT PRIMARY KEY,
    placa VARCHAR(7) NOT NULL,
    descricao VARCHAR(150) NOT NULL,
    ano_fabricacao DATETIME NOT NULL,
    modelo VARCHAR(100) NOT NULL
);

CREATE TABLE dCondutores_R (
    id INT PRIMARY KEY,
    nome VARCHAR(150) NOT NULL
);

CREATE TABLE fPosicao_R (
    id INT IDENTITY(1,1) PRIMARY KEY,
    condutor_id INT,
    veiculo_id INT NOT NULL,
    latitude VARCHAR(50) NOT NULL,
    longitude VARCHAR(50) NOT NULL,
    data_localizacao DATETIME NOT NULL,
    FOREIGN KEY (condutor_id) REFERENCES dCondutores_R(id),
    FOREIGN KEY (veiculo_id) REFERENCES dveiculos_R(id)
);


-- Inserir esses dados antes de executar o codigo
INSERT INTO dCondutores_R (id, nome) VALUES 
(9999, 'Desconhecido'),
(9998, 'Null')
