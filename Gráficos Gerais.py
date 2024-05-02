import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np

# Carregar os DataFrames
df_pagos = pd.read_parquet("C:/Users/ACER/Meu Drive/Hospital Nossa Senhora das Mercês/Códigos Python/Códigos Funcionando/Dataframes/01-10-22_30-04-24/pagos_01-10-22_30-04-24.parquet")
df_nao_pagos = pd.read_parquet("C:/Users/ACER/Meu Drive/Hospital Nossa Senhora das Mercês/Códigos Python/Códigos Funcionando/Dataframes/01-10-22_30-04-24/nao_pagos_01-10-22_30-04-24.parquet")

# Converter datas e criar colunas 'Mês'
df_pagos['Mês'] = pd.to_datetime(df_pagos['Pago'], format='%d/%m/%Y').dt.to_period('M').dt.start_time
df_nao_pagos['Mês'] = pd.to_datetime(df_nao_pagos['Data'], format='%d/%m/%Y').dt.to_period('M').dt.start_time

output_directory_teste = "C:/Users/ACER/Meu Drive/Hospital Nossa Senhora das Mercês/Códigos Python/Códigos Funcionando/Gráficos Médicos/teste"

medicos_cooperados = pd.read_excel("C:/Users/ACER/Meu Drive/Hospital Nossa Senhora das Mercês/Códigos Python/Códigos Funcionando/listagem_medicos_cooperados.xlsx")
medicos_cooperados.drop(columns=["CRM"], inplace=True)
lista_medicos_cooperados = medicos_cooperados['Nome'].to_list()

df_nao_pagos = df_nao_pagos[~((df_nao_pagos['Medico'].isin(lista_medicos_cooperados)) & (df_nao_pagos['Convenio'] == 'Unimed'))]

def plot_procedimentos(df_pagos, df_nao_pagos, output_directory):
    # Total de pagos e não pagos por mês
    pagos_por_mes = df_pagos.groupby('Mês').size()
    nao_pagos_por_mes = df_nao_pagos.groupby('Mês').size()

    plt.figure(figsize=(14, 7))
    pagos_por_mes.plot(label='Pagos', marker='o', linestyle='-', color='blue')
    nao_pagos_por_mes.plot(label='Não Pagos', marker='x', linestyle='--', color='red')
    plt.title('Total de Procedimentos Pagos e Não Pagos por Mês')
    plt.xlabel('Mês')
    plt.ylabel('Quantidade de Procedimentos')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f"{output_directory}/total_pagos_nao_pagos_por_mes.png")
    plt.close()

    # Aplicar Viridis para gráficos por convênio
    cmap = plt.get_cmap('viridis')
    
    for status, df in [('Pagos', df_pagos), ('Não Pagos', df_nao_pagos)]:
        convenios_por_mes = df.groupby(['Mês', 'Convenio']).size().unstack(fill_value=0)
        n_convenios = len(convenios_por_mes.columns)
        nrows = (n_convenios + 2) // 3  # Assegura que haja linhas suficientes para todos os convênios
        fig, axs = plt.subplots(nrows=nrows, ncols=3, figsize=(18, 3 * nrows), sharex=True, squeeze=False)

        axs = axs.flatten()  # Achata o array de axes para facilitar a iteração
        for i, convenio in enumerate(convenios_por_mes.columns):
            ax = axs[i]
            ax.plot(convenios_por_mes.index, convenios_por_mes[convenio], label=f'{convenio}', marker='o', linestyle='-', color=cmap(i / n_convenios))
            ax.set_title(f'Procedimentos {status} para Convênio: {convenio}')
            ax.set_xlabel('Mês')
            ax.set_ylabel('Quantidade de Procedimentos')
            ax.legend()
            ax.grid(True)
            # Definir o formato de data para o eixo x
            ax.xaxis.set_major_locator(mdates.MonthLocator())
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m\n%y'))  # Formato: "Abreviação do Mês Ano"
        
        # Oculta os axes extras se houver
        for ax in axs[n_convenios:]:
            ax.set_visible(False)

        plt.tight_layout()
        plt.savefig(f"{output_directory}/detalhado_{status.lower()}_por_convenio_por_mes.png")
        plt.close(fig)


plot_procedimentos(df_pagos, df_nao_pagos, output_directory_teste)