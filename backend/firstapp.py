from __future__ import print_function
import pandas as pd
from datetime import datetime
from flask import Flask, jsonify
from flask_cors import CORS
import numpy as np
from auth import spreadsheet_service
from auth import drive_service
import time
from googleapiclient.errors import HttpError
from datetime import timedelta
import math

app = Flask(__name__)
CORS(app) # Permite que o React acesse a API

# Função para chamada com reintento e espera
def chamada_com_espera(request, tentativas_max=5, tempo_espera=60):
    tentativas = 0
    while tentativas < tentativas_max:
        try:
            # Executa a requisição
            return request.execute()
        except HttpError as e:
            # Verifica se é erro 429 (quota excedida)
            if hasattr(e, 'resp') and e.resp.status == 429:
                tentativas += 1
                print(f"Erro 429: Reintentar em {tempo_espera} segundos (tentativa {tentativas}/{tentativas_max})")
                time.sleep(tempo_espera)  # Espera 60 segundos antes de tentar novamente
            else:
                # Se for outro erro, lança o erro
                raise
    raise Exception("Máximo de tentativas atingido")

# Função para obter o dia da semana
def obter_dia_da_semana(data):
    data_obj = pd.to_datetime(data) if isinstance(data, str) else data
    dias_da_semana = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
    dia_da_semana_numero = data_obj.weekday()
    return dias_da_semana[dia_da_semana_numero]

# Função para calcular o microciclo (semana) com base na data
def calcular_microciclo(data, primeira_data):
    """
    Calcula o microciclo garantindo que:
    - O primeiro microciclo começa na primeira segunda-feira antes ou após a primeira data disponível.
    - Todos os microciclos seguintes seguem um padrão de segunda a domingo.
    """
    data = pd.to_datetime(data)
    primeira_data = pd.to_datetime(primeira_data)

    # Encontrar o primeiro domingo a partir da primeira data disponível
    primeiro_domingo = primeira_data + timedelta(days=(6 - primeira_data.weekday()))

    # Se a data ainda estiver no primeiro microciclo (até o primeiro domingo)
    if data <= primeiro_domingo:
        return 1
    
    # Encontrar a primeira segunda-feira após o primeiro domingo
    primeira_segunda = primeiro_domingo + timedelta(days=1)

    # Calcular o número de semanas completas a partir da primeira segunda-feira
    semanas_passadas = (data - primeira_segunda).days // 7

    return semanas_passadas + 2


# Função para carregar dados do Google Sheets
def carregar_dados_wellness():
    range_name ='dados_wellness!A:H'
    spreadsheet_id = '15VCHZTSwrCecWMWCyxJ5PSS5nxXRXsz6rKw_xK5aBxw'

    try: 

        # Busca os dados da planilha
        result = chamada_com_espera(spreadsheet_service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range_name))
        valores = result.get('values', [])

        if not valores or len(valores) < 2:
            return {}  # Retorna um dicionário vazio se não houver dados
    
        # Criar um DataFrame com os dados
        colunas = valores[0]  # A primeira linha contém os nomes das colunas
        df = pd.DataFrame(valores[1:], columns=colunas)  # As demais linhas são os dados

        # Garantir que a coluna de data seja convertida corretamente para datetime
        df['Carimbo de data/hora'] = pd.to_datetime(df['Carimbo de data/hora'], errors='coerce')
        df = df.dropna(subset=['Carimbo de data/hora'])  # Remove entradas inválidas

        # Encontrar a primeira data disponível no Excel
        primeira_data = df['Carimbo de data/hora'].min()

        dados_wellness = {}

        for _, linha in df.iterrows():
            jogador = linha.get('Nome', '')
            data = linha['Carimbo de data/hora']  
            dia_da_semana = obter_dia_da_semana(data)
            microciclo = calcular_microciclo(data, primeira_data)  # Calcular o microciclo com base na data

            if jogador not in dados_wellness:
                dados_wellness[jogador] = {}

            # Extrair os dados relevantes (exemplo para 'sono', 'fadiga', etc.)
            if microciclo not in dados_wellness[jogador]:
                dados_wellness[jogador][microciclo] = {}

            # Extrair os dados relevantes (exemplo para 'sono', 'fadiga', etc.)
            dados_wellness[jogador][microciclo][dia_da_semana] = {
                'sono': int(linha.get('Como foi o teu sono na última noite?', '0')) if linha.get('Como foi o teu sono na última noite?', '').isdigit() else 0,
                'fadiga': int(linha.get('Qual o teu nível de fadiga (cansaço)?', '0')) if linha.get('Qual o teu nível de fadiga (cansaço)?', '').isdigit() else 0,
                'dor_muscular': int(linha.get('Como estás em relação às dores musculares?', '0')) if linha.get('Como estás em relação às dores musculares?', '').isdigit() else 0,
                'stress': int(linha.get('Qual o teu nível de Stress?', '0')) if linha.get('Qual o teu nível de Stress?', '').isdigit() else 0,
            }

            # Remover repetições e garantir que cada jogador apareça uma vez
        jogadores_unicos = list(set(dados_wellness.keys()))  # Usando set para remover duplicados

        return dados_wellness, jogadores_unicos
    
    except HttpError as error:
        # Se o erro não for de cota (429), levanta o erro
        if error.resp.status != 429:
            print(f"Erro ao carregar dados: {error}")
            raise error
        else:
            print("Erro 429: Excedeu o limite de requisições")
            raise

