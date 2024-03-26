import pandas as pd
import numpy as np
from tkinter import Tk, filedialog, simpledialog, messagebox
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_RIGHT  # Importação necessária para centralizar o texto
import os

# Função para formatar valores em formato de moeda

def formatar_valor(valor):
    return "R${:,.2f}".format(valor).replace(",", "X").replace(".", ",").replace("X", ".")

# Função para converter valor formatado de volta para float
def valor_para_float(valor_formatado):
    return float(valor_formatado)

def converter_valor_monetario_para_float(valor_monetario):
    # Remove o símbolo de moeda e substitui a vírgula por ponto
    valor_formatado = valor_monetario.replace('R$', '').replace(',', '.').replace('.', '')
    # Converte para float
    return float(valor_formatado)

# Definição das cores para a tabela
cor_cabecalho = colors.HexColor("#CF2D2D")
cor_linhas_impar = colors.HexColor("#CF9595")
cor_linhas_par = colors.HexColor("#F5D5D9")

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
    header_text = f"Relatório de Valores Faturados Não Pagos"
    canvas.setFont('Helvetica', 12)
    canvas.drawString(doc.width + doc.leftMargin - 150, doc.height + doc.topMargin - 20, header_text)

    # Linha do cabeçalho
    canvas.line(doc.leftMargin, doc.height + doc.topMargin - max_height - 5, doc.width + doc.leftMargin, doc.height + doc.topMargin - max_height - 5)

    # Rodapé
    footer_text_right = "Página %d" % doc.page
    canvas.setFont('Helvetica', 10)
    canvas.drawString(doc.width + doc.leftMargin - 50, 0.25 * inch, footer_text_right)

    footer_text_left = "Data = Data do Faturamento"
    canvas.setFont('Helvetica', 10)
    canvas.drawString(doc.leftMargin, 0.25 * inch, footer_text_left)

    # Linha do rodapé
    canvas.line(doc.leftMargin, 0.5 * inch, doc.width + doc.leftMargin, 0.5 * inch)
    
    canvas.restoreState()

def generate_pdf_table(data, output_file_path, titulo_texto, additional_tables=[]):
    # Ajusta as margens do documento
    doc = SimpleDocTemplate(output_file_path, pagesize=landscape(letter), leftMargin=0.5*inch, rightMargin=0.5*inch, topMargin=1.5*inch, bottomMargin=1*inch)
    
    # Estilos para o título
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    title_style.alignment = TA_CENTER  # Define o alinhamento como centralizado
    
    titulo = Paragraph(titulo_texto, title_style)

    elements = [titulo]

    # Função interna para criar e estilizar tabelas
    def create_styled_table(data):
        table = Table(data)
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
    
        # Aplicar cores alternadas manualmente linha por linha
        for i in range(1, len(data)):  # Começando da linha 1 porque a linha 0 é o cabeçalho
            bgcolor = cor_linhas_impar if i % 2 != 0 else cor_linhas_par
            table_style.add('BACKGROUND', (0, i), (-1, i), bgcolor)
    
        table.setStyle(table_style)
        return table

    # Adiciona a primeira tabela principal
    main_table = create_styled_table(data)
    elements.append(main_table)

    # Adiciona tabelas adicionais, se houver
    for additional_table in additional_tables:
        table_title, table_data = additional_table
        heading_style = styles['Heading2']
        heading_style.alignment = TA_CENTER  # Centraliza o título da tabela adicional
        
        elements.append(Paragraph(table_title, heading_style))  # Aplicando o estilo centralizado ao título
        additional_table = create_styled_table(table_data)
        elements.append(additional_table)

    doc.build(elements, onFirstPage=on_page, onLaterPages=on_page)

