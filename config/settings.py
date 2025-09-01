"""
Configurações do Catalog Builder
"""
import os
from pathlib import Path

# Diretórios do projeto
PROJECT_ROOT = Path(__file__).parent.parent
SRC_DIR = PROJECT_ROOT / "src"
CONFIG_DIR = PROJECT_ROOT / "config"
OUTPUT_DIR = PROJECT_ROOT / "output"
TEMP_DIR = PROJECT_ROOT / "temp"

# Configurações do Google Sheets
GOOGLE_CREDENTIALS_FILE = CONFIG_DIR / "credentials.json"
GOOGLE_TOKEN_FILE = CONFIG_DIR / "token.json"

# Configurações do PDF
PDF_CONFIG = {
    "page_size": "A4",
    "margins": {
        "top": 50,
        "bottom": 50,
        "left": 50,
        "right": 50
    },
    "grid": {
        "columns": 2,
        "rows_per_page": 4,
        "spacing": 20
    },
    "image": {
        "max_width": 200,
        "max_height": 200,
        "quality": 85
    }
}

# Configurações de imagem
IMAGE_CONFIG = {
    "download_timeout": 30,
    "max_file_size": 5 * 1024 * 1024,  # 5MB
    "allowed_formats": [".jpg", ".jpeg", ".png", ".webp"],
    "temp_dir": TEMP_DIR
}

# Configurações do Google Sheets (estrutura esperada)
SHEETS_CONFIG = {
    "columns": {
        "name": "Nome",
        "price": "Preço",
        "description": "Descrição",
        "image_url": "URL da Imagem",
        "category": "Categoria",
        "size": "Tamanho",
        "color": "Cor",
        "quantity": "Quantidade"
    }
}