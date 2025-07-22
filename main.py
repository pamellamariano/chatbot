from module1 import PlantaoManager

def main():
    print("🤖 Bem-vindo! / Welcome!")

    idioma = input("Escolha o idioma / Choose your language (pt/en): ").strip().lower()
    if idioma not in ['pt', 'en']:
        print("Idioma não reconhecido. / Unrecognized language. Usando português por padrão.")
        idioma = 'pt'

    nome_usuario = input("Digite seu nome / Enter your name: ").strip()
    manager = PlantaoManager('plantoes.csv', nome_usuario, idioma=idioma)

    while True:
        print("\n" + "-" * 40)
        if idioma == 'pt':
            print(f"🤖 Olá, {nome_usuario}! O que você deseja fazer?")
            print("1. Ver meu próximo plantão")
            print("2. Verificar se tenho plantão em uma data")
            print("3. Ver nome e telefone do escalation em uma data")
            print("4. Cadastrar plantonistas")
            print("5. Cadastrar escalations")
            print("0. Sair")
        else:
            print(f"🤖 Hello, {nome_usuario}! What would you like to do?")
            print("1. See my next on-call")
            print("2. Check if I’m on-call on a specific date")
            print("3. Get name and phone of escalation for a date")
            print("4. Register on-call contacts")
            print("5. Register escalation contacts")
            print("0. Exit")

        opcao = input("> ").strip()

        if opcao == '0':
            print("Até logo! / See you later!")
            break

        elif opcao == '1':
            print(manager.responder('próximo plantão' if idioma == 'pt' else 'next on-call'))

        elif opcao == '2':
            data = input("Digite a data (dd/mm/aaaa): " if idioma == 'pt' else "Enter the date (dd/mm/yyyy): ")
            comando = f"plantão no dia {data}" if idioma == 'pt' else f"on-call on {data}"
            print(manager.responder(comando))

        elif opcao == '3':
            data = input("Digite a data (dd/mm/aaaa): " if idioma == 'pt' else "Enter the date (dd/mm/yyyy): ")
            comando = f"escalation phone {data}"
            print(manager.responder(comando))

        elif opcao == '4':
            if idioma == 'pt':
                texto = input("Informe os plantonistas no formato Nome:Telefone separados por vírgula\nEx: Pamela:+55 (41) 98778-1355, João:+55 (41) 99999-0000\n> ")
                texto = f"Plantonistas são {texto}"
            else:
                texto = input("Enter on-call contacts as Name:Phone separated by commas\nEx: Pamela:+55 (41) 98778-1355, John:+55 (41) 99999-0000\n> ")
                texto = f"Plantonistas are {texto}"
            print(manager.responder(texto))

        elif opcao == '5':
            if idioma == 'pt':
                texto = input("Informe os escalations no formato Nome:Telefone separados por vírgula\nEx: Harry:+55 (41) 98888-0000, Lucas:+55 (41) 98888-1111\n> ")
                texto = f"Escalations são {texto}"
            else:
                texto = input("Enter escalation contacts as Name:Phone separated by commas\nEx: Harry:+55 (41) 98888-0000, Lucas:+55 (41) 98888-1111\n> ")
                texto = f"Escalations are {texto}"
            print(manager.responder(texto))

        else:
            print("Opção inválida!" if idioma == 'pt' else "Invalid option!")

if __name__ == "__main__":
    main()
