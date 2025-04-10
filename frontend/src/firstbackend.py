from flask import Flask, jsonify
from flask_cors import CORS
import random
import numpy as np

app = Flask(__name__)
CORS(app) # Permite que o React acesse a API


# Simular Jogadores (mais tarde é para pegar do banco de dados)
jogadores = ["Telma Pereira", "Inês Freitas", "Diana Freitas", "Shelby"]

# Dias da semana
dias_semana = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]

# Duração fixa do treino em minutos
DURACAO_TREINO = 90

# Criar dados aleatórios do Wellness para 8 microciclos (semanas)
questionario = {}

for jogador in jogadores:
    questionario[jogador] = {}  # Criar um dicionário para cada jogador
    for i in range(1, 9):  # Criar 8 microciclos (semanas)
        microciclo = f"microciclo_{i}"
        questionario[jogador][microciclo] = {}
        for dia in dias_semana:
            questionario[jogador][microciclo][dia] = {
                "sono": random.randint(1, 7),  # Sono entre 1 e 7
                "fadiga": random.randint(1, 7),  # Fadiga de 1 a 7
                "dor_muscular": random.randint(1, 7),  # Dor muscular de 1 a 7
                "stress": random.randint(1, 7),  # Stress de 1 a 7
            }


# Criar dados aleatórios da PSE para 8 microciclos (semanas)
pse = {}

for jogador in jogadores:
    pse[jogador] = {} 
    for i in range(1, 9):  # Criar 8 microciclos (semanas)
        microciclo = f"microciclo_{i}"
        pse[jogador][microciclo] = {}
        for dia in dias_semana:
            pse[jogador][microciclo][dia] = {
                "PSE": random.randint(1,10) # PSE aleatório entre 1 e 10,
            }

# Dicionário Carga Interna
carga_interna = {}

for jogador in jogadores:
    carga_interna[jogador] = {} 
    for i in range(1, 9):  # Criar 8 microciclos (semanas)
        microciclo = f"microciclo_{i}"
        carga_interna[jogador][microciclo] = {}
        for dia in dias_semana:
            valor_pse = pse[jogador][microciclo][dia]["PSE"]
            carga_interna[jogador][microciclo][dia] = {
                "Carga_Interna": valor_pse * DURACAO_TREINO 
            }

# Calcular o Rácio Carga Aguda/Crónica para a Carga Interna
def calcular_racio(jogador):
    racios = {}  # Dicionário para armazenar os rácios de cada microciclo
    total_carga_ate_agora = 0  # Variável para armazenar o total de carga acumulada até o momento
    for i in range(1, 9):  # Para cada microciclo
        microciclo = f"microciclo_{i}"
        total_carga_microciclo = 0

        if i == 1:
            racio = 0
            for dia in dias_semana:
                total_carga_microciclo += carga_interna[jogador][microciclo][dia]["Carga_Interna"]
            
            total_carga_ate_agora = total_carga_microciclo
        
        else:

            # Soma a carga interna de todos os dias do microciclo
            for dia in dias_semana:
                total_carga_microciclo += carga_interna[jogador][microciclo][dia]["Carga_Interna"]
            
            # Atualiza o total acumulado de carga até o microciclo atual
            total_carga_ate_agora += total_carga_microciclo
        
            # Média acumulada até o microciclo atual
            media_acumulada = total_carga_ate_agora / i  
        
            # Rácio carga aguda/crónica (carga do microciclo atual / média acumulada)
            racio = round(total_carga_microciclo / media_acumulada, 2) if media_acumulada != 0 else 1
                     
            racios[microciclo] = racio

    return racios

# Dicionário Carga Externa DT
carga_externa_dt = {}

for jogador in jogadores:
    carga_externa_dt[jogador] = {} 
    for i in range(1, 9):  # Criar 8 microciclos (semanas)
        microciclo = f"microciclo_{i}"
        carga_externa_dt[jogador][microciclo] = {}
        for dia in dias_semana:
            carga_externa_dt[jogador][microciclo][dia] = {
                "Carga_Externa_DT": random.randint(8000, 15000),
            }

