#!/usr/bin/env python3
"""
Catalog Builder - Gerador Automático de Catálogo de Roupas
Script principal para gerar catálogo a partir do Google Sheets
"""
import sys
import argparse
import os
from pathlib import Path
from typing import List, Dict, Any
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Adiciona src ao path
sys.path.append(str(Path(__file__).parent / "src"))

from src.google_sheets.sheets_connector import GoogleSheetsConnector
from src.google_sheets.data_processor import DataProcessor
from src.image_processing.image_downloader import ImageDownloader
from src.pdf_generator.pdf_builder import PDFBuilder
from config.settings import OUTPUT_DIR
from src.logger import (
    info, success, error, warning, debug, progress, 
    section, config, stats, exception
)


class CatalogBuilder:
    """Classe principal do Catalog Builder"""
    
    def __init__(self):
        self.sheets_connector = GoogleSheetsConnector()
        self.data_processor = DataProcessor()
        self.image_downloader = ImageDownloader()
        self.pdf_builder = PDFBuilder()
    
    def authenticate_google_sheets(self) -> bool:
        """Autentica com Google Sheets"""
        info("Autenticando com Google Sheets...")
        return self.sheets_connector.authenticate()
    
    def fetch_products_data(self, spreadsheet_id: str, sheet_name: str = "Sheet1") -> List[Dict[str, Any]]:
        """
        Busca dados dos produtos do Google Sheets
        
        Args:
            spreadsheet_id: ID da planilha
            sheet_name: Nome da aba
        
        Returns:
            Lista de produtos processados
        """
        info(f"Buscando dados da planilha: {spreadsheet_id}")
        
        # Busca dados brutos
        raw_products = self.sheets_connector.get_products_data(spreadsheet_id, sheet_name)
        
        if not raw_products:
            error("Nenhum produto encontrado na planilha")
            return []
        
        info(f"Encontrados {len(raw_products)} produtos na planilha")
        
        # Processa dados
        processed_products = self.data_processor.process_products(raw_products)
        
        if not processed_products:
            error("Nenhum produto válido após processamento")
            return []
        
        success(f"{len(processed_products)} produtos válidos processados")
        
        # Mostra estatísticas
        stats_data = self.data_processor.get_statistics(processed_products)
        self._print_statistics(stats_data)
        
        return processed_products
    
    def download_product_images(self, products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Baixa imagens dos produtos
        
        Args:
            products: Lista de produtos
        
        Returns:
            Lista de produtos com imagens baixadas
        """
        progress("Baixando imagens dos produtos...")
        
        products_with_images = self.image_downloader.download_product_images(products)
        
        success(f"{len(products_with_images)} imagens baixadas com sucesso")
        
        # Mostra estatísticas de download
        download_stats = self.image_downloader.get_download_stats()
        stats(download_stats)
        
        return products_with_images
    
    def generate_catalog(self, products: List[Dict[str, Any]], 
                        output_filename: str = None, 
                        catalog_type: str = "grid",
                        template_name: str = None,
                        custom_context: Dict[str, Any] = None,
                        color_scheme: str = None) -> bool:
        """
        Gera catálogo em PDF
        
        Args:
            products: Lista de produtos
            output_filename: Nome do arquivo de saída
            catalog_type: Tipo de catálogo ('grid', 'simple', 'html', 'canva')
            template_name: Nome do template HTML (para catalog_type='html')
            custom_context: Contexto adicional para templates HTML
            color_scheme: Esquema de cores a aplicar
        
        Returns:
            True se catálogo foi gerado com sucesso
        """
        if not output_filename:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"catalogo_{timestamp}.pdf"
        
        progress(f"Gerando catálogo: {output_filename}")
        
        if catalog_type == "simple":
            success_flag = self.pdf_builder.generate_simple_catalog(products, output_filename)
        elif catalog_type == "html":
            template = template_name or "catalogo_simples.html"
            # Define esquema 'suave' como padrão se nenhum for especificado
            default_scheme = color_scheme or "suave"
            success_flag = self.pdf_builder.generate_html_catalog(
                products, template, output_filename, custom_context, default_scheme
            )
        elif catalog_type == "canva":
            error("Para usar templates do Canva, use o método generate_catalog_from_canva()")
            return False
        else:  # grid (padrão) - agora usa template simples otimizado
            template = template_name or "catalogo_simples.html"
            # Define esquema 'suave' como padrão se nenhum for especificado
            default_scheme = color_scheme or "suave"
            success_flag = self.pdf_builder.generate_html_catalog(
                products, template, output_filename, custom_context, default_scheme
            )
        
        if success_flag:
            output_path = OUTPUT_DIR / output_filename
            success(f"Catálogo gerado com sucesso: {output_path}")
            return True
        else:
            error("Erro ao gerar catálogo")
            return False
    
    def cleanup(self):
        """Limpa arquivos temporários"""
        progress("Limpando arquivos temporários...")
        self.image_downloader.cleanup_temp_images()
    
    def _print_statistics(self, stats_data: Dict[str, Any]):
        """Imprime estatísticas dos produtos"""
        info("Estatísticas dos Produtos:")
        
        if stats_data.get('total_products'):
            info(f"   Total: {stats_data['total_products']}")
        
        if stats_data.get('price_range', {}).get('min', 0) > 0:
            price_range = stats_data['price_range']
            info(f"   Preço: R$ {price_range['min']:.2f} - R$ {price_range['max']:.2f}")
            info(f"   Média: R$ {price_range['average']:.2f}")
        
        if stats_data.get('categories'):
            info(f"   Categorias: {len(stats_data['categories'])}")
        
        if stats_data.get('sizes'):
            info(f"   Tamanhos: {len(stats_data['sizes'])}")
        
        if stats_data.get('colors'):
            info(f"   Cores: {len(stats_data['colors'])}")
    
    def run_full_process(self, spreadsheet_id: str, sheet_name: str = "Sheet1", 
                        output_filename: str = None, catalog_type: str = "grid",
                        download_images: bool = True, template_name: str = None,
                        color_scheme: str = None) -> bool:
        """
        Executa processo completo de geração do catálogo
        
        Args:
            spreadsheet_id: ID da planilha
            sheet_name: Nome da aba
            output_filename: Nome do arquivo de saída
            catalog_type: Tipo de catálogo
            download_images: Se deve baixar imagens
            template_name: Nome do template HTML (para catalog_type='html')
            color_scheme: Esquema de cores a aplicar
        
        Returns:
            True se processo foi concluído com sucesso
        """
        try:
            section("Iniciando Catalog Builder")
            
            # 1. Autentica com Google Sheets
            if not self.authenticate_google_sheets():
                error("Falha na autenticação com Google Sheets")
                return False
            
            # 2. Busca dados dos produtos
            products = self.fetch_products_data(spreadsheet_id, sheet_name)
            if not products:
                return False
            
            # 3. Baixa imagens (se solicitado)
            if download_images:
                products = self.download_product_images(products)
                if not products:
                    error("Nenhum produto com imagem válida")
                    return False
            
            # 4. Gera catálogo
            success_flag = self.generate_catalog(products, output_filename, catalog_type, template_name, None, color_scheme)
            
            # 5. Limpa arquivos temporários
            self.cleanup()
            
            if success_flag:
                section("Processo concluído com sucesso!")
                return True
            else:
                return False
                
        except KeyboardInterrupt:
            warning("Processo interrompido pelo usuário")
            self.cleanup()
            return False
        except Exception as e:
            exception("Erro inesperado", e)
            self.cleanup()
            return False


def get_config_from_env():
    """
    Obtém configurações das variáveis de ambiente
    
    Returns:
        Dicionário com as configurações
    """
    config_data = {}
    
    # SPREADSHEET_ID é obrigatório
    spreadsheet_id = os.getenv('SPREADSHEET_ID')
    if not spreadsheet_id:
        error("Variável SPREADSHEET_ID não encontrada no arquivo .env")
        error("Configure a variável SPREADSHEET_ID no arquivo .env")
        return None
    
    config_data['spreadsheet_id'] = spreadsheet_id
    
    # Configurações opcionais com valores padrão
    config_data['sheet_name'] = os.getenv('SHEET_NAME', 'Sheet1')
    config_data['output_filename'] = os.getenv('OUTPUT_FILENAME') or None
    config_data['catalog_type'] = os.getenv('CATALOG_TYPE', 'grid')
    config_data['download_images'] = os.getenv('DOWNLOAD_IMAGES', 'true').lower() == 'true'
    
    return config_data


def main():
    """Função principal"""
    parser = argparse.ArgumentParser(
        description="Catalog Builder - Gerador Automático de Catálogo de Roupas",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:

1. Usando variáveis de ambiente (recomendado):
   Configure o arquivo .env com SPREADSHEET_ID e execute:
   python main.py

2. Sobrescrevendo configurações do .env:
   python main.py --sheet-name "Produtos" --output "meu_catalogo.pdf"

3. Modo simples (sem imagens):
   python main.py --type simple --no-images

4. Usando templates HTML/CSS:
   python main.py --type html --template catalogo_simples.html

Variáveis de ambiente disponíveis:
- SPREADSHEET_ID: ID da planilha (obrigatório)
- SHEET_NAME: Nome da aba (padrão: Sheet1)
- OUTPUT_FILENAME: Nome do arquivo de saída
- CATALOG_TYPE: Tipo de catálogo (grid/simple/html)
- DOWNLOAD_IMAGES: Baixar imagens (true/false)
        """
    )
    
    # Argumentos opcionais para sobrescrever configurações do .env
    parser.add_argument(
        "--sheet-name", "-s",
        help="Nome da aba da planilha (sobrescreve SHEET_NAME do .env)"
    )
    
    parser.add_argument(
        "--output", "-o",
        help="Nome do arquivo de saída (sobrescreve OUTPUT_FILENAME do .env)"
    )
    
    parser.add_argument(
        "--type", "-t",
        choices=["grid", "simple", "html"],
        help="Tipo de catálogo: grid (com imagens), simple (lista) ou html (templates HTML/CSS) (sobrescreve CATALOG_TYPE do .env)"
    )
    
    parser.add_argument(
        "--template", "-T",
        help="Nome do template HTML (para --type html)"
    )
    
    parser.add_argument(
        "--color-scheme", "-c",
        help="Esquema de cores a aplicar (baseado na logo)"
    )
    
    parser.add_argument(
        "--list-schemes",
        action="store_true",
        help="Lista esquemas de cores disponíveis e sai"
    )
    
    parser.add_argument(
        "--no-images",
        action="store_true",
        help="Não baixar imagens (sobrescreve DOWNLOAD_IMAGES do .env)"
    )
    
    parser.add_argument(
        "--spreadsheet-id",
        help="ID da planilha (sobrescreve SPREADSHEET_ID do .env)"
    )
    
    args = parser.parse_args()
    
    # Se solicitado listar esquemas de cores
    if args.list_schemes:
        from src.pdf_generator.pdf_builder import PDFBuilder
        builder = PDFBuilder()
        schemes = builder.list_available_color_schemes()
        
        section("Esquemas de Cores Disponíveis")
        for key, name in schemes.items():
            info(f"  {key}: {name}")
        
        print("\nUso: python main.py --color-scheme <nome_do_esquema>")
        print("Exemplo: python main.py --color-scheme suave")
        sys.exit(0)
    
    # Obtém configurações do .env
    config_data = get_config_from_env()
    if not config_data:
        sys.exit(1)
    
    # Sobrescreve com argumentos da linha de comando se fornecidos
    if args.spreadsheet_id:
        config_data['spreadsheet_id'] = args.spreadsheet_id
    if args.sheet_name:
        config_data['sheet_name'] = args.sheet_name
    if args.output:
        config_data['output_filename'] = args.output
    if args.type:
        config_data['catalog_type'] = args.type
    if args.template:
        config_data['template_name'] = args.template
    if args.color_scheme:
        config_data['color_scheme'] = args.color_scheme
    if args.no_images:
        config_data['download_images'] = False
    
    # Mostra configurações que serão usadas
    section("Configurações")
    config("Planilha", config_data['spreadsheet_id'])
    config("Aba", config_data['sheet_name'])
    config("Tipo", config_data['catalog_type'])
    if config_data.get('template_name'):
        config("Template", config_data['template_name'])
    color_scheme_display = config_data.get('color_scheme') or "suave (padrão)"
    config("Esquema de cores", color_scheme_display)
    config("Baixar imagens", config_data['download_images'])
    if config_data['output_filename']:
        config("Arquivo de saída", config_data['output_filename'])
    
    # Cria instância do Catalog Builder
    builder = CatalogBuilder()
    
    # Executa processo completo
    success_flag = builder.run_full_process(
        spreadsheet_id=config_data['spreadsheet_id'],
        sheet_name=config_data['sheet_name'],
        output_filename=config_data['output_filename'],
        catalog_type=config_data['catalog_type'],
        download_images=config_data['download_images'],
        template_name=config_data.get('template_name'),
        color_scheme=config_data.get('color_scheme')
    )
    
    sys.exit(0 if success_flag else 1)


if __name__ == "__main__":
    main()
