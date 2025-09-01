"""
Templates e layouts para o PDF
"""
from typing import Dict, Any
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT


class PDFTemplates:
    """Templates e estilos para diferentes tipos de catálogo"""
    
    # Cores do tema
    COLORS = {
        'primary': HexColor('#2c3e50'),      # Azul escuro
        'secondary': HexColor('#34495e'),    # Cinza escuro
        'accent': HexColor('#e74c3c'),       # Vermelho
        'text': HexColor('#2c3e50'),         # Texto principal
        'muted': HexColor('#7f8c8d'),        # Texto secundário
        'light': HexColor('#ecf0f1'),        # Fundo claro
        'border': HexColor('#bdc3c7')        # Bordas
    }
    
    @staticmethod
    def get_minimal_style() -> Dict[str, ParagraphStyle]:
        """Estilo minimalista"""
        return {
            'title': ParagraphStyle(
                name='MinimalTitle',
                fontSize=20,
                spaceAfter=20,
                alignment=TA_CENTER,
                textColor=PDFTemplates.COLORS['primary']
            ),
            'product_name': ParagraphStyle(
                name='MinimalProductName',
                fontSize=11,
                fontName='Helvetica-Bold',
                spaceAfter=4,
                alignment=TA_CENTER,
                textColor=PDFTemplates.COLORS['text']
            ),
            'product_price': ParagraphStyle(
                name='MinimalProductPrice',
                fontSize=12,
                fontName='Helvetica-Bold',
                spaceAfter=4,
                alignment=TA_CENTER,
                textColor=PDFTemplates.COLORS['accent']
            )
        }
    
    @staticmethod
    def get_elegant_style() -> Dict[str, ParagraphStyle]:
        """Estilo elegante"""
        return {
            'title': ParagraphStyle(
                name='ElegantTitle',
                fontSize=24,
                spaceAfter=30,
                alignment=TA_CENTER,
                textColor=PDFTemplates.COLORS['primary'],
                fontName='Helvetica-Bold'
            ),
            'product_name': ParagraphStyle(
                name='ElegantProductName',
                fontSize=12,
                fontName='Helvetica-Bold',
                spaceAfter=6,
                alignment=TA_CENTER,
                textColor=PDFTemplates.COLORS['secondary']
            ),
            'product_price': ParagraphStyle(
                name='ElegantProductPrice',
                fontSize=14,
                fontName='Helvetica-Bold',
                spaceAfter=6,
                alignment=TA_CENTER,
                textColor=PDFTemplates.COLORS['accent']
            ),
            'product_description': ParagraphStyle(
                name='ElegantProductDescription',
                fontSize=9,
                spaceAfter=6,
                alignment=TA_CENTER,
                textColor=PDFTemplates.COLORS['muted'],
                fontName='Helvetica'
            )
        }
    
    @staticmethod
    def get_modern_style() -> Dict[str, ParagraphStyle]:
        """Estilo moderno"""
        return {
            'title': ParagraphStyle(
                name='ModernTitle',
                fontSize=22,
                spaceAfter=25,
                alignment=TA_CENTER,
                textColor=PDFTemplates.COLORS['primary'],
                fontName='Helvetica-Bold'
            ),
            'product_name': ParagraphStyle(
                name='ModernProductName',
                fontSize=11,
                fontName='Helvetica-Bold',
                spaceAfter=5,
                alignment=TA_CENTER,
                textColor=PDFTemplates.COLORS['text']
            ),
            'product_price': ParagraphStyle(
                name='ModernProductPrice',
                fontSize=13,
                fontName='Helvetica-Bold',
                spaceAfter=5,
                alignment=TA_CENTER,
                textColor=PDFTemplates.COLORS['accent']
            ),
            'product_info': ParagraphStyle(
                name='ModernProductInfo',
                fontSize=8,
                spaceAfter=3,
                alignment=TA_CENTER,
                textColor=PDFTemplates.COLORS['muted'],
                fontName='Helvetica'
            )
        }
    
    @staticmethod
    def get_style_by_name(style_name: str) -> Dict[str, ParagraphStyle]:
        """
        Retorna estilo por nome
        
        Args:
            style_name: Nome do estilo ('minimal', 'elegant', 'modern')
        
        Returns:
            Dicionário com estilos
        """
        styles = {
            'minimal': PDFTemplates.get_minimal_style(),
            'elegant': PDFTemplates.get_elegant_style(),
            'modern': PDFTemplates.get_modern_style()
        }
        
        return styles.get(style_name, PDFTemplates.get_elegant_style())
    
    @staticmethod
    def get_available_styles() -> list:
        """Retorna lista de estilos disponíveis"""
        return ['minimal', 'elegant', 'modern']