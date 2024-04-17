from PyPDF2 import PdfReader, PdfWriter
import os
from tkinter import Tk, filedialog, simpledialog, messagebox

def selecionar_arquivo_e_diretorio():
    root = Tk()
    root.withdraw()  # Não mostrar a janela completa do Tk
    root.attributes('-topmost', True)
    path_to_file_tabelas = filedialog.askdirectory(title="Selecione o arquivo de tabelas")
    path_to_file_graficos = filedialog.askdirectory(title="Selecione o arquivo de gráficos")
    output_directory = filedialog.askdirectory(title="Selecione o diretório onde salvar o arquivo processado")
    root.destroy()
    return path_to_file_tabelas, path_to_file_graficos, output_directory
# Caminhos dos diretórios
diretorio1, diretorio2, diretorio_final = selecionar_arquivo_e_diretorio()
 

# Listar os arquivos nos diretórios
arquivos1 = set(os.listdir(diretorio1))
arquivos2 = set(os.listdir(diretorio2))

# Encontrar arquivos comuns nos dois diretórios
arquivos_comuns = arquivos1.intersection(arquivos2)

# Função para combinar PDFs
def combinar_pdfs(nome_arquivo):
    writer = PdfWriter()

    # Adicionar páginas do primeiro diretório
    with open(os.path.join(diretorio1, nome_arquivo), 'rb') as f:
        reader = PdfReader(f)
        for pagina in reader.pages:
            writer.add_page(pagina)

    # Adicionar páginas do segundo diretório
    with open(os.path.join(diretorio2, nome_arquivo), 'rb') as f:
        reader = PdfReader(f)
        for pagina in reader.pages:
            writer.add_page(pagina)

    # Salvar o PDF combinado
    with open(os.path.join(diretorio_final, nome_arquivo), 'wb') as f:
        writer.write(f)

# Combinar todos os PDFs de mesmo nome
for arquivo in arquivos_comuns:
    if arquivo.endswith('.pdf'):  # Verificar se é um arquivo PDF
        combinar_pdfs(arquivo)
        print(f"Combinado: {arquivo}")

print("Todos os PDFs combinados com sucesso!")