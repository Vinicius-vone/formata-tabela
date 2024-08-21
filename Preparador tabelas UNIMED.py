import pandas as pd
from tkinter import Tk, filedialog, messagebox
import os

def caminho_do_arquivo():
    root = Tk()
    root.withdraw()  # Não mostrar a janela completa do Tk
    root.attributes('-topmost', True)
    path_to_file = filedialog.askopenfilename(title="Selecione o arquivo xlsx de materiais", filetypes=[("All files", "*.*"), ("All files", "*.*")])
    output_directory = filedialog.askdirectory(title="Selecione a pasta de saída para os arquivos xlsx processados")
    root.destroy()
    return path_to_file, output_directory

def mostrar_mensagem():
    root = Tk()
    root.withdraw()  # Esconde a janela principal do tkinter
    root.attributes('-topmost', True)
    messagebox.showinfo("Processamento Concluído", f"Tabelas processadas salvas em: {pasta_saida}")
    root.destroy()

df_caminho, pasta_saida = caminho_do_arquivo()

# Extrair o nome do arquivo com a extensão
nome_arquivo_com_extensao = os.path.basename(df_caminho)

# Extrair o nome do arquivo sem a extensão
nome_arquivo, extensao = os.path.splitext(nome_arquivo_com_extensao)

df = pd.read_excel(df_caminho, dtype=object)

df = df[['TISS Código do Material', 'Descrição do Produto', 'Unid Mín Fração', 'Valor']]
df = df.rename(columns={'TISS Código do Material': '1-TISS Código do Material', 'Descrição do Produto': '2-Descrição do Produto', 'Unid Mín Fração': '3-Unid Mín Fração', 'Valor': '4-Valor'})

df.to_excel(f'{pasta_saida}/{nome_arquivo}_exported.xlsx', index=False)
mostrar_mensagem()