def selecionar_arquivo_e_diretorio():
    root = Tk()
    root.withdraw()  # Não mostrar a janela completa do Tk
    root.attributes('-topmost', True)
    path_to_file = filedialog.askopenfilename(title="Selecione o arquivo Excel", filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")])
    output_directory = filedialog.askdirectory(title="Selecione o diretório onde salvar o arquivo processado")
    root.destroy()
    return path_to_file, output_directory

def mostrar_mensagem():
    root = Tk()
    root.withdraw()  # Esconde a janela principal do tkinter
    root.attributes('-topmost', True)
    messagebox.showinfo("Processamento Concluído", f"Arquivo processado salvo em: {output_directory}")
    root.destroy()

path_to_file, output_directory = selecionar_arquivo_e_diretorio()
dados_crua_inicial = pd.read_excel(path_to_file)

dicionario_convenios = {
    'BANCO DO BRASIL':"Banco do Brasil", 'POLICIA MILITAR':"Polícia Militar", 'CEMIG SAUDE':"CEMIG", 'FUSEX':"FUSEX",
    'ASSEFAZ':"ASSEFAZ", 'CAIXA ECONOMICA FEDERAL':"Caixa Econômica", 'ECT (EMP. BRAS. DE CORREIOS E TELEG.)':"ECT", 'SUL AMERICA AETNA SEGUROS E PREVIDENCIA':"Sul América", 
    'SUL AMERICA AETNA SEGUROS E PREVIDENCIA':"SASC", 
    'SAUDE BRADESCO EMPRESARIAL':"Bradesco Emp", 'CONSORCIO INTERMUNICIPAL DE SAUDE DAS VERTENTES':"Cisver", 'PLAMEDH':"Plamedh", 
    'FUNDACAO LIBERTAS (PREVIMINAS)':"Previminas", 'BRASIL ASSISTENCIA S/A':"Brasil Assistencia",
    'USISAUDE (FUNDAÇAO SAO FRANCISCO XAVIER)':"Usisaude", 'PATRONAL':"GEAP", 'AECO':"AECO", "UNIMED":"Unimed", 'CASU':"CASU", 
    'FUNDAFFEMG':"FUNDAFFEMG", 
    'SAUDE BRADESCO INDIVIDUAL':"Bradesco Ind", 'A.M.M.P.':"AMMP", "PREMIUM SAUDE":"Premium Saude","SUL AMERICA AETNA SEGUROS E PR":"Sul América",
    'CONSORCIO INTERMUNICIPAL DE SA':"Cisver"
    }

# Inicializações

dados_crua_inicial = dados_crua_inicial[dados_crua_inicial["Pago"].isna()][["Registro", "Procedimento", "Paciente", "V. Faturado", "Data"]]
dados_crua = dados_crua_inicial.ffill()



medico_atual = ''
convenio_atual = ''
dados_processados = []


for index, linha in dados_crua.iterrows():
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

dados_filtrados = pd.DataFrame(dados_processados)


# Ajustando as colunas de data para o formato correto
dados_filtrados['Data'] = pd.to_datetime(dados_filtrados['Data'], errors='coerce')
dados_filtrados['Data'] = pd.to_datetime(dados_filtrados['Data']).dt.strftime('%d/%m/%Y')
dados_filtrados = dados_filtrados[~dados_filtrados['Procedimento'].str.contains("Serv. Profissionais", na=False)]

# Gerar PDFs separados por médico
for nome_medico, grupo in dados_filtrados.groupby('Medico'):
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
     dados_soma_total = [["Total Faturado"], [total_faturado_formatado]]

     # Preparar dados para terceira tabela
     totais_por_paciente = grupo_sem_medico.groupby("Paciente")["V. Faturado"].sum().reset_index()
     totais_por_paciente["V. Faturado"] = totais_por_paciente["V. Faturado"].apply(formatar_valor)
     
     # Preparar dados para a primeira tabela
     grupo_sem_medico["V. Faturado"] = grupo_sem_medico["V. Faturado"].apply(formatar_valor)
     dados_pdf = [grupo_sem_medico.columns.to_list()] + grupo_sem_medico.values.tolist()

     #Preparar dados do total

     dados_pdf_soma_conv = [soma_por_convenio.columns.to_list()] + soma_por_convenio.values.tolist()
     dados_pdf_serv_profissionais = [totais_por_paciente.columns.tolist()] + totais_por_paciente.values.tolist()
     nome_arquivo = ''.join(e for e in nome_medico if e.isalnum() or e in [' ', '_', '-']).strip()
     caminho_completo = os.path.join(output_directory, f"{nome_arquivo}_faturados_não_pagos_relatorio.pdf")
     titulo_texto = f"Valores Faturados Não Pagos: {nome_medico}"     # Chamar a função modificada para gerar o PDF incluindo a segunda tabela
     generate_pdf_table(dados_pdf, caminho_completo, titulo_texto, [("Totais por Convênio", dados_pdf_soma_conv), ("Totais por Paciente", dados_pdf_serv_profissionais), ("Soma Total", dados_soma_total)])


#mostrar_mensagem()