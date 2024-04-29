import pandas as pd
import re


def extract_doctor_name(text):
    clean_text = text.split('CPF/CGC:')[0].strip()
    # Regex pattern to find "CRM/CRO:" followed by space and digits
    pattern = r"CRM/CRO:\s+\d+\s+"
    # Using re.sub to replace the matched pattern with an empty string
    clean_text = re.sub(pattern, '', clean_text)
    return clean_text

# Caminho para o arquivo de texto
file_path = 'C:/Users/ACER/Meu Drive/Hospital Nossa Senhora das Mercês/Códigos Python/Códigos Funcionando/Arquivos TXT SPData/SUS - Ambulatorio - 10-10-2023_10-04-2024.TXT'
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
                    "Repasse": match.group(9),
                    "Médico": current_doctor
                }
                all_data.append(data)

# Criar DataFrame
df = pd.DataFrame(all_data)
# Exibir as primeiras linhas do DataFrame
print(df.head(60))