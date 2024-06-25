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
    "| HOSPITAL NOSSA SENHORA DAS MERCES              Faturamento Convenios - Glosas(Listagem IV) -                 Não Pagas",
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
    "Total de Registros por Convênio =>",
    "|                                                                                 Total p/este prestador ->",
    "|                                                                               Repasse p/este prestador ->"
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


def on_page(canvas, doc):
    canvas.saveState()
    styles = getSampleStyleSheet()

    # Carrega a imagem e ajusta seu tamanho proporcionalmente
    header = Image('C:/Users/ACER/Meu Drive/Hospital Nossa Senhora das Mercês/Modelo LaTeX/Logo hospital.png')
    max_height = 0.3 * inch  # Altura máxima para a imagem do cabeçalho
    image_aspect = header.imageWidth / header.imageHeight  # Calcula a proporção da imagem

    # Ajusta a altura e largura da imagem mantendo a proporção
    header.drawHeight = max_height
    header.drawWidth = max_height * image_aspect

    # Desenha a imagem no cabeçalho
    header.wrapOn(canvas, doc.width, doc.topMargin)
    header.drawOn(canvas, doc.leftMargin, doc.height + doc.topMargin - max_height)

    # Texto do cabeçalho
    header_text = f"Relatório de Valores"
    canvas.setFont('Helvetica', 12)
    canvas.drawString(doc.width + doc.leftMargin - 120, doc.height + doc.topMargin - 20, header_text)
    header_text_c = f"{subtitulo}"
    canvas.setFont('Helvetica', 12)
    canvas.drawString(doc.width + doc.leftMargin - 440, doc.height + doc.topMargin - 20, header_text_c)
    

    # Linha do cabeçalho
    canvas.line(doc.leftMargin, doc.height + doc.topMargin - max_height - 5, doc.width + doc.leftMargin, doc.height + doc.topMargin - max_height - 5)
  
    # Rodapé
    footer_text_right = "Página %d" % doc.page
    canvas.setFont('Helvetica', 10)
    canvas.drawString(doc.width + doc.leftMargin - 50, 0.25 * inch, footer_text_right)

    footer_text_left = "Data = Data do Faturamento | Pago = Data do Pagamento | Realizado = Data do Procedimento"
    canvas.setFont('Helvetica', 10)
    canvas.drawString(doc.leftMargin, 0.25 * inch, footer_text_left)

    # Linha do rodapé
    canvas.line(doc.leftMargin, 0.5 * inch, doc.width + doc.leftMargin, 0.5 * inch)
    
    canvas.restoreState()

