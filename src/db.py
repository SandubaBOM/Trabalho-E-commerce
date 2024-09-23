import sqlite3
from sqlite3 import Error

DATABASE = 'meubanco.db'

def create_connection():
    """ Cria uma conexão com o banco de dados SQLite """
    connection = None
    try:
        connection = sqlite3.connect('hamburgueria.db')  # Certifique-se de que o nome do banco está correto
        print("Conexão bem-sucedida ao banco de dados.")
        return connection
    except Error as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
    return connection 



def create_tables():
    connection = create_connection()
    if connection is not None:
        cursor = connection.cursor()

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Endereco (
            cliente_id INTEGER,
            cep INTEGER,
            rua TEXT,
            bairro TEXT,
            numero_casa INTEGER,
            FOREIGN KEY (cliente_id) REFERENCES Clientes(id_cliente)
        );
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Clientes (
            id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            telefone TEXT UNIQUE NOT NULL
        );
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Produto (
            id_produto INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_produto TEXT,
            valor_prod REAL,
            categoria TEXT,
            tamanho TEXT,
            ponto_carne TEXT
        );
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Pedido (
            id_compra INTEGER PRIMARY KEY AUTOINCREMENT,
            produto_id INTEGER,
            cliente_id INTEGER,
            forma_pagamento TEXT,
            status TEXT,
            FOREIGN KEY (produto_id) REFERENCES Produto(id_produto),
            FOREIGN KEY (cliente_id) REFERENCES Clientes(id_cliente)
        );
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Feedback (
            client_id INTEGER,
            produtoId INTEGER,
            descricao_avalia TEXT,
            FOREIGN KEY (client_id) REFERENCES Clientes(id_cliente),
            FOREIGN KEY (produtoId) REFERENCES Produto(id_produto)
        );
        ''')

        cursor.execute('''
    CREATE TABLE IF NOT EXISTS Sacola (
        cliente_id INTEGER NOT NULL,
        produto_nome TEXT NOT NULL,  -- Nome do produto
        quantidade INTEGER NOT NULL,
        preco REAL NOT NULL,          -- Preço do produto
        data_adicionada TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (cliente_id) REFERENCES Clientes(id_cliente)
    );
''')


        connection.commit()
        cursor.close()
        connection.close()
    else:
        print("Erro! Não foi possível conectar ao banco de dados.")




    
    