# Calcular o Rácio Carga Aguda/Crónica para a Carga Externa DT
def calcular_racio_dt(jogador):
    racios_dt = {}  # Dicionário para armazenar os rácios de cada microciclo
    total_carga_externa_dt_ate_agora = 0  # Variável para armazenar o total de carga acumulada até o momento
    for i in range(1, 9):  # Para cada microciclo
        microciclo = f"microciclo_{i}"
        total_carga_externa_dt_microciclo = 0

        if i == 1:
            racio_dt = 0
            for dia in dias_semana:
                total_carga_externa_dt_microciclo += carga_externa_dt[jogador][microciclo][dia]["Carga_Externa_DT"]
            
            total_carga_externa_dt_ate_agora = total_carga_externa_dt_microciclo
        
        else:

            # Soma a carga interna de todos os dias do microciclo
            for dia in dias_semana:
                total_carga_externa_dt_microciclo += carga_externa_dt[jogador][microciclo][dia]["Carga_Externa_DT"]
            
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
    m_dt = {}  # Dicionário para armazenar os rácios de cada microciclo
    carga_externa_dt_anterior = 0  # Variável para armazenar o total de carga da semana anterior
    for i in range(1, 9):  # Para cada microciclo
        microciclo = f"microciclo_{i}"
        total_carga_externa_dt_microciclo = 0
        

        if i == 1:
            valor_m_dt = 0
            for dia in dias_semana:
                total_carga_externa_dt_microciclo += carga_externa_dt[jogador][microciclo][dia]["Carga_Externa_DT"]
            
                    
        else:

            # Soma a carga interna de todos os dias do microciclo
            for dia in dias_semana:
                total_carga_externa_dt_microciclo += carga_externa_dt[jogador][microciclo][dia]["Carga_Externa_DT"]
                         
            # M% (carga do microciclo atual / média acumulada)
            valor_m_dt = round(((total_carga_externa_dt_microciclo - carga_externa_dt_anterior )/ total_carga_externa_dt_microciclo) * 100, 2) if total_carga_externa_dt_microciclo != 0 else 1
                     
        m_dt[microciclo] = valor_m_dt
        
        carga_externa_dt_anterior = total_carga_externa_dt_microciclo

    return m_dt

# Dicionário Carga Externa HS
carga_externa_hs = {}

for jogador in jogadores:
    carga_externa_hs[jogador] = {} 
    for i in range(1, 9):  # Criar 8 microciclos (semanas)
        microciclo = f"microciclo_{i}"
        carga_externa_hs[jogador][microciclo] = {}
        for dia in dias_semana:
            carga_externa_hs[jogador][microciclo][dia] = {
                "Carga_Externa_HS": random.randint(900, 1500),
            }

# Calcular o Rácio Carga Aguda/Crónica para a Carga Externa HS
def calcular_racio_hs(jogador):
    racios_hs = {}  # Dicionário para armazenar os rácios de cada microciclo
    total_carga_externa_hs_ate_agora = 0  # Variável para armazenar o total de carga acumulada até o momento
    for i in range(1, 9):  # Para cada microciclo
        microciclo = f"microciclo_{i}"
        total_carga_externa_hs_microciclo = 0

        if i == 1:
            racio_hs = 0
            for dia in dias_semana:
                total_carga_externa_hs_microciclo += carga_externa_hs[jogador][microciclo][dia]["Carga_Externa_HS"]
            
            total_carga_externa_hs_ate_agora = total_carga_externa_hs_microciclo
        
        else:

            # Soma a carga externa hs de todos os dias do microciclo
            for dia in dias_semana:
                total_carga_externa_hs_microciclo += carga_externa_hs[jogador][microciclo][dia]["Carga_Externa_HS"]
            
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
    m_hs = {}  # Dicionário para armazenar os rácios de cada microciclo
    carga_externa_hs_anterior = 0  # Variável para armazenar o total de carga da semana anterior
    for i in range(1, 9):  # Para cada microciclo
        microciclo = f"microciclo_{i}"
        total_carga_externa_hs_microciclo = 0

        if i == 1:
            valor_m_hs = 0
            for dia in dias_semana:
                total_carga_externa_hs_microciclo += carga_externa_hs[jogador][microciclo][dia]["Carga_Externa_HS"]
            
                    
        else:

            # Soma a carga interna de todos os dias do microciclo
            for dia in dias_semana:
                total_carga_externa_hs_microciclo += carga_externa_hs[jogador][microciclo][dia]["Carga_Externa_HS"]
                         
            # M% (carga do microciclo atual / média acumulada)
            valor_m_hs = round(((total_carga_externa_hs_microciclo - carga_externa_hs_anterior )/ total_carga_externa_hs_microciclo) * 100, 2) if total_carga_externa_hs_microciclo != 0 else 1
                     
        m_hs[microciclo] = valor_m_hs
        
        carga_externa_hs_anterior = total_carga_externa_hs_microciclo

    return m_hs

