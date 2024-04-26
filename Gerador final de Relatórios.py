import subprocess

def run_script(script_name):
    """ Função para executar um script Python """
    try:
        # subprocess.run espera o comando como uma lista onde o primeiro elemento é o executável (python) e o segundo o script
        subprocess.run(["python", script_name], check=True)
        print(f"{script_name} executado com sucesso!")
    except subprocess.CalledProcessError:
        print(f"Falha ao executar {script_name}")

def main():
    # Lista dos scripts para executar em ordem
    scripts = ["Formatação de tabelas para PDF - Modelo IV por médico -Completa.py", "gerador de gráficos.py", "Geração tabelas Endoscopia.py", "Unificador de PDFs.py"]
    
    # Executar cada script na lista
    for script in scripts:
        run_script(script)

if __name__ == "__main__":
    main()