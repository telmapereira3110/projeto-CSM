from __future__ import print_function
import pandas as pd
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
from urllib.parse import unquote
import numpy as np
from auth import spreadsheet_service
from auth import drive_service
import time
from googleapiclient.errors import HttpError
from datetime import timedelta
import math
import os
from google.oauth2 import service_account
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env (se estiver rodando localmente)
load_dotenv()  # Se você estiver testando localmente, coloque as variáveis no arquivo .env

# Carregar as credenciais do Google a partir das variáveis de ambiente
google_credentials = {
    "type": "service_account",
    "project_id": os.getenv('GOOGLE_PROJECT_ID'),
    "private_key_id": os.getenv('GOOGLE_PRIVATE_KEY_ID'),
    "private_key": os.getenv('GOOGLE_PRIVATE_KEY').replace("\\n", "\n"),  # Corrigindo quebras de linha
    "client_email": os.getenv('GOOGLE_CLIENT_EMAIL'),
    "client_id": os.getenv('GOOGLE_CLIENT_ID'),
    "auth_uri": os.getenv('GOOGLE_AUTH_URI'),
    "token_uri": os.getenv('GOOGLE_TOKEN_URI'),
    "auth_provider_x509_cert_url": os.getenv('GOOGLE_AUTH_PROVIDER_CERT_URL'),
    "client_x509_cert_url": os.getenv('GOOGLE_CLIENT_X509_CERT_URL')
}

# Gerar as credenciais com base nas variáveis de ambiente
credentials = service_account.Credentials.from_service_account_info(google_credentials)

# Usar essas credenciais para autenticação com as APIs do Google
from googleapiclient.discovery import build

# Para a API de Google Sheets
spreadsheet_service = build('sheets', 'v4', credentials=credentials)

# Para a API de Google Drive
drive_service = build('drive', 'v3', credentials=credentials)

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "https://projeto-csm.vercel.app"}})# Permite que o React acesse a API

# Variáveis globais para o cache
# cache_dados = {
#    "timestamp_pse": None,
#    "dados_pse": None,
#    "timestamp_wellness": None,
#    "dados_wellness": None
#}

# Tempo de validade do cache (ex: 10 minutos)
# CACHE_TTL = timedelta(minutes=10)

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

def carregar_dados_wellness():
    now = datetime.now()

    # Verifica se já temos dados no cache e se estão dentro do TTL
    #if cache_dados["dados_wellness"] is not None and cache_dados["timestamp_wellness"] is not None:
        #if now - cache_dados["timestamp_wellness"] < CACHE_TTL:
            #return cache_dados["dados_wellness"]
        
    range_name = 'dados_wellness!A:H'
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
        primeira_data_wellness = df['Carimbo de data/hora'].min()

        dados_wellness = {}

        for _, linha in df.iterrows():
            jogador = linha.get('Nome', '')
            data = linha['Carimbo de data/hora']
            data_str = data.strftime('%Y-%m-%d')  # Converter a data para string no formato YYYY-MM-DD
            dia_da_semana = obter_dia_da_semana(data)
            microciclo = calcular_microciclo(data, primeira_data_wellness)  # Calcular o microciclo com base na data

            if jogador not in dados_wellness:
                dados_wellness[jogador] = {}

            if microciclo not in dados_wellness[jogador]:
                dados_wellness[jogador][microciclo] = {}

            # Armazenar a data e os valores dentro do microciclo
            dados_wellness[jogador][microciclo][dia_da_semana] = {
                'data': data_str,
                'sono': int(linha.get('Como foi o teu sono na última noite?', '0')) if linha.get('Como foi o teu sono na última noite?', '').isdigit() else 0,
                'fadiga': int(linha.get('Qual o teu nível de fadiga (cansaço)?', '0')) if linha.get('Qual o teu nível de fadiga (cansaço)?', '').isdigit() else 0,
                'dor_muscular': int(linha.get('Como estás em relação às dores musculares?', '0')) if linha.get('Como estás em relação às dores musculares?', '').isdigit() else 0,
                'stress': int(linha.get('Qual o teu nível de Stress?', '0')) if linha.get('Qual o teu nível de Stress?', '').isdigit() else 0,
            }

        # Lista única de jogadores
        jogadores_unicos = list(dados_wellness.keys())

        # Atualiza o cache
        #cache_dados["dados_wellness"] = dados_wellness
        #cache_dados["timestamp_wellness"] = datetime.now()

        print(f"Retornando dados: {dados_wellness} e jogadores: {jogadores_unicos}")  # Adicionando print para depuração

        return dados_wellness, jogadores_unicos

    except HttpError as error:
        if error.resp.status != 429:
            print(f"Erro ao carregar dados: {error}")
            raise error
        else:
            print("Erro 429: Excedeu o limite de requisições")
            raise

