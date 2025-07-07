import banco_dados as bd
import sqlite3

def consultar_cliente_por_cpf(conn, cpf):
    """Consulta um cliente pelo seu CPF e retorna todos os seus dados."""
    if not conn:
        print("Erro: Conexão com o banco de dados não foi fornecida.")
        return None

    try:
        numeros_cpf = ''.join(filter(str.isdigit, str(cpf)))
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM clientes WHERE cpf = ?", (numeros_cpf,))
        
        return cursor.fetchone()
    except sqlite3.Error as e:
        print(f"Erro ao consultar cliente: {e}")
        return None

