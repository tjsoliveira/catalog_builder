"""
Módulo simplificado para aplicação de esquema de cores
"""
from typing import Dict
from src.logger import info


class ColorSchemeGenerator:
    """Classe simplificada para aplicação de esquema de cores"""
    
    def __init__(self):
        self.color_schemes = {
            "default": {
                "name": "Esquema Padrão",
                "description": "Esquema de cores padrão do catálogo"
            }
        }
    
    def generate_color_schemes(self, logo_path: str = None) -> Dict[str, Dict[str, str]]:
        """
        Gera esquemas de cores (simplificado - apenas default)
        
        Args:
            logo_path: Caminho para o arquivo da logo (ignorado por simplicidade)
        
        Returns:
            Dicionário com esquema de cores padrão
        """
        info("Usando esquema de cores padrão (sistema simplificado)")
        return self.color_schemes
    
    def get_scheme_info(self) -> Dict[str, str]:
        """Retorna informações sobre os esquemas disponíveis"""
        return {key: scheme["name"] for key, scheme in self.color_schemes.items()}
    
    def apply_scheme_to_html(self, html_content: str, scheme_name: str) -> str:
        """
        Aplica um esquema de cores ao HTML usando classes CSS
        
        Args:
            html_content: Conteúdo HTML original
            scheme_name: Nome do esquema a aplicar
        
        Returns:
            HTML com o esquema de cores aplicado
        """
        # Apenas esquema default é suportado
        if scheme_name != "default":
            info(f"Esquema '{scheme_name}' não suportado, usando 'default'")
            scheme_name = "default"
        
        # Adiciona a classe do esquema ao body
        modified_html = html_content.replace(
            '<body class="bg-white p-6">',
            '<body class="bg-white p-6 scheme-default">'
        )
        
        return modified_html
    
    def list_available_color_schemes(self) -> Dict[str, str]:
        """Lista esquemas de cores disponíveis"""
        return self.get_scheme_info()