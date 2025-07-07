if tipo == "Cliente":
    query = """
    SELECT nome, sobrenome, cpf, sexo, telefone, email, cartao,
           rua, numero, bairro, cidade, estado, complemento,
           NULL as conta_bancaria, NULL as agencia, NULL as cargo
    FROM clientes
    WHERE LOWER(nome) LIKE %s OR cpf LIKE %s
    """
else:
    query = """
    SELECT nome, sobrenome, cpf, sexo, telefone, email,
           NULL as cartao,
           rua, numero, bairro, cidade, estado, complemento,
           conta_bancaria, agencia, cargo
    FROM funcionarios
    WHERE LOWER(nome) LIKE %s OR cpf LIKE %s
    """
