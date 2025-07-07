import tkinter as tk
from tkinter import ttk
import mysql.connector
from tkinter import messagebox
import random

# Configurações de conexão MySQL (altere para suas credenciais)
config_db = {
    'user': 'root',
    'password': 'jess3246',
    'host': 'localhost',
    'database': 'trabalho_final'
}

# Cores
cor_fundo = "#e6e6fa"
cor_indigo = "#4b0082"
cor_botao = "#f8f8ff"

# Constantes para Shamir
PRIMO = 208351617316091241234326746312124448251235562226470491514186331217050270460481
SEGREDO_SISTEMA = 123456789
NUM_GERENTES = 5
LIMIAR_ABORTAR = 3

# Função para conectar ao banco de dados
def conectar_bd():
    return mysql.connector.connect(**config_db)

# Estilo
def configurar_estilo():
    style = ttk.Style()
    style.theme_use('clam')
    style.configure("TButton",
                    font=("Helvetica", 14),
                    padding=10,
                    background=cor_botao,
                    foreground="black",
                    borderwidth=1)
    style.map("TButton",
              background=[("active", "#dcdcdc")],
              relief=[("pressed", "sunken"), ("!pressed", "raised")])

# Limpar tela
def limpar_tela():
    for widget in frame_conteudo.winfo_children():
        widget.destroy()

# =================== FUNÇÕES SHAMIR ===================

def inverso_modular(a, p=PRIMO):
    lm, hm = 1, 0
    low, high = a % p, p
    while low > 1:
        r = high // low
        nm, new = hm - lm * r, high - low * r
        lm, low, hm, high = nm, new, lm, low
    return lm % p

def polinomio_random(t, secreto, p=PRIMO):
    coeficientes = [secreto] + [random.randrange(0, p) for _ in range(t - 1)]
    return coeficientes

def avaliar_polinomio(coeficientes, x, p=PRIMO):
    resultado = 0
    for i, coef in enumerate(coeficientes):
        resultado = (resultado + (coef * pow(x, i, p))) % p
    return resultado

def gerar_shares(n, t, secreto, p=PRIMO):
    coef = polinomio_random(t, secreto, p)
    shares = [(i, avaliar_polinomio(coef, i, p)) for i in range(1, n + 1)]
    return shares

def lagrange_interpolacao(x, x_s, y_s, p=PRIMO):
    total = 0
    k = len(x_s)
    for i in range(k):
        xi, yi = x_s[i], y_s[i]
        li = 1
        for j in range(k):
            if i == j:
                continue
            xj = x_s[j]
            num = (x - xj) % p
            den = (xi - xj) % p
            li = (li * num * inverso_modular(den, p)) % p
        total = (total + yi * li) % p
    return total

def reconstruir_segredo(shares, p=PRIMO):
    x_s, y_s = zip(*shares)
    return lagrange_interpolacao(0, x_s, y_s, p)

# Salvar shares no banco
def salvar_shares_no_bd(shares, gerentes):
    conexao = conectar_bd()
    cursor = conexao.cursor()
    try:
        cursor.execute("DELETE FROM shares")  # Limpa shares antigas
        for (x, y), gerente in zip(shares, gerentes):
            sql = "INSERT INTO shares (gerente_id, x, y) VALUES (%s, %s, %s)"
            cursor.execute(sql, (gerente['id'], x, y))
        conexao.commit()
        print("Shares distribuídas e salvas no banco!")
    except mysql.connector.Error as err:
        print("Erro ao salvar shares:", err)
    finally:
        cursor.close()
        conexao.close()


# Apagar dados sensíveis
def apagar_dados():
    conexao = conectar_bd()
    cursor = conexao.cursor()
    try:
        cursor.execute("DELETE FROM clientes")
        cursor.execute("DELETE FROM funcionarios WHERE cargo != 'Gerente'")
        conexao.commit()
        print("Dados apagados com sucesso.")
        messagebox.showinfo("Abortar Sistema", "Dados apagados com sucesso.")
    except mysql.connector.Error as err:
        print("Erro ao apagar dados:", err)
        messagebox.showerror("Erro", f"Erro ao apagar dados: {err}")
    finally:
        cursor.close()
        conexao.close()

