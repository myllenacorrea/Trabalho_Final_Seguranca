import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
import random

# =============================================
# CONFIGURAÇÕES E CONSTANTES
# =============================================

# Configurações do banco de dados
CONFIG_DB = {
    'user': 'root',
    'password': 'jess3246',
    'host': 'localhost',
    'database': 'trabalho_final'
}

# Configurações de cores
CORES = {
    'fundo': "#e6e6fa",
    'indigo': "#4b0082",
    'botao': "#f8f8ff"
}

# Configurações para o esquema de Shamir
SHAMIR_CONFIG = {
    'primo': 208351617316091241234326746312124448251235562226470491514186331217050270460481,
    'segredo_sistema': 123456789,
    'num_gerentes': 5,
    'limiar_abortar': 3
}

# =============================================
# FUNÇÕES DE BANCO DE DADOS
# =============================================

def conectar_bd():
    """Estabelece conexão com o banco de dados"""
    return mysql.connector.connect(**CONFIG_DB)

def executar_consulta(query, params=None, fetch_one=False):
    """Executa uma consulta no banco de dados"""
    conexao = conectar_bd()
    cursor = conexao.cursor(dictionary=True)
    try:
        cursor.execute(query, params or ())
        if fetch_one:
            resultado = cursor.fetchone()
        else:
            resultado = cursor.fetchall()
        conexao.commit()
        return resultado
    except mysql.connector.Error as err:
        print(f"Erro na consulta: {err}")
        return None
    finally:
        cursor.close()
        conexao.close()

# =============================================
# FUNÇÕES DE CRIPTOGRAFIA (SHAMIR)
# =============================================

def inverso_modular(a, p=SHAMIR_CONFIG['primo']):
    """Calcula o inverso modular de a mod p"""
    lm, hm = 1, 0
    low, high = a % p, p
    while low > 1:
        r = high // low
        nm, new = hm - lm * r, high - low * r
        lm, low, hm, high = nm, new, lm, low
    return lm % p

def polinomio_random(t, secreto, p=SHAMIR_CONFIG['primo']):
    """Gera um polinômio aleatório de grau t-1"""
    return [secreto] + [random.randrange(0, p) for _ in range(t - 1)]

def avaliar_polinomio(coeficientes, x, p=SHAMIR_CONFIG['primo']):
    """Avalia o polinômio no ponto x"""
    resultado = 0
    for i, coef in enumerate(coeficientes):
        resultado = (resultado + (coef * pow(x, i, p))) % p
    return resultado

def gerar_shares(n, t, secreto, p=SHAMIR_CONFIG['primo']):
    """Gera n shares com limiar t"""
    coef = polinomio_random(t, secreto, p)
    return [(i, avaliar_polinomio(coef, i, p)) for i in range(1, n + 1)]

def lagrange_interpolacao(x, x_s, y_s, p=SHAMIR_CONFIG['primo']):
    """Interpolação de Lagrange para reconstruir o segredo"""
    total = 0
    k = len(x_s)
    for i in range(k):
        xi, yi = x_s[i], y_s[i]
        li = 1
        for j in range(k):
            if i == j:
                continue
            xj = x_s[j]
            li = (li * (x - xj) * inverso_modular(xi - xj, p)) % p
        total = (total + yi * li) % p
    return total

def reconstruir_segredo(shares, p=SHAMIR_CONFIG['primo']):
    """Reconstrói o segredo a partir das shares"""
    x_s, y_s = zip(*shares)
    return lagrange_interpolacao(0, x_s, y_s, p)

def salvar_shares_no_bd(shares, gerentes):
    """Armazena as shares no banco de dados"""
    conexao = conectar_bd()
    cursor = conexao.cursor()
    try:
        cursor.execute("DELETE FROM shares")  # Limpa shares antigas
        for (x, y), gerente in zip(shares, gerentes):
            cursor.execute("INSERT INTO shares (gerente_id, x, y) VALUES (%s, %s, %s)", 
                          (gerente['id'], x, y))
        conexao.commit()
        messagebox.showinfo("Sucesso", "Shares distribuídas e salvas no banco!")
    except mysql.connector.Error as err:
        messagebox.showerror("Erro", f"Erro ao salvar shares: {err}")
    finally:
        cursor.close()
        conexao.close()