# Função para carregar dados da PSE, da Carga Interna e da Carga Externa em Distância Total (DT) e em Distância a Alta Velocidade (HS)
def carregar_dados_pse_carga_treino():
    range_name ='gpexe_0125!A:Y'
    spreadsheet_id = '1RSBz3OHn7b-G2qD9aRh9Fb69ipUiKIev_wQoSjm4j7k'

    try:

        # Usando chamada_com_espera para garantir que, se o limite for excedido, o código tente novamente
        result = chamada_com_espera(spreadsheet_service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range_name))
        valores = result.get('values', [])

        if not valores or len(valores) < 2:
            return {}, {}, {}, {}, {}

        # Criar um DataFrame com os dados
        colunas = valores[0]  # A primeira linha contém os nomes das colunas
        df = pd.DataFrame(valores[1:], columns=colunas)

        # Garantir que a coluna de data seja convertida corretamente para datetime
        df['start date/time'] = pd.to_datetime(df['start date/time'], errors='coerce')

        # Filtrar linhas com datas inválidas
        df = df.dropna(subset=['start date/time'])

        if df.empty:
            return {}, {}, {}, {}, {}
        
        # Encontrar a primeira data disponível e remover horas/minutos/segundos
        primeira_data_pse = df['start date/time'].min().normalize()

        dados_pse = {}
        carga_interna = {}
        carga_externa_dt = {}
        carga_externa_hs = {}

        # Função auxiliar para converter valores numéricos corretamente
        def converter_para_float(valor):
            try:
                return float(str(valor).replace(',', '.'))
            except ValueError:
                return 0.0 

        for _, linha in df.iterrows():
            jogador = str(linha.get('athlete', '').strip())
            data = linha['start date/time']
            data_str = data.strftime('%Y-%m-%d')  # Converter a data para string no formato YYYY-MM-DD
            dia_da_semana = obter_dia_da_semana(data)
            microciclo = calcular_microciclo(data.normalize(), primeira_data_pse)

            # Inicializar dicionários para o jogador e microciclo
            for dic in [dados_pse, carga_interna, carga_externa_dt, carga_externa_hs]:
                dic.setdefault(jogador, {}).setdefault(microciclo, {}).setdefault(dia_da_semana, [])

            # Pegar na PSE 
            pse_valor = linha.get('RPE', '').strip()

            # Se PSE for vazio ou inválido, assume None
            try:
                pse_valor = int(pse_valor) if pse_valor else None

            except ValueError:
                pse_valor = None

            # Pegar na Duração do Treino/Jogo
            duracao_treino = linha.get('duration (mm:ss)', '').strip()

            if duracao_treino:
                try:
                    # Remover os últimos 3 caracteres se o formato for MM:SS:00
                    if len(duracao_treino) > 5 and duracao_treino[-3:] == ':00':
                        duracao_treino = duracao_treino[:-3]  # Fica apenas com MM:SS
                    
                    minutos, segundos = map(int, duracao_treino.split(':'))  # Separar minutos e segundos
                    duracao_treino = minutos + (segundos / 60)  # Converter segundos para fração de minuto
                except ValueError:
                    duracao_treino = 0 # Caso tenha erro na conversão, define como 0
            else: 
                duracao_treino = 0  # Se estiver vazio, assume 0

            # Se PSE estiver ausente, a carga interna será None
            carga_int = (pse_valor * duracao_treino) if pse_valor is not None else None

            # Pegar na Distância Total
            dist_total = converter_para_float(linha.get('distance (m)', '').strip())

            # Pegar na Distância Percorrida a Alta Velocidade
            hs_z4 = converter_para_float(linha.get('distance / speed Z4 (m)', '').strip())
            hs_z5 = converter_para_float(linha.get('distance / speed Z5 (m)', '').strip())
            
            hs_total = hs_z4 + hs_z5

            # Adicionar dados ao dicionário como uma nova entrada na lista
            if pse_valor is not None:
                dados_pse[jogador][microciclo][dia_da_semana].append({
                'data_treino': data_str,
                'pse': pse_valor
                })

            carga_interna[jogador][microciclo][dia_da_semana].append({
                'data_treino': data_str,
                'duracao': duracao_treino,
                'carga_interna': carga_int
            })

            carga_externa_dt[jogador][microciclo][dia_da_semana].append({
                'data_treino': data_str,
                'distancia_total': dist_total
            })

            carga_externa_hs[jogador][microciclo][dia_da_semana].append({
                'data_treino': data_str,
                'distancia_hs': hs_total
            })

        print("dados_pse:", dados_pse)

        return dados_pse, carga_interna, carga_externa_dt, carga_externa_hs
    
    except HttpError as error:
        # Se o erro não for de cota (429), levanta o erro
        if error.resp.status != 429:
            print(f"Erro ao carregar dados: {error}")
            raise error
        else:
            print("Erro 429: Excedeu o limite de requisições")
            raise

