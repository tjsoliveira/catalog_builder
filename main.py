#!/usr/bin/env python3
"""
Catalog Builder - Gerador Automático de Catálogo de Roupas
Script principal para gerar catálogo a partir do Google Sheets
"""
import sys
import argparse
from pathlib import Path
from typing import List, Dict, Any

# Adiciona src ao path
sys.path.append(str(Path(__file__).parent / "src"))

from src.google_sheets.sheets_connector import GoogleSheetsConnector
from src.google_sheets.data_processor import DataProcessor
from src.image_processing.image_downloader import ImageDownloader
from src.pdf_generator.pdf_builder import PDFBuilder
from config.settings import OUTPUT_DIR


class CatalogBuilder:
    """Classe principal do Catalog Builder"""
    
    def __init__(self):
        self.sheets_connector = GoogleSheetsConnector()
        self.data_processor = DataProcessor()
        self.image_downloader = ImageDownloader()
        self.pdf_builder = PDFBuilder()
    
    def authenticate_google_sheets(self) -> bool:
        """Autentica com Google Sheets"""
        print("🔐 Autenticando com Google Sheets...")
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
        print(f"📊 Buscando dados da planilha: {spreadsheet_id}")
        
        # Busca dados brutos
        raw_products = self.sheets_connector.get_products_data(spreadsheet_id, sheet_name)
        
        if not raw_products:
            print("❌ Nenhum produto encontrado na planilha")
            return []
        
        print(f"📋 Encontrados {len(raw_products)} produtos na planilha")
        
        # Processa dados
        processed_products = self.data_processor.process_products(raw_products)
        
        if not processed_products:
            print("❌ Nenhum produto válido após processamento")
            return []
        
        print(f"✅ {len(processed_products)} produtos válidos processados")
        
        # Mostra estatísticas
        stats = self.data_processor.get_statistics(processed_products)
        self._print_statistics(stats)
        
        return processed_products
    
    def download_product_images(self, products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Baixa imagens dos produtos
        
        Args:
            products: Lista de produtos
        
        Returns:
            Lista de produtos com imagens baixadas
        """
        print("🖼️  Baixando imagens dos produtos...")
        
        products_with_images = self.image_downloader.download_product_images(products)
        
        print(f"📸 {len(products_with_images)} imagens baixadas com sucesso")
        
        # Mostra estatísticas de download
        download_stats = self.image_downloader.get_download_stats()
        print(f"📊 Estatísticas: {download_stats['downloaded_images']} imagens, "
              f"{download_stats['total_size_mb']} MB")
        
        return products_with_images
    
    def generate_catalog(self, products: List[Dict[str, Any]], 
                        output_filename: str = None, 
                        catalog_type: str = "grid") -> bool:
        """
        Gera catálogo em PDF
        
        Args:
            products: Lista de produtos
            output_filename: Nome do arquivo de saída
            catalog_type: Tipo de catálogo ('grid' ou 'simple')
        
        Returns:
            True se catálogo foi gerado com sucesso
        """
        if not output_filename:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"catalogo_{timestamp}.pdf"
        
        print(f"📄 Gerando catálogo: {output_filename}")
        
        if catalog_type == "simple":
            success = self.pdf_builder.generate_simple_catalog(products, output_filename)
        else:
            success = self.pdf_builder.generate_catalog(products, output_filename)
        
        if success:
            output_path = OUTPUT_DIR / output_filename
            print(f"✅ Catálogo gerado com sucesso: {output_path}")
            return True
        else:
            print("❌ Erro ao gerar catálogo")
            return False
    
    def cleanup(self):
        """Limpa arquivos temporários"""
        print("🧹 Limpando arquivos temporários...")
        self.image_downloader.cleanup_temp_images()
    
    def _print_statistics(self, stats: Dict[str, Any]):
        """Imprime estatísticas dos produtos"""
        print("\n📊 Estatísticas dos Produtos:")
        print(f"   Total: {stats['total_products']}")
        
        if stats['price_range']['min'] > 0:
            print(f"   Preço: R$ {stats['price_range']['min']:.2f} - R$ {stats['price_range']['max']:.2f}")
            print(f"   Média: R$ {stats['price_range']['average']:.2f}")
        
        if stats['categories']:
            print(f"   Categorias: {len(stats['categories'])}")
        
        if stats['sizes']:
            print(f"   Tamanhos: {len(stats['sizes'])}")
        
        if stats['colors']:
            print(f"   Cores: {len(stats['colors'])}")
        print()
    
    def run_full_process(self, spreadsheet_id: str, sheet_name: str = "Sheet1", 
                        output_filename: str = None, catalog_type: str = "grid",
                        download_images: bool = True) -> bool:
        """
        Executa processo completo de geração do catálogo
        
        Args:
            spreadsheet_id: ID da planilha
            sheet_name: Nome da aba
            output_filename: Nome do arquivo de saída
            catalog_type: Tipo de catálogo
            download_images: Se deve baixar imagens
        
        Returns:
            True se processo foi concluído com sucesso
        """
        try:
            print("🚀 Iniciando Catalog Builder...")
            print("=" * 50)
            
            # 1. Autentica com Google Sheets
            if not self.authenticate_google_sheets():
                print("❌ Falha na autenticação com Google Sheets")
                return False
            
            # 2. Busca dados dos produtos
            products = self.fetch_products_data(spreadsheet_id, sheet_name)
            if not products:
                return False
            
            # 3. Baixa imagens (se solicitado)
            if download_images:
                products = self.download_product_images(products)
                if not products:
                    print("❌ Nenhum produto com imagem válida")
                    return False
            
            # 4. Gera catálogo
            success = self.generate_catalog(products, output_filename, catalog_type)
            
            # 5. Limpa arquivos temporários
            self.cleanup()
            
            if success:
                print("=" * 50)
                print("🎉 Processo concluído com sucesso!")
                return True
            else:
                return False
                
        except KeyboardInterrupt:
            print("\n⏹️  Processo interrompido pelo usuário")
            self.cleanup()
            return False
        except Exception as e:
            print(f"❌ Erro inesperado: {e}")
            self.cleanup()
            return False


def main():
    """Função principal"""
    parser = argparse.ArgumentParser(
        description="Catalog Builder - Gerador Automático de Catálogo de Roupas"
    )
    
    parser.add_argument(
        "spreadsheet_id",
        help="ID da planilha do Google Sheets (da URL)"
    )
    
    parser.add_argument(
        "--sheet-name", "-s",
        default="Sheet1",
        help="Nome da aba da planilha (padrão: Sheet1)"
    )
    
    parser.add_argument(
        "--output", "-o",
        help="Nome do arquivo de saída (padrão: catalogo_YYYYMMDD_HHMMSS.pdf)"
    )
    
    parser.add_argument(
        "--type", "-t",
        choices=["grid", "simple"],
        default="grid",
        help="Tipo de catálogo: grid (com imagens) ou simple (lista)"
    )
    
    parser.add_argument(
        "--no-images",
        action="store_true",
        help="Não baixar imagens (gera catálogo simples)"
    )
    
    args = parser.parse_args()
    
    # Cria instância do Catalog Builder
    builder = CatalogBuilder()
    
    # Executa processo completo
    success = builder.run_full_process(
        spreadsheet_id=args.spreadsheet_id,
        sheet_name=args.sheet_name,
        output_filename=args.output,
        catalog_type=args.type,
        download_images=not args.no_images
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()