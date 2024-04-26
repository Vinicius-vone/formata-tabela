import pandas as pd
import re


# Caminho para o arquivo de texto
file_path = 'C:/Users/ACER/Meu Drive/Hospital Nossa Senhora das Mercês/Códigos Python/Códigos Funcionando/Arquivos TXT SPData/SUS - AIH - 10-10-2023_10-04-2024.TXT'
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
                data.append([aih, paciente, procedimento, internacao, alta, ato, quantidade, pontos, valor, valor_repassado, current_doctor])

# Criar DataFrame
df = pd.DataFrame(data, columns=['AIH', 'Paciente', 'Procedimento', 'Internação', 'Alta', 'Ato', 'Quantidade', 'Pontos', 'Valor', 'Valor Repassado', 'Médico'])

# Exibir as primeiras linhas do DataFrame
print(df.head(20))