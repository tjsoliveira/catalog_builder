#!/usr/bin/env python3
"""
Script para gerar catálogos com todos os esquemas de cores disponíveis
"""
import os
import sys
from pathlib import Path

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

from main import CatalogBuilder
from config.settings import OUTPUT_DIR
from src.logger import info, success, error

def generate_catalogs_for_all_schemes():
    """Gera catálogos para todos os esquemas de cores disponíveis"""
    
    # Esquemas disponíveis
    schemes = ["default", "dark_mode", "minimal"]
    
    # Configuração básica (você pode ajustar conforme necessário)
    config = {
        'spreadsheet_id': os.getenv('SPREADSHEET_ID'),
        'sheet_name': os.getenv('SHEET_NAME', 'Sheet1'),
        'catalog_type': 'html',
        'download_images': True,
        'template_name': 'catalogo_simples.html'
    }
    
    if not config['spreadsheet_id']:
        error("SPREADSHEET_ID não configurado. Configure no arquivo .env")
        return False
    
    # Cria instância do Catalog Builder
    builder = CatalogBuilder()
    
    success_count = 0
    
    for scheme in schemes:
        try:
            info(f"Gerando catálogo com esquema: {scheme}")
            
            # Nome do arquivo de saída
            output_filename = f"catalogo_{scheme}.pdf"
            
            # Executa processo completo
            success_flag = builder.run_full_process(
                spreadsheet_id=config['spreadsheet_id'],
                sheet_name=config['sheet_name'],
                output_filename=output_filename,
                catalog_type=config['catalog_type'],
                download_images=config['download_images'],
                template_name=config['template_name'],
                color_scheme=scheme
            )
            
            if success_flag:
                success(f"✅ Catálogo '{output_filename}' gerado com sucesso!")
                success_count += 1
            else:
                error(f"❌ Erro ao gerar catálogo '{output_filename}'")
                
        except Exception as e:
            error(f"❌ Erro ao gerar catálogo com esquema '{scheme}': {e}")
    
    
    if success_count > 0:
        info(f"\n📁 Catálogos gerados em: {OUTPUT_DIR}")
        for scheme in schemes:
            output_file = OUTPUT_DIR / f"catalogo_{scheme}.pdf"
            if output_file.exists():
                info(f"   - catalogo_{scheme}.pdf")
    
    return success_count == len(schemes)

if __name__ == "__main__":
    success_flag = generate_catalogs_for_all_schemes()
    sys.exit(0 if success_flag else 1)