# Função para carregar dados da PSE, da Carga Interna e da Carga Externa em Distância Total (DT) e em Distância a Alta Velocidade (HS)
def carregar_dados_pse_carga_treino():
    now = datetime.now()

    # Verifica se já temos dados no cache e se estão dentro do TTL
    #if cache_dados["dados_pse"] is not None and cache_dados["timestamp_pse"] is not None:
        #if now - cache_dados["timestamp_pse"] < CACHE_TTL:
            #return cache_dados["dados_pse"]
        
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
                    duracao_treino = round(duracao_treino, 2)  # Duas casas decimais
                except ValueError:
                    duracao_treino = 0 # Caso tenha erro na conversão, define como 0
            else: 
                duracao_treino = 0  # Se estiver vazio, assume 0

            # Se PSE estiver ausente, a carga interna será None
            if pse_valor is not None:
                carga_int = math.ceil(pse_valor * duracao_treino)  # Arredondado para cima (sem casas decimais)
            else:
                carga_int = None

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
                'duracao_treino': duracao_treino,
                'carga_interna': carga_int
            })

            carga_externa_dt[jogador][microciclo][dia_da_semana].append({
                'data_treino': data_str,
                'distancia_total': round(dist_total, 2)
            })

            carga_externa_hs[jogador][microciclo][dia_da_semana].append({
                'data_treino': data_str,
                'distancia_hs': round(hs_total, 2)
            })

            # Atualiza o cache
        #cache_dados["dados_pse"] = ( dados_pse, carga_interna, carga_externa_dt, carga_externa_hs)
        #cache_dados["timestamp_pse"] = datetime.now()

        return dados_pse, carga_interna, carga_externa_dt, carga_externa_hs
    
    except HttpError as error:
        # Se o erro não for de cota (429), levanta o erro
        if error.resp.status != 429:
            print(f"Erro ao carregar dados: {error}")
            raise error
        else:
            print("Erro 429: Excedeu o limite de requisições")
            raise

