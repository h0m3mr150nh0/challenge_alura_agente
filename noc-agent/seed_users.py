import sys
from src.database import init_db, cadastrar_usuario, listar_usuarios, deletar_usuario

def popular_banco():
    print("\n[+] Inicializando o banco de dados...")
    init_db()

    print("\n[+] Cadastrando usuário Administrador...")
    sucesso_admin, msg_admin = cadastrar_usuario('admin', 'admin123', 'Administrador NOC', 'Masculino', is_admin=True)
    print(f"    [ADMIN] {msg_admin}")

    print("\n[+] Cadastrando operadores e usuários de teste...")
    usuarios = [
        ('carlos.silva', '123456', 'Carlos Silva', 'Masculino'),
        ('ana.souza', '123456', 'Ana Souza', 'Feminino'),
        ('bruno.lima', '123456', 'Bruno Lima', 'Masculino'),
        ('mariana.costa', '123456', 'Mariana Costa', 'Feminino'),
        ('rodrigo.alves', '123456', 'Rodrigo Alves', 'Masculino'),
        ('camila.rocha', '123456', 'Camila Rocha', 'Feminino'),
        ('lucas.mendes', '123456', 'Lucas Mendes', 'Masculino'),
        ('fernanda.dias', '123456', 'Fernanda Dias', 'Feminino'),
        ('diego.martins', '123456', 'Diego Martins', 'Masculino'),
        ('patricia.gomes', '123456', 'Patricia Gomes', 'Feminino')
    ]

    for user, senha, nome, genero in usuarios:
        sucesso, msg = cadastrar_usuario(user, senha, nome, genero)
        status = 'OK' if sucesso else 'SKIP'
        print(f"    [{status}] {user}: {msg}")
        
    print("\n[✔] Processo de povoamento concluído com sucesso!")

def remover_usuario_menu():
    print("\n--- GERENCIAMENTO DE REMOÇÃO DE USUÁRIOS ---")
    
    usuarios = listar_usuarios()
    if not usuarios:
        print("[!] Nenhum usuário cadastrado no banco de dados.")
        return

    print("\nUsuários cadastrados atualmente:")
    print("-" * 50)
    for u in usuarios:
        tipo = "ADMIN" if u['is_admin'] else "OPERADOR"
        print(f" ID: {u['id']} | Username: {u['username']} | Nome: {u['nome_completo']}")
    print("-" * 50)

    usuario_alvo = input("\nDigite o 'username' exato do usuário que deseja remover (ou Enter para cancelar): ").strip()
    
    if not usuario_alvo:
        print("Operação cancelada.")
        return

    confirmacao = input(f"Tem certeza absoluta que deseja remover o usuário '{usuario_alvo}'? (s/n): ").strip().lower()
    
    if confirmacao == 's':
        sucesso, msg = deletar_usuario(usuario_alvo)
        if sucesso:
            print(f"[✔] {msg}")
        else:
            print(f"[X] {msg}")
    else:
        print("Remoção cancelada pelo operador.")

def main():
    while True:
        print("\n==========================================")
        print("   UTILITÁRIO DE GESTÃO DE USERS (NOC)    ")
        print("==========================================")
        print("1. Povoar banco (Criar Admin e Usuários)")
        print("2. Listar / Remover usuário")
        print("3. Sair")
        
        escolha = input("\nSelecione uma opção (1-3): ").strip()
        
        if escolha == '1':
            popular_banco()
        elif escolha == '2':
            remover_usuario_menu()
        elif escolha == '3':
            print("Encerrando utilitário. Até logo!")
            sys.exit(0)
        else:
            print("[!] Opção inválida. Por favor, escolha 1, 2 ou 3.")

if __name__ == '__main__':
    main()