# =============================================
# FUNÇÕES DE SEGURANÇA E LIMPEZA
# =============================================

def apagar_dados():
    """Apaga dados sensíveis do sistema"""
    try:
        executar_consulta("DELETE FROM clientes")
        executar_consulta("DELETE FROM funcionarios WHERE cargo != 'Gerente'")
        messagebox.showinfo("Abortar Sistema", "Dados apagados com sucesso.")
    except mysql.connector.Error as err:
        messagebox.showerror("Erro", f"Erro ao apagar dados: {err}")

# =============================================
# FUNÇÕES DE INTERFACE GRÁFICA
# =============================================

class Aplicacao:
    def __init__(self, root):
        self.root = root
        self.root.title("Trabalho Final")
        self.root.geometry("1000x750")
        self.root.configure(bg=CORES['fundo'])
        
        self.configurar_estilo()
        self.criar_interface()
        self.mostrar_tela_inicial()
    
    def configurar_estilo(self):
        """Configura o estilo visual da aplicação"""
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TButton",
                      font=("Helvetica", 14),
                      padding=10,
                      background=CORES['botao'],
                      foreground="black",
                      borderwidth=1)
        style.map("TButton",
                background=[("active", "#dcdcdc")],
                relief=[("pressed", "sunken"), ("!pressed", "raised")])
    
    def criar_interface(self):
        """Cria a estrutura básica da interface"""
        self.frame_conteudo = tk.Frame(self.root, bg=CORES['fundo'])
        self.frame_conteudo.pack(expand=True)
    
    def limpar_tela(self):
        """Limpa o frame de conteúdo"""
        for widget in self.frame_conteudo.winfo_children():
            widget.destroy()
    
    # ============= TELAS PRINCIPAIS =============
    
    def mostrar_tela_inicial(self):
        """Exibe a tela inicial do sistema"""
        self.limpar_tela()
        
        titulo = tk.Label(self.frame_conteudo, text="Tela Inicial", 
                         font=("Helvetica", 28, "bold"), 
                         bg=CORES['fundo'], fg=CORES['indigo'])
        titulo.pack(pady=40)
        
        botoes = [
            ("Consultar", self.mostrar_tela_consultar),
            ("Cadastrar", self.mostrar_tela_cadastrar),
            ("Administrar", self.verificar_senha_administrador)
        ]
        
        for texto, comando in botoes:
            ttk.Button(self.frame_conteudo, text=texto, command=comando).pack(pady=10)
    
    def mostrar_tela_cadastrar(self):
        """Exibe a tela de cadastro"""
        self.limpar_tela()
        
        titulo = tk.Label(self.frame_conteudo, text="Cadastrar", 
                         font=("Helvetica", 26, "bold"), 
                         bg=CORES['fundo'], fg=CORES['indigo'])
        titulo.pack(pady=40)
        
        botoes = [
            ("Cliente", self.mostrar_tela_cadastro_cliente),
            ("Funcionário", self.mostrar_tela_cadastro_funcionario),
            ("Voltar", self.mostrar_tela_inicial)
        ]
        
        for texto, comando in botoes:
            ttk.Button(self.frame_conteudo, text=texto, command=comando).pack(pady=10)
    
    def mostrar_tela_consultar(self):
        """Exibe a tela de consulta"""
        self.limpar_tela()
        
        titulo = tk.Label(self.frame_conteudo, text="Consultar", 
                         font=("Helvetica", 26, "bold"), 
                         bg=CORES['fundo'], fg=CORES['indigo'])
        titulo.pack(pady=20)
        
        # Frame para filtros
        frame_filtros = tk.Frame(self.frame_conteudo, bg=CORES['fundo'])
        frame_filtros.pack(pady=10)
        
        # Combobox para selecionar tipo de consulta
        tk.Label(frame_filtros, text="Consultar:", bg=CORES['fundo']).pack(side="left", padx=5)
        self.tipo_consulta = ttk.Combobox(frame_filtros, values=["Cliente", "Funcionário"], 
                                         state="readonly", width=15)
        self.tipo_consulta.set("Cliente")
        self.tipo_consulta.pack(side="left", padx=5)
        
        # Entrada para busca
        tk.Label(frame_filtros, text="Busca por nome ou CPF:", bg=CORES['fundo']).pack(side="left", padx=5)
        self.entrada_busca = tk.Entry(frame_filtros, width=30)
        self.entrada_busca.pack(side="left", padx=5)
        
        # Botão de busca
        ttk.Button(frame_filtros, text="Buscar", command=self.preencher_tabela).pack(side="left", padx=5)
        
        # Frame para a tabela
        frame_tabela = tk.Frame(self.frame_conteudo, bg=CORES['fundo'])
        frame_tabela.pack(pady=20, fill="both", expand=True)
        
        # Configuração da tabela
        colunas = (
            "Nome", "Sobrenome", "CPF", "Sexo", "Telefone", "Email", "Número do Cartão",
            "Rua", "Número", "Bairro", "Cidade", "Estado", "Complemento",
            "Conta Bancária", "Agência", "Cargo"
        )
        
        self.tabela = ttk.Treeview(frame_tabela, columns=colunas, show="headings", height=10)
        
        # Configurar colunas
        for col in colunas:
            self.tabela.heading(col, text=col)
            self.tabela.column(col, width=120, anchor="center")
        
        # Scrollbars
        scroll_x = tk.Scrollbar(frame_tabela, orient="horizontal", command=self.tabela.xview)
        scroll_y = tk.Scrollbar(frame_tabela, orient="vertical", command=self.tabela.yview)
        self.tabela.configure(xscrollcommand=scroll_x.set, yscrollcommand=scroll_y.set)
        
        # Layout
        self.tabela.grid(row=0, column=0, sticky="nsew")
        scroll_x.grid(row=1, column=0, sticky="ew")
        scroll_y.grid(row=0, column=1, sticky="ns")
        
        frame_tabela.grid_rowconfigure(0, weight=1)
        frame_tabela.grid_columnconfigure(0, weight=1)
        
        # Botão voltar
        ttk.Button(self.frame_conteudo, text="Voltar", command=self.mostrar_tela_inicial).pack(pady=10)
        
        # Preencher tabela inicialmente
        self.preencher_tabela()
    
    def verificar_senha_administrador(self):
        """Exibe janela para verificação de senha de administrador"""
        def validar():
            if entrada_senha.get() == "SegComp20251":
                senha_window.destroy()
                self.mostrar_tela_administrar()
            else:
                messagebox.showerror("Erro", "Senha incorreta!")
        
        senha_window = tk.Toplevel(self.root)
        senha_window.title("Autenticação")
        senha_window.geometry("300x150")
        senha_window.configure(bg=CORES['fundo'])
        
        tk.Label(senha_window, text="Digite a senha:", bg=CORES['fundo'], 
                font=("Helvetica", 12)).pack(pady=10)
        entrada_senha = tk.Entry(senha_window, show="*", font=("Helvetica", 12), width=25)
        entrada_senha.pack(pady=5)
        
        ttk.Button(senha_window, text="Confirmar", command=validar).pack(pady=10)
    
    # ============= TELAS DE ADMINISTRAÇÃO =============
    
    def mostrar_tela_administrar(self):
        """Exibe a tela de administração"""
        self.limpar_tela()
        
        titulo = tk.Label(self.frame_conteudo, text="Administrar", 
                         font=("Helvetica", 28, "bold"), 
                         bg=CORES['fundo'], fg=CORES['indigo'])
        titulo.pack(pady=40)
        
        botoes = [
            ("Alterar Cadastro", self.mostrar_tela_alterar_cadastro),
            ("Distribuir Shares", self.mostrar_tela_distribuir_chaves),
            ("Abortar Sistema", self.mostrar_tela_abort),
            ("Voltar", self.mostrar_tela_inicial)
        ]
        
        for texto, comando in botoes:
            if texto == "Voltar":
                ttk.Button(self.frame_conteudo, text=texto, width=10, command=comando).pack(pady=30)
            else:
                ttk.Button(self.frame_conteudo, text=texto, width=25, command=comando).pack(pady=10)
    
    def mostrar_tela_alterar_cadastro(self):
        """Exibe a tela para alteração de cadastros"""
        self.limpar_tela()
        
        titulo = tk.Label(self.frame_conteudo, text="Alterar Cadastro", 
                         font=("Helvetica", 28, "bold"), 
                         bg=CORES['fundo'], fg=CORES['indigo'])
        titulo.pack(pady=30)
        
        botoes = [
            ("Alterar Dados Cliente", lambda: messagebox.showinfo("Info", "Funcionalidade em desenvolvimento")),
            ("Alterar Dados Funcionário", lambda: messagebox.showinfo("Info", "Funcionalidade em desenvolvimento")),
            ("Remover Cliente", self.mostrar_tela_remover_cliente),
            ("Remover Funcionário", self.mostrar_tela_remover_funcionario),
            ("Voltar", self.mostrar_tela_administrar)
        ]
        
        for texto, comando in botoes:
            if texto == "Voltar":
                ttk.Button(self.frame_conteudo, text=texto, command=comando).pack(pady=30)
            else:
                ttk.Button(self.frame_conteudo, text=texto, width=30, command=comando).pack(pady=10)
    
    def mostrar_tela_remover_cliente(self):
        """Exibe a tela para remoção de cliente"""
        self.limpar_tela()
        
        titulo = tk.Label(self.frame_conteudo, text="Remover Cliente", 
                         font=("Helvetica", 26, "bold"), 
                         bg=CORES['fundo'], fg=CORES['indigo'])
        titulo.pack(pady=20)
        
        frame = tk.Frame(self.frame_conteudo, bg=CORES['fundo'])
        frame.pack(pady=10)
        
        tk.Label(frame, text="Informe o CPF do cliente:", bg=CORES['fundo']).grid(row=0, column=0, padx=5, pady=5)
        self.entrada_cpf_cliente = tk.Entry(frame, width=30)
        self.entrada_cpf_cliente.grid(row=0, column=1, padx=5, pady=5)
        
        botoes = tk.Frame(self.frame_conteudo, bg=CORES['fundo'])
        botoes.pack(pady=20)
        
        ttk.Button(botoes, text="Remover", command=self.remover_cliente).pack(side="left", padx=10)
        ttk.Button(botoes, text="Voltar", command=self.mostrar_tela_alterar_cadastro).pack(side="left", padx=10)
    
    def mostrar_tela_remover_funcionario(self):
        """Exibe a tela para remoção de funcionário"""
        self.limpar_tela()
        
        titulo = tk.Label(self.frame_conteudo, text="Remover Funcionário", 
                         font=("Helvetica", 26, "bold"), 
                         bg=CORES['fundo'], fg=CORES['indigo'])
        titulo.pack(pady=20)
        
        frame = tk.Frame(self.frame_conteudo, bg=CORES['fundo'])
        frame.pack(pady=10)
        
        tk.Label(frame, text="Informe o CPF do funcionário:", bg=CORES['fundo']).grid(row=0, column=0, padx=5, pady=5)
        self.entrada_cpf_funcionario = tk.Entry(frame, width=30)
        self.entrada_cpf_funcionario.grid(row=0, column=1, padx=5, pady=5)
        
        botoes = tk.Frame(self.frame_conteudo, bg=CORES['fundo'])
        botoes.pack(pady=20)
        
        ttk.Button(botoes, text="Remover", command=self.remover_funcionario).pack(side="left", padx=10)
        ttk.Button(botoes, text="Voltar", command=self.mostrar_tela_alterar_cadastro).pack(side="left", padx=10)
    
    def mostrar_tela_distribuir_chaves(self):
        """Exibe a tela para distribuição de chaves Shamir"""
        self.limpar_tela()
        
        titulo = tk.Label(self.frame_conteudo, text="Distribuir Shares", 
                         font=("Helvetica", 28, "bold"), 
                         bg=CORES['fundo'], fg=CORES['indigo'])
        titulo.pack(pady=20)
        
        tk.Label(self.frame_conteudo, text="Gerentes cadastrados no sistema:", 
                bg=CORES['fundo'], fg=CORES['indigo'], 
                font=("Helvetica", 14)).pack(pady=10)
        
        frame_gerentes = tk.Frame(self.frame_conteudo, bg=CORES['fundo'])
        frame_gerentes.pack()
        
        # Obter gerentes do banco de dados
        gerentes = executar_consulta("SELECT id, nome, sobrenome FROM funcionarios WHERE cargo='Gerente'")
        
        if not gerentes:
            messagebox.showwarning("Aviso", "Nenhum gerente encontrado no sistema.")
            self.mostrar_tela_administrar()
            return
        
        for gerente in gerentes:
            tk.Label(frame_gerentes, 
                    text=f"ID: {gerente['id']} - {gerente['nome']} {gerente['sobrenome']}", 
                    bg=CORES['fundo'], font=("Helvetica", 12)).pack(anchor="w")
        
        def distribuir():
            shares = gerar_shares(len(gerentes), SHAMIR_CONFIG['limiar_abortar'], SHAMIR_CONFIG['segredo_sistema'])
            salvar_shares_no_bd(shares, gerentes)
        
        ttk.Button(self.frame_conteudo, text="Gerar e Distribuir Shares", command=distribuir).pack(pady=20)
        ttk.Button(self.frame_conteudo, text="Voltar", command=self.mostrar_tela_administrar).pack()
    
    def mostrar_tela_abort(self):
        """Exibe a tela para abortar o sistema"""
        self.limpar_tela()
        
        titulo = tk.Label(self.frame_conteudo, text="Abortar Sistema", 
                         font=("Helvetica", 28, "bold"), 
                         bg=CORES['fundo'], fg=CORES['indigo'])
        titulo.pack(pady=20)
        
        tk.Label(self.frame_conteudo, 
                text=f"Informe pelo menos {SHAMIR_CONFIG['limiar_abortar']} shares para recuperar o segredo e abortar o sistema.", 
                bg=CORES['fundo']).pack(pady=10)
        
        frame_shares = tk.Frame(self.frame_conteudo, bg=CORES['fundo'])
        frame_shares.pack(pady=10)
        
        self.entradas_shares = []
        
        for i in range(SHAMIR_CONFIG['limiar_abortar']):
            tk.Label(frame_shares, text=f"Share {i+1}", bg=CORES['fundo']).grid(row=i, column=0, padx=5, pady=5)
            id_entry = tk.Entry(frame_shares, width=10)
            id_entry.grid(row=i, column=1, padx=5, pady=5)
            tk.Label(frame_shares, text="Valor:", bg=CORES['fundo']).grid(row=i, column=2, padx=5, pady=5)
            val_entry = tk.Entry(frame_shares, width=40)
            val_entry.grid(row=i, column=3, padx=5, pady=5)
            self.entradas_shares.append((id_entry, val_entry))
        
        botoes = tk.Frame(self.frame_conteudo, bg=CORES['fundo'])
        botoes.pack(pady=20)
        
        ttk.Button(botoes, text="Confirmar Abortamento", command=self.abortar_sistema).pack(side="left", padx=10)
        ttk.Button(botoes, text="Voltar", command=self.mostrar_tela_administrar).pack(side="left", padx=10)
    
    # ============= TELAS DE CADASTRO =============
    
    def mostrar_tela_cadastro_cliente(self):
        """Exibe a tela de cadastro de cliente"""
        self.limpar_tela()
        
        titulo = tk.Label(self.frame_conteudo, text="Cadastro Cliente", 
                         font=("Helvetica", 26, "bold"), 
                         bg=CORES['fundo'], fg=CORES['indigo'])
        titulo.pack(pady=20)
        
        frame_formulario = tk.Frame(self.frame_conteudo, bg=CORES['fundo'])
        frame_formulario.pack()
        
        self.entradas_cliente = {}
        
        def adicionar_campo(label_text, chave, row):
            tk.Label(frame_formulario, text=f"{label_text}:", bg=CORES['fundo'], 
                    anchor="e", width=20).grid(row=row, column=0, padx=5, pady=5)
            entry = tk.Entry(frame_formulario, width=40)
            entry.grid(row=row, column=1, padx=5, pady=5)
            self.entradas_cliente[chave] = entry
        
        linha = 0
        adicionar_campo("Nome", "nome", linha); linha += 1
        adicionar_campo("Sobrenome", "sobrenome", linha); linha += 1
        adicionar_campo("CPF", "cpf", linha); linha += 1
        
        tk.Label(frame_formulario, text="Sexo:", bg=CORES['fundo'], 
                anchor="e", width=20).grid(row=linha, column=0, padx=5, pady=5)
        sexo_cb = ttk.Combobox(frame_formulario, values=["F", "M", "Outro"], 
                              width=37, state="readonly")
        sexo_cb.grid(row=linha, column=1, padx=5, pady=5)
        self.entradas_cliente["sexo"] = sexo_cb
        linha += 1
        
        adicionar_campo("Telefone", "telefone", linha); linha += 1
        adicionar_campo("E-mail", "email", linha); linha += 1
        adicionar_campo("Número do Cartão", "cartao", linha); linha += 1
        
        tk.Label(frame_formulario, text="Endereço:", bg=CORES['fundo'], 
                fg=CORES['indigo'], font=("Helvetica", 14, "bold")).grid(row=linha, column=0, columnspan=2, pady=(15, 5))
        linha += 1
        adicionar_campo("Rua", "rua", linha); linha += 1
        adicionar_campo("Número", "numero", linha); linha += 1
        adicionar_campo("Bairro", "bairro", linha); linha += 1
        adicionar_campo("Cidade", "cidade", linha); linha += 1
        adicionar_campo("Estado", "estado", linha); linha += 1
        adicionar_campo("Complemento", "complemento", linha); linha += 1
        
        botoes = tk.Frame(self.frame_conteudo, bg=CORES['fundo'])
        botoes.pack(pady=20)
        
        ttk.Button(botoes, text="Salvar", command=self.salvar_cliente).pack(side="left", padx=10)
        ttk.Button(botoes, text="Voltar", command=self.mostrar_tela_cadastrar).pack(side="left", padx=10)
    
    def mostrar_tela_cadastro_funcionario(self):
        """Exibe a tela de cadastro de funcionário"""
        self.limpar_tela()
        
        titulo = tk.Label(self.frame_conteudo, text="Cadastro Funcionário", 
                         font=("Helvetica", 26, "bold"), 
                         bg=CORES['fundo'], fg=CORES['indigo'])
        titulo.pack(pady=20)
        
        frame_formulario = tk.Frame(self.frame_conteudo, bg=CORES['fundo'])
        frame_formulario.pack()
        
        self.entradas_funcionario = {}
        
        # Criar colunas
        coluna1 = tk.Frame(frame_formulario, bg=CORES['fundo'])
        coluna2 = tk.Frame(frame_formulario, bg=CORES['fundo'])
        coluna3 = tk.Frame(frame_formulario, bg=CORES['fundo'])
        
        coluna1.grid(row=0, column=0, padx=15, pady=10, sticky="n")
        coluna2.grid(row=0, column=1, padx=15, pady=10, sticky="n")
        coluna3.grid(row=0, column=2, padx=15, pady=10, sticky="n")
        
        def adicionar_campo(frame, label_text, chave, row, width=30):
            tk.Label(frame, text=f"{label_text}:", bg=CORES['fundo'], 
                    anchor="e", width=20).grid(row=row, column=0, padx=5, pady=5)
            entry = tk.Entry(frame, width=width)
            entry.grid(row=row, column=1, padx=5, pady=5)
            self.entradas_funcionario[chave] = entry
        
        def adicionar_combobox(frame, label_text, chave, row, values, width=30):
            tk.Label(frame, text=f"{label_text}:", bg=CORES['fundo'], 
                    anchor="e", width=20).grid(row=row, column=0, padx=5, pady=5)
            cb = ttk.Combobox(frame, values=values, width=width, state="readonly")
            cb.grid(row=row, column=1, padx=5, pady=5)
            self.entradas_funcionario[chave] = cb
        
        # Coluna 1 - Dados pessoais
        linha = 0
        adicionar_campo(coluna1, "Nome", "nome", linha); linha += 1
        adicionar_campo(coluna1, "Sobrenome", "sobrenome", linha); linha += 1
        adicionar_campo(coluna1, "CPF", "cpf", linha); linha += 1
        adicionar_combobox(coluna1, "Sexo", "sexo", linha, ["F", "M", "Outro"]); linha += 1
        adicionar_campo(coluna1, "Telefone", "telefone", linha); linha += 1
        adicionar_campo(coluna1, "E-mail", "email", linha); linha += 1
        
        # Coluna 2 - Endereço
        tk.Label(coluna2, text="Endereço:", bg=CORES['fundo'], 
                fg=CORES['indigo'], font=("Helvetica", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=(0,10))
        linha = 1
        adicionar_campo(coluna2, "Rua", "rua", linha); linha += 1
        adicionar_campo(coluna2, "Número", "numero", linha); linha += 1
        adicionar_campo(coluna2, "Bairro", "bairro", linha); linha += 1
        adicionar_campo(coluna2, "Cidade", "cidade", linha); linha += 1
        adicionar_campo(coluna2, "Estado", "estado", linha); linha += 1
        adicionar_campo(coluna2, "Complemento", "complemento", linha); linha += 1
        
        # Coluna 3 - Dados profissionais
        tk.Label(coluna3, text="Pagamentos:", bg=CORES['fundo'], 
                fg=CORES['indigo'], font=("Helvetica", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=(0,10))
        linha = 1
        adicionar_campo(coluna3, "Conta Bancária", "conta_bancaria", linha); linha += 1
        adicionar_campo(coluna3, "Agência", "agencia", linha); linha += 1
        adicionar_combobox(coluna3, "Cargo", "cargo", linha, ["Vendedor", "Gerente", "Administrador"]); linha += 1
        
        botoes = tk.Frame(self.frame_conteudo, bg=CORES['fundo'])
        botoes.pack(pady=20)
        
        ttk.Button(botoes, text="Salvar", command=self.salvar_funcionario).pack(side="left", padx=10)
        ttk.Button(botoes, text="Voltar", command=self.mostrar_tela_cadastrar).pack(side="left", padx=10)
    
    # ============= FUNÇÕES AUXILIARES =============
    
    def preencher_tabela(self):
        """Preenche a tabela de consulta com dados do banco"""
        tipo = self.tipo_consulta.get()
        termo = self.entrada_busca.get().lower()
        self.tabela.delete(*self.tabela.get_children())
        
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
        
        resultados = executar_consulta(query, (f"%{termo}%", f"%{termo}%"))
        
        if resultados:
            for item in resultados:
                valores = []
                for col in self.tabela["columns"]:
                    chave = col.lower().replace(" ", "_")
                    valor = item.get(chave, "-")
                    valores.append(valor)
                self.tabela.insert("", "end", values=valores)
    
    def salvar_cliente(self):
        """Salva um novo cliente no banco de dados"""
        dados = {chave: entrada.get() for chave, entrada in self.entradas_cliente.items()}
        
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
            executar_consulta(sql, valores)
            messagebox.showinfo("Sucesso", "Cliente salvo com sucesso!")
        except mysql.connector.Error as err:
            messagebox.showerror("Erro", f"Erro ao salvar cliente: {err}")
    
    def salvar_funcionario(self):
        """Salva um novo funcionário no banco de dados"""
        dados = {chave: entrada.get() for chave, entrada in self.entradas_funcionario.items()}
        
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
            executar_consulta(sql, valores)
            messagebox.showinfo("Sucesso", "Funcionário salvo com sucesso!")
        except mysql.connector.Error as err:
            messagebox.showerror("Erro", f"Erro ao salvar funcionário: {err}")
    
    def remover_cliente(self):
        """Remove um cliente do banco de dados"""
        cpf = self.entrada_cpf_cliente.get()
        if not cpf:
            messagebox.showwarning("Atenção", "Digite um CPF.")
            return
        
        cliente = executar_consulta("SELECT * FROM clientes WHERE cpf = %s", (cpf,), fetch_one=True)
        
        if cliente:
            confirmar = messagebox.askyesno("Confirmação", f"Tem certeza que deseja remover o cliente de CPF {cpf}?")
            if confirmar:
                try:
                    executar_consulta("DELETE FROM clientes WHERE cpf = %s", (cpf,))
                    messagebox.showinfo("Sucesso", "Cliente removido com sucesso.")
                except mysql.connector.Error as err:
                    messagebox.showerror("Erro", f"Erro ao remover cliente: {err}")
        else:
            messagebox.showerror("Erro", "Cliente não encontrado.")
    
    def remover_funcionario(self):
        """Remove um funcionário do banco de dados"""
        cpf = self.entrada_cpf_funcionario.get()
        if not cpf:
            messagebox.showwarning("Atenção", "Digite um CPF.")
            return
        
        funcionario = executar_consulta("SELECT id FROM funcionarios WHERE cpf = %s", (cpf,), fetch_one=True)
        
        if funcionario:
            confirmar = messagebox.askyesno("Confirmação", f"Tem certeza que deseja remover o funcionário de CPF {cpf}?")
            if confirmar:
                try:
                    # Deleta shares primeiro (se houver)
                    executar_consulta("DELETE FROM shares WHERE gerente_id = %s", (funcionario["id"],))
                    # Depois deleta o funcionário
                    executar_consulta("DELETE FROM funcionarios WHERE id = %s", (funcionario["id"],))
                    messagebox.showinfo("Sucesso", "Funcionário removido com sucesso.")
                except mysql.connector.Error as err:
                    messagebox.showerror("Erro", f"Erro ao remover funcionário: {err}")
        else:
            messagebox.showerror("Erro", "Funcionário não encontrado.")
    
    def abortar_sistema(self):
        """Tenta abortar o sistema verificando as shares"""
        try:
            shares = []
            for id_ent, val_ent in self.entradas_shares:
                x = int(id_ent.get())
                y = int(val_ent.get())
                shares.append((x, y))
            
            segredo_recuperado = reconstruir_segredo(shares)
            
            if segredo_recuperado == SHAMIR_CONFIG['segredo_sistema']:
                apagar_dados()
                messagebox.showinfo("Abortar Sistema", "Segredo validado. Sistema abortado com sucesso.")
                self.mostrar_tela_inicial()
            else:
                messagebox.showerror("Erro", "Segredo inválido. Abortamento não autorizado.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao tentar abortar o sistema:\n{e}")

# =============================================
# INICIALIZAÇÃO DA APLICAÇÃO
# =============================================

if __name__ == "__main__":
    root = tk.Tk()
    app = Aplicacao(root)
    root.mainloop()