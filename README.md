Códigos em Python criados para realizar a formatação de tabelas de excel pré filtradas de relatórios do SPData para geração de relatórios em arquivos PDF, onde são gerados um arquivo para cada médico com os valores referentes aos procedimentos realizados, contendo informações sobre data de faturamento do pedido, data de pagamento, valores glosados, valores faturados, valores pagos, convenio e motivo das glosas. Essas informações são separadas em tabelas onde são apresentados todos os procedimentos em todos os pacientes, os valores totais por paciente, valores totais por convenio e valores totais. Para que o código funcione deve ser ralizado o pré processamento dos dados .txt extraidos do programa SPData. O procedimento é:
1.	Salve o relatório retirado do modelo IV da aba de glosas – listagens;
2.	Importe o relatório para o excel por meio da aba Dados;
3.	Selecione a coluna e na aba dados use a função “Texto para Colunas”;
4.	Utilize como delimitador o caracter “|” e clique em continuar;
5.	Por meio do filtro, limpe todas as linahas e conlunas com informações desneessárias;
6.	Use uma linha com o nome das colunas para atualizar o cabeçalho da tabela;
7.	Limpar todos os espaços em branco de todas as linhas em branco e dos rótulos das colunas.
8.	Alterar somente o nome da coluna “Baixa” para “Pagos”
9.	Rodar o script.

