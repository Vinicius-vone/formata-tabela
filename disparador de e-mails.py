import pandas as pd
import win32com.client as win32

# Assinatura do e-mail
assinatura = """<p style="text-align: left;"><strong>Alfredo Vincícius Andrade Guimarães</strong><br>
<strong>Pós-doutorando</strong><br>
<strong>PPGF - UFSJ</strong><br>
<strong>Telefone: (32)98808-3456</strong> </p>
<p style="text-align: left;"><a href="mailto:afredovag@yahoo.com.br">E-mail</a>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
<a href="https://wa.me/5532988083456">WhatsApp</a>"""

# Leitura dos dados de uma planilha Excel
def fetch_student_data(file_path):
    try:
        df = pd.read_excel(file_path)
        return df[['nome', 'matricula', 'nota', 'email']].values.tolist()
    except Exception as e:
        print(f"Erro ao ler a planilha Excel: {e}")
        return []

def initialize_outlook():
    try:
        outlook = win32.Dispatch('outlook.application')
        return outlook
    except Exception as e:
        print(f"Erro ao inicializar o Outlook: {e}")
        return None

def send_email_via_outlook(outlook, to_email, subject, body):
    try:
        mail = outlook.CreateItem(0)
        mail.To = to_email
        mail.Subject = subject
        mail.HTMLBody = body
        mail.Send()
        print(f"E-mail enviado para {to_email}")
    except Exception as e:
        print(f"Erro ao enviar e-mail para {to_email}: {e}")

# Função principal
def main():
    file_path = "alunos.xlsx"  # Substitua pelo caminho para a sua planilha Excel
    alunos = fetch_student_data(file_path)
    outlook = initialize_outlook()

    if outlook:
        for nome, matricula, nota, email in alunos:
            # Personalizando o conteúdo do e-mail
            subject = "Sua nota da prova"
            body = f"""<p>Olá, {nome}!</p>
            <p>Sua matrícula: {matricula}<br>Sua nota: {nota}</p>
            <p>Atenciosamente,<br>Equipe Acadêmica</p>
            {assinatura}"""
            
            # Enviando o e-mail
            send_email_via_outlook(outlook, email, subject, body)

if __name__ == "__main__":
    main()
