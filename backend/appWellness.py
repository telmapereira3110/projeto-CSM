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

def carregar_dados_wellness():
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

        return dados_wellness, jogadores_unicos

    except HttpError as error:
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

    # Garantir que o microciclo é tratado como string para manter o formato original
    #microciclo = f"microciclo_{microciclo}"

    if jogador in dados_wellness and microciclo in dados_wellness[jogador]:
        return jsonify(dados_wellness[jogador][microciclo])
    else:
        return jsonify({"erro": "Jogador ou Microciclo não encontrado"}), 404

if __name__ == '__main__':
    app.run(debug=False, use_reloader=False)