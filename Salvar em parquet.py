import pandas as pd
import numpy as np
from tkinter import Tk, filedialog, simpledialog, messagebox
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER  # Importação necessária para centralizar o texto
import os
import re
import matplotlib.pyplot as plt
import glob

#FORMATAÇÃO DO DATAFRAME A PARTIR DO ARQUIVO TXT RETIRADO DIRETAMENTE DO SPDATA
# Padrões de linhas para ignorar
ignore_patterns = [
    "+-------------------------------------------------------------------------------------------------------------------------------------------------------Spdata-+",
    "| HOSPITAL NOSSA SENHORA DAS MERCES              Faturamento Convenios - Glosas(Listagem IV) -                                                            |",
    "| HOSPITAL NOSSA SENHORA DAS MERCES              Faturamento Convenios - Glosas(Listagem IV) -                 Apenas Glosas                                   |",
    "| HOSPITAL NOSSA SENHORA DAS MERCES              Faturamento Convenios - Glosas(Listagem IV) -                 Todas                                           |",

    "+----------+----------+------------------------------+--------------------------+-----------------+----------+-------------+-------------+----------+----------+",
    "| Processamento:",
    "|                       Subtotal              --->>",
    "|                       Total para este medico -->>",
    "|                                Total da conta ->>",
    "+----------------------------------------------------+-------------------------------------------------------+-------------+-------------+----------+----------+",
    "|     C.D.C.: 000000 a 999999   Unidade: 00 a 99   |",
    "| Registro |  Data    | Paciente                     | Procedimento             | Motivo da Glosa |  Baixa   | V. Faturado | V. Recebido | Diferenca|  A Maior |",
    "|                       Total Geral           --->>  |                Número de Contas: 4099                 |   665.099,50|   137.092,37|-528.155,02|    147,89|",
    "|                       Total Convenio        -->> ",
    "|                       Total Geral           --->> ",
    "|                       Total para este medico -->>  |",
    "| HOSPITAL NOSSA SENHORA DAS MERCES              Faturamento Convenios - Glosas(Listagem IV) -                 Apenas Pagas                                    |",
    "| HOSPITAL NOSSA SENHORA DAS MERCES              Faturamento Convenios - Glosas(Listagem IV) -                 Não Pagas                                       |",
    "| Sistema de Gestão Hospitalar                 Faturamento de Convenios",
    "+------------------------------------+-+---------+------+-+--+-+----------+----------+-------+---+---+---+---+----+----+--------------------------+------------+",
    "|      Nome do Paciente              |R|Registro |N.Fis.|T|R |N|Dt. Atend.| Dt. Alta |Horario|SP |SH |RC |MM |Emit|Fech| Convenio                 | Valor Conta|",
    "+------------------------------------+-+---------+------+-+--+-+----------+----------+-------+---+---+---+---+----+----+--------------------------+------------+",
    "|  Total de Registros por Médico   =>",
    "+--------------------------------------------------------------------------------------------------------------------------------------------------------------+",
    "|                                       S.P.Data - Servico de Processamento de Dados Ltda. - Telefone: (031)3399-2500                                          |",
    "|             Total de Registros   =>",
    "|                                                 HOSPITAL NOSSA SENHORA DAS MERCES                                                                            |",
    "| Emitido em:                 Processamento:                C.D.C.: 000000 a 999999               Unidade: 00 a 99 |"
    "|                                                                                                                                                              |",
    "+-------------------------------------------------------------------------------------------------------------------------------------------------------Spdata-+",
    "| Sistema de Gestão Hospitalar                                       Fatura de Prestadores de Servico - Analitica - V  ",
    "| (Valores Faturados)           Com Valores do Filme no Total       Valores do Filme não Somado ao Repasse                                                     |",
    "|                                                 HOSPITAL NOSSA SENHORA DAS MERCES                                                                            |",
    "| Emitido em: ",
    "+--------------------------------------------------------------------------------------------------------------------------------------------------------------+",
    "| CNPJ: 24.731.747/0001-88 PRACA BARAO DE ITAMBE, 31                Bairro: CENTRO                    Cidade: SAO JOAO DEL REI             Fone: 32 3379-2800  |",
    "+---------+-+-----------------------------------------+----------+-------------------------------------------+-----+-----+--------+----------+------+----------+"
    "| Conta   |C| Nome do Paciente                        |Data Atend|Procedimento AMB                           |Qtde |C.H. | Filme  |Vlr. Total|  %Rp |  Valor   |",
    "+---------+-+-----------------------------------------+----------+-------------------------------------------+-----+-----+--------+----------+------+----------+",
    "|                                                                                     Valor Total ----->>> ",
    "|                                            S.P.Data Servico de Processamento de Dados Ltda - Tel.:(31) 3399-2500                                             |",
    "| (Valores Pagos)               Com Valores do Filme no Total       Valores do Filme não Somado ao Repasse                                                     |",
    "+----------+----------+------------------------------+--------------------------+-----------------+----------+-------------+-------------+----------+----------+",
    "|                       Subtotal              --->>  |",
    "|                       Total para este medico -->>  |",
    "| Registro |  Data    | Paciente                     | Procedimento             | Motivo da Glosa |  Baixa   | V. Faturado | V. Recebido | Diferenca|  A Maior |"

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
    path_to_file_pagos = filedialog.askopenfilename(title="Selecione o arquivo de texto dos pedidos pagos", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
    path_to_file_nao_pagos = filedialog.askopenfilename(title="Selecione o arquivo de texto dos pedidos não pagos", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
    path_to_file_a_faturar = filedialog.askopenfilename(title="Selecione o arquivo de texto dos pedidos a faturar", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
    path_to_file_endo_pago = filedialog.askopenfilename(title="Selecione o arquivo de texto das endoscopias pagas", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
    path_to_file_endo_nao_pago = filedialog.askopenfilename(title="Selecione o arquivo de texto das endoscopias não pagas", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
    path_to_file_sus_aih = filedialog.askopenfilename(title="Selecione o arquivo de texto dos pedidos SUS AIH", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
    path_to_file_sus_ambulatorio = filedialog.askopenfilename(title="Selecione o arquivo de texto dos pedidos SUS Ambulatorio", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
    output_directory = filedialog.askdirectory(title="Selecione o diretório para salvar o arquivo PDF")
    subtitulo = simpledialog.askstring("Subtítulo", "Digite o período:", parent=root)
    root.destroy()
    return path_to_file_pagos, path_to_file_nao_pagos, path_to_file_a_faturar, subtitulo, path_to_file_endo_pago, path_to_file_endo_nao_pago, path_to_file_sus_aih, path_to_file_sus_ambulatorio, output_directory


def dados_sus_aih(file_path):
    file_path = path_to_file_sus_aih
    ignore_text = ['189-HOSPITAL NOSSA SENHORA DAS MERCES', "Sistema de Gerenciamento Hospitalar", "Complexidade"]  # Texto a ser ignorado
    # Lista para armazenar os dados
    data = []
    # Abrir e ler o arquivo de textoS
    with open(file_path, 'r', encoding='ISO-8859-1') as file:
        current_doctor = None  # Inicializar a variável do médico aqui
        for line in file:
            if any(text in line for text in ignore_text):
                continue  # Ignorar a linha
            # Atualizar o nome do médico quando uma nova linha de médico for encontrada
            if 'CPF:' in line:
                current_doctor = line.split('CPF:')[0].strip()
                continue  # Pular para a próxima iteração depois de atualizar o médico

            # Processar linhas de dados
            if line.strip() and line[0].isdigit():
                # Regex detalhada para capturar todos os campos
                regex = r"(\d+) ([\w\s]+?) +(\d{10}) ([\w\s]+?) (\d{2}/\d{2}/\d{4}) (\d{2}/\d{2}/\d{4}) ([\w-]+) +(\d+) +(\d+) +(\d+,\d+) +(\d+,\d+)"
                match = re.match(regex, line)
                if match:
                    groups = match.groups()
                    aih = groups[0]
                    paciente = groups[1]
                    codigo_procedimento = groups[2]
                    descricao_procedimento = groups[3]
                    procedimento = f"{codigo_procedimento} {descricao_procedimento}"
                    internacao = groups[4]
                    alta = groups[5]
                    ato = groups[6]
                    quantidade = groups[7]
                    pontos = groups[8]
                    valor = groups[9]
                    valor_repassado = groups[10]
                    
                    # Adicionar linha ao conjunto de dados
                    data.append([aih, paciente, procedimento, internacao, alta, ato, quantidade, valor, current_doctor])

    # Criar DataFrame
    return pd.DataFrame(data, columns=['AIH', 'Paciente', 'Procedimento', 'Internação', 'Alta', 'Ato', 'Quantidade', 'Valor', 'Medico'])

def dados_sus_ambulatorio(file_path):
    def extract_doctor_name(text):
        clean_text = text.split('CPF/CGC:')[0].strip()
        # Regex pattern to find "CRM/CRO:" followed by space and digits
        pattern = r"CRM/CRO:\s+\d+\s+"
        # Using re.sub to replace the matched pattern with an empty string
        clean_text = re.sub(pattern, '', clean_text)
        return clean_text

    # Caminho para o arquivo de texto
    file_path = path_to_file_sus_ambulatorio
    ignore_text = ['189 HOSPITAL NOSSA SENHORA DAS MERCES', "Sistema de Gerenciamento Hospitalar", "Complexidade", "+----------------------------------------------------------------------------------------------------------------------------Spdata-+",
                "| Emitido em:", "Sistema de Gestão Hospitalar", "+-----------------------------------------------------------------------------------------------------------------------------------+", "Unidade:"]  # Texto a ser ignorado
    # Lista para armazenar os dados
    all_data = []
    # Abrir e ler o arquivo de textoS
    with open(file_path, 'r', encoding='ISO-8859-1') as file:
        current_doctor = None  # Inicializar a variável do médico aqui
        for line in file:
            if any(text in line for text in ignore_text):
                continue  # Ignorar a linha
            # Atualizar o nome do médico quando uma nova linha de médico for encontrada
            if 'CRM/CRO:' in line:
                current_doctor = extract_doctor_name(line)
                continue  # Pular para a próxima iteração depois de atualizar o médico
            pattern = r"(\d{8})\s+([A-Z\s]+)\s+(\d{2}\.\d{2}\.\d{2}\.\d{3}-\d)\s+(\d{2}/\d{2}/\d{4})\s+(\w+)\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)\s+([\d,]+(?:\s+\(\d+,\d+%\)))"
            match = re.match(pattern, line.strip())
            #     r"(\d{8})"           # (\d{8}): Matches exactly 8 digits, captures the "Conta" (Account number).
            #     r"\s+"               # \s+: Matches one or more whitespace characters, used as a separator.
            #     r"([A-Z\s]+?)"       # ([A-Z\s]+?): Matches a sequence of uppercase letters and spaces, non-greedy; captures "Paciente" (Patient name).
            #     r"\s+"               # Separator.
            #     r"(\d{2}\.\d{2}\.\d{2}\.\d{3}-\d)"  # Matches a specific pattern like '03.01.01.004-8', captures "Procto" (Procedure code).
            #     r"\s+"               # Separator.
            #     r"(\d{2}/\d{2}/\d{4})"  # Matches dates in the format DD/MM/YYYY, captures "Data" (Date).
            #     r"\s+"               # Separator.
            #     r"(\w+)"             # (\w+): Matches one or more word characters (letters, digits, underscore), captures "Ato" (Action/Procedure type).
            #     r"\s+"               # Separator.
            #     r"([\d,]+)"          # ([\d,]+): Matches a sequence of digits or commas, captures "Vlr. Hosp." (Hospital Value).
            #     r"\s+"               # Separator.
            #     r"([\d,]+)"          # Matches a sequence of digits or commas, captures "Vlr. Medico" (Doctor's Fee).
            #     r"\s+"               # Separator.
            #     r"([\d,]+)"          # Matches a sequence of digits or commas, captures "Valor" (Total Value).
            #     r"\s+"               # Separator.
            #     r"([\d,]+(?:\s+\(\d+,\d+%?\)))"  # Complex pattern for "Repasse": includes digits, commas, and optionally a percentage in parentheses.
            if match:
                    data = {
                        "Conta": match.group(1),
                        "Paciente": match.group(2).strip(),
                        "Procto": match.group(3),
                        "Data": match.group(4),
                        "Ato": match.group(5),
                        "Vlr. Hosp.": match.group(6),
                        "Vlr. Medico": match.group(7),
                        "Valor": match.group(8),
                        "Medico": current_doctor
                    }
                    all_data.append(data)

    # Criar DataFrame
    return pd.DataFrame(all_data)


path_to_file_pagos, path_to_file_nao_pagos, path_to_file_a_faturar, subtitulo, path_to_file_endo_pago, path_to_file_endo_nao_pago, path_to_file_sus_aih, path_to_file_sus_ambulatorio, output_directory = selecionar_arquivo_e_diretorio()
#FORMATAÇÃO DO DATAFRAME A PARTIR DO ARQUIVO TXT RETIRADO DIRETAMENTE DO SPDATA
# Ler arquivo e criar lista
lines_list_pagos = read_file_to_list(path_to_file_pagos)
lines_list_nao_pagos = read_file_to_list(path_to_file_nao_pagos)
lines_list_a_faturar = read_file_to_list(path_to_file_a_faturar)
lines_list_endo_pago = read_file_to_list(path_to_file_endo_pago)
lines_list_endo_nao_pago = read_file_to_list(path_to_file_endo_nao_pago)
lines_list_sus_aih = read_file_to_list(path_to_file_sus_aih)
lines_list_sus_ambulatorio = read_file_to_list(path_to_file_sus_ambulatorio)

# Dividir cada linha pela barra vertical '|' e remover espaços vazios das strings resultantes
data_pagos = [line.split('|') for line in lines_list_pagos]
# Remover espaços vazios em cada elemento da lista
data_pagos = [[item.strip() for item in row] for row in data_pagos]

data_nao_pagos = [line.split('|') for line in lines_list_nao_pagos]
# Remover espaços vazios em cada elemento da lista
data_nao_pagos = [[item.strip() for item in row] for row in data_nao_pagos]

data_a_faturar = [line.split('|') for line in lines_list_a_faturar]
# Remover espaços vazios em cada elemento da lista
data_a_faturar = [[item.strip() for item in row] for row in data_a_faturar]

data_endo_pagos = [line.split('|') for line in lines_list_endo_pago]
# Remover espaços vazios em cada elemento da lista
data_endo_pagos = [[item.strip() for item in row] for row in data_endo_pagos]

data_endo_nao_pagos = [line.split('|') for line in lines_list_endo_nao_pago]
# Remover espaços vazios em cada elemento da lista
data_endo_nao_pagos = [[item.strip() for item in row] for row in data_endo_nao_pagos]

# Criar DataFrame
dados_crua_inicial_pagos = pd.DataFrame(data_pagos)
dados_crua_inicial_nao_pagos = pd.DataFrame(data_nao_pagos)
dados_crua_inicial_a_faturar = pd.DataFrame(data_a_faturar)
dados_crua_inicial_endo_pagos = pd.DataFrame(data_endo_pagos)
dados_crua_inicial_endo_nao_pagos = pd.DataFrame(data_endo_nao_pagos)

# Substitui strings vazias por NaN para identificar corretamente campos vazios
dados_crua_inicial_pagos.replace('', pd.NA, inplace=True)

# Remove linhas onde todos os campos estão vazios
dados_crua_inicial_pagos.dropna(how='all', inplace=True)
dados_crua_inicial_pagos = dados_crua_inicial_pagos.drop(dados_crua_inicial_pagos.columns[[0, 10, 11]], axis=1)
# Se necessário, você pode querer resetar os índices após remover linhas
dados_crua_inicial_pagos.reset_index(drop=True, inplace=True)
dados_crua_inicial_pagos.columns = ['Registro', 'Data', 'Paciente', 'Procedimento', 'Motivo da Glosa', 'Pago', 'V. Faturado', 'V. Recebido', 'Diferenca']

dados_crua_inicial_nao_pagos.replace('', pd.NA, inplace=True)

# Remove linhas onde todos os campos estão vazios
dados_crua_inicial_nao_pagos.dropna(how='all', inplace=True)
dados_crua_inicial_nao_pagos = dados_crua_inicial_nao_pagos.drop(dados_crua_inicial_nao_pagos.columns[[0, 10, 11]], axis=1)
# Se necessário, você pode querer resetar os índices após remover linhas
dados_crua_inicial_nao_pagos.reset_index(drop=True, inplace=True)
dados_crua_inicial_nao_pagos.columns = ['Registro', 'Data', 'Paciente', 'Procedimento', 'Motivo da Glosa', 'Realizado', 'V. Faturado', 'V. Recebido', 'Diferenca']

dados_crua_inicial_a_faturar.replace('', pd.NA, inplace=True)

# Remove linhas onde todos os campos estão vazios
dados_crua_inicial_a_faturar.dropna(how='all', inplace=True)
dados_crua_inicial_a_faturar = dados_crua_inicial_a_faturar.drop(dados_crua_inicial_a_faturar.columns[[0, 2, 4, 5, 6, 7,  10, 11, 12, 13, 14, 15, 16, 18, 19]], axis=1)
# Se necessário, você pode querer resetar os índices após remover linhas
dados_crua_inicial_a_faturar.reset_index(drop=True, inplace=True)
dados_crua_inicial_a_faturar.columns = ['Nome do Paciente', 'Registro', 'Atendimento', 'Alta', 'Convenio']
dados_crua_inicial_a_faturar = dados_crua_inicial_a_faturar[~dados_crua_inicial_a_faturar['Nome do Paciente'].str.contains("Emitido em:", na=False)]
dados_crua_inicial_a_faturar['Convenio'] = dados_crua_inicial_a_faturar['Convenio'].str.replace('^\d+-', '', regex=True)

# Substitui strings vazias por NaN para identificar corretamente campos vazios
dados_crua_inicial_endo_pagos.replace('', pd.NA, inplace=True)
# Remove linhas onde todos os campos estão vazios
dados_crua_inicial_endo_pagos.dropna(how='all', inplace=True)
dados_crua_inicial_endo_pagos = dados_crua_inicial_endo_pagos.drop(dados_crua_inicial_endo_pagos.columns[[0, 2, 6, 7, 8, 9, 10, 12]], axis=1)
dados_crua_inicial_endo_pagos.reset_index(drop=True, inplace=True)
dados_crua_inicial_endo_pagos.columns = ['Conta', 'Paciente', 'Data Atend.', 'Procedimento', 'Valor']


dados_crua_inicial_endo_nao_pagos.replace('', pd.NA, inplace=True)
# Remove linhas onde todos os campos estão vazios
dados_crua_inicial_endo_nao_pagos.dropna(how='all', inplace=True)
dados_crua_inicial_endo_nao_pagos = dados_crua_inicial_endo_nao_pagos.drop(dados_crua_inicial_endo_nao_pagos.columns[[0, 2, 6, 7, 8, 9, 10, 12]], axis=1)
dados_crua_inicial_endo_nao_pagos.reset_index(drop=True, inplace=True)
dados_crua_inicial_endo_nao_pagos.columns = ['Conta', 'Paciente', 'Data Atend.', 'Procedimento', 'Valor']




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
    "PATRONAL-GEAP":'GEAP', "CASU - CAIXA DE ASSISTENCIA A": "Caixa Econômica", "SASC - SANTA CASA SAUDE COMPLE":"SASC", 
    "AECO-ASSOCIACAO DOS EMPREGADOS":"AECO", "CONSORCIO INTERMUNICI":"Cisver", "GV CLINICAS MEDICINA":"GV", "SUL AMERICA AETNA SEG":"Sul América", 
    "SAUDE BRADESCO EMPRES":"Bradesco Emp", "CAIXA ECONOMICA FEDER":"Caixa Econômica", "FUNDACAO LIBERTAS (PR":"Previminas", "ALBERGUE SANTO ANTONI":"Albergue S. Antônio",
    "SAUDE BRADESCO INDIVI":"Bradesco Ind", "ECT (EMP. BRAS. DE CO":"ECT", "PROASERV":"Proaserv", "CASU - CAIXA DE ASSIS":"CASU", "SASC - SANTA CASA SAU":"SASC",
    "USISAUDE (FUNDAÇAO SA":"Usisaude", "AECO-ASSOCIACAO DOS E":"AECO", "SABIN SINAI VITA ASSI":"SABIN", "CONSORCIO INTERMUNICIPAL DE SAUDE":"Cisver", "SASC - SANTA CASA SAUDE COMPLEMENT":"SASC",
    "ECT (EMP. BRAS. DE CORREIOS E TELE":"ECT"
    }



#Criação das colunas com o nome do médico e com o nome do convênio para os pagos, não pagos e a faturar
medico_atual_pagos = ''
medico_atual_nao_pagos = ''
medico_atual_a_faturar = ''
convenio_atual_pagos = ''
convenio_atual_nao_pagos = ''
medico_atual_endo_pagos = ''
medico_atual_endo_nao_pagos = ''
convenio_atual_endo_pagos = ''
convenio_atual_endo_nao_pagos = ''
dados_processados_pagos = []
dados_processados_nao_pagos = []
dados_processados_a_faturar = []
dados_processados_endo_pagos =[]
dados_precessados_endo_nao_pagos = []


#Cria as tabelas a partir dos dados obtidos de cada arquivo txt, incluindo p médico e o convênio em cada linha de forma interativa
for index, linha in dados_crua_inicial_pagos.iterrows():
    registro = str(linha['Registro']).strip()
    if "Convenio:" in registro:
        convenio_atual_pagos = " ".join(registro.split()[2:])
        convenio_atual_pagos = dicionario_convenios.get(convenio_atual_pagos, convenio_atual_pagos)
    elif "Medico..:" in registro:
        medico_atual_pagos = " ".join(registro.split()[2:])
    else:
        # Inclui a linha atual no processamento, adicionando o médico e convênio atuais
        dados_processados_pagos.append({
            **linha.to_dict(), # Mantém todas as colunas originais
            'Medico': medico_atual_pagos,
            'Convenio': convenio_atual_pagos
        })

for index, linha in dados_crua_inicial_nao_pagos.iterrows():
    registro = str(linha['Registro']).strip()
    if "Convenio:" in registro:
        convenio_atual_nao_pagos = " ".join(registro.split()[2:])
        convenio_atual_nao_pagos = dicionario_convenios.get(convenio_atual_nao_pagos, convenio_atual_nao_pagos)
    elif "Medico..:" in registro:
        medico_atual_nao_pagos = " ".join(registro.split()[2:])
    else:
        # Inclui a linha atual no processamento, adicionando o médico e convênio atuais
        dados_processados_nao_pagos.append({
            **linha.to_dict(), # Mantém todas as colunas originais
            'Medico': medico_atual_nao_pagos,
            'Convenio': convenio_atual_nao_pagos
        })

for index, linha in dados_crua_inicial_a_faturar.iterrows():
    registro = str(linha['Nome do Paciente']).strip()
    if "Medico:" in registro:
        medico_atual_a_faturar = re.sub('^\d+ - ', '', " ".join(registro.split()[1:])).strip()  # Atualiza o médico atual, removendo o código
    else:
        # Inclui a linha atual no processamento, adicionando o médico e convênio atuais
        dados_processados_a_faturar.append({
            **linha.to_dict(), # Mantém todas as colunas originais
            'Medico': medico_atual_a_faturar
        })

for index, linha in dados_crua_inicial_endo_pagos.iterrows():
    registro = str(linha['Conta']).strip()
    if "Convenio.:" in registro:
        convenio_atual_endo_pagos = " ".join(registro.split()[3:])
        convenio_atual_endo_pagos = dicionario_convenios.get(convenio_atual_endo_pagos, convenio_atual_endo_pagos)
    elif "Laboratorio:" in registro:
        medico_atual_endo_pagos = " ".join(registro.split()[1:])
        medico_atual_endo_pagos = medico_atual_endo_pagos.replace(" Exame de Endoscopia Digestiva", "")
    else:
        # Inclui a linha atual no processamento, adicionando o médico e convênio atuais
        dados_processados_endo_pagos.append({
            **linha.to_dict(), # Mantém todas as colunas originais
            'Medico': medico_atual_endo_pagos,
            'Convenio': convenio_atual_endo_pagos
        })

for index, linha in dados_crua_inicial_endo_nao_pagos.iterrows():
    registro = str(linha['Conta']).strip()
    if "Convenio.:" in registro:
        convenio_atual_endo_nao_pagos = " ".join(registro.split()[3:])
        convenio_atual_endo_nao_pagos = dicionario_convenios.get(convenio_atual_endo_nao_pagos, convenio_atual_endo_nao_pagos)
    elif "Laboratorio:" in registro:
        medico_atual_endo_nao_pagos = " ".join(registro.split()[1:])
        medico_atual_endo_nao_pagos = medico_atual_endo_nao_pagos.replace(" Exame de Endoscopia Digestiva", "")
    else:
        # Inclui a linha atual no processamento, adicionando o médico e convênio atuais
        dados_precessados_endo_nao_pagos.append({
            **linha.to_dict(), # Mantém todas as colunas originais
            'Medico': medico_atual_endo_nao_pagos,
            'Convenio': convenio_atual_endo_nao_pagos
        })
#Criando os dataframes a parti da tabela gerada pelo código de inclusão de médicos e fazendo o ffill para completar os valores faltantes
dados_processados_pagos = pd.DataFrame(dados_processados_pagos)
dados_processados_pagos_final = dados_processados_pagos.ffill()

dados_processados_nao_pagos = pd.DataFrame(dados_processados_nao_pagos)
dados_processados_nao_pagos_final = dados_processados_nao_pagos.ffill()
dados_processados_nao_pagos_final = dados_processados_nao_pagos_final[["Registro", "Data", "Paciente", "Procedimento", "Realizado", "V. Faturado", "Medico", "Convenio"]]

dados_processados_a_faturar = pd.DataFrame(dados_processados_a_faturar)
dados_processados_a_faturar_final = dados_processados_a_faturar.ffill()
dados_processados_a_faturar_final['Convenio'] = dados_processados_a_faturar_final['Convenio'].map(dicionario_convenios)


dados_processados_pagos_df = pd.DataFrame(dados_processados_pagos_final)
dados_processados_nao_pagos_df = pd.DataFrame(dados_processados_nao_pagos_final)
dados_processados_a_faturar_df = pd.DataFrame(dados_processados_a_faturar_final)

dados_processados_endo_pagos = pd.DataFrame(dados_processados_endo_pagos)
dados_processados_endo_pagos_final = dados_processados_endo_pagos.ffill()
dados_processados_endo_pagos_df = pd.DataFrame(dados_processados_endo_pagos_final)


dados_precessados_endo_nao_pagos = pd.DataFrame(dados_precessados_endo_nao_pagos)
dados_precessados_endo_nao_pagos_final = dados_precessados_endo_nao_pagos.ffill()
dados_precessados_endo_nao_pagos_df = pd.DataFrame(dados_precessados_endo_nao_pagos_final)

#Ajustando as datas e os formatos de Data
dados_processados_pagos_df['Data'] = pd.to_datetime(dados_processados_pagos_df['Data'], errors='coerce', format='%d/%m/%Y')
dados_processados_pagos_df['Pago'] = pd.to_datetime(dados_processados_pagos_df['Pago'], errors='coerce', format='%d/%m/%Y')
dados_processados_pagos_df['Data'] = pd.to_datetime(dados_processados_pagos_df['Data']).dt.strftime('%d/%m/%Y')
dados_processados_pagos_df['Pago'] = pd.to_datetime(dados_processados_pagos_df['Pago']).dt.strftime('%d/%m/%Y')
dados_processados_nao_pagos_df['Data'] = pd.to_datetime(dados_processados_nao_pagos_df['Data'], errors='coerce', format='%d/%m/%Y')
dados_processados_nao_pagos_df['Data'] = pd.to_datetime(dados_processados_nao_pagos_df['Data']).dt.strftime('%d/%m/%Y')
dados_processados_nao_pagos_df['Realizado'] = pd.to_datetime(dados_processados_nao_pagos_df['Realizado'], errors='coerce', format='%d/%m/%Y')
dados_processados_nao_pagos_df['Realizado'] = pd.to_datetime(dados_processados_nao_pagos_df['Realizado']).dt.strftime('%d/%m/%Y')
dados_processados_a_faturar_df['Alta'] = pd.to_datetime(dados_processados_a_faturar_df['Alta'], errors='coerce', format='%d/%m/%Y')
dados_processados_a_faturar_df['Atendimento'] = pd.to_datetime(dados_processados_a_faturar_df['Atendimento'], errors='coerce', format='%d/%m/%Y')
dados_processados_a_faturar_df['Alta'] = pd.to_datetime(dados_processados_a_faturar_df['Alta']).dt.strftime('%d/%m/%Y')
dados_processados_a_faturar_df['Atendimento'] = pd.to_datetime(dados_processados_a_faturar_df['Atendimento']).dt.strftime('%d/%m/%Y')
dados_processados_endo_pagos_df['Data Atend.'] = pd.to_datetime(dados_processados_endo_pagos_df['Data Atend.'], errors='coerce', format='%d/%m/%Y')
dados_precessados_endo_nao_pagos_df['Data Atend.'] = pd.to_datetime(dados_precessados_endo_nao_pagos_df['Data Atend.'], errors='coerce', format='%d/%m/%Y')
dados_processados_endo_pagos_df['Data Atend.'] = pd.to_datetime(dados_processados_endo_pagos_df['Data Atend.']).dt.strftime('%d/%m/%Y')
dados_precessados_endo_nao_pagos_df['Data Atend.'] = pd.to_datetime(dados_precessados_endo_nao_pagos_df['Data Atend.']).dt.strftime('%d/%m/%Y')


#Retirando as linhas que contêm a palavra "Serv. Profissionais"
dados_processados_pagos_df = dados_processados_pagos_df[~dados_processados_pagos_df['Procedimento'].str.contains("Serv. Profissionais", na=False)]
dados_processados_nao_pagos_df = dados_processados_nao_pagos_df[~dados_processados_nao_pagos_df['Procedimento'].str.contains("Serv. Profissionais", na=False)]
retirar_palavras = ["Total Convenio", "V. Recebido", "Valor Geral", "Conta"]
for palavra in retirar_palavras:
    dados_processados_endo_pagos_df = dados_processados_endo_pagos_df[~dados_processados_endo_pagos_df['Conta'].str.contains(palavra, na=False)]
    dados_precessados_endo_nao_pagos_df = dados_precessados_endo_nao_pagos_df[~dados_precessados_endo_nao_pagos_df['Conta'].str.contains(palavra, na=False)]


id_dados_processados_endo_pagos_df = dados_processados_endo_pagos_df['Conta'].unique()
# Filtrando o dataframe df_faturados para remover os procedimentos já pagos
dados_precessados_endo_nao_pagos_df = dados_precessados_endo_nao_pagos_df[~dados_precessados_endo_nao_pagos_df['Conta'].isin(id_dados_processados_endo_pagos_df)]

dados_processados_sus_aih_df = dados_sus_aih(path_to_file_sus_aih)
dados_processados_sus_ambulatorio_df = dados_sus_ambulatorio(path_to_file_sus_ambulatorio)


dados_processados_a_faturar_df.to_parquet(f"{output_directory}/a_faturar_{subtitulo}.parquet")
dados_processados_pagos_df.to_parquet(f"{output_directory}/pagos_{subtitulo}.parquet")
dados_processados_nao_pagos_df.to_parquet(f"{output_directory}/nao_pagos_{subtitulo}.parquet")
dados_processados_endo_pagos_df.to_parquet(f"{output_directory}/endo_pagos_{subtitulo}.parquet")
dados_precessados_endo_nao_pagos_df.to_parquet(f"{output_directory}/endo_nao_pagos_{subtitulo}.parquet")
dados_processados_sus_aih_df.to_parquet(f"{output_directory}/sus_aih_{subtitulo}.parquet")
dados_processados_sus_ambulatorio_df.to_parquet(f"{output_directory}/sus_ambulatorio_{subtitulo}.parquet")