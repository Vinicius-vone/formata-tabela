import pdfplumber
import pandas as pd

caminho_pdf = "C:/Users/TI2/Downloads/247317470001-sadt (8).pdf"

tabelas = []

with pdfplumber.open(caminho_pdf) as pdf:
    for page in pdf.pages:
        table = page.extract_table()
        if table:
            # A primeira linha vira cabeçalho
            df = pd.DataFrame(table[1:], columns=table[0])
            tabelas.append(df)

# Junta tudo
df_final = pd.concat(tabelas, ignore_index=True)

# Salva em Excel
df_final.to_excel("C:/Users/TI2/Downloads/247317470001-sadt (8).xlsx", index=False)