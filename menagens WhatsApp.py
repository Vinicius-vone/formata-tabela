import pandas as pd
from tkinter import Tk, filedialog
import pyautogui as pag

pag.PAUSE = 1

def selecionar_arquivo():
    root = Tk()
    root.withdraw()  # Não mostrar a janela completa do Tk
    root.attributes('-topmost', True)
    path_to_file = filedialog.askopenfilename(title="Selecione o arquivo Excel")
    return path_to_file

def enviar_mensagem(nome, arquivo, mensagem):
    try: 
        pag.sleep(2)
        pag.click(x=188, y=106)
        pag.sleep(2)
        pag.write(f"{nome}")
        pag.sleep(1)
        pag.press('enter')
        pag.sleep(2)
        pag.click(x=542, y=696)
        pag.sleep(2)
        pag.click(x=597, y=306)
        pag.sleep(2)
        pag.write(arquivo)
        pag.sleep(2)
        pag.press('enter')
        pag.sleep(2)
        pag.write(mensagem)
        pag.sleep(5)
        pag.press('enter')
        pag.sleep(6)
        return f"Arquivo de {nome} enviado com sucesso!"
    except Exception as nome:
        return f"Não foi possível enviar o arquivo de {nome}."

# Selecionar o arquivo
# caminho_do_arquivo = selecionar_arquivo()


# # Carregar a planilha
# planilha = pd.read_excel(caminho_do_arquivo, sheet_name='Plan1')
# contatos_df = pd.DataFrame(planilha)
# contatos_df = contatos_df[['Nome', 'Telefone']]
# contatos_df.dropna(subset=['Telefone'], inplace=True)
# contatos_df['Telefone'] = contatos_df['Telefone'].astype(str).str.replace('.0', '')
# contatos_df.head(20)
# contatos_df = contatos_df.drop(labels=[0,1,2,3,4,5,6,7], axis=0)
# contatos_df['Telefone'] = '55' + contatos_df['Telefone']
# contatos_df.head(20)
# # Inicializar um dicionário vazio
# dicionario = contatos_df.set_index('Nome')['Telefone'].to_dict()
# print(dicionario)

# nomes = contatos_df['Nome'].tolist()

periodo_referencia = "10 de outubro de 2023 a 10 de abril de 2024"

nomes = ['Celular Hospital', 'Vini']

# Iterar sobre a lista de médicos
pag.click(x=227, y=752)
for nome in nomes:
    nome_formatado = nome.upper()
    arquivo = f"{nome_formatado}_relatorio.pdf"
    mensagem = f"Prezado Dr(a). {nome}, segue em anexo o relatório de Honorários Médicos do período de referência compreendido entre {periodo_referencia}."
    enviar_mensagem(nome, arquivo, mensagem)