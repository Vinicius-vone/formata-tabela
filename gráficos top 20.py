import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def valor_para_float(valor_formatado):
    if isinstance(valor_formatado, str) and (',' in valor_formatado or '.' in valor_formatado):
        # Substitui ponto por nada e vírgula por ponto
        valor_formatado = valor_formatado.replace('.', '').replace(',', '.')
    # Tenta converter para float, se não for uma string retorna o valor como está
    return float(valor_formatado) if isinstance(valor_formatado, str) else valor_formatado


# Supondo que você já carregou o DataFrame em 'df'
df_pagos = pd.read_parquet("C:/Users/ACER/Meu Drive/Hospital Nossa Senhora das Mercês/Códigos Python/Códigos Funcionando/Dataframes/01-10-22_30-04-24/pagos_01-10-22_30-04-24.parquet")

# Calcular o custo médio por procedimento
df_pagos["V. Faturado"] = df_pagos["V. Faturado"].apply(valor_para_float)

custo_medio_procedimento = df_pagos.groupby('Procedimento')['V. Faturado'].mean().sort_values(ascending=False)

# Selecionar os top 20 procedimentos mais bem pagos
top20_procedimentos = custo_medio_procedimento.head(20)

# Visualizar o custo médio dos top 20 procedimentos
plt.figure(figsize=(12, 8))
top20_procedimentos.plot(kind='bar', color='skyblue')
plt.title('Top 20 Custo Médio por Procedimento')
plt.xlabel('Tipo de Procedimento')
plt.ylabel('Custo Médio')
plt.xticks(rotation=90)
plt.grid(True)
plt.tight_layout()
plt.show()

# Visualizar a distribuição de custos para os top 20 procedimentos usando um boxplot
top20_df = df_pagos[df_pagos['Procedimento'].isin(top20_procedimentos.index)]

plt.figure(figsize=(12, 8))
sns.boxplot(x='Procedimento', y='V. Faturado', data=top20_df)
plt.title('Distribuição de Custos para os Top 20 Procedimentos')
plt.xlabel('Tipo de Procedimento')
plt.ylabel('Valor Pago')
plt.xticks(rotation=90)
plt.grid(True)
plt.tight_layout()
plt.show()