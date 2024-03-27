import pandas as pd
import numpy as np
from tkinter import Tk, filedialog, simpledialog, messagebox
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_RIGHT  # Importação necessária para centralizar o texto
import os

#FORMATAÇÃO DO DATAFRAME A PARTIR DO ARQUIVO TXT RETIRADO DIRETAMENTE DO SPDATA
# Padrões de linhas para ignorar
ignore_patterns = [
    "+-------------------------------------------------------------------------------------------------------------------------------------------------------Spdata-+",
    "| HOSPITAL NOSSA SENHORA DAS MERCES              Faturamento Convenios - Glosas(Listagem IV) -                 Todas                                           |",
    "+----------+----------+------------------------------+--------------------------+-----------------+----------+-------------+-------------+----------+----------+",
    "| Processamento: Janeiro/2024 a Março/2024     Remessa: 000 a 999 Medicos: Todos                Prestadores: Todos",
    "|                       Subtotal              --->>",
    "|                       Total para este medico -->>",
    "|                                Total da conta ->>",
    "+----------------------------------------------------+-------------------------------------------------------+-------------+-------------+----------+----------+",
    "| Convenio: 0004 BANCO DO BRASIL  a  0200 PLAMEDH                                                                 C.D.C.: 000000 a 999999   Unidade: 00 a 99   |",
    "| Registro |  Data    | Paciente                     | Procedimento             | Motivo da Glosa |  Baixa   | V. Faturado | V. Recebido | Diferenca|  A Maior |",
    "|                       Total Geral           --->>  |                Número de Contas: 4099                 |   665.099,50|   137.092,37|-528.155,02|    147,89|",
    "|                       Total Convenio        -->> ",
    "|                       Total Geral           --->> "
]

def line_should_be_ignored(line):
    """
    Verifica se a linha contém algum dos padrões especificados para ser ignorada.
    """
    for pattern in ignore_patterns:
        if pattern in line:
            return True
    return False

def read_file_to_list(input_file_path):
    """
    Lê o arquivo e retorna uma lista com as linhas que não contêm os padrões especificados.
    """
    lines = []
    with open(input_file_path, 'r', encoding='ISO-8859-1') as infile:
        for line in infile:
            if not line_should_be_ignored(line):
                # Adiciona a linha à lista, removendo espaços extras e o caractere de nova linha
                cleaned_line = line.strip()
                lines.append(cleaned_line)
    return lines

# Função para formatar valores em formato de moeda

def formatar_valor(valor):
    return "R${:,.2f}".format(valor).replace(",", "X").replace(".", ",").replace("X", ".")

# Função para converter valor formatado de volta para float
def valor_para_float(valor_formatado):
    if isinstance(valor_formatado, str) and (',' in valor_formatado or '.' in valor_formatado):
        # Substitui ponto por nada e vírgula por ponto
        valor_formatado = valor_formatado.replace('.', '').replace(',', '.')
    # Tenta converter para float, se não for uma string retorna o valor como está
    return float(valor_formatado) if isinstance(valor_formatado, str) else valor_formatado
    

def converter_valor_monetario_para_float(valor_monetario):
    # Remove o símbolo de moeda e substitui a vírgula por ponto
    valor_formatado = valor_monetario.replace('R$', '').replace(',', '.').replace('.', '')
    # Converte para float
    return float(valor_formatado)

