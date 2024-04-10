import pandas as pd
from selenium.webdriver.common.keys import Keys
import pyperclip
import time
import csv
from tkinter import Tk, filedialog
from openpyxl import load_workbook

def selecionar_arquivo():
    Tk().withdraw()  # Não mostrar a janela completa do Tk
    path_to_file = filedialog.askopenfilename(title="Selecione o arquivo Excel")
    return path_to_file

# Caminho do seu arquivo CSV
caminho_do_arquivo = selecionar_arquivo()


# Carregar a planilha
planilha = pd.read_excel(caminho_do_arquivo)
wb = load_workbook(filename=caminho_do_arquivo)
sheet = wb.active  # Assumindo que os dados estão na primeira aba

# Inicializar um dicionário vazio
dicionario = {}

# Supondo que a primeira linha tenha os cabeçalhos
# e 'Name' e 'Home Phone' sejam os títulos das colunas desejadas
for row in sheet.iter_rows(min_row=2, values_only=True):
    nome = row[0]  # Assumindo que 'Name' esteja na primeira coluna
    home_phone = row[1]  # Assumindo que 'Home Phone' esteja na segunda coluna
    
    dicionario[nome] = home_phone

# Exibir o dicionário

print(dicionario)