# Calcular a Monotonia
def calcular_monotonia(jogador, carga_interna, dias_semana):
    monotonia_micro = {} # Dicionário para armazenar a monotonia de cada microciclo
    for i in range(1, 9):  # Para cada microciclo
        microciclo = f"microciclo_{i}"
        total_carga_microciclo = []

        for dia in dias_semana:
            # Lista com os valores de carga interna dos dias do microciclo
            if microciclo in carga_interna.get(jogador, {}) and dia in carga_interna[jogador][microciclo]:
                total_carga_microciclo.append(carga_interna[jogador][microciclo][dia]["Carga_Interna"])

        # Calcula média e desvio padrão
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
def calcular_strain(jogador, carga_interna, dias_semana, monotonia_micro):
    strain_micro = {}

    for i in range(1, 9):  # Para cada microciclo
        microciclo = f"microciclo_{i}"
        total_carga_microciclo = []  # Lista para armazenar os valores de carga interna

        for dia in dias_semana:
            # Verifica se o microciclo e o dia existem antes de acessar os dados
            if microciclo in carga_interna.get(jogador, {}) and dia in carga_interna[jogador][microciclo]:
                total_carga_microciclo.append(carga_interna[jogador][microciclo][dia]["Carga_Interna"])

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

# Função para calcular a média das variaveis da lista "questionario" e ficar só com um valor para cada microciclo
def calcular_media_wellness(jogador, questionario):
    media_wellness = {}

    if jogador not in questionario:
        return {}

    for microciclo, dias in questionario[jogador].items():
        soma_variaveis = {"sono": 0, "fadiga": 0, "dor_muscular": 0, "stress": 0}
        total_dias = len(dias)

        # Somar todas as variáveis por microciclo
        for valores in dias.values():
            for var in soma_variaveis:
                soma_variaveis[var] += valores[var]

        # Calcular a média das variáveis e a média final do microciclo
        media_microciclo = np.mean(list(soma_variaveis.values())) / total_dias
        media_wellness[microciclo] = round(media_microciclo, 2)  # Arredonda para 2 casas decimais

    return media_wellness

# Criar o dicionário dados ontendo os valores da variável (ex: ACWR PSE, ACWR DT, Wellness, Monotonia, Strain)
dados = {}
for jogador in jogadores:
    dados[jogador] = {}
    racios = calcular_racio(jogador)
    racios_dt = calcular_racio_dt(jogador)
    media_wellness = calcular_media_wellness(jogador, questionario)
    monotonia_micro = calcular_monotonia(jogador, carga_interna, dias_semana)
    strain_micro = calcular_strain(jogador, carga_interna, dias_semana, monotonia_micro)

    for i in range(1,9):
        microciclo = f"microciclo_{i}"

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
        for variavel in variaveis:
            valores = []

            # Coletar valores de todos os jogadores para a variável no microciclo atual
            for jogador in dados:
                if microciclo in dados[jogador] and variavel in dados[jogador][microciclo]:
                    valores.append(dados[jogador][microciclo][variavel])

            # Calcular média e desvio padrão
            if valores:
                media = np.mean(valores)
                desvio_padrao = np.std(valores, ddof=1)  # ddof=1 para desvio padrão amostral
            else:
                continue

            for  jogador in dados:
                if microciclo in dados[jogador] and variavel in dados[jogador][microciclo]:
                    valor = dados[jogador][microciclo][variavel]
                    z_score = round((valor-media)/desvio_padrao, 2) if desvio_padrao != 0 else 0

                    # Guardar o resultado na estrutura correta
                    if microciclo not in z_scores[jogador]:
                        z_scores[jogador][microciclo] = {}
                    z_scores[jogador][microciclo][variavel] = z_score

    return z_scores