# =================== TELAS ===================

def mostrar_tela_inicial():
    limpar_tela()
    titulo = tk.Label(frame_conteudo, text="Tela Inicial", font=("Helvetica", 28, "bold"), bg=cor_fundo, fg=cor_indigo)
    titulo.pack(pady=40)
    ttk.Button(frame_conteudo, text="Consultar", command=mostrar_tela_consultar).pack(pady=10)
    ttk.Button(frame_conteudo, text="Cadastrar", command=mostrar_tela_cadastrar).pack(pady=10)
    ttk.Button(frame_conteudo, text="Administrar", command=mostrar_tela_administrar).pack(pady=10)

# Tela Cadastrar
def mostrar_tela_cadastrar():
    limpar_tela()
    titulo = tk.Label(frame_conteudo, text="Cadastrar", font=("Helvetica", 26, "bold"), bg=cor_fundo, fg=cor_indigo)
    titulo.pack(pady=40)
    ttk.Button(frame_conteudo, text="Cliente", command=mostrar_tela_cadastro_cliente).pack(pady=10)
    ttk.Button(frame_conteudo, text="Funcionário", command=mostrar_tela_cadastro_funcionario).pack(pady=10)
    ttk.Button(frame_conteudo, text="Voltar", command=mostrar_tela_inicial).pack(pady=20)

