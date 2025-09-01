"""
Conector para Google Sheets API
"""
import os
import pickle
from typing import List, Dict, Any
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from config.settings import GOOGLE_CREDENTIALS_FILE, GOOGLE_TOKEN_FILE, SHEETS_CONFIG


class GoogleSheetsConnector:
    """Classe para conectar e ler dados do Google Sheets"""
    
    # Escopo necessário para acessar Google Sheets
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    
    def __init__(self):
        self.service = None
        self.credentials = None
    
    def authenticate(self) -> bool:
        """
        Autentica com a API do Google Sheets
        Retorna True se autenticação foi bem-sucedida
        """
        try:
            # Verifica se já existe token salvo
            if os.path.exists(GOOGLE_TOKEN_FILE):
                with open(GOOGLE_TOKEN_FILE, 'rb') as token:
                    self.credentials = pickle.load(token)
            
            # Se não há credenciais válidas, solicita autorização
            if not self.credentials or not self.credentials.valid:
                if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                    self.credentials.refresh(Request())
                else:
                    if not os.path.exists(GOOGLE_CREDENTIALS_FILE):
                        raise FileNotFoundError(
                            f"Arquivo de credenciais não encontrado: {GOOGLE_CREDENTIALS_FILE}\n"
                            "Baixe o arquivo credentials.json do Google Cloud Console"
                        )
                    
                    flow = InstalledAppFlow.from_client_secrets_file(
                        GOOGLE_CREDENTIALS_FILE, self.SCOPES)
                    self.credentials = flow.run_local_server(port=0)
                
                # Salva as credenciais para próximas execuções
                with open(GOOGLE_TOKEN_FILE, 'wb') as token:
                    pickle.dump(self.credentials, token)
            
            # Cria o serviço
            self.service = build('sheets', 'v4', credentials=self.credentials)
            return True
            
        except Exception as e:
            print(f"Erro na autenticação: {e}")
            return False
    
    def read_sheet_data(self, spreadsheet_id: str, range_name: str) -> List[List[str]]:
        """
        Lê dados de uma planilha específica
        
        Args:
            spreadsheet_id: ID da planilha (da URL)
            range_name: Range a ser lido (ex: 'Sheet1!A1:Z100')
        
        Returns:
            Lista de listas com os dados
        """
        try:
            if not self.service:
                raise Exception("Serviço não inicializado. Execute authenticate() primeiro.")
            
            sheet = self.service.spreadsheets()
            result = sheet.values().get(
                spreadsheetId=spreadsheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            return values
            
        except HttpError as e:
            print(f"Erro ao ler planilha: {e}")
            return []
    
    def get_products_data(self, spreadsheet_id: str, sheet_name: str = "Sheet1") -> List[Dict[str, Any]]:
        """
        Lê dados de produtos da planilha e retorna em formato estruturado
        
        Args:
            spreadsheet_id: ID da planilha
            sheet_name: Nome da aba
        
        Returns:
            Lista de dicionários com dados dos produtos
        """
        try:
            # Lê todos os dados da planilha
            range_name = f"{sheet_name}!A1:Z1000"  # Ajuste conforme necessário
            raw_data = self.read_sheet_data(spreadsheet_id, range_name)
            
            if not raw_data:
                return []
            
            # Primeira linha são os cabeçalhos
            headers = raw_data[0]
            products = []
            
            # Processa cada linha de dados
            for row in raw_data[1:]:
                if not row:  # Pula linhas vazias
                    continue
                
                # Cria dicionário do produto
                product = {}
                for i, header in enumerate(headers):
                    value = row[i] if i < len(row) else ""
                    product[header] = value
                
                # Valida se tem dados mínimos
                if product.get(SHEETS_CONFIG["columns"]["name"]):
                    products.append(product)
            
            return products
            
        except Exception as e:
            print(f"Erro ao processar dados dos produtos: {e}")
            return []