def generate_pdf_table(output_file_path, nome_medico, subtitulo, data_pagos=[], data_nao_pagos=[]):
    # Definindo as cores para as tabelas pagos e não pagos
    cor_cabecalho_pagos = colors.HexColor("#52c569")
    cor_linhas_impar_pagos = colors.HexColor("#86d549")
    cor_linhas_par_pagos = colors.HexColor("#c2df23")
    
    cor_cabecalho_nao_pagos = colors.HexColor("#d5546e")
    cor_linhas_impar_nao_pagos = colors.HexColor("#e76f5a")
    cor_linhas_par_nao_pagos = colors.HexColor("#f68d45")

    doc = SimpleDocTemplate(output_file_path, pagesize=landscape(letter), leftMargin=0.5*inch, rightMargin=0.5*inch, topMargin=1.5*inch, bottomMargin=1*inch)
    styles = getSampleStyleSheet()

    # Estilo e título principal do documento
    title_style = styles['Title']
    title_style.alignment = TA_CENTER
    titulo = Paragraph(nome_medico, title_style)
    elements = [titulo]

    subtitulo_style = styles['Title']  # Ou escolha outro estilo conforme necessário
    subtitulo_style.alignment = TA_CENTER
    subtitulo_para = Paragraph(subtitulo, subtitulo_style)
    elements.append(Spacer(1, 12))  # Ajuste o espaço conforme necessário
    elements.append(subtitulo_para)
    
    header_style = styles['Heading1']
    header_style.alignment = TA_CENTER
    
    # Função interna para criar e estilizar tabelas
    def create_styled_table(title, data, cor_cabecalho, cor_linhas_impar, cor_linhas_par):
        heading_style = styles['Heading2']
        heading_style.alignment = TA_CENTER
        elements.append(Paragraph(title, heading_style))  # Adiciona o título da tabela centralizado
        table = Table(data, repeatRows = 1)
        table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), cor_cabecalho),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ])
        
        for i in range(1, len(data)):
            bgcolor = cor_linhas_impar if i % 2 != 0 else cor_linhas_par
            table_style.add('BACKGROUND', (0, i), (-1, i), bgcolor)
        
        table.setStyle(table_style)
        elements.append(table)

    # Adicionando cabeçalho e tabelas para pagos
    if data_pagos:
        elements.append(Paragraph("Valores Pagos", styles['Heading1']))
        for title, data in data_pagos:
            create_styled_table(title, data, cor_cabecalho_pagos, cor_linhas_impar_pagos, cor_linhas_par_pagos)
    # Insere um PageBreak apenas se ambos os conjuntos de dados não estiverem vazios
    if data_pagos and data_nao_pagos:
            elements.append(PageBreak())
    # Adicionando cabeçalho e tabelas para não pagos
    if data_nao_pagos:
        elements.append(Paragraph("Valores Faturados", styles['Heading1']))
        for title, data in data_nao_pagos:
            create_styled_table(title, data, cor_cabecalho_nao_pagos, cor_linhas_impar_nao_pagos, cor_linhas_par_nao_pagos)

    doc.build(elements, onFirstPage=on_page, onLaterPages=on_page)



def mostrar_mensagem():
    root = Tk()
    root.withdraw()  # Esconde a janela principal do tkinter
    root.attributes('-topmost', True)
    messagebox.showinfo("Processamento Concluído", f"Tabelas processadas salvas em: {output_directory}")
    root.destroy()


path_to_file_pagos = "C:/Users/ACER/Meu Drive/Hospital Nossa Senhora das Mercês/Códigos Python/Códigos Funcionando/Arquivos TXT SPData/Gustavo Amorim Ferreira/Gustavo amorim ferreira - Pagos.TXT" 
path_to_file_nao_pagos = "C:/Users/ACER/Meu Drive/Hospital Nossa Senhora das Mercês/Códigos Python/Códigos Funcionando/Arquivos TXT SPData/Gustavo Amorim Ferreira/Gustavo amorim ferreira - nao Pagos.TXT"
output_directory = "C:/Users/ACER/Meu Drive/Hospital Nossa Senhora das Mercês/Códigos Python/Códigos Funcionando/Relatórios Médicos/Gustavo Amorim Ferreira"
subtitulo = 'Dez/23 a Jun/24'
#FORMATAÇÃO DO DATAFRAME A PARTIR DO ARQUIVO TXT RETIRADO DIRETAMENTE DO SPDATA
# Ler arquivo e criar lista
lines_list_pagos = read_file_to_list(path_to_file_pagos)
lines_list_nao_pagos = read_file_to_list(path_to_file_nao_pagos)

# Dividir cada linha pela barra vertical '|' e remover espaços vazios das strings resultantes
data_pagos = [line.split('|') for line in lines_list_pagos]
# Remover espaços vazios em cada elemento da lista
data_pagos = [[item.strip() for item in row] for row in data_pagos]

data_nao_pagos = [line.split('|') for line in lines_list_nao_pagos]
# Remover espaços vazios em cada elemento da lista
data_nao_pagos = [[item.strip() for item in row] for row in data_nao_pagos]


# Criar DataFrame
dados_crua_inicial_pagos = pd.DataFrame(data_pagos)
dados_crua_inicial_nao_pagos = pd.DataFrame(data_nao_pagos)


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
    "ECT (EMP. BRAS. DE CORREIOS E TELE":"ECT", "ALBERGUE SANTO ANTONIO":"Albergue S. Antônio", "SIND TRAB IND MET MEC M EL SID":"Sind.Trab. Ind.", "GV CLINICAS MEDICINA DO TRABALHO":"GV",
    }