# Tela Cadastrar Cliente
def mostrar_tela_cadastro_cliente():
    limpar_tela()
    titulo = tk.Label(frame_conteudo, text="Cadastro Cliente", font=("Helvetica", 26, "bold"), bg=cor_fundo, fg=cor_indigo)
    titulo.pack(pady=20)
    frame_formulario = tk.Frame(frame_conteudo, bg=cor_fundo)
    frame_formulario.pack()
    entradas = {}

    def adicionar_campo(label_text, chave, row):
        tk.Label(frame_formulario, text=f"{label_text}:", bg=cor_fundo, anchor="e", width=20).grid(row=row, column=0, padx=5, pady=5)
        entry = tk.Entry(frame_formulario, width=40)
        entry.grid(row=row, column=1, padx=5, pady=5)
        entradas[chave] = entry

    linha = 0
    adicionar_campo("Nome", "nome", linha); linha += 1
    adicionar_campo("Sobrenome", "sobrenome", linha); linha += 1
    adicionar_campo("CPF", "cpf", linha); linha += 1

    tk.Label(frame_formulario, text="Sexo:", bg=cor_fundo, anchor="e", width=20).grid(row=linha, column=0, padx=5, pady=5)
    sexo_cb = ttk.Combobox(frame_formulario, values=["F", "M", "Outro"], width=37, state="readonly")
    sexo_cb.grid(row=linha, column=1, padx=5, pady=5)
    entradas["sexo"] = sexo_cb
    linha += 1

    adicionar_campo("Telefone", "telefone", linha); linha += 1
    adicionar_campo("E-mail", "email", linha); linha += 1
    adicionar_campo("Número do Cartão", "cartao", linha); linha += 1

    tk.Label(frame_formulario, text="Endereço:", bg=cor_fundo, fg=cor_indigo, font=("Helvetica", 14, "bold")).grid(row=linha, column=0, columnspan=2, pady=(15, 5))
    linha += 1
    adicionar_campo("Rua", "rua", linha); linha += 1
    adicionar_campo("Número", "numero", linha); linha += 1
    adicionar_campo("Bairro", "bairro", linha); linha += 1
    adicionar_campo("Cidade", "cidade", linha); linha += 1
    adicionar_campo("Estado", "estado", linha); linha += 1
    adicionar_campo("Complemento", "complemento", linha); linha += 1

    def salvar_cliente():
        dados = {chave: entrada.get() for chave, entrada in entradas.items()}
        conexao = conectar_bd()
        cursor = conexao.cursor()
        sql = """
        INSERT INTO clientes
        (nome, sobrenome, cpf, sexo, telefone, email, cartao, rua, numero, bairro, cidade, estado, complemento)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        valores = (
            dados.get("nome"),
            dados.get("sobrenome"),
            dados.get("cpf"),
            dados.get("sexo"),
            dados.get("telefone"),
            dados.get("email"),
            dados.get("cartao"),
            dados.get("rua"),
            dados.get("numero"),
            dados.get("bairro"),
            dados.get("cidade"),
            dados.get("estado"),
            dados.get("complemento")
        )
        try:
            cursor.execute(sql, valores)
            conexao.commit()
            messagebox.showinfo("Sucesso", "Cliente salvo com sucesso!")
        except mysql.connector.Error as err:
            messagebox.showerror("Erro", f"Erro ao salvar cliente: {err}")
        finally:
            cursor.close()
            conexao.close()

    botoes = tk.Frame(frame_conteudo, bg=cor_fundo)
    botoes.pack(pady=20)
    ttk.Button(botoes, text="Salvar", command=salvar_cliente).pack(side="left", padx=10)
    ttk.Button(botoes, text="Voltar", command=mostrar_tela_cadastrar).pack(side="left", padx=10)

# Tela Cadastro Funcionário (três colunas)
def mostrar_tela_cadastro_funcionario():
    limpar_tela()
    titulo = tk.Label(frame_conteudo, text="Cadastro Funcionário", font=("Helvetica", 26, "bold"), bg=cor_fundo, fg=cor_indigo)
    titulo.pack(pady=20)
    frame_formulario = tk.Frame(frame_conteudo, bg=cor_fundo)
    frame_formulario.pack()
    entradas = {}

    coluna1 = tk.Frame(frame_formulario, bg=cor_fundo)
    coluna2 = tk.Frame(frame_formulario, bg=cor_fundo)
    coluna3 = tk.Frame(frame_formulario, bg=cor_fundo)

    coluna1.grid(row=0, column=0, padx=15, pady=10, sticky="n")
    coluna2.grid(row=0, column=1, padx=15, pady=10, sticky="n")
    coluna3.grid(row=0, column=2, padx=15, pady=10, sticky="n")

    def adicionar_campo(frame, label_text, chave, row, width=30):
        tk.Label(frame, text=f"{label_text}:", bg=cor_fundo, anchor="e", width=20).grid(row=row, column=0, padx=5, pady=5)
        entry = tk.Entry(frame, width=width)
        entry.grid(row=row, column=1, padx=5, pady=5)
        entradas[chave] = entry

    def adicionar_combobox(frame, label_text, chave, row, values, width=30):
        tk.Label(frame, text=f"{label_text}:", bg=cor_fundo, anchor="e", width=20).grid(row=row, column=0, padx=5, pady=5)
        cb = ttk.Combobox(frame, values=values, width=width, state="readonly")
        cb.grid(row=row, column=1, padx=5, pady=5)
        entradas[chave] = cb

    linha = 0
    adicionar_campo(coluna1, "Nome", "nome", linha); linha += 1
    adicionar_campo(coluna1, "Sobrenome", "sobrenome", linha); linha += 1
    adicionar_campo(coluna1, "CPF", "cpf", linha); linha += 1
    adicionar_combobox(coluna1, "Sexo", "sexo", linha, ["F", "M", "Outro"]); linha += 1
    adicionar_campo(coluna1, "Telefone", "telefone", linha); linha += 1
    adicionar_campo(coluna1, "E-mail", "email", linha); linha += 1

    tk.Label(coluna2, text="Endereço:", bg=cor_fundo, fg=cor_indigo, font=("Helvetica", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=(0,10))
    linha = 1
    adicionar_campo(coluna2, "Rua", "rua", linha); linha += 1
    adicionar_campo(coluna2, "Número", "numero", linha); linha += 1
    adicionar_campo(coluna2, "Bairro", "bairro", linha); linha += 1
    adicionar_campo(coluna2, "Cidade", "cidade", linha); linha += 1
    adicionar_campo(coluna2, "Estado", "estado", linha); linha += 1
    adicionar_campo(coluna2, "Complemento", "complemento", linha); linha += 1

    tk.Label(coluna3, text="Pagamentos:", bg=cor_fundo, fg=cor_indigo, font=("Helvetica", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=(0,10))
    linha = 1
    adicionar_campo(coluna3, "Conta Bancária", "conta_bancaria", linha); linha += 1
    adicionar_campo(coluna3, "Agência", "agencia", linha); linha += 1
    adicionar_combobox(coluna3, "Cargo", "cargo", linha, ["Vendedor", "Gerente", "Administrador"]); linha += 1

    def salvar_funcionario():
        dados = {chave: entrada.get() for chave, entrada in entradas.items()}
        conexao = conectar_bd()
        cursor = conexao.cursor()
        sql = """
        INSERT INTO funcionarios
        (nome, sobrenome, cpf, sexo, telefone, email, rua, numero, bairro, cidade, estado, complemento,
         conta_bancaria, agencia, cargo)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        valores = (
            dados.get("nome"),
            dados.get("sobrenome"),
            dados.get("cpf"),
            dados.get("sexo"),
            dados.get("telefone"),
            dados.get("email"),
            dados.get("rua"),
            dados.get("numero"),
            dados.get("bairro"),
            dados.get("cidade"),
            dados.get("estado"),
            dados.get("complemento"),
            dados.get("conta_bancaria"),
            dados.get("agencia"),
            dados.get("cargo")
        )
        try:
            cursor.execute(sql, valores)
            conexao.commit()
            messagebox.showinfo("Sucesso", "Funcionário salvo com sucesso!")
        except mysql.connector.Error as err:
            messagebox.showerror("Erro", f"Erro ao salvar funcionário: {err}")
        finally:
            cursor.close()
            conexao.close()

    botoes = tk.Frame(frame_conteudo, bg=cor_fundo)
    botoes.pack(pady=20)
    ttk.Button(botoes, text="Salvar", command=salvar_funcionario).pack(side="left", padx=10)
    ttk.Button(botoes, text="Voltar", command=mostrar_tela_cadastrar).pack(side="left", padx=10)