# Calcular o Rácio Carga Aguda/Crónica para a Carga Interna
def calcular_racio(jogador):
    _, carga_interna, _, _ = carregar_dados_pse_carga_treino()
    
    if jogador not in carga_interna:
        return None
    
    racios = {}  # Dicionário para armazenar os rácios de cada microciclo
    total_carga_ate_agora = 0  # Variável para armazenar o total de carga acumulada até o momento
    
    microciclos = sorted(carga_interna[jogador].keys())  # Ordenar os microciclos para cálculo correto

    for i, microciclo in enumerate(microciclos, start=1):  # Para cada microciclo
        
        # Soma da carga interna do microciclo atual
        total_carga_microciclo = sum(
            treino["carga_interna"] 
            for dias in carga_interna[jogador][microciclo].values() 
            for treino in dias
            if treino["carga_interna"] is not None
        )

        if i == 1:
            racio = 0 # No primeiro microciclo não há média crônica para comparar
                    
        else:
            total_carga_ate_agora += total_carga_microciclo  # Atualiza o total acumulado de carga
            media_acumulada = total_carga_ate_agora / i # Média acumulada até esse microciclo
            racio = round(total_carga_microciclo / media_acumulada, 2) if media_acumulada != 0 else 1

        racios[microciclo] = racio

    return racios


# Calcular o Rácio Carga Aguda/Crónica para a Carga Externa DT
def calcular_racio_dt(jogador):
    _, _, carga_externa_dt, _ = carregar_dados_pse_carga_treino()

    if jogador not in carga_externa_dt:
        return None
    
    racios_dt = {}  # Dicionário para armazenar os rácios de cada microciclo
    total_carga_externa_dt_ate_agora = 0  # Variável para armazenar o total de carga acumulada até o momento
    
    microciclos = sorted(carga_externa_dt[jogador].keys())
    
    for i, microciclo in enumerate(microciclos, start=1):  # Para cada microciclo
        
        total_carga_externa_dt_microciclo = sum(treino["distancia_total"] for treino in carga_externa_dt[jogador][microciclo] if treino["distancia_total"] is not None)

        if i == 1:
            racio_dt = 0
        
        else:
            
            # Atualiza o total acumulado de carga até o microciclo atual
            total_carga_externa_dt_ate_agora += total_carga_externa_dt_microciclo
        
            # Média acumulada até o microciclo atual
            media_acumulada_dt = total_carga_externa_dt_ate_agora / i  
        
            # Rácio carga aguda/crónica (carga do microciclo atual / média acumulada)
            racio_dt = round(total_carga_externa_dt_microciclo / media_acumulada_dt, 2) if media_acumulada_dt != 0 else 1
                     
        racios_dt[microciclo] = racio_dt

    return racios_dt


