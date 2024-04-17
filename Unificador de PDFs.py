from PyPDF2 import PdfReader, PdfWriter
import os
from tkinter import Tk, filedialog, simpledialog, messagebox
import glob

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


def delete_pdf_files(diretorio_tabelas, diretorio_graficos):
    # Cria o caminho completo para buscar arquivos .png
    search_path_tabelas = os.path.join(diretorio_tabelas, '*.pdf')
    search_path_graficos = os.path.join(diretorio_graficos, '*.pdf')
    # Usa glob para encontrar todos os arquivos .png no diretório especificado
    png_files = glob.glob(search_path_tabelas) + glob.glob(search_path_graficos)
    
    # Itera sobre a lista de arquivos .png encontrados e os remove
    for file_path in png_files:
        try:
            os.remove(file_path)
            print(f"Arquivo {file_path} deletado com sucesso.")
        except Exception as e:
            print(f"Erro ao deletar o arquivo {file_path}: {e}")

# Combinar todos os PDFs de mesmo nome
for arquivo in arquivos_comuns:
    if arquivo.endswith('.pdf'):  # Verificar se é um arquivo PDF
        combinar_pdfs(arquivo)
        print(f"Combinado: {arquivo}")

delete_pdf_files(diretorio1, diretorio2)
print("Todos os PDFs combinados com sucesso!")