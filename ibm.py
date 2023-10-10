# importando as bibliotacas ultilizadas no codigo
import matplotlib.pyplot as plt
import requests
import numpy as np
import pandas as pd
import json


df = pd.read_csv('dados-gas.csv',sep=';')

# tratando os dias para apresentar melhor nos graficos
df['dias'] = df['dias'].str.replace('/','-')
dados = df.copy() # para não desestruturar meu banco de dados, realizei uma copia
meses_em_portugues = ['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez']
meses_em_ingles = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

# Substitua os nomes dos meses em português pelos nomes em inglês
dados['mes'] = dados['mes'].replace(meses_em_portugues, meses_em_ingles)

# Agora, você pode usar a função to_datetime
dados['mes'] = pd.to_datetime(dados['mes'], format='%b')

# Formate a coluna 'mes' para exibir apenas o valor correspondente do mês
dados['mes'] = dados['mes'].dt.strftime('%B')  # Isso exibirá o nome completo do mês

dataframes_por_mes = {}

# Lista de meses únicos no DataFrame
meses_unicos = dados['mes'].unique()

# Iterar pelos meses únicos e criar DataFrames separados
for mes in meses_unicos:
    df_mes = dados[dados['mes'] == mes]
    dataframes_por_mes[mes] = df_mes


# Agora, para cada mês, extraia os valores de 'valor_do_gas' em uma lista
valores_por_mes_gas = {}
valores_por_mes_umid = {}
for mes, df_mes in dataframes_por_mes.items():
    valores_gas = df_mes['valor_do_gas'].tolist()
    valores_umid = df_mes['umidade'].tolist()
    valores_por_mes_gas[mes] = valores_gas
    valores_por_mes_umid[mes] = valores_umid