def selecionar_arquivo_e_diretorio():
    root = Tk()
    root.withdraw()  # Não mostrar a janela completa do Tk
    root.attributes('-topmost', True)
    path_to_file = filedialog.askopenfilename(title="Selecione o arquivo de texto", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
    root.destroy()
    return path_to_file, 

path_to_file = selecionar_arquivo_e_diretorio()

#FORMATAÇÃO DO DATAFRAME A PARTIR DO ARQUIVO TXT RETIRADO DIRETAMENTE DO SPDATA
# Ler arquivo e criar lista
lines_list = read_file_to_list(path_to_file)

# Dividir cada linha pela barra vertical '|' e remover espaços vazios das strings resultantes
data = [line.split('|') for line in lines_list]
# Remover espaços vazios em cada elemento da lista
data = [[item.strip() for item in row] for row in data]

# Criar DataFrame
dados_crua_inicial = pd.DataFrame(data)

# O DataFrame agora possui as linhas como entradas, mas pode ter colunas de mais ou de menos dependendo do conteúdo das linhas.
# Você pode precisar ajustar os nomes das colunas manualmente, dependendo da estrutura do seu arquivo e do número de colunas esperadas.
# Por exemplo, se esperamos 10 colunas, podemos nomeá-las assim:

# Substitui strings vazias por NaN para identificar corretamente campos vazios
dados_crua_inicial.replace('', pd.NA, inplace=True)

# Remove linhas onde todos os campos estão vazios
dados_crua_inicial.dropna(how='all', inplace=True)
dados_crua_inicial = dados_crua_inicial.drop(dados_crua_inicial.columns[[0, 10, 11]], axis=1)
# Se necessário, você pode querer resetar os índices após remover linhas
dados_crua_inicial.reset_index(drop=True, inplace=True)
dados_crua_inicial.columns = ['Registro', 'Data', 'Paciente', 'Procedimento', 'Motivo da Glosa', 'Pago', 'V. Faturado', 'V. Recebido', 'Diferenca']


#Dicionário com os nomes corretos para os convenios
dicionario_convenios = {
    'BANCO DO BRASIL':"Banco do Brasil", 'POLICIA MILITAR':"Polícia Militar", 'CEMIG SAUDE':"CEMIG", 'FUSEX':"FUSEX",
    'ASSEFAZ':"ASSEFAZ", 'CAIXA ECONOMICA FEDERAL':"Caixa Econômica", 'ECT (EMP. BRAS. DE CORREIOS E TELEG.)':"ECT", 'SUL AMERICA AETNA SEGUROS E PREVIDENCIA':"Sul América", 
    'SANTA CASA SAUDE COMPLEMENTAR':"SASC", 
    'SAUDE BRADESCO EMPRESARIAL':"Bradesco Emp", 'CONSORCIO INTERMUNICIPAL DE SAUDE DAS VERTENTES':"Cisver", 'PLAMEDH':"Plamedh", 
    'FUNDACAO LIBERTAS (PREVIMINAS)':"Previminas", 'BRASIL ASSISTENCIA S/A':"Brasil Assistencia",
    'USISAUDE (FUNDAÇAO SAO FRANCISCO XAVIER)':"Usisaude", 'PATRONAL':"GEAP", 'AECO':"AECO", "UNIMED":"Unimed", 'CASU':"CASU", 
    'FUNDAFFEMG':"FUNDAFFEMG", 
    'SAUDE BRADESCO INDIVIDUAL':"Bradesco Ind", 'A.M.M.P.':"AMMP", "PREMIUM SAUDE":"Premium Saude","SUL AMERICA AETNA SEGUROS E PR":"Sul América",
    'CONSORCIO INTERMUNICIPAL DE SA':"Cisver", "USISAUDE (FUNDAÇAO SAO FRANCIS":'Usisaude', "ECT (EMP. BRAS. DE CORREIOS E": 'ECT',
    "PATRONAL-GEAP":'GEAP', "CASU - CAIXA DE ASSISTENCIA A": "Caixa Econômica", "SASC - SANTA CASA SAUDE COMPLE":"SASC"
    }



#Completa os valores faltantes do arquivo excel de entrada


#Criação das colunas com o nome do médico e com o nome do convênio para os pagos e não pagos
medico_atual = ''
convenio_atual = ''
dados_processados = []

for index, linha in dados_crua_inicial.iterrows():
    registro = str(linha['Registro']).strip()
    if "Convenio:" in registro:
        convenio_atual = " ".join(registro.split()[2:])
        convenio_atual = dicionario_convenios.get(convenio_atual, convenio_atual)
    elif "Medico..:" in registro:
        medico_atual = " ".join(registro.split()[2:])  # Atualiza o médico atual, removendo o código
    else:
        # Inclui a linha atual no processamento, adicionando o médico e convênio atuais
        dados_processados.append({
            **linha.to_dict(), # Mantém todas as colunas originais
            'Medico': medico_atual,
            'Convenio': convenio_atual
        })
dados_processados_pagos = pd.DataFrame(dados_processados)

dados_processados_pagos_1 = dados_processados_pagos[dados_processados_pagos['Pago'].notna()]
dados_processados_pagos_final = dados_processados_pagos_1.ffill()

dados_processados_nao_pagos = pd.DataFrame(dados_processados)

dados_processados_nao_pagos_1 = dados_processados_nao_pagos[dados_processados_nao_pagos['Pago'].isna()][["Registro", "Procedimento", "Paciente", "V. Faturado", "Data", "Convenio", "Medico"]]
dados_processados_nao_pagos_final = dados_processados_nao_pagos_1.ffill()


dados_processados_pagos_df = pd.DataFrame(dados_processados_pagos_final)
dados_processados_nao_pagos_df = pd.DataFrame(dados_processados_nao_pagos_final)

#Ajustando as datas e os formatos de Data
dados_processados_pagos_df['Data'] = pd.to_datetime(dados_processados_pagos_df['Data'], errors='coerce', format='%d/%m/%Y')
dados_processados_pagos_df['Pago'] = pd.to_datetime(dados_processados_pagos_df['Pago'], errors='coerce')
dados_processados_pagos_df['Data'] = pd.to_datetime(dados_processados_pagos_df['Data']).dt.strftime('%d/%m/%Y')
dados_processados_pagos_df['Pago'] = pd.to_datetime(dados_processados_pagos_df['Pago']).dt.strftime('%d/%m/%Y')
dados_processados_nao_pagos_df['Data'] = pd.to_datetime(dados_processados_nao_pagos_df['Data'], errors='coerce', format='%d/%m/%Y')
dados_processados_nao_pagos_df['Data'] = pd.to_datetime(dados_processados_nao_pagos_df['Data']).dt.strftime('%d/%m/%Y')

dados_processados_pagos_df = dados_processados_pagos_df[~dados_processados_pagos_df['Procedimento'].str.contains("Serv. Profissionais", na=False)]
dados_processados_nao_pagos_df = dados_processados_nao_pagos_df[~dados_processados_nao_pagos_df['Procedimento'].str.contains("Serv. Profissionais", na=False)]


dados_processados_pagos_df.to_excel('C:/Users/ACER/Meu Drive/Hospital Nossa Senhora das Mercês/Dashboard/Projeto Diagnóstico de Faturamento/dados_processados_pagos_df.xlsx', index=False)
dados_processados_nao_pagos_df.to_excel('C:/Users/ACER/Meu Drive/Hospital Nossa Senhora das Mercês/Dashboard/Projeto Diagnóstico de Faturamento/dados_processados_nao_pagos_df.xlsx', index=False)