def calcular_metricas_carga_treino(jogador):
    _, carga_interna, carga_externa_dt, carga_externa_hs = carregar_dados_pse_carga_treino()

    # Inicializar dicionários
    racio_carga_interna = {}
    racio_carga_externa_dt = {}
    m_porcento_dt = {}
    racio_carga_externa_hs = {}
    m_porcento_hs = {}

    def calcular_racio(cargas, chave):
        racios = {}
        total_ate_agora = 0
        microciclos = sorted(cargas[jogador].keys())

        for i, microciclo in enumerate(microciclos, start=1):
            cargas_validas = [
                treino[chave]
                for dias in cargas[jogador][microciclo].values()
                for treino in dias
                if treino[chave] is not None
            ]

            if not cargas_validas:
                racios[microciclo] = "indisponível"
                continue

            total_microciclo = sum(cargas_validas)

            if i == 1:
                racio = 0
            else:
                media = total_ate_agora / (i - 1)
                racio = round(total_microciclo / media, 2) if media != 0 else "indisponível"

            racios[microciclo] = racio
            total_ate_agora += total_microciclo

        return racios

    def calcular_m_porcento(cargas, chave):
        m_porcento = {}
        carga_anterior = 0
        microciclos = sorted(cargas[jogador].keys())

        for i, microciclo in enumerate(microciclos, start=1):
            total = sum(
                treino[chave]
                for dias in cargas[jogador][microciclo].values()
                for treino in dias
                if treino[chave] is not None
            )

            if i == 1:
                m = 0
            else:
                m = round(((total - carga_anterior) / total) * 100, 2) if total != 0 else 1

            m_porcento[microciclo] = m
            carga_anterior = total

        return m_porcento

    if jogador in carga_interna:
        racio_carga_interna = calcular_racio(carga_interna, "carga_interna")

    if jogador in carga_externa_dt:
        racio_carga_externa_dt = calcular_racio(carga_externa_dt, "distancia_total")
        m_porcento_dt = calcular_m_porcento(carga_externa_dt, "distancia_total")

    if jogador in carga_externa_hs:
        racio_carga_externa_hs = calcular_racio(carga_externa_hs, "distancia_hs")
        m_porcento_hs = calcular_m_porcento(carga_externa_hs, "distancia_hs")

    return racio_carga_interna, racio_carga_externa_dt, m_porcento_dt, racio_carga_externa_hs, m_porcento_hs

def calcular_monotonia_strain(jogador, carga_interna):
    if jogador not in carga_interna:
        return {}, {}

    monotonia_micro = {}
    strain_micro = {}

    for microciclo, dias in carga_interna[jogador].items():
        # Extrair todas as cargas internas do microciclo (de todos os dias)
        cargas = [
            treino["carga_interna"]
            for dia in dias.values()
            for treino in dia
            if treino["carga_interna"] is not None
        ]

        if cargas:
            media = np.mean(cargas)
            desvio_padrao = np.std(cargas, ddof=1)
            monotonia = float(round(media / desvio_padrao, 2)) if desvio_padrao != 0 else 0
            total_carga = sum(cargas)
            strain = float(round(monotonia * total_carga, 2))
        else:
            monotonia = 0
            strain = 0

        monotonia_micro[microciclo] = monotonia
        strain_micro[microciclo] = strain

    return monotonia_micro, strain_micro

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
                    if isinstance(valores[var], (int, float)):  # Verifica se é um número inteiro ou float
                        soma_variaveis[var] += float(valores[var])
                
                except ValueError:
                    soma_variaveis[var] += 0  # Se não for um número válido, considera como 0

        # Verificar se há dias para calcular a média (evitar divisão por zero)
        if total_dias > 0:
            # Calcular a média das variáveis por microciclo
            media_microciclo = np.mean(list(soma_variaveis.values())) / total_dias
            media_wellness[microciclo] = float(round(media_microciclo, 2))  # Arredonda para 2 casas decimais

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

        # Calcular as métricas de carga de treino para o jogador
        racio_carga_interna, racio_carga_externa_dt, _, _, _ = calcular_metricas_carga_treino(jogador)

        # Calcular monotonia e strain para o jogador
        monotonia_micro, strain_micro = calcular_monotonia_strain(jogador, carga_interna)

        # Iterar pelos microciclos para cada jogador
        for microciclo in sorted(carga_interna.get(jogador, {}).keys()):
            dados[jogador][microciclo] = {
                "ACWR PSE": racio_carga_interna.get(microciclo, 0),
                "ACWR DT": racio_carga_externa_dt.get(microciclo, 0),
                "Wellness": media_wellness.get(microciclo, 0),
                "Monotonia": monotonia_micro.get(microciclo, 0),
                "Strain": strain_micro.get(microciclo, 0),
            }

    print(dados)  # imprime tudo o que foi gerado

    return dados

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
                        try:
                            valor = float(valor)
                            if not np.isnan(valor):
                                valores.append(valor)
                        except (ValueError, TypeError):
                            continue  # Ignora valores inválidos

                # Calcular média e desvio padrão
                if valores:
                    media = np.nanmean(valores)
                    desvio_padrao = np.nanstd(valores, ddof=1)  # ddof=1 para desvio padrão amostral
                else:
                    media = 0
                    desvio_padrao = 1  # Se não há valores, evitamos a divisão por 0

                # Calcular o Z-score apenas se o jogador tem esse valor
                if microciclo in dados[jogador] and variavel in dados[jogador][microciclo]:
                    try:
                        valor = float(dados[jogador][microciclo][variavel])
                        z_score = round((valor - media) / desvio_padrao, 2) if desvio_padrao != 0 and not np.isnan(valor) else 0
                    except (ValueError, TypeError):
                        z_score = 0
                        
                    z_scores[jogador][microciclo][variavel] = z_score

    return z_scores