#Criação das colunas com o nome do médico e com o nome do convênio para os pagos, não pagos e a faturar
medico_atual_pagos = ''
medico_atual_nao_pagos = ''
convenio_atual_pagos = ''
convenio_atual_nao_pagos = ''
dados_processados_pagos = []
dados_processados_nao_pagos = []



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


#Criando os dataframes a parti da tabela gerada pelo código de inclusão de médicos e fazendo o ffill para completar os valores faltantes
dados_processados_pagos = pd.DataFrame(dados_processados_pagos)
dados_processados_pagos_final = dados_processados_pagos.ffill()

dados_processados_nao_pagos = pd.DataFrame(dados_processados_nao_pagos)
dados_processados_nao_pagos_final = dados_processados_nao_pagos.ffill()
dados_processados_nao_pagos_final = dados_processados_nao_pagos_final[["Registro", "Data", "Paciente", "Procedimento", "Realizado", "V. Faturado", "Medico", "Convenio"]]

dados_processados_pagos_df = pd.DataFrame(dados_processados_pagos_final)
dados_processados_nao_pagos_df = pd.DataFrame(dados_processados_nao_pagos_final)


#Ajustando as datas e os formatos de Data
dados_processados_pagos_df['Data'] = pd.to_datetime(dados_processados_pagos_df['Data'], errors='coerce', format='%d/%m/%Y')
dados_processados_pagos_df['Pago'] = pd.to_datetime(dados_processados_pagos_df['Pago'], errors='coerce', format='%d/%m/%Y')
dados_processados_pagos_df['Data'] = pd.to_datetime(dados_processados_pagos_df['Data']).dt.strftime('%d/%m/%Y')
dados_processados_pagos_df['Pago'] = pd.to_datetime(dados_processados_pagos_df['Pago']).dt.strftime('%d/%m/%Y')
dados_processados_nao_pagos_df['Data'] = pd.to_datetime(dados_processados_nao_pagos_df['Data'], errors='coerce', format='%d/%m/%Y')
dados_processados_nao_pagos_df['Data'] = pd.to_datetime(dados_processados_nao_pagos_df['Data']).dt.strftime('%d/%m/%Y')
dados_processados_nao_pagos_df['Realizado'] = pd.to_datetime(dados_processados_nao_pagos_df['Realizado'], errors='coerce', format='%d/%m/%Y')
dados_processados_nao_pagos_df['Realizado'] = pd.to_datetime(dados_processados_nao_pagos_df['Realizado']).dt.strftime('%d/%m/%Y')

#Retirando as linhas que contêm a palavra "Serv. Profissionais"
dados_processados_pagos_df = dados_processados_pagos_df[~dados_processados_pagos_df['Procedimento'].str.contains("Serv. Profissionais", na=False)]
dados_processados_nao_pagos_df = dados_processados_nao_pagos_df[~dados_processados_nao_pagos_df['Procedimento'].str.contains("Serv. Profissionais", na=False)]

#Criação dos dicionários para cada médico
dados_medicos_pagos = {}
dados_medicos_nao_pagos = {}

