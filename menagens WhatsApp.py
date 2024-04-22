import pandas as pd
from selenium.webdriver.common.keys import Keys
import pyperclip
import time
import csv
from tkinter import Tk, filedialog
from openpyxl import load_workbook
import selenium as sl
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time


def selecionar_arquivo():
    root = Tk()
    root.withdraw()  # Não mostrar a janela completa do Tk
    root.attributes('-topmost', True)
    path_to_file = filedialog.askopenfilename(title="Selecione o arquivo Excel")
    return path_to_file

# Caminho do seu arquivo CSV
caminho_do_arquivo = selecionar_arquivo()


# Carregar a planilha
planilha = pd.read_excel(caminho_do_arquivo, sheet_name='Plan1')
contatos_df = pd.DataFrame(planilha)
contatos_df = contatos_df[['Nome', 'Telefone']]
contatos_df.dropna(subset=['Telefone'], inplace=True)
contatos_df['Telefone'] = contatos_df['Telefone'].astype(str).str.replace('.0', '')
contatos_df.head(20)
contatos_df = contatos_df.drop(labels=[0,1,2,3,4,5,6,7], axis=0)
contatos_df['Telefone'] = '55' + contatos_df['Telefone']
contatos_df.head(20)
# Inicializar um dicionário vazio
dicionario = contatos_df.set_index('Nome')['Telefone'].to_dict()




print(dicionario)