# Calcular o M% para a Carga Externa DT
def calcular_m_dt(jogador):
    _, _, carga_externa_dt, _ = carregar_dados_pse_carga_treino()

    if jogador not in carga_externa_dt:
        return None
    
    m_dt = {}  # Dicionário para armazenar os rácios de cada microciclo
    carga_externa_dt_anterior = 0  # Variável para armazenar o total de carga da semana anterior

    microciclos = sorted(carga_externa_dt[jogador].keys())

    for i, microciclo in enumerate(microciclos, start=1):

        total_carga_externa_dt_microciclo = sum(treino["distancia_total"] for treino in carga_externa_dt[jogador][microciclo] if treino["distancia_total"] is not None)

        if i == 1:
            valor_m_dt = 0         
                    
        else:          
            # M% (carga do microciclo atual / média acumulada)
            valor_m_dt = round(((total_carga_externa_dt_microciclo - carga_externa_dt_anterior )/ total_carga_externa_dt_microciclo) * 100, 2) if total_carga_externa_dt_microciclo != 0 else 1
                     
        m_dt[microciclo] = valor_m_dt
        
        carga_externa_dt_anterior = total_carga_externa_dt_microciclo

    return m_dt

# Calcular o Rácio Carga Aguda/Crónica para a Carga Externa HS
def calcular_racio_hs(jogador):
    _, _, _, carga_externa_hs = carregar_dados_pse_carga_treino()

    if jogador not in carga_externa_hs:
        return None
    
    racios_hs = {}  # Dicionário para armazenar os rácios de cada microciclo
    total_carga_externa_hs_ate_agora = 0  # Variável para armazenar o total de carga acumulada até o momento
    
    microciclos = sorted(carga_externa_hs[jogador].keys())
    
    for i, microciclo in enumerate(microciclos, start=1):  # Para cada microciclo
        
        total_carga_externa_hs_microciclo = sum(treino["distancia_hs"] for treino in carga_externa_hs[jogador][microciclo] if treino["distancia_hs"] is not None)

        if i == 1:
            racio_hs = 0
        
        else:
            
            # Atualiza o total acumulado de carga até o microciclo atual
            total_carga_externa_hs_ate_agora += total_carga_externa_hs_microciclo
        
            # Média acumulada até o microciclo atual
            media_acumulada_hs = total_carga_externa_hs_ate_agora / i  
        
            # Rácio carga aguda/crónica (carga do microciclo atual / média acumulada)
            racio_hs = round(total_carga_externa_hs_microciclo / media_acumulada_hs, 2) if media_acumulada_hs != 0 else 1
                     
        racios_hs[microciclo] = racio_hs

    return racios_hs

# Calcular o M% para a Carga Externa HS
def calcular_m_hs(jogador):
    _, _, _, carga_externa_hs = carregar_dados_pse_carga_treino()

    if jogador not in carga_externa_hs:
        return None
    
    m_hs = {}  # Dicionário para armazenar os rácios de cada microciclo
    carga_externa_hs_anterior = 0  # Variável para armazenar o total de carga da semana anterior

    microciclos = sorted(carga_externa_hs[jogador].keys())

    for i, microciclo in enumerate(microciclos, start=1):

        total_carga_externa_hs_microciclo = sum(treino["distancia_hs"] for treino in carga_externa_hs[jogador][microciclo] if treino["distancia_hs"] is not None)

        if i == 1:
            valor_m_hs = 0         
                    
        else:          
            # M% (carga do microciclo atual / média acumulada)
            valor_m_hs = round(((total_carga_externa_hs_microciclo - carga_externa_hs_anterior )/ total_carga_externa_hs_microciclo) * 100, 2) if total_carga_externa_hs_microciclo != 0 else 1
                     
        m_hs[microciclo] = valor_m_hs
        
        carga_externa_hs_anterior = total_carga_externa_hs_microciclo

    return m_hs

# Calcular a Monotonia
def calcular_monotonia(jogador, carga_interna):

    if jogador not in carga_interna:
        return None
    
    monotonia_micro = {} # Dicionário para armazenar a monotonia de cada microciclo
    
    for microciclo, treinos in carga_interna[jogador].items():  # Itera pelos microciclos do jogador
        total_carga_microciclo = [
            treino["carga_interna"] for treino in treinos if treino["carga_interna"] is not None
        ]

        # Calcula média e desvio padrão se houver dados
        if total_carga_microciclo:
            media_carga_microciclo = np.mean(total_carga_microciclo)  # Média da carga interna
            desvio_padrao = np.std(total_carga_microciclo, ddof=1)  # Desvio padrão amostral

            # Evita divisão por zero
            monotonia = round(media_carga_microciclo / desvio_padrao, 2) if desvio_padrao != 0 else 0
        
        else:
            monotonia = 0

        monotonia_micro[microciclo] = monotonia  # Armazena no dicionário

    return monotonia_micro

