library(readxl)
library(dplyr)
library(stringr)
library(tidyr)
library(writexl)
library(plyr)

# Substitua pelo caminho correto para o seu arquivo
path_to_file <- "C:/Users/ACER/Meu Drive/Hospital Nossa Senhora das Mercês/Dashboard/Projeto Diagnóstico de Faturamento/Honorários médicos - Analítica - Modelo X - Pagos- Completa.xlsx"


# Carregar os dados
dados_crua <- read_excel(path_to_file)

# Preparar um dataframe para os dados processados
dados_processados <- data.frame(
  Data = as.Date(character()),
  Nome_do_Paciente = character(),
  Valor = as.character(character()),
  Convenio = character(),
  CodConvenio = as.integer(character()),
  Medico = character(),
  stringsAsFactors = FALSE
)

medico_atual <- NA
convenio_atual <- NA
cod_convenio_atual <- NA

# Processar as linhas
for (i in 1:nrow(dados_crua)) {
  linha <- dados_crua[i, ]
  # Ajuste 'Coluna1' para a coluna real onde os dados estão localizados
  if (!is.na(linha$Ato)) {
  if (str_detect(linha$Ato, "Nome do Medico:")) {
    medico_atual <- str_extract(linha$Ato, "(?<=Nome do Medico: ).*(?= CRM:)")
  } else if (str_detect(linha$Ato, "Convenio:")) {
    convenio_info <- str_match(linha$Ato, "Convenio: (\\d+) - (.+)")
    cod_convenio_atual <- convenio_info[2]
    convenio_atual <- str_trim(convenio_info[3])
  } else if (!is.na(as.Date(linha$Data)) && !is.na(as.character(linha$Valor))) {
    # Supondo que 'ColunaData' e 'ColunaValor' são os nomes das colunas com essas informações
    nova_linha <- tibble(
      Data = as.Date(linha$Data),
      Nome_do_Paciente = linha$`Nome do Paciente`, # ajuste para a coluna real
      Valor = as.character(linha$Valor),
      Convenio = convenio_atual,
      CodConvenio = as.integer(cod_convenio_atual),
      Medico = medico_atual
    )
    dados_processados <- bind_rows(dados_processados, nova_linha)
  }
}
}
# Remover linhas vazias, se houver
dados_processados <- dados_processados %>% filter(!is.na(Data))

#transformando os valores em números decimais (para entrar corretamente no excel se preciso)
dados_processados <- transform(dados_processados, Valor = as.double(Valor))
#checagem dos tipos de dados do dataframe
sapply(dados_processados, mode)
sapply(dados_processados, class)

#MODIFICAR O NOME DOS CONVÊNIOS
#Criando uma lista com os nomes dos convênios maiúsculos e errados
ConveniosMaiusculo <- as.character(unique(dados_processados$Convenio))

#Criando uma lista com os nomes dos convênios corretos
ConveniosCorreto <- c("Banco do Brasil", "Polícia Militar", "CEMIG", "FUSEX",
                      "ASSEFAZ", "Caixa Econômica", "ECT", "Sul América", "SASC", 
                      "Bradesco Emp", "Cisver", "Plamedh", "Previminas", "Brasil Assistencia",
                      "Usisaude", "GEAP", "AECO", "Unimed", "CASU", "FUNDAFFEMG", 
                      "Bradesco Ind", "AMMP", "Premium Saude")
#Criando um dicionário onde NomerErrado é a chave para o NomeCerto
dicionarioconvenios <- setNames(ConveniosCorreto, ConveniosMaiusculo)
#Exemplo


#Código para criar mudar o nome no dataset

Dados_final <- dados_processados


Dados_final$Convenio <- mapvalues(Dados_final$Convenio, from = names(dicionarioconvenios), to = dicionarioconvenios)


#Criar um arquivo .xlsx com o dataframe processado
write_xlsx(Dados_final, "Dados_finais_Valores_pagos.xlsx")
