import banco_dados as bd
import sqlite3

def cpf_ja_existe(conn, cpf):
    """
    Verifica se um CPF já está cadastrado no banco de dados.
    Retorna True se o CPF existir, e False caso contrário.
    """
    try:
        # Limpa o CPF para garantir que estamos comparando apenas os números
        numeros_cpf = ''.join(filter(str.isdigit, str(cpf)))
        
        cursor = conn.cursor()
        
        # SELECT EXISTS retorna 1 (verdadeiro) se encontrar,
        # ou 0 (falso) se encontrar.
        query = "SELECT EXISTS(SELECT 1 FROM clientes WHERE cpf = ? LIMIT 1)"
        
        cursor.execute(query, (numeros_cpf,))
        
        # O resultado de fetchone() será (1,) se existir ou (0,) se não existir.
        resultado = cursor.fetchone()[0]
        
        return resultado == 1
        
    except sqlite3.Error as e:
        print(f"Erro ao verificar CPF: {e}")
        # Em caso de erro, é mais seguro assumir que a verificação falhou
        # e não permitir o cadastro para evitar duplicatas.
        return True