#Preparação dos dados por médico para os pedidos não pagos
for nome_medico_nao_pagos, grupo in dados_processados_nao_pagos_df.groupby("Medico"):
    # Removendo a coluna "Medico" do DataFrame antes de gerar o PDF
    grupo_sem_medico = grupo.drop('Medico', axis=1)
    # Converter a coluna "Valor" formatada de volta para float
    grupo_sem_medico["V. Faturado"] = grupo_sem_medico["V. Faturado"].apply(valor_para_float)
    # Agrupar por convênio e somar valores
    soma_por_convenio = grupo_sem_medico.groupby('Convenio')["V. Faturado"].sum().reset_index()
    #Gerando a soma total para cada uma das colunas
    total_faturado = grupo_sem_medico['V. Faturado'].sum()
    # Formatar as colunas de valores para o formato de moeda
    soma_por_convenio["V. Faturado"] = soma_por_convenio["V. Faturado"].apply(formatar_valor)
    total_faturado_formatado = formatar_valor(total_faturado)
    # Preparar dados para terceira tabela
    totais_por_paciente = grupo_sem_medico.groupby("Paciente")["V. Faturado"].sum().reset_index()
    totais_por_paciente["V. Faturado"] = totais_por_paciente["V. Faturado"].apply(formatar_valor)
    # Preparar dados para a primeira tabela
    grupo_sem_medico["V. Faturado"] = grupo_sem_medico["V. Faturado"].apply(formatar_valor)
    #Criação dos objetos para incluir na lista a ser enviada para a contrução das tabelas
    dados_nao_pagos_soma_total = [["Total Faturado"], [total_faturado_formatado]]
    dados_pdf_nao_pagos = [grupo_sem_medico.columns.to_list()] + grupo_sem_medico.values.tolist()
    dados_pdf_nao_pagos_soma_conv = [soma_por_convenio.columns.to_list()] + soma_por_convenio.values.tolist()
    dados_pdf_nao_pagos_paciente = [totais_por_paciente.columns.tolist()] + totais_por_paciente.values.tolist()
    #Lista final para a construção das tabelas
    dados_medicos_nao_pagos[nome_medico_nao_pagos] = [dados_nao_pagos_soma_total, dados_pdf_nao_pagos, dados_pdf_nao_pagos_soma_conv, dados_pdf_nao_pagos_paciente]


#Preparação dos dados por médico para os pedidos pagos
for nome_medico_pagos, grupo in dados_processados_pagos_df.groupby("Medico"):
    # Removendo a coluna "Medico" do DataFrame antes de gerar o PDF
    grupo_sem_medico = grupo.drop('Medico', axis=1)
    # Converter a coluna "Valor" formatada de volta para float
    grupo_sem_medico["V. Faturado"] = grupo_sem_medico["V. Faturado"].apply(valor_para_float)
    # Agrupar por convênio e somar valores
    soma_por_convenio = grupo_sem_medico.groupby('Convenio')["V. Faturado"].sum().reset_index()
    #Gerando a soma total para cada uma das colunas
    total_faturado = grupo_sem_medico['V. Faturado'].sum()
    # Removendo a coluna "Medico" do DataFrame antes de gerar o PDF
    grupo_sem_medico = grupo.drop('Medico', axis=1)
    # Converter a coluna "Valor" formatada de volta para float
    grupo_sem_medico["V. Faturado"] = grupo_sem_medico["V. Faturado"].apply(valor_para_float)
    grupo_sem_medico['V. Recebido'] = grupo_sem_medico['V. Recebido'].apply(valor_para_float)
    grupo_sem_medico['Diferenca'] = grupo_sem_medico['Diferenca'].apply(valor_para_float)
    # Agrupar por convênio e somar valores
    soma_por_convenio = grupo_sem_medico.groupby('Convenio').agg({'V. Faturado': 'sum', 'V. Recebido': 'sum', 'Diferenca': 'sum'}).reset_index()
    #Gerando a soma total para cada uma das colunas
    total_faturado = soma_por_convenio['V. Faturado'].sum()
    total_recebido = soma_por_convenio['V. Recebido'].sum()
    total_diferenca = soma_por_convenio['Diferenca'].sum()
    # Formatar as colunas de valores para o formato de moeda
    soma_por_convenio["V. Faturado"] = soma_por_convenio["V. Faturado"].apply(formatar_valor)
    soma_por_convenio['V. Recebido'] = soma_por_convenio['V. Recebido'].apply(formatar_valor)
    soma_por_convenio['Diferenca'] = soma_por_convenio['Diferenca'].apply(formatar_valor)
    total_faturado_formatado = formatar_valor(total_faturado)
    total_recebido_formatado = formatar_valor(total_recebido)
    total_diferenca_formatado = formatar_valor(total_diferenca)
    dados_pagos_soma_total = [["Total Faturado", "Total Recebido", "Total Diferença"], [total_faturado_formatado, total_recebido_formatado, total_diferenca_formatado]]
    #Totais por paciente
    totais_por_paciente = grupo_sem_medico.groupby("Paciente")[["V. Faturado","V. Recebido", "Diferenca"]].sum().reset_index()
    totais_por_paciente["V. Faturado"] = totais_por_paciente["V. Faturado"].apply(formatar_valor)
    totais_por_paciente["V. Recebido"] = totais_por_paciente["V. Recebido"].apply(formatar_valor)
    totais_por_paciente["Diferenca"] = totais_por_paciente["Diferenca"].apply(formatar_valor)
    grupo_sem_medico["V. Faturado"] = grupo_sem_medico["V. Faturado"].apply(formatar_valor)
    grupo_sem_medico['V. Recebido'] = grupo_sem_medico['V. Recebido'].apply(formatar_valor)
    grupo_sem_medico['Diferenca'] = grupo_sem_medico['Diferenca'].apply(formatar_valor)
    #Criação dos objetos para incluir na lista a ser enviada para a contrução das tabelas
    dados_pdf_pagos = [grupo_sem_medico.columns.to_list()] + grupo_sem_medico.values.tolist()
    dados_pdf_pagos_soma_conv = [soma_por_convenio.columns.to_list()] + soma_por_convenio.values.tolist()
    dados_pdf_pagos_por_paciente = [totais_por_paciente.columns.tolist()] + totais_por_paciente.values.tolist()
    #Lista final para a construção das tabelas
    dados_medicos_pagos[nome_medico_pagos] = [dados_pagos_soma_total, dados_pdf_pagos, dados_pdf_pagos_soma_conv, dados_pdf_pagos_por_paciente]