def get_z_score(jogador, microciclo, variavel):

    dados = criar_dados()
    z_scores = calcular_z_score(dados)

    # Verifica se o jogador, microciclo e variável existem nos Z-scores calculados
    if jogador not in z_scores or microciclo not in z_scores[jogador]:
        return jsonify({"erro": "Jogador ou microciclo não encontrado"}), 404
    
    # Busca o Z-score para a variável no microciclo do jogador
    z_score = z_scores[jogador][microciclo].get(variavel, None)

    if z_score is None:
        return jsonify({"erro": "Variável não encontrada para o microciclo"}), 404
    
    return jsonify({
        "jogador": jogador,
        "microciclo": microciclo,
        "variavel": variavel,
        "z_score": z_score
    })

@app.route('/api/users')
def get_user_data():
    try: 
        data = {'key': 'value'}
        response = jsonify(data)
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

def decode_nome(nome):
    return unquote(nome)


# Rota para buscar jogadores
@app.route('/api/jogadores', methods=['GET'])
def get_jogadores():
    try:
        _, jogadores_unicos = carregar_dados_wellness()  # Carregar os dados atualizados
        return jsonify(jogadores_unicos)
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


# Rota para buscar microciclos
@app.route('/api/microciclos', methods=['GET'])
def get_microciclos():
    try: 
        # Carregar os dados do Google Sheets ou do arquivo Excel
        dados_wellness, _ = carregar_dados_wellness()

        # Obter todos os microciclos únicos dos jogadores
        microciclos = set()

        for jogador in dados_wellness:
            microciclos.update(dados_wellness[jogador].keys())

        # Ordenar os microciclos numericamente
        microciclos = sorted(microciclos, key=int)

        return jsonify(microciclos)
        
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
        

# Rota para buscar os dados wellness
@app.route('/api/wellness/<jogador>/<int:microciclo>', methods=['GET'])
def get_wellness(jogador, microciclo):
    try:
        jogador = decode_nome(jogador)
        dados_wellness, _= carregar_dados_wellness()

        if jogador in dados_wellness and microciclo in dados_wellness[jogador]:
            return jsonify(dados_wellness[jogador][microciclo])
        else:
            return jsonify({"erro": "Jogador ou Microciclo não encontrado"}), 404
    
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
        

# Rota para buscar os dados da PSE de um jogador e microciclo específico
@app.route('/api/pse/<jogador>/<int:microciclo>', methods=['GET'])
def get_pse(jogador, microciclo):
    try:
        jogador = decode_nome(jogador)
        dados_pse, _, _, _ = carregar_dados_pse_carga_treino()

        if jogador in dados_pse and microciclo in dados_pse[jogador]:
            return jsonify(dados_pse[jogador][microciclo])
        else:
            return jsonify({"erro": "Jogador ou Microciclo não encontrado"}), 404
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
        

