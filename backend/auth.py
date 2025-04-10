from __future__ import print_function
from googleapiclient.discovery import build
from google.oauth2 import service_account
import os

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

# Função para obter as credenciais da conta de serviço a partir das variáveis de ambiente
def obter_credenciais():
    # Obtém as variáveis de ambiente que foram configuradas no Render
    google_project_id = os.getenv('GOOGLE_PROJECT_ID')
    google_private_key_id = os.getenv('GOOGLE_PRIVATE_KEY_ID')
    google_private_key = os.getenv('GOOGLE_PRIVATE_KEY').replace('\\n', '\n')  # Corrige a quebra de linha
    google_client_email = os.getenv('GOOGLE_CLIENT_EMAIL')
    google_client_id = os.getenv('GOOGLE_CLIENT_ID')
    google_auth_uri = os.getenv('GOOGLE_AUTH_URI')
    google_token_uri = os.getenv('GOOGLE_TOKEN_URI')
    google_auth_provider_cert_url = os.getenv('GOOGLE_AUTH_PROVIDER_CERT_URL')
    google_client_x509_cert_url = os.getenv('GOOGLE_CLIENT_X509_CERT_URL')

    # Define o payload da credencial
    credentials_info = {
        'type': 'service_account',
        'project_id': google_project_id,
        'private_key_id': google_private_key_id,
        'private_key': google_private_key,
        'client_email': google_client_email,
        'client_id': google_client_id,
        'auth_uri': google_auth_uri,
        'token_uri': google_token_uri,
        'auth_provider_x509_cert_url': google_auth_provider_cert_url,
        'client_x509_cert_url': google_client_x509_cert_url,
    }

    # Cria as credenciais usando as variáveis de ambiente
    credentials = service_account.Credentials.from_service_account_info(credentials_info)

    return credentials

# Use a função para obter as credenciais
credentials = obter_credenciais()

# Construa os serviços da API usando as credenciais obtidas
spreadsheet_service = build('sheets', 'v4', credentials=credentials)
drive_service = build('drive', 'v3', credentials=credentials)