# Tela Consultar
def mostrar_tela_consultar():
    limpar_tela()
    titulo = tk.Label(frame_conteudo, text="Consultar", font=("Helvetica", 26, "bold"), bg=cor_fundo, fg=cor_indigo)
    titulo.pack(pady=20)
    frame_filtros = tk.Frame(frame_conteudo, bg=cor_fundo)
    frame_filtros.pack(pady=10)

    tk.Label(frame_filtros, text="Consultar:", bg=cor_fundo).pack(side="left", padx=5)
    tipo_cb = ttk.Combobox(frame_filtros, values=["Cliente", "Funcionário"], state="readonly", width=15)
    tipo_cb.set("Cliente")
    tipo_cb.pack(side="left", padx=5)

    tk.Label(frame_filtros, text="Busca por nome ou CPF:", bg=cor_fundo).pack(side="left", padx=5)
    entrada_busca = tk.Entry(frame_filtros, width=30)
    entrada_busca.pack(side="left", padx=5)

    colunas = (
        "Nome", "Sobrenome", "CPF", "Sexo", "Telefone", "Email", "Número do Cartão",
        "Rua", "Número", "Bairro", "Cidade", "Estado", "Complemento",
        "Conta Bancária", "Agência", "Cargo"
    )

    # Frame para a tabela e scrollbars
    frame_tabela = tk.Frame(frame_conteudo, bg=cor_fundo)
    frame_tabela.pack(pady=20, fill="both", expand=True)

    # Treeview
    tabela = ttk.Treeview(frame_tabela, columns=colunas, show="headings", height=10)

    # Configurar colunas
    for col in colunas:
        tabela.heading(col, text=col)
        tabela.column(col, width=120, anchor="center")

    # Scrollbars
    scroll_x = tk.Scrollbar(frame_tabela, orient="horizontal", command=tabela.xview)
    scroll_y = tk.Scrollbar(frame_tabela, orient="vertical", command=tabela.yview)
    tabela.configure(xscrollcommand=scroll_x.set, yscrollcommand=scroll_y.set)

    # Posicionamento com grid
    tabela.grid(row=0, column=0, sticky="nsew")
    scroll_x.grid(row=1, column=0, sticky="ew")
    scroll_y.grid(row=0, column=1, sticky="ns")

    # Configurar expansão do frame_tabela
    frame_tabela.grid_rowconfigure(0, weight=1)
    frame_tabela.grid_columnconfigure(0, weight=1)

    def preencher_tabela():
        tipo = tipo_cb.get()
        termo = entrada_busca.get().lower()
        tabela.delete(*tabela.get_children())

        conexao = conectar_bd()
        cursor = conexao.cursor(dictionary=True)

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

        like_termo = f"%{termo}%"
        cursor.execute(query, (like_termo, like_termo))
        resultados = cursor.fetchall()

        for item in resultados:
            valores = []
            for col in colunas:
                chave = col.lower().replace(" ", "_")
                valor = item.get(chave)
                if valor is None or valor == "":
                    valor = "-"
                valores.append(valor)
            tabela.insert("", "end", values=valores)

        cursor.close()
        conexao.close()

    ttk.Button(frame_filtros, text="Buscar", command=preencher_tabela).pack(side="left", padx=5)
    ttk.Button(frame_conteudo, text="Voltar", command=mostrar_tela_inicial).pack(pady=10)

    preencher_tabela()