# Rota para buscar os dados da Carga Interna de um jogador e microciclo específico
@app.route('/api/carga_interna/<jogador>/<int:microciclo>', methods=['GET'])
def get_carga_interna(jogador, microciclo):
    try:
        jogador = decode_nome(jogador)
        _, carga_interna, _, _ = carregar_dados_pse_carga_treino()

        if jogador in carga_interna and microciclo in carga_interna[jogador]:
            return jsonify(carga_interna[jogador][microciclo])
        else:
            return jsonify({"erro": "Jogador ou Microciclo não encontrado"}), 404
    
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

# Rota para buscar o rácio carga aguda/crónica para a Carga Interna de um jogador
@app.route('/api/racio/<jogador>')
def get_racio(jogador):
    try:
        jogador = decode_nome(jogador)
        racio_carga_interna, _, _, _, _ = calcular_metricas_carga_treino(jogador)

        if racio_carga_interna:
            return jsonify(racio_carga_interna)
        else:
            return jsonify({"erro": "Jogador não encontrado ou sem dados"}), 404

    except Exception as e:
        return jsonify({"erro": str(e)}), 500
        
    
# Rota para buscar os dados da Carga Externa em DT de um jogador e microciclo específico
@app.route('/api/carga_externa_dt/<jogador>/<int:microciclo>')
def get_carga_externa_dt(jogador, microciclo):
    try:
        jogador = decode_nome(jogador)
        _, _, carga_externa_dt, _ = carregar_dados_pse_carga_treino()
        if jogador in carga_externa_dt and microciclo in carga_externa_dt[jogador]:
            return jsonify(carga_externa_dt[jogador][microciclo])
        else:
            return jsonify({"erro": "Jogador ou Microciclo não encontrado"}), 404

    except Exception as e:
        return jsonify({"erro": str(e)}), 500
        
    
# Rota para buscar o rácio carga aguda/crónica para a Carga Externa DT de um jogador
@app.route('/api/racio_dt/<jogador>')
def get_racio_dt(jogador):
    try:
        jogador = decode_nome(jogador)
        _, racio_carga_externa_dt, _, _, _ = calcular_metricas_carga_treino(jogador)

        if racio_carga_externa_dt:
            return jsonify(racio_carga_externa_dt)
        else:
            return jsonify({"erro": "Jogador não encontrado ou sem dados"}), 404

    except Exception as e:
        return jsonify({"erro": str(e)}), 500
        
    
# Rota para buscar o M% para a Carga Externa DT de um jogador
@app.route('/api/m_dt/<jogador>')
def get_m_dt(jogador):
    try:
        jogador = decode_nome(jogador)
        _, _, m_porcento_dt, _, _ = calcular_metricas_carga_treino(jogador)

        if m_porcento_dt:        
            return jsonify(m_porcento_dt)
        else:
            return jsonify({"erro": "Jogador não encontrado"}), 404 

    except Exception as e:
        return jsonify({"erro": str(e)}), 500
        

# Rota para buscar os dados da Carga Externa em HS de um jogador e microciclo específico
@app.route('/api/carga_externa_hs/<jogador>/<int:microciclo>')
def get_carga_externa_hs(jogador, microciclo):
    try: 
        jogador = decode_nome(jogador)
        _, _, _, carga_externa_hs = carregar_dados_pse_carga_treino()
        if jogador in carga_externa_hs and microciclo in carga_externa_hs[jogador]:
            return jsonify(carga_externa_hs[jogador][microciclo])
        else:
            return jsonify({"erro": "Jogador ou Microciclo não encontrado"}), 404

    except Exception as e:
        return jsonify({"erro": str(e)}), 500
        
    
# Rota para buscar o rácio carga aguda/crónica para a Carga Externa HS de um jogador
@app.route('/api/racio_hs/<jogador>')
def get_racio_hs(jogador):
    try: 
        jogador = decode_nome(jogador)
        _, _, _, racio_carga_externa_hs, _ = calcular_metricas_carga_treino(jogador)

        if racio_carga_externa_hs:
            return jsonify(racio_carga_externa_hs)
        else:
            return jsonify({"erro": "Jogador não encontrado ou sem dados"}), 404

    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    
