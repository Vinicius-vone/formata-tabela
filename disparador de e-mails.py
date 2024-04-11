import win32com.client as win32
import pandas as pd
from tkinter import Tk, filedialog


def selecionar_anexo():
    root = Tk()
    root.withdraw()  # Não mostrar a janela completa do Tk
    root.attributes('-topmost', True)
    path_to_file = filedialog.askopenfilename(title="Selecione o arquvivo a ser anexado")
    return selecionar_anexo(path_to_file)



# Criando integração do Python com o Outlook
outlook = win32.Dispatch('outlook.application')

# Criando um e-mail
email = outlook.CreateItem(0)
emails = {} #não sei ainda como vou fazer a lista
periodo = {} #ainda vou ver como criar a variável, deixei como lista só pra deixa o objeto periodo já criado
medico = {} #Lista de médicos para iterar no código e enviar o e-mail para todos


# Configurando as informações do e-mail
email.To = f"{emails}"
email.Subject = f"HNSM - Relatório de Honorários Médicos - {periodo}"
email.HTMLBody = f"""

<p>Prezado Dr.{medico}</p>

<p> Segue em anexo o relatório dos honorários médicos a respeito dos procedimentos pagos, faturados e a faturar referentes ao período de {periodo}</p>

<p>Atenciosamente,</p>
<p> Alfredo Vinícius Andrade Guimarães</p>
<p> Setor de Faturamento</p>
<p> Hospital de Nossa Senhora das Mercês</p>
<p> Fone: (32)98447-5784 (WhatsApp e Telegram)</p>
<img src="Logo hospital.png" />
"""


anexo = selecionar_anexo()
email.Attachments.Add(anexo)


email.Send()
