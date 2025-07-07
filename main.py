import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import banco_dados as db

class AppCadastro:
    def __init__(self, root):
        """Construtor da classe de aplicação."""
        self.root = root
        self.root.title("Cadastro de Clientes")
        self.root.geometry("400x250") # Define um tamanho inicial para a janela
        self.menu()
        self.root.protocol("WM_DELETE_WINDOW")

    def menu(self):
        """Cria e organiza todos os widgets na janela."""
        # Cria um frame (container) para organizar os widgets
        frame = ttk.Frame(self.root, padding="10 10 10 10")
        frame.pack(fill=tk.BOTH, expand=True)

        # Labels e Entradas de texto
        ttk.Button(frame, text="Cadastrar Usuário").grid()
        ttk.Button(frame, text="Consultar Usuário").grid(padx=50, pady= 30)
        ttk.Button(frame, text="Acesso Restrito (Funcionário)").grid(padx=240, pady= 60)

    #funcao para fechar o banco de dados 

# --- Bloco Principal para Iniciar a Aplicação ---
if __name__ == "__main__":
    # Cria a janela principal
    root = tk.Tk()
    # Cria uma instância da nossa aplicação
    app = AppCadastro(root)
    # Inicia o loop de eventos da interface gráfica (essencial!)
    root.mainloop()