# Calcular Z-scores das variáveis
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

# Dicionário CMJ
cmj = {}

for jogador in jogadores:
    cmj[jogador] = {} 
    for i in range(1, 9):  # Criar 8 microciclos (semanas)
        microciclo = f"microciclo_{i}"
        cmj[jogador][microciclo] = {
            "CMJ": random.randint(15, 40),
        }

# Dicionário SJ
sj = {}

for jogador in jogadores:
    sj[jogador] = {} 
    for i in range(1, 9):  # Criar 8 microciclos (semanas)
        microciclo = f"microciclo_{i}"
        sj[jogador][microciclo] = {
            "SJ": random.randint(15, 40),
        }

    
# Rota para buscar jogadores
@app.route('/api/jogadores')
def get_jogadores():
    return jsonify(list(questionario.keys()))

# Rota para buscar os dados do questionário de um jogador e microciclo específico
@app.route('/api/questionario/<jogador>/<microciclo>')
def get_questionario(jogador, microciclo):
    if jogador in questionario and microciclo in questionario[jogador]:
        return jsonify(questionario[jogador][microciclo])
    else:
        return jsonify({"erro": "Jogador ou Microciclo não encontrado"}), 404

# Rota para buscar os dados da PSE de um jogador e microciclo específico
@app.route('/api/pse/<jogador>/<microciclo>')
def get_pse(jogador, microciclo):
    if jogador in pse and microciclo in pse[jogador]:
        return jsonify(pse[jogador][microciclo])
    else:
        return jsonify({"erro": "Jogador ou Microciclo não encontrado"}), 404

# Rota para buscar os dados da Carga Interna de um jogador e microciclo específico
@app.route('/api/carga_interna/<jogador>/<microciclo>')
def get_carga_interna(jogador, microciclo):
    if jogador in carga_interna and microciclo in carga_interna[jogador]:
        return jsonify(carga_interna[jogador][microciclo])
    else:
        return jsonify({"erro": "Jogador ou Microciclo não encontrado"}), 404

# Rota para buscar o rácio carga aguda/crónica para a Carga Interna de um jogador
@app.route('/api/racio/<jogador>')
def get_racio(jogador):
    if jogador in carga_interna:
        racios = calcular_racio(jogador)
        return jsonify(racios)
    else:
        return jsonify({"erro": "Jogador não encontrado"}), 404
    
# Rota para buscar os dados da Carga Externa em DT de um jogador e microciclo específico
@app.route('/api/carga_externa_dt/<jogador>/<microciclo>')
def get_carga_externa_dt(jogador, microciclo):
    if jogador in carga_externa_dt and microciclo in carga_externa_dt[jogador]:
        return jsonify(carga_externa_dt[jogador][microciclo])
    else:
        return jsonify({"erro": "Jogador ou Microciclo não encontrado"}), 404

# Rota para buscar o rácio carga aguda/crónica para a Carga Externa DT de um jogador
@app.route('/api/racio_dt/<jogador>')
def get_racio_dt(jogador):
    if jogador in carga_externa_dt:
        racios_dt = calcular_racio_dt(jogador)
        return jsonify(racios_dt)
    else:
        return jsonify({"erro": "Jogador não encontrado"}), 404
    
# Rota para buscar os dados da Carga Externa em HS de um jogador e microciclo específico
@app.route('/api/carga_externa_hs/<jogador>/<microciclo>')
def get_carga_externa_hs(jogador, microciclo):
    if jogador in carga_externa_hs and microciclo in carga_externa_hs[jogador]:
        return jsonify(carga_externa_hs[jogador][microciclo])
    else:
        return jsonify({"erro": "Jogador ou Microciclo não encontrado"}), 404