# Tela Administrar
def mostrar_tela_administrar():
    limpar_tela()
    titulo = tk.Label(frame_conteudo, text="Administrar", font=("Helvetica", 28, "bold"), bg=cor_fundo, fg=cor_indigo)
    titulo.pack(pady=40)

    botoes_frame = tk.Frame(frame_conteudo, bg=cor_fundo)
    botoes_frame.pack(pady=20)

    ttk.Button(botoes_frame, text="Alterar Cadastro", width=25, command=lambda: messagebox.showinfo("Info", "Funcionalidade em desenvolvimento")).pack(pady=10)
    ttk.Button(botoes_frame, text="Distribuir Shares", width=25, command=mostrar_tela_distribuir_chaves).pack(pady=10)
    ttk.Button(botoes_frame, text="Abortar Sistema", width=25, command=mostrar_tela_abort).pack(pady=10)
    ttk.Button(frame_conteudo, text="Voltar", width=10, command=mostrar_tela_inicial).pack(pady=30)

# Tela Distribuir Chaves (show gerentes e gera shares)
def mostrar_tela_distribuir_chaves():
    limpar_tela()
    titulo = tk.Label(frame_conteudo, text="Distribuir Shares", font=("Helvetica", 28, "bold"), bg=cor_fundo, fg=cor_indigo)
    titulo.pack(pady=20)

    texto = tk.Label(frame_conteudo, text="Gerentes cadastrados no sistema:", bg=cor_fundo, fg=cor_indigo, font=("Helvetica", 14))
    texto.pack(pady=10)

    frame_gerentes = tk.Frame(frame_conteudo, bg=cor_fundo)
    frame_gerentes.pack()

    conexao = conectar_bd()
    cursor = conexao.cursor(dictionary=True)
    cursor.execute("SELECT id, nome, sobrenome FROM funcionarios WHERE cargo='Gerente'")
    gerentes = cursor.fetchall()
    cursor.close()
    conexao.close()

    if not gerentes:
        messagebox.showwarning("Aviso", "Nenhum gerente encontrado no sistema.")
        mostrar_tela_administrar()
        return

    for gerente in gerentes:
        lbl = tk.Label(frame_gerentes, text=f"ID: {gerente['id']} - {gerente['nome']} {gerente['sobrenome']}", bg=cor_fundo, font=("Helvetica", 12))
        lbl.pack(anchor="w")

    def distribuir():
        shares = gerar_shares(len(gerentes), LIMIAR_ABORTAR, SEGREDO_SISTEMA)
        salvar_shares_no_bd(shares, gerentes)
        messagebox.showinfo("Sucesso", f"Shares geradas e distribuídas para {len(gerentes)} gerentes.\nLimiar: {LIMIAR_ABORTAR}")

    ttk.Button(frame_conteudo, text="Gerar e Distribuir Shares", command=distribuir).pack(pady=20)
    ttk.Button(frame_conteudo, text="Voltar", command=mostrar_tela_administrar).pack()