# Calcular o Strain
def calcular_strain(jogador, carga_interna):
    if jogador not in carga_interna:
        return None
    
    monotonia_micro = calcular_monotonia(jogador, carga_interna)  # Primeiro, calcular a monotonia
    strain_micro = {}

    for microciclo, treinos in carga_interna[jogador].items():  # Itera pelos microciclos do jogador
        total_carga_microciclo = [
            treino["carga_interna"] for treino in treinos if treino["carga_interna"] is not None
        ]
        
        # Se houver dados, calcula o strain
        if total_carga_microciclo:
            total_carga = np.sum(total_carga_microciclo)  # Soma de todas as cargas internas no microciclo
            monotonia = monotonia_micro.get(microciclo, 0)  # Obtém a monotonia do microciclo

        # Strain = monotonia * total carga interna
            strain = round(monotonia * total_carga, 2)
        else:
            strain = 0  # Se não houver dados, o strain é 0

        strain_micro[microciclo] = strain  # Armazena o strain no dicionário

    return strain_micro

# Função para calcular a média das variáveis de wellness para cada microciclo
def calcular_media_wellness(jogador, dados_wellness):
    media_wellness = {}

    if jogador not in dados_wellness:
        return {}

    for microciclo, dias in dados_wellness[jogador].items():
        soma_variaveis = {"sono": 0, "fadiga": 0, "dor_muscular": 0, "stress": 0}
        total_dias = len(dias)

        # Somar todas as variáveis por microciclo
        for valores in dias.values():
            for var in soma_variaveis:
                try:
                    # Verifica se o valor é válido (não vazio e é numérico)
                    if valores[var] != '' and valores[var].isdigit():
                        soma_variaveis[var] += float(valores[var])
                
                except ValueError:
                    soma_variaveis[var] += 0  # Se não for um número válido, considera como 0

        # Verificar se há dias para calcular a média (evitar divisão por zero)
        if total_dias > 0:
            # Calcular a média das variáveis por microciclo
            media_microciclo = np.mean(list(soma_variaveis.values())) / total_dias
            media_wellness[microciclo] = round(media_microciclo, 2)  # Arredonda para 2 casas decimais

    return media_wellness

# Função para criar o dicionário dados ontendo os valores da variável (ex: ACWR PSE, ACWR DT, Wellness, Monotonia, Strain)
def criar_dados():
    
    # Inicializa o dicionário para armazenar os dados por jogador
    dados = {}

    # Carregar os dados de wellness e carga interna
    dados_wellness, _ = carregar_dados_wellness()  # Carregar dados de wellness
    _, carga_interna, _, _ = carregar_dados_pse_carga_treino()  # Carregar dados de carga interna

    # Iterar sobre todos os jogadores
    for jogador in carga_interna:  # Para cada jogador nos dados de carga interna
        dados[jogador] = {}  # Inicializa o dicionário para o jogador

        # Verificar se o jogador tem dados válidos de wellness e carga interna
        if jogador in dados_wellness:
            media_wellness = calcular_media_wellness(jogador, dados_wellness)
        else:
            media_wellness = {}  # Definir como vazio se não houver dados

        # Calcular os rácios e métricas se o jogador tem dados de carga interna
        if jogador in carga_interna:
            racios = calcular_racio(jogador)
            racios_dt = calcular_racio_dt(jogador)
            monotonia_micro = calcular_monotonia(jogador, carga_interna)
            strain_micro = calcular_strain(jogador, carga_interna)

        else:
            racios = {}
            racios_dt = {}
            monotonia_micro = {}
            strain_micro = {}

        # Iterar pelos microciclos para cada jogador
        for microciclo in sorted(carga_interna.get(jogador, {}).keys()):  # Ordenar os microciclos 
            dados[jogador][microciclo] = {
                "ACWR PSE": racios.get(microciclo, 0),
                "ACWR DT": racios_dt.get(microciclo, 0),
                "Wellness": media_wellness.get(microciclo, 0),
                "Monotonia": monotonia_micro.get(microciclo, 0),
                "Strain": strain_micro.get(microciclo, 0)
            }


