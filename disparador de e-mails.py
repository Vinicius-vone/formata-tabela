import win32com.client as win32
import pandas as pd
from tkinter import Tk, filedialog
import os
import unicodedata

def normalizar_nome(nome):
    nome_sem_acentos = ''.join(c for c in unicodedata.normalize('NFD', nome) if unicodedata.category(c) != 'Mn')
    nome_upper = nome_sem_acentos.upper()
    # Remover palavras específicas do nome do arquivo
    nome_limpo = nome_upper.replace('_RELATORIO', '').replace('.PDF', '')
    return nome_limpo

# Seleção dos anexos - Cria uma lista com o nome de todos os arquivos presentes na pasta selecionada
# Cria e esconde a janela principal do Tkinter
root = Tk()
root.withdraw()
# Abre a janela de diálogo para o usuário escolher uma pasta
folder_selected = filedialog.askdirectory()
arquivos = os.listdir(folder_selected)

#Definição da assinatura a ser inserida no e-mail
assinatura = """<p style="text-align: left;"><strong>Alfredo Vincícius Andrade Guimarães</strong><br>
<strong>Setor de Faturamento</strong><br>
<strong>Hospital de Nossa Senhora das Mercês</strong><br>
<strong>Telefone: (32)98808-3456</strong> </p>
<p style="text-align: left;"><a href="mailto:alfredovinicius@hospitaldasmerces.com">E-mail</a>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
<a href="https://wa.me/5532984475784">WhatsApp</a>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <a href="https://t.me/viniciushnsm">Telegram</a></p>"""

# Criando integração do Python com o Outlook
outlook = win32.Dispatch("Outlook.Application")
medicos_emails = {
    "Alfredo Vinícius": "email1@example.com",
    "Maria Clara": "email2@example.com",
    # Adicione mais médicos conforme necessário
}
periodo = "10 de outubro de 2023 a 10 de abril de 2024" #ainda vou ver como criar a variável, deixei como lista só pra deixa o objeto periodo já criado

for medico, email_medico in medicos_emails.items():
    nome_normalizado = normalizar_nome(medico)

    # Tentativa de encontrar um arquivo que corresponda ao nome normalizado do médico
    arquivo_medico = next((arq for arq in arquivos if nome_normalizado in normalizar_nome(arq)), None)

    if arquivo_medico:
        caminho_completo_arquivo = os.path.join(folder_selected, arquivo_medico)
        
        # Criando um e-mail
        email = outlook.CreateItem(0)
        email.To = email_medico
        email.Subject = f"HNSM - Relatório de Honorários Médicos - {periodo}"
        email.HTMLBody = f"""
        <p>Prezado(a) Dr(a). {medico},</p>
        <p>Segue em anexo o relatório dos honorários médicos a respeito dos procedimentos pagos, faturados e a faturar referentes ao período de {periodo}.</p>
        <p>Atenciosamente,</p>
        {assinatura}
        """
        email.Attachments.Add(caminho_completo_arquivo)
        email.Send()
    else:
        print(f"Arquivo não encontrado para o médico: {medico}")
