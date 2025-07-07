#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para criar e configurar o banco de dados SQLite para o sistema de clientes.

Este script deve ser executado uma vez para preparar o ambiente.
Ele cria o arquivo do banco de dados (se não existir) e a tabela 'clientes'.
"""

import sqlite3

# --- Configurações ---
NOME_ARQUIVO_BD = 'clientes.db'

# --- Comandos SQL ---
SQL_CRIACAO_TABELA = """
CREATE TABLE IF NOT EXISTS clientes (
    cpf TEXT PRIMARY KEY NOT NULL,
    nome TEXT NOT NULL,
    email TEXT UNIQUE,
    telefone TEXT,
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    endereco TEXT,
    nome_mae TEXT NOT NULL,
    nome_pai TEXT NOT NULL,
    rg TEXT NOT NULL UNIQUE,
    sexo TEXT NOT NULL,
    orientacao_sexual TEXT,
    genero TEXT NOT NULL,
    numero_cartao TEXT NOT NULL,
    chave_publica TEXT NOT NULL
);
"""

def criar_banco_de_dados():
    """
    Função principal que conecta ao banco de dados e cria a tabela 'clientes'.
    """
    conexao = None
    
    try:
        print(f"Conectando ao banco de dados '{NOME_ARQUIVO_BD}'...")
        conexao = sqlite3.connect(NOME_ARQUIVO_BD)
        cursor = conexao.cursor()
        
        print("Criando a tabela 'clientes' (se ela não existir)...")
        cursor.execute(SQL_CRIACAO_TABELA)
        
        conexao.commit()
        
        print("\n[SUCESSO] Banco de dados e tabela 'clientes' configurados com sucesso!")
        
    except sqlite3.Error as e:
        print(f"\n[ERRO] Ocorreu um erro ao configurar o banco de dados: {e}")
        