class AirQualityAnalyzer:
    def __init__(self,df):
      """
      Inicializa a classe AirQualityAnalyzer.

      :param df: O DataFrame contendo os dados de qualidade do ar.
      """
      self.dados_ar = []
      self.dados_umidade = []
      self.df = dados
      self.meses = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
      self.dataframes_por_mes = {}
      self.opcao = 0
      self.valores_led_buzzer = []  # Lista para armazenar valores LED e Buzzer

    def exibir_menu(self):
      """
      Exibe o menu principal da aplicação.
      """
      print('_' * 30)
      print('\n         AXION GREEN')
      print('_' * 30)
      print('\nBem-vindo ao Analisador de Qualidade do Ar\n')
      print('Opções:')
      print("(1) Selecionar os dados lidos")
      print("(2) Ver gráfico da qualidade do ar")
      print("(3) Ver gráfico da umidade do ar")
      print("(4) Ver gráficos de qualidade de ar e umidade combinados")
      print("(5) Ver gráfico de qualidade de ar por umidade")
      print("(6) Ver gráfico com derivada")
      print("(7) Estimar mês com base em valor desejado")
      print("(8) Estimar mêses com base de valores 0 a 10")
      print("(9) Informar a região para o banco de dados")
      print("(10) Ver tabela anual")
      print("(0) Sair\n")

          
    def classificar_qualidade(self, valor):
      """
      Classifica as leituras visto o mês selecionado.

      :param valor: O valor de qualidade do ar a ser classificado.
      :return: A classificação LED e Buzzer correspondentes.
      :return: JSON qualificação
      """
      classificacoes = {
            (1, 3): ('VERDE', 'Notone'),
            (3, 6): ('AMARELO', 'Notone'),
            (6, 11): ('VERMELHO', 'Tone')
            }
      for intervalo, (led, buzzer) in classificacoes.items():
          if intervalo[0] <= valor < intervalo[1]:
              self.valores_led_buzzer.append({'LED': led, 'Buzzer': buzzer})
              return led, buzzer

    def salvar_valores_led_buzzer(self):
        # Salvar os valores LED e Buzzer em um arquivo JSON
        with open('valores_led_buzzer.json', 'w') as json_file:
            json.dump(self.valores_led_buzzer, json_file)

    def validar_input(self, prompt, valor_minimo, valor_maximo):
      """
        Tratamento de erros para entrada do usuário.

        :param prompt: A mensagem de prompt a ser exibida.
        :param valor_minimo: O valor mínimo permitido.
        :param valor_maximo: O valor máximo permitido.
        :return: O valor de entrada válido.
      """
      while True:
          try:
              valor = int(input(prompt))
              if valor_minimo <= valor <= valor_maximo:
                  return valor
              else:
                  print(f"Digite um número entre {valor_minimo} e {valor_maximo}")
          except ValueError:
              print("Entrada inválida. Digite um número válido.")


    def selecionar_mes_e_inserir_valores(self):
      """
        Seleciona os meses para a análise mensal.

        :return: O DataFrame do mês selecionado.
      """
      for i, mes in enumerate(self.meses, start=1):
        print(f"({i}) {mes}")

      opcao = self.validar_input("Opção: ", 1, len(self.meses))
      mes_selecionado = self.meses[opcao - 1]

      # Acesse o DataFrame do mês selecionado usando query
      df_mes_selecionado = self.df[self.df['mes'] == mes_selecionado]

      if not df_mes_selecionado.empty:
          print('_' * 30)
          print(f"\nValores do mês de {mes_selecionado}:")
          print(df_mes_selecionado)
          return df_mes_selecionado
      else:
          print("Mês não encontrado.")
          return None  # Adicione esta linha



    def inserir_dados(self, df_mes_selecionado):
      """
        Insere os valores mensais para plotagem de gráfico.

        :param df_mes_selecionado: O DataFrame do mês selecionado.
      """
      self.dados_ar = [(valor_gas, self.classificar_qualidade(valor_gas)[0]) for valor_gas in df_mes_selecionado['valor_do_gas']]
      self.dados_umidade = list(df_mes_selecionado['umidade'])
      self.dados_dias = []
      for dia in df_mes_selecionado['dias']:
        self.dados_dias.append(dia)



    def tabela_anual(self):
      """
      Tabela para apresentar a média anual até o momento.
      """
      # Crie listas vazias para armazenar as médias anuais
      medias_anuais_gas = []
      medias_anuais_umid = []

      # Crie um DataFrame para as médias anuais
      df_medias_anuais = pd.DataFrame(columns=['Mês', 'Média_Gás', 'Média_Umidade'])

      # Itere pelos meses e calcule as médias
      for mes, valores_gas in valores_por_mes_gas.items():
          media_gas = sum(valores_gas) // len(valores_gas)
          medias_anuais_gas.append(media_gas)

      for mes, valores_umid in valores_por_mes_umid.items():
          media_umid = sum(valores_umid) // len(valores_umid)
          medias_anuais_umid.append(media_umid)

      # Preencha o DataFrame das médias anuais
      df_medias_anuais['Mês'] = valores_por_mes_gas.keys()
      df_medias_anuais['Média_Gás'] = medias_anuais_gas
      df_medias_anuais['Média_Umidade'] = medias_anuais_umid

      # Exiba o DataFrame das médias anuais
      print(df_medias_anuais)


    def calcular_derivada(self, dados):
      """
      Calcula a derivada dos valores de gás.

      :param dados: Os valores de gás para os quais a derivada será calculada.
      :return: A derivada dos valores de gás.
      """
      derivada = np.gradient(dados)
      return derivada


    def estimar_mes_valor(self, valor_desejado):
      """
        Estima o mês com base em um valor desejado de qualidade do ar.

        :param valor_desejado: O valor desejado de qualidade do ar.
        :return: O mês estimado e a classificação correspondente.
      """
      qualidade_numeros = [ar for ar, _ in self.dados_ar]
      derivada_ar = self.calcular_derivada(qualidade_numeros)

      def funcao_qualidade(mes):
          return qualidade_numeros[int(mes)]

      def derivada_funcao(mes):
          h = 1  # Usar 1 mês de diferença para o cálculo da derivada
          if 0 <= mes < len(qualidade_numeros) - h:
              return (funcao_qualidade(mes + h) - funcao_qualidade(mes)) / h
          else:
              return 0  # Retorna 0 para os casos onde a diferença não é possível

      mes_estimado = None

      for mes_inicial in range(len(qualidade_numeros)):
          mes_atual = mes_inicial
          for _ in range(100):  # Limita o número de iterações
              if derivada_funcao(mes_atual) == 0:
                  break
              mes_atual = mes_atual - (funcao_qualidade(mes_atual) - valor_desejado) / derivada_funcao(mes_atual)
              if 0 <= mes_atual < len(qualidade_numeros):
                  mes_estimado = self.meses[int(np.floor(mes_atual + 0.5))]
                  led, _ = self.classificar_qualidade(valor_desejado)
                  return mes_estimado, led

      return "Não estimado", "Notone"



    def estimar_meses_valores(self):
      """
      Estima meses futuros com base em valores de 0 a 10.
      """
      for valor_desejado in range(1, 11):
          mes_estimado = self.estimar_mes_valor(valor_desejado)
          _, classificacao = self.classificar_qualidade(valor_desejado)
          print(f"Valor desejado: {valor_desejado}, Mês estimado: {mes_estimado}, Classificação: {classificacao}")




    def plotar_grafico_qualidade(self):
      """
      Plota o gráfico da qualidade do ar.
      """
      plt.plot([ar for ar, _ in self.dados_ar], color='darkcyan', label='Qualidade do ar')
      plt.title('Qualidade do ar - Anual')
      plt.xlabel('Dias no mes')
      plt.ylabel('Valor')
      plt.yticks(range(11))
      plt.legend()

      plt.show()
      self.plotar_grafico_barras()  #chama a funcao de plot do grafico de barras



    def plotar_grafico_barras(self):
      """
      Plota gráficos de qualidade de ar em barra.
      """
      classificacoes = {'VERDE': 0, 'AMARELO': 0, 'VERMELHO': 0}  # array para guardar a qualidade durante o ano

      for _, led in self.dados_ar:
          classificacoes[led] += 1

      classificacoes_nomes = list(classificacoes.keys())
      quantidade = list(classificacoes.values())

      plt.bar(classificacoes_nomes, quantidade, color=['green', 'yellow', 'red'])
      plt.title('Distribuição de Classificações da Qualidade do Ar')
      plt.xlabel('Classificação')
      plt.ylabel('Quantidade')
      plt.show()

    def plotar_grafico_umidade(self):
      """
      Plota o gráfico da umidade do ar em relação aos meses.
      """
      plt.plot(self.dados_umidade, color='blue', label='Umidade do ar')
      plt.title('Umidade do ar - Anual')
      plt.xlabel('Dias no mes')
      plt.ylabel('Valor')
      plt.yticks(range(15))
      plt.show()
      plt.legend()


    def plotar_graficos_combinados(self):
      """
      Junta o gráfico de qualidade de ar e a umidade para análise.
      """
      plt.plot([ar for ar, _ in self.dados_ar], color='darkcyan', label='Qualidade do ar')
      plt.plot(self.dados_umidade, color='blue', label='Umidade do ar')
      plt.title('Qualidade e Umidade do ar - Anual')
      plt.xlabel('Dias')
      plt.ylabel('Valor')
      plt.legend()
      plt.show()

    def plotar_grafico_qualidade_por_umidade(self):
      """
      Gráfico de dispersão para verificar a relação entre qualidade de ar e umidade.
      """
      qualidade_numeros = [ar for ar, _ in self.dados_ar]
      umidade = self.dados_umidade
      plt.scatter(umidade, qualidade_numeros, color='darkcyan')
      plt.title('Relação entre Qualidade do Ar e Umidade do Ar')
      plt.xlabel('Umidade do Ar')
      plt.ylabel('Qualidade do Ar')
      plt.xticks(range(1, 13))
      plt.yticks(range(1, 13))
      plt.grid()
      plt.legend()
      plt.show()

    def plotar_grafico_derivada_qualidade(self):
      """
      Plota o gráfico da derivada da qualidade do ar.
      """
      qualidade_numeros = [ar for ar, _ in self.dados_ar]
      derivada_ar = self.calcular_derivada(qualidade_numeros)

      plt.plot(derivada_ar, color='orange', label='Derivada da Qualidade do ar')
      plt.title('Derivada da Qualidade do ar')
      plt.xlabel('Dias')
      plt.ylabel('Taxa de Mudança')
      plt.legend()
      plt.show()


    def menu_nova_operacao(self):
      '''
      Menu após a primeira interação
      '''
      print('\n')
      print("_________________________________")
      print("	       MENU")
      print("_________________________________")
      print("Escolha uma opção:\n")
      print("(1) Selecionar valores de um mes específico")
      print("(2) Ver gráfico da qualidade do ar")
      print("(3) Ver gráfico da umidade do ar")
      print("(4) Ver gráficos de qualidade de ar e umidade combinados")
      print("(5) Ver gráfico de qualidade de ar por umidade")
      print("(6) Ver gráfico com derivada")
      print("(7) Estimar mês com base em valor desejado")
      print("(8) Estimar mêses com base de valores 0 a 10")
      print("(9) Informar a região para o banco de dados")
      print("(10) Ver tabela anual")
      print("(0) Sair\n")

    def informar_regiao(self):
      '''
      API de cep para relizar a analize para cada lugar selecionado
      '''
      print('\n')
      print("_________________________________")
      print("	       CEP                ")
      print("_________________________________")
      cep = input("Digite o CEP da região: ")
      self.verificar_cep(cep)

    def verificar_cep(self, cep):
      """
      Verifica o CEP com uma API.

      :param cep: O CEP a ser verificado.
      """
      url = f"https://viacep.com.br/ws/{cep}/json/"
      response = requests.get(url)

      if response.status_code == 200:
          endereco = response.json()
          print("\n[ CEP encontrado ]\n")
          print(f"CEP: {endereco['cep']}")
          print(f"Logradouro: {endereco['logradouro']}")
          print(f"Complemento: {endereco['complemento']}")
          print(f"Bairro: {endereco['bairro']}")
          print(f"Cidade: {endereco['localidade']}")
          print(f"Estado: {endereco['uf']}")
          print('\n')
      else:
          print("CEP não encontrado.")



    def main(self):
      '''
      Realiza as interações do usuario para cada opção selecionada
      '''
      self.exibir_menu()

      while self.opcao != 11:
          self.opcao = int(input('Opção: '))
          print('\n')
          if self.opcao == 1:
              #  self.inserir_dados()
              print(self.df)
              df_mes_selecionado = self.selecionar_mes_e_inserir_valores()
              if df_mes_selecionado is not None:
                  self.inserir_dados(df_mes_selecionado)  # Passe o DataFrame do mês selecionado para inserir_dados
          elif self.opcao == 2:
              self.plotar_grafico_qualidade()
          elif self.opcao == 3:
              self.plotar_grafico_umidade()
          elif self.opcao == 4:
              self.plotar_graficos_combinados()
          elif self.opcao == 5:
              self.plotar_grafico_qualidade_por_umidade()
          elif self.opcao == 6:
              self.plotar_grafico_derivada_qualidade()
          elif self.opcao == 7:
              try:
                valor_desejado = self.validar_input("Digite o valor desejado de qualidade do ar: ", 1, 10)
                mes_estimado = self.estimar_mes_valor(valor_desejado)
                print(f"O mês estimado para alcançar a qualidade do ar desejada é: {mes_estimado}")
              except ValueError:
                print("Valor desejado inválido. Digite um número entre 1 e 10.")
          elif self.opcao == 8:
                self.estimar_meses_valores()
          elif self.opcao == 9:
              self.informar_regiao()
          elif self.opcao == 10:
              self.tabela_anual()
          elif self.opcao == 0:
              print('Obrigado por testar nosso codigo!')
              print('.'*30)
              print('DESLIGANDO')
              break
          else:
              print('Opção inválida. Por favor, escolha novamente.')

          self.menu_nova_operacao()

if __name__ == "__main__":
  '''
    INICIA O PROGRAMA
  '''
  analyzer =  AirQualityAnalyzer(df)
  analyzer.main()
  analyzer.salvar_valores_led_buzzer()  # Chama a função para salvar os valores no final da execução