def calcular_z_score(dados):
    """
    Calcula o Z-score de uma variável específica para todos os jogadores.
    :param dados: Dicionário contendo os valores da variável (ex: ACWR PSE, ACWR DT, Wellness, Monotonia, Strain)
    :param microciclo: O microciclo específico para cálculo do Z-score
    :return: Dicionário contendo o Z-score de cada jogador para a variável analisada
    """
    z_scores = {}

    if not dados:
        return {}
    
    # Obter lista de microciclos e variáveis
    microciclos = list(next(iter(dados.values())).keys())  # Pega os microciclos de um jogador qualquer
    variaveis = list(next(iter(dados.values())).values())[0].keys()  # Pega as variáveis do primeiro microciclo

    # Coletar valores de todos os jogadores para o microciclo especificado
    for jogador in dados:
        z_scores[jogador] = {}

    for microciclo in microciclos:
        z_scores[jogador][microciclo] = {}

        for variavel in variaveis:
            valores = []

            # Coletar valores de todos os jogadores para a variável no microciclo atual
            for jogador_dados in dados.values():
                if microciclo in jogador_dados and variavel in jogador_dados[microciclo]:
                    valor = jogador_dados[microciclo][variavel]
                    if valor is not None:
                        valores.append(valor)

            # Calcular média e desvio padrão
            if valores:
                media = np.mean(valores)
                desvio_padrao = np.std(valores, ddof=1)  # ddof=1 para desvio padrão amostral
            else:
                media = 0
                desvio_padrao = 1  # Se não há valores, evitamos a divisão por 0

            if microciclo in dados[jogador] and variavel in dados[jogador][microciclo]:
                valor = dados[jogador][microciclo][variavel]
                z_score = round((valor-media)/desvio_padrao, 2) if desvio_padrao != 0 else 0

                z_scores[jogador][microciclo][variavel] = z_score

    return z_scores

# Calcular Z-scores das variáveis
dados = criar_dados()
z_scores = calcular_z_score(dados)

# Função auxiliar para buscar o Z-score de uma variável específica
def get_z_score(jogador, microciclo, variavel):

    if jogador not in z_scores or microciclo not in z_scores[jogador]:
        return jsonify({"erro": "Jogador ou microciclo não encontrado"}), 404
    
    return jsonify({
        "jogador": jogador,
        "microciclo": microciclo,
        "variavel": variavel,
        "z_score": z_scores[jogador][microciclo].get(variavel, 0)
    })

# Função para carregar os dados do CMJ e SJ do Google Sheets
def carregar_dados_cmj_sj():
    range_name = 'cmj_sj!A:D'  # Nome correto da aba e colunas
    spreadsheet_id = '1CM-UKcOOWM1LLbBP_OL5nqL7n2IG0MZPQA10WeadQek'

    try:

        # Buscar os dados da planilha
        result = chamada_com_espera(spreadsheet_service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range_name))
        valores = result.get('values', [])

        if not valores or len(valores) < 2:
            return {}, {}

        # Criar DataFrame
        colunas = valores[0]
        df = pd.DataFrame(valores[1:], columns=colunas)

        # Garantir que a coluna de data seja convertida corretamente para datetime
        df['Data'] = pd.to_datetime(df['Data'], format='%d/%m/%Y')

        # Determinar a primeira data para calcular microciclos
        primeira_data = df['Data'].min()

        # Inicializar dicionários separados para CMJ e SJ
        cmj = {}
        sj = {}

        for _, linha in df.iterrows():
            jogador = linha.get('Nome', '').strip()

            # Verifica se o nome do jogador é válido (não vazio)
            if not jogador:
                continue
            
            data = linha['Data']
            microciclo = calcular_microciclo(data, primeira_data)

            # Criar dicionário para cada jogador se ainda não existir
            if jogador not in cmj:
                cmj[jogador] = {}
                sj[jogador] = {}

            # Verificar se há valor no CMJ e SJ, senão colocar None
            cmj_valor = linha.get('Height_CMJ', '').strip()
            sj_valor = linha.get('Height_SJ', '').strip()

            try:
                cmj_valor = float(cmj_valor) if cmj_valor else None
            except ValueError:
                cmj_valor = None

            try:
                sj_valor = float(sj_valor) if sj_valor else None
            except ValueError:
                sj_valor = None

            # Armazenar os valores, mesmo que None
            cmj[jogador][microciclo] = {"CMJ": cmj_valor}
            sj[jogador][microciclo] = {"SJ": sj_valor}

        return cmj, sj

    except HttpError as error:
        # Se o erro não for de cota (429), levanta o erro
        if error.resp.status != 429:
            print(f"Erro ao carregar dados: {error}")
            raise error
        else:
            print("Erro 429: Excedeu o limite de requisições")
            raise

    
