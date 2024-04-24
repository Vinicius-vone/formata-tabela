from PyPDF2 import PdfReader, PdfWriter
import os
from tkinter import Tk, filedialog, simpledialog, messagebox
import glob

def selecionar_arquivo_e_diretorio():
    root = Tk()
    root.withdraw()  # Não mostrar a janela completa do Tk
    root.attributes('-topmost', True)
    output_directory = filedialog.askdirectory(title="Selecione o diretório onde salvar o arquivo processado")
    root.destroy()
    return output_directory
# Caminhos dos diretórios
diretorio_final = selecionar_arquivo_e_diretorio()
diretorio1 = "C:/Users/ACER/Meu Drive/Hospital Nossa Senhora das Mercês/Códigos Python/Códigos Funcionando/Tabelas Médicos"
diretorio2 = "C:/Users/ACER/Meu Drive/Hospital Nossa Senhora das Mercês/Códigos Python/Códigos Funcionando/Gráficos Médicos"
diretorio3 = "C:/Users/ACER/Meu Drive/Hospital Nossa Senhora das Mercês/Códigos Python/Códigos Funcionando/Tabelas Endoscopia"

# Listar os arquivos nos diretórios
arquivos1 = set(os.listdir(diretorio1))
arquivos2 = set(os.listdir(diretorio2))
arquivos3 = set(os.listdir(diretorio3))


# Encontrar arquivos comuns nos dois diretórios
arquivos_comuns = arquivos1.intersection(arquivos2).intersection(arquivos3)

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
            
    with open(os.path.join(diretorio3, nome_arquivo), 'rb') as f:
        reader = PdfReader(f)
        for pagina in reader.pages:
            writer.add_page(pagina)

    # Salvar o PDF combinado
    with open(os.path.join(diretorio_final, nome_arquivo), 'wb') as f:
        writer.write(f)


def delete_pdf_files(diretorio_tabelas, diretorio_graficos, diretorio_endoscopia):
    # Cria o caminho completo para buscar arquivos .png
    search_path_tabelas = os.path.join(diretorio_tabelas, '*.pdf')
    search_path_graficos = os.path.join(diretorio_graficos, '*.pdf')
    search_path_endoscopia = os.path.join(diretorio_endoscopia, '*.pdf')
    # Usa glob para encontrar todos os arquivos .png no diretório especificado
    pdf_files = glob.glob(search_path_tabelas) + glob.glob(search_path_graficos) + glob.glob(search_path_endoscopia)
    # Itera sobre a lista de arquivos .png encontrados e os remove
    for file_path in pdf_files:
        try:
            os.remove(file_path)
            print(f"Arquivo {file_path} deletado com sucesso.")
        except Exception as e:
            print(f"Erro ao deletar o arquivo {file_path}: {e}")

def mostrar_mensagem():
    root = Tk()
    root.withdraw()  # Esconde a janela principal do tkinter
    root.attributes('-topmost', True)
    messagebox.showinfo("Processamento Concluído", f"Arquivos combinados salvos em: {diretorio_final}")
    root.destroy()

# Combinar todos os PDFs de mesmo nome
for arquivo in arquivos_comuns:
    if arquivo.endswith('.pdf'):  # Verificar se é um arquivo PDF
        combinar_pdfs(arquivo)
        print(f"Combinado: {arquivo}")

delete_pdf_files(diretorio1, diretorio2, diretorio3)
mostrar_mensagem()