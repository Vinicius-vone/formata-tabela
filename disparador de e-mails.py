import win32com.client as win32
import pandas as pd
from tkinter import Tk, filedialog
import os


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
emails = "kelonios2000@yahoo.com.br" #não sei ainda como vou fazer a lista
periodo = "10 de outubro de 2023 a 10 de abril de 2024" #ainda vou ver como criar a variável, deixei como lista só pra deixa o objeto periodo já criado

#AINDA É NECESSÁRIA A CRIAÇÃO DE UM DICIONÁRIO ONDE A CHAVE É NO NOME DO MÉDICO E O VALOR É O EMAIL. ESSE DICIONÁRIO VAI SER USADO
#NA ITERAÇÃO PARA QUE A PARTIR DO NOME DO MÉDICO SEJA POSSÍVEL ESCOLHER O EMAIL E O ARQUIVO PRESENTE NA PASTA DE RELATÓRIOS

#BLOCO ABAIXO DEVE SER ITERADO SOBRE TODOS OS MÉDICOS E PARA CADA NOME DE MÉDICO ADICIONAR O ARQUIVO PRESENTE NA LISTA
#DE ARQUIVOS CRIADA A PARTIR DA PASTA SELECIONADA
# Criando um e-mail
email = outlook.CreateItem(0)
medico = "Alfredo Vinícius" #Lista de médicos para iterar no código e enviar o e-mail para todos
# Configurando as informações do e-mail
email.To = f"{emails}"
email.Subject = f"HNSM - Relatório de Honorários Médicos - {periodo}"
email.HTMLBody = f"""
<p>Prezado Dr.{medico}</p>
<p> Segue em anexo o relatório dos honorários médicos a respeito dos procedimentos pagos, faturados e a faturar referentes ao período de {periodo}</p>
<p>Aenciosamente,<\p>
{assinatura}
"""
anexo = f"C:/Users/ACER/Meu Drive/Hospital Nossa Senhora das Mercês/Códigos Python/Códigos Funcionando/Reatórios Médicos/{arquivos}"
email.Attachments.Add(anexo)
email.Send()
