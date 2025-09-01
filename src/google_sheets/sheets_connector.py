"""
Conector para Google Sheets API
"""
import os
import pickle
import json
from typing import List, Dict, Any
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from config.settings import GOOGLE_CREDENTIALS_FILE, GOOGLE_TOKEN_FILE, SHEETS_CONFIG
from src.logger import info, success, error, warning, debug, exception


class GoogleSheetsConnector:
    """Classe para conectar e ler dados do Google Sheets"""
    
    # Escopo necessário para acessar Google Sheets
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    
    def __init__(self):
        self.service = None
        self.credentials = None
    
    def _detect_credentials_type(self) -> str:
        """
        Detecta o tipo de credenciais no arquivo JSON
        
        Returns:
            'service_account' ou 'oauth2'
        """
        try:
            with open(GOOGLE_CREDENTIALS_FILE, 'r') as f:
                creds_data = json.load(f)
                cred_type = creds_data.get('type', 'oauth2')
                debug(f"Tipo de credenciais detectado: {cred_type}")
                return cred_type
        except Exception as e:
            warning(f"Erro ao detectar tipo de credenciais: {e}")
            return 'oauth2'  # Default para OAuth2
    
    def authenticate(self) -> bool:
        """
        Autentica com a API do Google Sheets
        Suporta tanto Service Account quanto OAuth2
        
        Returns:
            True se autenticação foi bem-sucedida
        """
        try:
            if not os.path.exists(GOOGLE_CREDENTIALS_FILE):
                error(f"Arquivo de credenciais não encontrado: {GOOGLE_CREDENTIALS_FILE}")
                error("Baixe o arquivo credentials.json do Google Cloud Console")
                return False
            
            # Detecta o tipo de credenciais
            creds_type = self._detect_credentials_type()
            
            if creds_type == 'service_account':
                return self._authenticate_service_account()
            else:
                return self._authenticate_oauth2()
                
        except Exception as e:
            exception("Erro na autenticação", e)
            return False
    
    def _authenticate_service_account(self) -> bool:
        """
        Autentica usando Service Account
        
        Returns:
            True se autenticação foi bem-sucedida
        """
        try:
            info("Usando Service Account para autenticação")
            
            # Cria credenciais da Service Account
            self.credentials = service_account.Credentials.from_service_account_file(
                GOOGLE_CREDENTIALS_FILE, 
                scopes=self.SCOPES
            )
            
            # Cria o serviço
            self.service = build('sheets', 'v4', credentials=self.credentials)
            
            success("Autenticação com Service Account bem-sucedida")
            return True
            
        except Exception as e:
            exception("Erro na autenticação da Service Account", e)
            return False
    
    def _authenticate_oauth2(self) -> bool:
        """
        Autentica usando OAuth2 (aplicação instalada)
        
        Returns:
            True se autenticação foi bem-sucedida
        """
        try:
            info("Usando OAuth2 para autenticação")
            
            # Verifica se já existe token salvo
            if os.path.exists(GOOGLE_TOKEN_FILE):
                debug(f"Token encontrado: {GOOGLE_TOKEN_FILE}")
                with open(GOOGLE_TOKEN_FILE, 'rb') as token:
                    self.credentials = pickle.load(token)
            
            # Se não há credenciais válidas, solicita autorização
            if not self.credentials or not self.credentials.valid:
                if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                    info("Token expirado, renovando...")
                    self.credentials.refresh(Request())
                else:
                    info("Solicitando autorização no navegador...")
                    flow = InstalledAppFlow.from_client_secrets_file(
                        GOOGLE_CREDENTIALS_FILE, self.SCOPES)
                    self.credentials = flow.run_local_server(port=0)
                
                # Salva as credenciais para próximas execuções
                debug(f"Salvando token: {GOOGLE_TOKEN_FILE}")
                with open(GOOGLE_TOKEN_FILE, 'wb') as token:
                    pickle.dump(self.credentials, token)
            
            # Cria o serviço
            self.service = build('sheets', 'v4', credentials=self.credentials)
            
            success("Autenticação OAuth2 bem-sucedida")
            return True
            
        except Exception as e:
            exception("Erro na autenticação OAuth2", e)
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
                error("Serviço não inicializado. Execute authenticate() primeiro.")
                return []
            
            debug(f"Lendo dados: {spreadsheet_id} - {range_name}")
            sheet = self.service.spreadsheets()
            result = sheet.values().get(
                spreadsheetId=spreadsheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            info(f"Dados lidos: {len(values)} linhas")
            return values
            
        except HttpError as e:
            error(f"Erro HTTP ao ler planilha: {e}")
            return []
        except Exception as e:
            exception("Erro inesperado ao ler planilha", e)
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
            info(f"Buscando dados da planilha: {spreadsheet_id}")
            info(f"Aba: {sheet_name}")
            
            # Lê todos os dados da planilha
            range_name = f"{sheet_name}!A1:Z1000"  # Ajuste conforme necessário
            raw_data = self.read_sheet_data(spreadsheet_id, range_name)
            
            if not raw_data:
                warning("Nenhum dado encontrado na planilha")
                return []
            
            # Primeira linha são os cabeçalhos
            headers = raw_data[0]
            debug(f"Cabeçalhos encontrados: {headers}")
            
            products = []
            
            # Processa cada linha de dados
            for i, row in enumerate(raw_data[1:], 1):
                if not row:  # Pula linhas vazias
                    continue
                
                # Cria dicionário do produto
                product = {}
                for j, header in enumerate(headers):
                    value = row[j] if j < len(row) else ""
                    product[header] = value
                
                # Valida se tem dados mínimos
                if product.get(SHEETS_CONFIG["columns"]["name"]):
                    products.append(product)
                    debug(f"Produto {i}: {product.get(SHEETS_CONFIG['columns']['name'])}")
                else:
                    warning(f"Linha {i} ignorada - sem nome do produto")
            
            info(f"Total de produtos processados: {len(products)}")
            return products
            
        except Exception as e:
            exception("Erro ao processar dados dos produtos", e)
            return []

    def list_sheets(self, spreadsheet_id: str) -> List[str]:
        """
        Lista todas as abas disponíveis na planilha
        
        Args:
            spreadsheet_id: ID da planilha
        
        Returns:
            Lista com nomes das abas
        """
        try:
            if not self.service:
                error("Serviço não inicializado. Execute authenticate() primeiro.")
                return []
            
            debug(f"Listando abas da planilha: {spreadsheet_id}")
            
            # Obtém metadados da planilha
            spreadsheet = self.service.spreadsheets().get(
                spreadsheetId=spreadsheet_id
            ).execute()
            
            sheets = spreadsheet.get('sheets', [])
            sheet_names = []
            
            for sheet in sheets:
                sheet_name = sheet.get('properties', {}).get('title', '')
                sheet_names.append(sheet_name)
                debug(f"Aba encontrada: '{sheet_name}'")
            
            info(f"Total de abas encontradas: {len(sheet_names)}")
            info(f"Abas disponíveis: {sheet_names}")
            
            return sheet_names
            
        except HttpError as e:
            error(f"Erro HTTP ao listar abas: {e}")
            return []
        except Exception as e:
            exception("Erro inesperado ao listar abas", e)
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
            info(f"Buscando dados da planilha: {spreadsheet_id}")
            info(f"Aba solicitada: '{sheet_name}'")
            
            # Primeiro, lista todas as abas disponíveis
            available_sheets = self.list_sheets(spreadsheet_id)
            
            if not available_sheets:
                error("Nenhuma aba encontrada na planilha")
                return []
            
            # Verifica se a aba solicitada existe
            if sheet_name not in available_sheets:
                warning(f"Aba '{sheet_name}' não encontrada!")
                warning(f"Abas disponíveis: {available_sheets}")
                
                # Sugere a primeira aba como alternativa
                if available_sheets:
                    suggested_sheet = available_sheets[0]
                    warning(f"Usando primeira aba disponível: '{suggested_sheet}'")
                    sheet_name = suggested_sheet
            
            # Lê todos os dados da planilha
            range_name = f"{sheet_name}!A1:Z1000"  # Ajuste conforme necessário
            raw_data = self.read_sheet_data(spreadsheet_id, range_name)
            
            if not raw_data:
                warning(f"Nenhum dado encontrado na aba '{sheet_name}'")
                return []
            
            # Primeira linha são os cabeçalhos
            headers = raw_data[0]
            debug(f"Cabeçalhos encontrados: {headers}")
            
            products = []
            
            # Processa cada linha de dados
            for i, row in enumerate(raw_data[1:], 1):
                if not row:  # Pula linhas vazias
                    continue
                
                # Cria dicionário do produto
                product = {}
                for j, header in enumerate(headers):
                    value = row[j] if j < len(row) else ""
                    product[header] = value
                
                # Valida se tem dados mínimos
                if product.get(SHEETS_CONFIG["columns"]["name"]):
                    products.append(product)
                    debug(f"Produto {i}: {product.get(SHEETS_CONFIG['columns']['name'])}")
                else:
                    warning(f"Linha {i} ignorada - sem nome do produto")
            
            info(f"Total de produtos processados: {len(products)}")
            return products
            
        except Exception as e:
            exception("Erro ao processar dados dos produtos", e)
            return []

            # Processa cada linha de dados
            for i, row in enumerate(raw_data[1:], 1):
                debug(f"Processando linha {i}: {row}")
                
                if not row:  # Pula linhas vazias
                    debug(f"Linha {i} está vazia, pulando...")
                    continue
                
                # Cria dicionário do produto
                product = {}
                for j, header in enumerate(headers):
                    value = row[j] if j < len(row) else ""
                    product[header] = value
                
                debug(f"Produto {i} criado: {product}")
                
                # Valida se tem dados mínimos
                product_name = product.get(SHEETS_CONFIG["columns"]["name"])
                if product_name and product_name.strip():
                    products.append(product)
                    debug(f"Produto {i} adicionado: {product_name}")
                else:
                    warning(f"Linha {i} ignorada - sem nome do produto válido")
                    debug(f"Nome encontrado: '{product_name}' (tipo: {type(product_name)})")
