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

# Variáveis globais para o cache
cache_dados = {
    "timestamp": None,
    "dados": None
}

# Tempo de validade do cache (ex: 10 minutos)
CACHE_TTL = timedelta(minutes=10)

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

# Função para carregar dados da PSE, da Carga Interna e da Carga Externa em Distância Total (DT) e em Distância a Alta Velocidade (HS)
def carregar_dados_pse_carga_treino():
    now = datetime.now()

    # Verifica se já temos dados no cache e se estão dentro do TTL
    if cache_dados["dados"] is not None and cache_dados["timestamp"] is not None:
        if now - cache_dados["timestamp"] < CACHE_TTL:
            return cache_dados["dados"]
        
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
            
            hs_total = round(hs_z4 + hs_z5, 2)

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
                'distancia_total': dist_total
            })

            carga_externa_hs[jogador][microciclo][dia_da_semana].append({
                'data_treino': data_str,
                'distancia_hs': hs_total
            })

        # Lista única de jogadores
        jogadores_unicos = list(dados_pse.keys())

        # Atualiza o cache
        #cache_dados["dados"] = (jogadores_unicos, dados_pse, carga_interna, carga_externa_dt, carga_externa_hs)
        #cache_dados["timestamp"] = datetime.now()

        return jogadores_unicos, dados_pse, carga_interna, carga_externa_dt, carga_externa_hs
    
    except HttpError as error:
        # Se o erro não for de cota (429), levanta o erro
        if error.resp.status != 429:
            print(f"Erro ao carregar dados: {error}")
            raise error
        else:
            print("Erro 429: Excedeu o limite de requisições")
            raise


def calcular_metricas_carga_treino(jogador):
    _, _, carga_interna, carga_externa_dt, carga_externa_hs = carregar_dados_pse_carga_treino()

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
                if isinstance(treino, dict) and chave in treino and treino[chave] is not None
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
                for treino in cargas[jogador][microciclo]
                if isinstance(treino, dict) and chave in treino and treino[chave] is not None
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

    print("racio_carga_interna:", racio_carga_interna)

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
            monotonia = round(media / desvio_padrao, 2) if desvio_padrao != 0 else 0
            total_carga = sum(cargas)
            strain = round(monotonia * total_carga, 2)
        else:
            monotonia = 0
            strain = 0

        monotonia_micro[microciclo] = monotonia
        strain_micro[microciclo] = strain

    return monotonia_micro, strain_micro
    

# Rota para buscar jogadores
@app.route('/api/jogadores', methods=['GET'])
def get_jogadores():
    jogadores_unicos, _, _, _, _ = carregar_dados_pse_carga_treino()  # Carregar os dados atualizados
    return jsonify(jogadores_unicos)

# Rota para buscar microciclos
@app.route('/api/microciclos', methods=['GET'])
def get_microciclos():
    # Carregar os dados do Google Sheets ou do arquivo Excel
    _, dados_pse, _, _, _ = carregar_dados_pse_carga_treino()

    # Obter todos os microciclos únicos dos jogadores
    microciclos = set()

    for jogador in dados_pse:
        microciclos.update(dados_pse[jogador].keys())

    # Ordenar os microciclos numericamente
    microciclos = sorted(microciclos, key=int)

    return jsonify(microciclos)

    
# Rota para buscar os dados da PSE de um jogador e microciclo específico
@app.route('/api/pse/<jogador>/<int:microciclo>', methods=['GET'])
def get_pse(jogador, microciclo):
    _, dados_pse, _, _, _ = carregar_dados_pse_carga_treino()

    if jogador in dados_pse and microciclo in dados_pse[jogador]:
        return jsonify(dados_pse[jogador][microciclo])
    else:
        return jsonify({"erro": "Jogador ou Microciclo não encontrado"}), 404
    

# Rota para buscar os dados da Carga Interna de um jogador e microciclo específico
@app.route('/api/carga_interna/<jogador>/<int:microciclo>', methods=['GET'])
def get_carga_interna(jogador, microciclo):
    _, _, carga_interna, _, _ = carregar_dados_pse_carga_treino()

    if jogador in carga_interna and microciclo in carga_interna[jogador]:
        return jsonify(carga_interna[jogador][microciclo])
    else:
        return jsonify({"erro": "Jogador ou Microciclo não encontrado"}), 404
    