# Rota para buscar jogadores
@app.route('/api/jogadores', methods=['GET'])
def get_jogadores():
    _, jogadores_unicos = carregar_dados_wellness()  # Carregar os dados atualizados
    return jsonify(jogadores_unicos)

# Rota para buscar microciclos
@app.route('/api/microciclos', methods=['GET'])
def get_microciclos():
    # Carregar os dados do Google Sheets ou do arquivo Excel
    dados_wellness, _ = carregar_dados_wellness()

    # Obter todos os microciclos únicos dos jogadores
    microciclos = set()

    for jogador in dados_wellness:
        microciclos.update(dados_wellness[jogador].keys())

    # Ordenar os microciclos numericamente
    microciclos = sorted(microciclos, key=int)

    return jsonify(microciclos)

# Rota para buscar os dados wellness
@app.route('/api/wellness/<jogador>/<int:microciclo>', methods=['GET'])
def get_wellness(jogador, microciclo):
    dados_wellness, _= carregar_dados_wellness()

    if jogador in dados_wellness and microciclo in dados_wellness[jogador]:
        return jsonify(dados_wellness[jogador][microciclo])
    else:
        return jsonify({"erro": "Jogador ou Microciclo não encontrado"}), 404


# Rota para buscar os dados da PSE de um jogador e microciclo específico
@app.route('/api/pse/<jogador>/<int:microciclo>', methods=['GET'])
def get_pse(jogador, microciclo):
    dados_pse, _, _, _ = carregar_dados_pse_carga_treino()

    if jogador in dados_pse and microciclo in dados_pse[jogador]:
        return jsonify(dados_pse[jogador][microciclo])
    else:
        return jsonify({"erro": "Jogador ou Microciclo não encontrado"}), 404

# Rota para buscar os dados da Carga Interna de um jogador e microciclo específico
@app.route('/api/carga_interna/<jogador>/<int:microciclo>', methods=['GET'])
def get_carga_interna(jogador, microciclo):
    _, carga_interna, _, _ = carregar_dados_pse_carga_treino()

    if jogador in carga_interna and microciclo in carga_interna[jogador]:
        return jsonify(carga_interna[jogador][microciclo])
    else:
        return jsonify({"erro": "Jogador ou Microciclo não encontrado"}), 404

# Rota para buscar o rácio carga aguda/crónica para a Carga Interna de um jogador
@app.route('/api/racio/<jogador>')
def get_racio(jogador):
    racios = calcular_racio(jogador)

    if racios:
        return jsonify(racios)
    else:
        return jsonify({"erro": "Jogador não encontrado ou sem dados"}), 404
    
# Rota para buscar os dados da Carga Externa em DT de um jogador e microciclo específico
@app.route('/api/carga_externa_dt/<jogador>/<int:microciclo>')
def get_carga_externa_dt(jogador, microciclo):
    _, _, carga_externa_dt, _ = carregar_dados_pse_carga_treino()
    if jogador in carga_externa_dt and microciclo in carga_externa_dt[jogador]:
        return jsonify(carga_externa_dt[jogador][microciclo])
    else:
        return jsonify({"erro": "Jogador ou Microciclo não encontrado"}), 404

# Rota para buscar o rácio carga aguda/crónica para a Carga Externa DT de um jogador
@app.route('/api/racio_dt/<jogador>')
def get_racio_dt(jogador):
    racios_dt = calcular_racio_dt(jogador) 

    if racios_dt:
        return jsonify(racios_dt)
    else:
        return jsonify({"erro": "Jogador não encontrado"}), 404
    
