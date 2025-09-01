"""
Otimizador de imagens para o catálogo
"""
from typing import Tuple, Optional
from pathlib import Path
from PIL import Image, ImageOps
import io

from config.settings import PDF_CONFIG


class ImageOptimizer:
    """Classe para otimizar imagens para o PDF"""
    
    def __init__(self):
        self.max_width = PDF_CONFIG["image"]["max_width"]
        self.max_height = PDF_CONFIG["image"]["max_height"]
        self.quality = PDF_CONFIG["image"]["quality"]
    
    def resize_image(self, image_path: str, max_width: int = None, max_height: int = None) -> Optional[Image.Image]:
        """
        Redimensiona imagem mantendo proporção
        
        Args:
            image_path: Caminho para a imagem
            max_width: Largura máxima (usa config se None)
            max_height: Altura máxima (usa config se None)
        
        Returns:
            Imagem redimensionada ou None se erro
        """
        try:
            max_width = max_width or self.max_width
            max_height = max_height or self.max_height
            
            with Image.open(image_path) as img:
                # Converte para RGB se necessário
                if img.mode in ('RGBA', 'LA', 'P'):
                    # Cria fundo branco para imagens com transparência
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Calcula novo tamanho mantendo proporção
                img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
                
                return img.copy()
                
        except Exception as e:
            print(f"Erro ao redimensionar imagem {image_path}: {e}")
            return None
    
    def create_thumbnail(self, image_path: str, size: Tuple[int, int] = (100, 100)) -> Optional[Image.Image]:
        """
        Cria thumbnail da imagem
        
        Args:
            image_path: Caminho para a imagem
            size: Tamanho do thumbnail (width, height)
        
        Returns:
            Thumbnail da imagem ou None se erro
        """
        try:
            with Image.open(image_path) as img:
                # Converte para RGB se necessário
                if img.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Cria thumbnail com crop central
                img.thumbnail(size, Image.Resampling.LANCZOS)
                
                # Se a imagem é menor que o tamanho desejado, centraliza
                if img.size != size:
                    new_img = Image.new('RGB', size, (255, 255, 255))
                    paste_x = (size[0] - img.size[0]) // 2
                    paste_y = (size[1] - img.size[1]) // 2
                    new_img.paste(img, (paste_x, paste_y))
                    img = new_img
                
                return img
                
        except Exception as e:
            print(f"Erro ao criar thumbnail {image_path}: {e}")
            return None
    
    def optimize_for_pdf(self, image_path: str) -> Optional[bytes]:
        """
        Otimiza imagem para uso no PDF
        
        Args:
            image_path: Caminho para a imagem
        
        Returns:
            Bytes da imagem otimizada ou None se erro
        """
        try:
            # Redimensiona a imagem
            img = self.resize_image(image_path)
            if not img:
                return None
            
            # Converte para bytes otimizados
            output = io.BytesIO()
            img.save(output, format='JPEG', quality=self.quality, optimize=True)
            return output.getvalue()
            
        except Exception as e:
            print(f"Erro ao otimizar imagem para PDF {image_path}: {e}")
            return None
    
    def get_image_info(self, image_path: str) -> dict:
        """
        Obtém informações da imagem
        
        Args:
            image_path: Caminho para a imagem
        
        Returns:
            Dicionário com informações da imagem
        """
        try:
            with Image.open(image_path) as img:
                return {
                    "size": img.size,
                    "mode": img.mode,
                    "format": img.format,
                    "file_size": Path(image_path).stat().st_size
                }
        except Exception as e:
            print(f"Erro ao obter informações da imagem {image_path}: {e}")
            return {}
    
    def batch_optimize(self, image_paths: list) -> dict:
        """
        Otimiza múltiplas imagens
        
        Args:
            image_paths: Lista de caminhos para imagens
        
        Returns:
            Dicionário com resultados da otimização
        """
        results = {
            "successful": [],
            "failed": [],
            "total_size_before": 0,
            "total_size_after": 0
        }
        
        for image_path in image_paths:
            try:
                # Informações antes da otimização
                info_before = self.get_image_info(image_path)
                results["total_size_before"] += info_before.get("file_size", 0)
                
                # Otimiza a imagem
                optimized_data = self.optimize_for_pdf(image_path)
                
                if optimized_data:
                    results["successful"].append(image_path)
                    results["total_size_after"] += len(optimized_data)
                else:
                    results["failed"].append(image_path)
                    
            except Exception as e:
                print(f"Erro ao processar {image_path}: {e}")
                results["failed"].append(image_path)
        
        return results