# Rota para buscar o rácio carga aguda/crónica para a Carga Externa HS de um jogador
@app.route('/api/racio_hs/<jogador>')
def get_racio_hs(jogador):
    if jogador in carga_externa_hs:
        racios_hs = calcular_racio_hs(jogador)
        return jsonify(racios_hs)
    else:
        return jsonify({"erro": "Jogador não encontrado"}), 404
    
# Rota para buscar o M% para a Carga Externa DT de um jogador
@app.route('/api/m_dt/<jogador>')
def get_m_dt(jogador):
    if jogador in carga_externa_dt:
        m_dt = calcular_m_dt(jogador)
        return jsonify(m_dt)
    else:
        return jsonify({"erro": "Jogador não encontrado"}), 404
    
# Rota para buscar o M% para a Carga Externa HS de um jogador
@app.route('/api/m_hs/<jogador>')
def get_m_hs(jogador):
    if jogador in carga_externa_hs:
        m_hs = calcular_m_hs(jogador)
        return jsonify(m_hs)
    else:
        return jsonify({"erro": "Jogador não encontrado"}), 404
    
# Rota para buscar os dados da Carga Interna de um jogador e microciclo específico
@app.route('/api/monotonia/<jogador>')
def get_monotonia(jogador):
    if jogador in carga_interna:
        monotonia_micro = calcular_monotonia(jogador, carga_interna, dias_semana)
        return jsonify(monotonia_micro)
    else:
        return jsonify({"erro": "Jogador não encontrado"}), 404
    
# Rota para buscar os dados da Strain de um jogador específico
@app.route('/api/strain/<jogador>')
def get_strain(jogador):
    if jogador in carga_interna:
        monotonia_micro = calcular_monotonia(jogador, carga_interna, dias_semana)
        strain_micro = calcular_strain(jogador, carga_interna, dias_semana, monotonia_micro)
        return jsonify(strain_micro)
    else:
        return jsonify({"erro": "Jogador não encontrado"}), 404
    
@app.route('/api/zscore/acwr_pse/<jogador>/<microciclo>', methods=['GET'])
def zscore_acwr_pse(jogador, microciclo):
    return get_z_score(jogador, microciclo, "ACWR PSE")


@app.route('/api/zscore/acwr_dt/<jogador>/<microciclo>', methods=['GET'])
def zscore_acwr_dt(jogador, microciclo):
    return get_z_score(jogador, microciclo, "ACWR DT")


@app.route('/api/zscore/wellness/<jogador>/<microciclo>', methods=['GET'])
def zscore_wellness(jogador, microciclo):
    return get_z_score(jogador, microciclo, "Wellness")


@app.route('/api/zscore/monotonia/<jogador>/<microciclo>', methods=['GET'])
def zscore_monotonia(jogador, microciclo):
    return get_z_score(jogador, microciclo, "Monotonia")


@app.route('/api/zscore/strain/<jogador>/<microciclo>', methods=['GET'])
def zscore_strain(jogador, microciclo):
    return get_z_score(jogador, microciclo, "Strain")

# Rota para buscar os dados do CMJ de um jogador e microciclo específico
@app.route('/api/cmj/<jogador>/<microciclo>')
def get_cmj(jogador, microciclo):
    if jogador in cmj and microciclo in cmj[jogador]:
        return jsonify(cmj[jogador][microciclo])
    else:
        return jsonify({"erro": "Jogador ou Microciclo não encontrado"}), 404
    
# Rota para buscar os dados do SJ de um jogador e microciclo específico
@app.route('/api/sj/<jogador>/<microciclo>')
def get_sj(jogador, microciclo):
    if jogador in sj and microciclo in sj[jogador]:
        return jsonify(sj[jogador][microciclo])
    else:
        return jsonify({"erro": "Jogador ou Microciclo não encontrado"}), 404
    
if __name__ == '__main__':
    app.run(debug=True)