# Rota para buscar os dados da Carga Externa em HS de um jogador e microciclo específico
@app.route('/api/carga_externa_hs/<jogador>/<int:microciclo>')
def get_carga_externa_hs(jogador, microciclo):
    _, _, _, carga_externa_hs = carregar_dados_pse_carga_treino()
    if jogador in carga_externa_hs and microciclo in carga_externa_hs[jogador]:
        return jsonify(carga_externa_hs[jogador][microciclo])
    else:
        return jsonify({"erro": "Jogador ou Microciclo não encontrado"}), 404

# Rota para buscar o rácio carga aguda/crónica para a Carga Externa HS de um jogador
@app.route('/api/racio_hs/<jogador>')
def get_racio_hs(jogador):
    racios_hs = calcular_racio_hs(jogador)
    if racios_hs:
        return jsonify(racios_hs)
    else:
        return jsonify({"erro": "Jogador não encontrado"}), 404
    
# Rota para buscar o M% para a Carga Externa DT de um jogador
@app.route('/api/m_dt/<jogador>')
def get_m_dt(jogador):
    m_dt = calcular_m_dt(jogador)

    if m_dt:        
        return jsonify(m_dt)
    else:
        return jsonify({"erro": "Jogador não encontrado"}), 404
    
# Rota para buscar o M% para a Carga Externa HS de um jogador
@app.route('/api/m_hs/<jogador>')
def get_m_hs(jogador):
    m_hs = calcular_m_hs(jogador)
    if m_hs:
        return jsonify(m_hs)
    else:
        return jsonify({"erro": "Jogador não encontrado"}), 404
    
# Rota para buscar os dados da Carga Interna de um jogador e microciclo específico
@app.route('/api/monotonia/<jogador>')
def get_monotonia(jogador):
    _, carga_interna, _, _ = carregar_dados_pse_carga_treino()  # Carregar os dados da carga interna
    if jogador in carga_interna:
        monotonia_micro = calcular_monotonia(jogador, carga_interna)
        return jsonify(monotonia_micro)
    else:
        return jsonify({"erro": "Jogador não encontrado"}), 404
    
# Rota para buscar os dados da Strain de um jogador específico
@app.route('/api/strain/<jogador>')
def get_strain(jogador):
    _, carga_interna, _, _ = carregar_dados_pse_carga_treino()  # Carregar os dados da carga interna
    if jogador in carga_interna:
        strain_micro = calcular_strain(jogador, carga_interna)
        return jsonify(strain_micro)
    else:
        return jsonify({"erro": "Jogador não encontrado"}), 404
    
@app.route('/api/zscore/acwr_pse/<jogador>/<int:microciclo>', methods=['GET'])
def zscore_acwr_pse(jogador, microciclo):
    return get_z_score(jogador, microciclo, "ACWR PSE")


@app.route('/api/zscore/acwr_dt/<jogador>/<int:microciclo>', methods=['GET'])
def zscore_acwr_dt(jogador, microciclo):
    return get_z_score(jogador, microciclo, "ACWR DT")


@app.route('/api/zscore/wellness/<jogador>/<int:microciclo>', methods=['GET'])
def zscore_wellness(jogador, microciclo):
    return get_z_score(jogador, microciclo, "Wellness")


@app.route('/api/zscore/monotonia/<jogador>/<int:microciclo>', methods=['GET'])
def zscore_monotonia(jogador, microciclo):
    return get_z_score(jogador, microciclo, "Monotonia")


@app.route('/api/zscore/strain/<jogador>/<int:microciclo>', methods=['GET'])
def zscore_strain(jogador, microciclo):
    return get_z_score(jogador, microciclo, "Strain")


# Rota para buscar os dados do CMJ de um jogador e microciclo específico
@app.route('/api/cmj/<jogador>/<int:microciclo>')
def get_cmj(jogador, microciclo):
    cmj, _ = carregar_dados_cmj_sj()
    if jogador in cmj and microciclo in cmj[jogador]:
        return jsonify(cmj[jogador][microciclo])
    else:
        return jsonify({"erro": "Jogador ou Microciclo não encontrado"}), 404
    
# Rota para buscar os dados do SJ de um jogador e microciclo específico
@app.route('/api/sj/<jogador>/<int:microciclo>')
def get_sj(jogador, microciclo):
    _, sj = carregar_dados_cmj_sj()
    if jogador in sj and microciclo in sj[jogador]:
        return jsonify(sj[jogador][microciclo])
    else:
        return jsonify({"erro": "Jogador ou Microciclo não encontrado"}), 404
    
if __name__ == '__main__':
    app.run(debug=False, use_reloader=False)