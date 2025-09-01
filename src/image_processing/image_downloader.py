"""
Downloader de imagens para o catálogo
"""
import os
import requests
from typing import Optional, List
from pathlib import Path
from PIL import Image
import hashlib
from urllib.parse import urlparse

from config.settings import IMAGE_CONFIG


class ImageDownloader:
    """Classe para baixar e gerenciar imagens dos produtos"""
    
    def __init__(self):
        self.temp_dir = IMAGE_CONFIG["temp_dir"]
        self.temp_dir.mkdir(exist_ok=True)
        self.downloaded_images = {}  # Cache de imagens baixadas
    
    def _get_image_filename(self, url: str, product_name: str) -> str:
        """
        Gera nome único para arquivo de imagem
        
        Args:
            url: URL da imagem
            product_name: Nome do produto
        
        Returns:
            Nome do arquivo
        """
        # Cria hash da URL para evitar conflitos
        url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
        
        # Limpa nome do produto para usar como nome de arquivo
        clean_name = "".join(c for c in product_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        clean_name = clean_name.replace(' ', '_')[:20]  # Limita tamanho
        
        # Pega extensão da URL
        parsed_url = urlparse(url)
        extension = os.path.splitext(parsed_url.path)[1]
        if not extension:
            extension = '.jpg'  # Default
        
        return f"{clean_name}_{url_hash}{extension}"
    
    def download_image(self, url: str, product_name: str) -> Optional[Path]:
        """
        Baixa imagem de uma URL
        
        Args:
            url: URL da imagem
            product_name: Nome do produto
        
        Returns:
            Caminho para imagem baixada ou None se falhou
        """
        try:
            # Verifica se já foi baixada
            if url in self.downloaded_images:
                return self.downloaded_images[url]
            
            # Gera nome do arquivo
            filename = self._get_image_filename(url, product_name)
            filepath = self.temp_dir / filename
            
            # Baixa a imagem
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(
                url, 
                headers=headers, 
                timeout=IMAGE_CONFIG["download_timeout"],
                stream=True
            )
            response.raise_for_status()
            
            # Verifica tamanho do arquivo
            content_length = response.headers.get('content-length')
            if content_length and int(content_length) > IMAGE_CONFIG["max_file_size"]:
                print(f"Imagem muito grande para {product_name}: {content_length} bytes")
                return None
            
            # Salva a imagem
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Verifica se é uma imagem válida
            try:
                with Image.open(filepath) as img:
                    img.verify()
            except Exception:
                print(f"Arquivo baixado não é uma imagem válida: {product_name}")
                filepath.unlink(missing_ok=True)
                return None
            
            # Adiciona ao cache
            self.downloaded_images[url] = filepath
            print(f"Imagem baixada: {product_name} -> {filename}")
            return filepath
            
        except requests.exceptions.RequestException as e:
            print(f"Erro ao baixar imagem para {product_name}: {e}")
            return None
        except Exception as e:
            print(f"Erro inesperado ao baixar imagem para {product_name}: {e}")
            return None
    
    def download_product_images(self, products: List[dict]) -> List[dict]:
        """
        Baixa imagens para uma lista de produtos
        
        Args:
            products: Lista de produtos com image_url
        
        Returns:
            Lista de produtos com caminho da imagem local
        """
        processed_products = []
        
        for product in products:
            image_url = product.get("image_url")
            product_name = product.get("name", "Produto")
            
            if not image_url:
                print(f"Produto sem URL de imagem: {product_name}")
                continue
            
            # Baixa a imagem
            image_path = self.download_image(image_url, product_name)
            
            if image_path:
                # Adiciona caminho da imagem ao produto
                product_copy = product.copy()
                product_copy["local_image_path"] = str(image_path)
                processed_products.append(product_copy)
            else:
                print(f"Falha ao baixar imagem para: {product_name}")
        
        return processed_products
    
    def cleanup_temp_images(self):
        """Remove todas as imagens temporárias"""
        try:
            for file_path in self.temp_dir.glob("*"):
                if file_path.is_file():
                    file_path.unlink()
            
            self.downloaded_images.clear()
            print("Imagens temporárias removidas")
            
        except Exception as e:
            print(f"Erro ao limpar imagens temporárias: {e}")
    
    def get_download_stats(self) -> dict:
        """
        Retorna estatísticas dos downloads
        
        Returns:
            Dicionário com estatísticas
        """
        total_files = len(list(self.temp_dir.glob("*")))
        total_size = sum(f.stat().st_size for f in self.temp_dir.glob("*") if f.is_file())
        
        return {
            "downloaded_images": len(self.downloaded_images),
            "temp_files": total_files,
            "total_size_mb": round(total_size / (1024 * 1024), 2)
        }