"""
Módulo para análise de cores da logo e geração de esquemas de cores
"""
from typing import List, Dict, Tuple, Optional
from pathlib import Path
import colorsys
from colorthief import ColorThief
from src.logger import info, success, error, warning, debug, exception


class ColorSchemeGenerator:
    """Classe para gerar esquemas de cores baseados na logo"""
    
    def __init__(self):
        self.primary_colors = []
        self.color_schemes = {}
    
    def analyze_logo_colors(self, logo_path: str) -> List[Tuple[int, int, int]]:
        """
        Analisa a logo e extrai as cores dominantes
        
        Args:
            logo_path: Caminho para o arquivo da logo
        
        Returns:
            Lista de cores RGB dominantes
        """
        try:
            if not Path(logo_path).exists():
                warning(f"Arquivo de logo não encontrado: {logo_path}")
                return []
            
            color_thief = ColorThief(logo_path)
            
            # Extrai a cor dominante
            dominant_color = color_thief.get_color(quality=1)
            
            # Extrai paleta de cores (máximo 6 cores)
            palette = color_thief.get_palette(color_count=6, quality=1)
            
            self.primary_colors = palette
            info(f"Cores extraídas da logo: {len(palette)} cores")
            debug(f"Cor dominante: {dominant_color}")
            debug(f"Paleta completa: {palette}")
            
            return palette
            
        except Exception as e:
            exception("Erro ao analisar cores da logo", e)
            return []
    
    def rgb_to_hex(self, rgb: Tuple[int, int, int]) -> str:
        """Converte RGB para HEX"""
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
    
    def lighten_color(self, rgb: Tuple[int, int, int], factor: float = 0.3) -> Tuple[int, int, int]:
        """Clareia uma cor RGB"""
        h, l, s = colorsys.rgb_to_hls(rgb[0]/255, rgb[1]/255, rgb[2]/255)
        l = min(1.0, l + factor)
        r, g, b = colorsys.hls_to_rgb(h, l, s)
        return (int(r * 255), int(g * 255), int(b * 255))
    
    def darken_color(self, rgb: Tuple[int, int, int], factor: float = 0.3) -> Tuple[int, int, int]:
        """Escurece uma cor RGB"""
        h, l, s = colorsys.rgb_to_hls(rgb[0]/255, rgb[1]/255, rgb[2]/255)
        l = max(0.0, l - factor)
        r, g, b = colorsys.hls_to_rgb(h, l, s)
        return (int(r * 255), int(g * 255), int(b * 255))
    
    def create_gradient_colors(self, color1: Tuple[int, int, int], color2: Tuple[int, int, int]) -> List[str]:
        """Cria cores para gradiente entre duas cores"""
        colors = []
        for i in range(5):
            factor = i / 4
            r = int(color1[0] + (color2[0] - color1[0]) * factor)
            g = int(color1[1] + (color2[1] - color1[1]) * factor)
            b = int(color1[2] + (color2[2] - color1[2]) * factor)
            colors.append(self.rgb_to_hex((r, g, b)))
        return colors
    
    def generate_color_schemes(self, logo_path: str = None) -> Dict[str, Dict[str, str]]:
        """
        Gera diferentes esquemas de cores baseados na logo ou usa esquemas padrão
        
        Args:
            logo_path: Caminho para o arquivo da logo (opcional)
        
        Returns:
            Dicionário com esquemas de cores
        """
        try:
            # Se não tem logo, usa esquemas padrão
            if not logo_path:
                info("Usando esquemas de cores padrão")
                schemes = self._get_default_schemes()
                self.color_schemes = schemes
                return schemes
                
            # Tenta analisar a logo
            palette = self.analyze_logo_colors(logo_path)
            
            if not palette:
                # Esquema padrão se não conseguir analisar
                warning("Não foi possível analisar cores da logo, usando esquemas padrão")
                schemes = self._get_default_schemes()
                self.color_schemes = schemes
                return schemes
            
            primary = palette[0]  # Cor dominante
            secondary = palette[1] if len(palette) > 1 else primary
            accent = palette[2] if len(palette) > 2 else secondary
            
            # Gera variações das cores
            primary_light = self.lighten_color(primary, 0.4)
            primary_dark = self.darken_color(primary, 0.3)
            secondary_light = self.lighten_color(secondary, 0.5)
            accent_light = self.lighten_color(accent, 0.6)
            
            schemes = {
                "default": {
                    "name": "Padrão",
                    "background": "#333333",        # Fundo da página
                    "product_bg": "#F8F9FA",        # Fundo dos cards de produto
                    "header_bg": "#333333",         # Laranja chamativo
                    "border_color": "#00A79D",      # Turquesa
                    "accent_color": "#6BC0C9",      # Azul claro
                    "text_primary": "#333333",
                    "text_secondary": "#6BC0C9",    # Azul claro
                    "price_color": "#6BC0C9",       # Roxo forte
                    "highlight_color": "#7AD0E0"    # Azul bebê
                },
                
                "dark_mode": {
                    "name": "Modo Escuro",
                    "background": "#1C1C1C",        # Fundo da página
                    "product_bg": "#2D2D2D",        # Fundo dos cards de produto
                    "header_bg": "#F28E30",         # Laranja chamativo
                    "border_color": "#00A79D",      # Turquesa
                    "accent_color": "#7AD0E0",      # Azul bebê
                    "text_primary": "#FFFFFF",
                    "text_secondary": "#7AD0E0",    # Azul bebê
                    "price_color": "#7F4C9E",       # Roxo forte
                    "highlight_color": "#6BC0C9"    # Azul claro
                },
                
                "minimal": {
                    "name": "Minimalista",
                    "background": "#F8F8F8",        # Fundo da página
                    "product_bg": "#FFFFFF",        # Fundo dos cards de produto
                    "header_bg": "#333333",
                    "border_color": "#DDDDDD",
                    "accent_color": "#00A79D",      # Turquesa
                    "text_primary": "#333333",
                    "text_secondary": "#6BC0C9",    # Azul claro
                    "price_color": "#F28E30",       # Laranja chamativo
                    "highlight_color": "#00A79D"    # Turquesa
                }
            }
            
            self.color_schemes = schemes
            success(f"Gerados {len(schemes)} esquemas de cores baseados na logo")
            
            return schemes
            
        except Exception as e:
            exception("Erro ao gerar esquemas de cores", e)
            return self._get_default_schemes()
    
    def _get_default_schemes(self) -> Dict[str, Dict[str, str]]:
        """Retorna esquemas de cores padrão"""
        return {
            "default": {
                "name": "Padrão",
                "background": "#F28E30",        # Fundo da página
                "product_bg": "#F28E30",        # Fundo dos cards de produto
                "header_bg": "#333333",         # Laranja chamativo
                "border_color": "#00A79D",      # Turquesa
                "accent_color": "#6BC0C9",      # Azul claro
                "text_primary": "#333333",
                "text_secondary": "#6BC0C9",    # Azul claro
                "price_color": "#7F4C9E",       # Roxo forte
                "highlight_color": "#7AD0E0"    # Azul bebê
            },
            
            "dark_mode": {
                "name": "Modo Escuro",
                "background": "#1C1C1C",        # Fundo da página
                "product_bg": "#2D2D2D",        # Fundo dos cards de produto
                "header_bg": "#F28E30",         # Laranja chamativo
                "border_color": "#00A79D",      # Turquesa
                "accent_color": "#7AD0E0",      # Azul bebê
                "text_primary": "#FFFFFF",
                "text_secondary": "#7AD0E0",    # Azul bebê
                "price_color": "#7F4C9E",       # Roxo forte
                "highlight_color": "#6BC0C9"    # Azul claro
            },
            
            "minimal": {
                "name": "Minimalista",
                "background": "#F8F8F8",        # Fundo da página
                "product_bg": "#FFFFFF",        # Fundo dos cards de produto
                "header_bg": "#333333",
                "border_color": "#DDDDDD",
                "accent_color": "#00A79D",      # Turquesa
                "text_primary": "#333333",
                "text_secondary": "#6BC0C9",    # Azul claro
                "price_color": "#F28E30",       # Laranja chamativo
                "highlight_color": "#00A79D"    # Turquesa
            }
        }
    
    def get_scheme_info(self) -> Dict[str, str]:
        """Retorna informações sobre os esquemas disponíveis"""
        info_dict = {}
        for key, scheme in self.color_schemes.items():
            info_dict[key] = scheme.get("name", key.capitalize())
        return info_dict
    
    def apply_scheme_to_css(self, css_content: str, scheme_name: str) -> str:
        """
        Aplica um esquema de cores ao CSS
        
        Args:
            css_content: Conteúdo CSS original
            scheme_name: Nome do esquema a aplicar
        
        Returns:
            CSS com o esquema de cores aplicado
        """
        if scheme_name not in self.color_schemes:
            warning(f"Esquema '{scheme_name}' não encontrado")
            return css_content
        
        scheme = self.color_schemes[scheme_name]
        
        # Substitui variáveis de cor no CSS
        modified_css = css_content
        
        # Substitui cores específicas
        replacements = {
            "background-color: #fff;": f"background-color: {scheme['background']};",
            "background: #fff;": f"background: {scheme['background']};",
            "border-bottom: 2px solid #e74c3c;": f"border-bottom: 2px solid {scheme['border_color']};",
            "color: #2c3e50;": f"color: {scheme['text_primary']};",
            "color: #7f8c8d;": f"color: {scheme['text_secondary']};",
            "color: #e74c3c;": f"color: {scheme['price_color']};",
            "border-left: 2px solid #3498db;": f"border-left: 2px solid {scheme['accent_color']};",
            "background-color: #f8f9fa;": f"background-color: {scheme.get('product_bg', scheme['background'])};",
            "color: #333;": f"color: {scheme['text_primary']};",
            "color: #666;": f"color: {scheme['text_secondary']};",
        }
        
        for old, new in replacements.items():
            modified_css = modified_css.replace(old, new)
        
        # Adiciona estilos específicos do esquema para garantir fundo completo
        page_background_css = f"""
/* Fundo da página - aplicado a toda a página */
@page {{
    background: {scheme['background']};
}}

html, body {{
    background: {scheme['background']} !important;
    min-height: 100vh;
    margin: 0;
    padding: 0;
}}

.container {{
    background: {scheme['background']};
    min-height: 100vh;
}}

/* Estilos específicos do esquema de cores */
.header {{
    background-color: {scheme.get('header_bg', scheme['background'])} !important;
    color: {scheme['text_primary']} !important;
}}

.header .title {{
    color: {scheme['text_primary']} !important;
}}

.header .subtitle {{
    color: {scheme['text_secondary']} !important;
}}

.produto {{
    background-color: {scheme.get('product_bg', scheme['background'])} !important;
    border-color: {scheme['border_color']} !important;
}}

.produto .nome {{
    color: {scheme['text_primary']} !important;
}}

.produto .descricao {{
    color: {scheme['text_secondary']} !important;
}}

.produto .preco {{
    color: {scheme['price_color']} !important;
}}

.produto .detalhe {{
    color: {scheme['text_secondary']} !important;
}}

/* Highlight color para elementos especiais */
.highlight {{
    color: {scheme.get('highlight_color', scheme['accent_color'])} !important;
}}

.accent-border {{
    border-color: {scheme['accent_color']} !important;
}}
"""
        
        # Adiciona o CSS de fundo ao início
        modified_css = page_background_css + modified_css
        
        # Adiciona estilos específicos para gradientes no header
        if "linear-gradient" in scheme.get("header_bg", ""):
            header_bg_css = f"""
.header {{
    background: {scheme['header_bg']} !important;
    color: {scheme['text_primary']} !important;
}}

.header .title {{
    color: {scheme['text_primary']} !important;
}}

.header .subtitle {{
    color: {scheme['text_secondary']} !important;
}}
"""
            modified_css = modified_css + header_bg_css
        
        return modified_css