# Rota para buscar o M% para a Carga Externa DT de um jogador
@app.route('/api/m_hs/<jogador>')
def get_m_hs(jogador):
    try: 
        jogador = decode_nome(jogador)
        _, _, _, _, m_porcento_hs = calcular_metricas_carga_treino(jogador)

        if m_porcento_hs:        
            return jsonify(m_porcento_hs)
        else:
            return jsonify({"erro": "Jogador não encontrado"}), 404

    except Exception as e:
        return jsonify({"erro": str(e)}), 500
        
    
# Rota para buscar os dados da Carga Interna de um jogador e microciclo específico
@app.route('/api/monotonia/<jogador>')
def get_monotonia(jogador):
    try: 
        jogador = decode_nome(jogador)
        _, carga_interna, _, _ = carregar_dados_pse_carga_treino()  # Carregar os dados da carga interna
        if jogador in carga_interna:
            monotonia_micro, _ = calcular_monotonia_strain(jogador, carga_interna)
            return jsonify(monotonia_micro)
        else:
            return jsonify({"erro": "Jogador não encontrado"}), 404

    except Exception as e:
        return jsonify({"erro": str(e)}), 500
        
    
# Rota para buscar os dados da Strain de um jogador específico
@app.route('/api/strain/<jogador>')
def get_strain(jogador):
    try: 
        jogador = decode_nome(jogador)
        _, carga_interna, _, _ = carregar_dados_pse_carga_treino()  # Carregar os dados da carga interna
        if jogador in carga_interna:
            _, strain_micro = calcular_monotonia_strain(jogador, carga_interna)
            return jsonify(strain_micro)
        else:
            return jsonify({"erro": "Jogador não encontrado"}), 404

    except Exception as e:
        return jsonify({"erro": str(e)}), 500
        
    
@app.route('/api/zscore/acwr_pse/<jogador>/<int:microciclo>', methods=['GET'])
def zscore_acwr_pse(jogador, microciclo):
    try:
        jogador = decode_nome(jogador)
        return get_z_score(jogador, microciclo, "ACWR PSE")
        
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@app.route('/api/zscore/acwr_dt/<jogador>/<int:microciclo>', methods=['GET'])
def zscore_acwr_dt(jogador, microciclo):
    try:
        jogador = decode_nome(jogador)
        return get_z_score(jogador, microciclo, "ACWR DT")

    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    

@app.route('/api/zscore/wellness/<jogador>/<int:microciclo>', methods=['GET'])
def zscore_wellness(jogador, microciclo):
    try:
        jogador = decode_nome(jogador)
        return get_z_score(jogador, microciclo, "Wellness")

    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@app.route('/api/zscore/monotonia/<jogador>/<int:microciclo>', methods=['GET'])
def zscore_monotonia(jogador, microciclo):
    try:
        jogador = decode_nome(jogador)
        return get_z_score(jogador, microciclo, "Monotonia")

    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@app.route('/api/zscore/strain/<jogador>/<int:microciclo>', methods=['GET'])
def zscore_strain(jogador, microciclo):
    try:
        jogador = decode_nome(jogador)
        return get_z_score(jogador, microciclo, "Strain")

    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    
    
# Rota para limpar o cache manualmente
#@app.route('/api/cache/clear', methods=['POST'])
#def clear_cache():
    #cache_dados["dados_pse"] = None
    #cache_dados["timestamp_pse"] = None
    #cache_dados["dados_wellness"] = None
    #cache_dados["timestamp_wellness"] = None
    #return jsonify({"mensagem": "Cache limpo com sucesso."})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Usar a porta definida pelo Render ou 5000 por padrão
    app.run(host="0.0.0.0", port=port)  # O Flask precisa ouvir em "0.0.0.0" no ambiente do Render