# Rota para buscar o rácio carga aguda/crónica para a Carga Interna de um jogador
@app.route('/api/racio/<jogador>')
def get_racio(jogador):
    racio_carga_interna, _, _, _, _ = calcular_metricas_carga_treino(jogador)

    if racio_carga_interna:
        return jsonify(racio_carga_interna)
    else:
        return jsonify({"erro": "Jogador não encontrado ou sem dados"}), 404
    
# Rota para buscar os dados da Carga Externa em DT de um jogador e microciclo específico
@app.route('/api/carga_externa_dt/<jogador>/<int:microciclo>')
def get_carga_externa_dt(jogador, microciclo):
    _, _, _, carga_externa_dt, _ = carregar_dados_pse_carga_treino()
    if jogador in carga_externa_dt and microciclo in carga_externa_dt[jogador]:
        return jsonify(carga_externa_dt[jogador][microciclo])
    else:
        return jsonify({"erro": "Jogador ou Microciclo não encontrado"}), 404
    
# Rota para buscar o rácio carga aguda/crónica para a Carga Externa DT de um jogador
@app.route('/api/racio_dt/<jogador>')
def get_racio_dt(jogador):
    _, racio_carga_externa_dt, _, _, _ = calcular_metricas_carga_treino(jogador)

    if racio_carga_externa_dt:
        return jsonify(racio_carga_externa_dt)
    else:
        return jsonify({"erro": "Jogador não encontrado ou sem dados"}), 404
    
# Rota para buscar o M% para a Carga Externa DT de um jogador
@app.route('/api/m_dt/<jogador>')
def get_m_dt(jogador):
    _, _, m_porcento_dt, _, _ = calcular_metricas_carga_treino(jogador)

    if m_porcento_dt:        
        return jsonify(m_porcento_dt)
    else:
        return jsonify({"erro": "Jogador não encontrado"}), 404  

# Rota para buscar os dados da Carga Externa em HS de um jogador e microciclo específico
@app.route('/api/carga_externa_hs/<jogador>/<int:microciclo>')
def get_carga_externa_hs(jogador, microciclo):
    _, _, _, _, carga_externa_hs = carregar_dados_pse_carga_treino()
    if jogador in carga_externa_hs and microciclo in carga_externa_hs[jogador]:
        return jsonify(carga_externa_hs[jogador][microciclo])
    else:
        return jsonify({"erro": "Jogador ou Microciclo não encontrado"}), 404
    
# Rota para buscar o rácio carga aguda/crónica para a Carga Externa HS de um jogador
@app.route('/api/racio_hs/<jogador>')
def get_racio_hs(jogador):
    _, _, _, racio_carga_externa_hs, _ = calcular_metricas_carga_treino(jogador)

    if racio_carga_externa_hs:
        return jsonify(racio_carga_externa_hs)
    else:
        return jsonify({"erro": "Jogador não encontrado ou sem dados"}), 404
    
# Rota para buscar o M% para a Carga Externa DT de um jogador
@app.route('/api/m_hs/<jogador>')
def get_m_hs(jogador):
    _, _, _, _, m_porcento_hs = calcular_metricas_carga_treino(jogador)

    if m_porcento_hs:        
        return jsonify(m_porcento_hs)
    else:
        return jsonify({"erro": "Jogador não encontrado"}), 404
    
# Rota para buscar os dados da Carga Interna de um jogador e microciclo específico
@app.route('/api/monotonia/<jogador>')
def get_monotonia(jogador):
    _, _, carga_interna, _, _ = carregar_dados_pse_carga_treino()  # Carregar os dados da carga interna
    if jogador in carga_interna:
        monotonia_micro, _ = calcular_monotonia_strain(jogador, carga_interna)
        return jsonify(monotonia_micro)
    else:
        return jsonify({"erro": "Jogador não encontrado"}), 404
    
# Rota para buscar os dados da Strain de um jogador específico
@app.route('/api/strain/<jogador>')
def get_strain(jogador):
    _, _, carga_interna, _, _ = carregar_dados_pse_carga_treino()  # Carregar os dados da carga interna
    if jogador in carga_interna:
        _, strain_micro = calcular_monotonia_strain(jogador, carga_interna)
        return jsonify(strain_micro)
    else:
        return jsonify({"erro": "Jogador não encontrado"}), 404
    
# Rota para limpar o cache manualmente
@app.route('/api/cache/clear', methods=['POST'])
def clear_cache():
    cache_dados["dados"] = None
    cache_dados["timestamp"] = None
    return jsonify({"mensagem": "Cache limpo com sucesso."})

if __name__ == '__main__':
    app.run(debug=True)