# Tela Abortar Sistema (requer inserir shares para recuperar segredo)
def mostrar_tela_abort():
    limpar_tela()
    titulo = tk.Label(frame_conteudo, text="Abortar Sistema", font=("Helvetica", 28, "bold"), bg=cor_fundo, fg=cor_indigo)
    titulo.pack(pady=20)

    instrucao = tk.Label(frame_conteudo, text=f"Informe pelo menos {LIMIAR_ABORTAR} shares para recuperar o segredo e abortar o sistema.", bg=cor_fundo)
    instrucao.pack(pady=10)

    frame_shares = tk.Frame(frame_conteudo, bg=cor_fundo)
    frame_shares.pack(pady=10)

    entradas_shares = []

    for i in range(LIMIAR_ABORTAR):
        tk.Label(frame_shares, text=f"Share {i+1} - ID Gerente:", bg=cor_fundo).grid(row=i, column=0, padx=5, pady=5)
        id_entry = tk.Entry(frame_shares, width=10)
        id_entry.grid(row=i, column=1, padx=5, pady=5)
        tk.Label(frame_shares, text="Valor:", bg=cor_fundo).grid(row=i, column=2, padx=5, pady=5)
        val_entry = tk.Entry(frame_shares, width=40)
        val_entry.grid(row=i, column=3, padx=5, pady=5)
        entradas_shares.append((id_entry, val_entry))

    def abortar():
        try:
            shares = []
            for id_ent, val_ent in entradas_shares:
                x = int(id_ent.get())
                y = int(val_ent.get())
                shares.append((x, y))
            segredo_recuperado = reconstruir_segredo(shares)
            if segredo_recuperado == SEGREDO_SISTEMA:
                apagar_dados()
                messagebox.showinfo("Abortar Sistema", "Segredo validado. Sistema abortado com sucesso.")
                mostrar_tela_inicial()
            else:
                messagebox.showerror("Erro", "Segredo inválido. Abortamento não autorizado.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao tentar abortar o sistema:\n{e}")

    botoes = tk.Frame(frame_conteudo, bg=cor_fundo)
    botoes.pack(pady=20)
    ttk.Button(botoes, text="Confirmar Abortamento", command=abortar).pack(side="left", padx=10)
    ttk.Button(botoes, text="Voltar", command=mostrar_tela_administrar).pack(side="left", padx=10)

# Janela principal
root = tk.Tk()
root.title("Trabalho Final")
root.geometry("1000x750")
root.configure(bg=cor_fundo)

configurar_estilo()
frame_conteudo = tk.Frame(root, bg=cor_fundo)
frame_conteudo.pack(expand=True)

mostrar_tela_inicial()

root.mainloop()