todos_medicos = set(dados_medicos_pagos.keys()) | set(dados_medicos_nao_pagos.keys())

#Ajusdtando as datas e os formatos de Data para a geração dos gráficos
dados_processados_pagos_df['Pago'] = pd.to_datetime(dados_processados_pagos_df['Pago'], errors='coerce', format='%d/%m/%Y')
dados_processados_nao_pagos_df['Data'] = pd.to_datetime(dados_processados_nao_pagos_df['Data'], errors='coerce', format='%d/%m/%Y')
dados_processados_pagos_df['Mês'] = dados_processados_pagos_df['Pago'].dt.to_period('M')
dados_processados_nao_pagos_df['Mês'] = dados_processados_nao_pagos_df['Data'].dt.to_period('M')
for nome_medico in todos_medicos:
    nome_arquivo = ''.join(e for e in nome_medico if e.isalnum() or e in [' ', '_', '-']).strip()
    caminho_completo = os.path.join(output_directory, f"{nome_arquivo}_relatorio.pdf")
    titulo_texto = f"Relatório de Honorários Médicos: {nome_medico}"

    # Inicializa listas vazias para tabelas pagas, não pagas e a faturar
    tabelas_pagos = []
    tabelas_nao_pagos = []

    # Verifica se o médico está presente nos dados pagos e adiciona as tabelas correspondentes
    if nome_medico in dados_medicos_pagos:
        for titulo, dados in [("Valores por procedimento", dados_medicos_pagos[nome_medico][1]),
                              ("Totais por Convênio", dados_medicos_pagos[nome_medico][2]),
                              ("Totais por Paciente", dados_medicos_pagos[nome_medico][3]),
                              ("Soma Total", dados_medicos_pagos[nome_medico][0])]:
            tabelas_pagos.append((titulo, dados))

    # Verifica se o médico está presente nos dados não pagos e adiciona as tabelas correspondentes
    if nome_medico in dados_medicos_nao_pagos:
        for titulo, dados in [("Valores por procedimento", dados_medicos_nao_pagos[nome_medico][1]),
                              ("Totais por Convênio", dados_medicos_nao_pagos[nome_medico][2]),
                              ("Totais por Paciente", dados_medicos_nao_pagos[nome_medico][3]),
                              ("Soma Total", dados_medicos_nao_pagos[nome_medico][0])]:
            tabelas_nao_pagos.append((titulo, dados))


    # Chama a função de geração de PDF apenas se houver tabelas para incluir
    if tabelas_pagos or tabelas_nao_pagos :
        generate_pdf_table(caminho_completo, titulo_texto, subtitulo, tabelas_pagos, tabelas_nao_pagos)

mostrar_mensagem()