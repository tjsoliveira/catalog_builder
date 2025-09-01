"""
Construtor de PDF para o catálogo
"""
from typing import List, Dict, Any, Optional
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, black, white
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.platypus.flowables import HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
from reportlab.lib import colors

from config.settings import PDF_CONFIG, OUTPUT_DIR
from src.image_processing.image_optimizer import ImageOptimizer
from src.logger import info, success, error, warning, debug, exception


class PDFBuilder:
    """Classe para construir PDF do catálogo"""
    
    def __init__(self):
        self.page_size = A4
        self.margins = PDF_CONFIG["margins"]
        self.grid_config = PDF_CONFIG["grid"]
        self.image_optimizer = ImageOptimizer()
        
        # Cria diretório de saída
        OUTPUT_DIR.mkdir(exist_ok=True)
        
        # Estilos do PDF
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Configura estilos customizados para o PDF"""
        # Título principal
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=HexColor('#2c3e50')
        ))
        
        # Nome do produto
        self.styles.add(ParagraphStyle(
            name='ProductName',
            parent=self.styles['Normal'],
            fontSize=12,
            fontName='Helvetica-Bold',
            spaceAfter=6,
            alignment=TA_CENTER,
            textColor=HexColor('#34495e')
        ))
        
        # Preço do produto
        self.styles.add(ParagraphStyle(
            name='ProductPrice',
            parent=self.styles['Normal'],
            fontSize=14,
            fontName='Helvetica-Bold',
            spaceAfter=6,
            alignment=TA_CENTER,
            textColor=HexColor('#e74c3c')
        ))
        
        # Descrição do produto
        self.styles.add(ParagraphStyle(
            name='ProductDescription',
            parent=self.styles['Normal'],
            fontSize=9,
            spaceAfter=6,
            alignment=TA_CENTER,
            textColor=HexColor('#7f8c8d')
        ))
        
        # Informações adicionais
        self.styles.add(ParagraphStyle(
            name='ProductInfo',
            parent=self.styles['Normal'],
            fontSize=8,
            spaceAfter=3,
            alignment=TA_CENTER,
            textColor=HexColor('#95a5a6')
        ))
    
    def _create_product_card(self, product: Dict[str, Any]) -> List:
        """
        Cria card de um produto
        
        Args:
            product: Dados do produto
        
        Returns:
            Lista de elementos do card
        """
        elements = []
        product_name = product.get('name', 'Produto sem nome')
        
        # Imagem do produto
        if product.get("local_image_path") and Path(product["local_image_path"]).exists():
            try:
                debug(f"Processando imagem do produto: {product_name}")
                
                # Otimiza imagem para PDF
                img_data = self.image_optimizer.optimize_for_pdf(product["local_image_path"])
                if img_data:
                    # Cria imagem temporária em memória
                    from io import BytesIO
                    img_buffer = BytesIO(img_data)
                    img = Image(img_buffer, width=PDF_CONFIG["image"]["max_width"], 
                               height=PDF_CONFIG["image"]["max_height"])
                    elements.append(img)
                    success(f"Imagem processada com sucesso: {product_name}")
                else:
                    warning(f"Falha ao otimizar imagem: {product_name}")
                    elements.append(Paragraph("Imagem não disponível", self.styles['ProductInfo']))
            except Exception as e:
                exception(f"Erro ao processar imagem do produto {product_name}", e)
                elements.append(Paragraph("Imagem não disponível", self.styles['ProductInfo']))
        else:
            warning(f"Imagem não encontrada para produto: {product_name}")
            elements.append(Paragraph("Imagem não disponível", self.styles['ProductInfo']))
        
        elements.append(Spacer(1, 6))
        
        # Nome do produto
        name = product.get("name", "Produto sem nome")
        elements.append(Paragraph(name, self.styles['ProductName']))
        
        # Preço
        price = product.get("price", 0)
        if price:
            price_text = f"R$ {price:.2f}".replace(".", ",")
            elements.append(Paragraph(price_text, self.styles['ProductPrice']))
        
        # Descrição
        description = product.get("description", "")
        if description:
            elements.append(Paragraph(description, self.styles['ProductDescription']))
        
        # Informações adicionais
        info_parts = []
        if product.get("category"):
            info_parts.append(f"Categoria: {product['category']}")
        if product.get("size"):
            info_parts.append(f"Tamanho: {product['size']}")
        if product.get("color"):
            info_parts.append(f"Cor: {product['color']}")
        
        if info_parts:
            info_text = " | ".join(info_parts)
            elements.append(Paragraph(info_text, self.styles['ProductInfo']))
        
        return elements
    
    def _create_products_grid(self, products: List[Dict[str, Any]]) -> List:
        """
        Cria grid de produtos
        
        Args:
            products: Lista de produtos
        
        Returns:
            Lista de elementos do grid
        """
        elements = []
        columns = self.grid_config["columns"]
        
        info(f"Criando grid com {len(products)} produtos em {columns} colunas")
        
        # Agrupa produtos em linhas
        for i in range(0, len(products), columns):
            row_products = products[i:i + columns]
            
            # Cria tabela para a linha
            table_data = []
            for product in row_products:
                product_elements = self._create_product_card(product)
                table_data.append(product_elements)
            
            # Adiciona colunas vazias se necessário
            while len(table_data) < columns:
                table_data.append([Spacer(1, 1)])
            
            # Cria tabela
            table = Table(table_data, colWidths=[self.page_size[0] / columns - 20] * columns)
            table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                ('TOPPADDING', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ]))
            
            elements.append(table)
            elements.append(Spacer(1, 20))
        
        return elements
    
    def generate_catalog(self, products: List[Dict[str, Any]], output_filename: str = "catalogo_produtos.pdf") -> bool:
        """
        Gera PDF do catálogo
        
        Args:
            products: Lista de produtos
            output_filename: Nome do arquivo de saída
        
        Returns:
            True se PDF foi gerado com sucesso
        """
        try:
            if not products:
                error("Nenhum produto para gerar catálogo")
                return False
            
            info(f"Gerando catálogo com {len(products)} produtos")
            
            # Caminho completo do arquivo
            output_path = OUTPUT_DIR / output_filename
            
            # Cria documento PDF
            doc = SimpleDocTemplate(
                str(output_path),
                pagesize=self.page_size,
                rightMargin=self.margins["right"],
                leftMargin=self.margins["left"],
                topMargin=self.margins["top"],
                bottomMargin=self.margins["bottom"]
            )
            
            # Elementos do PDF
            elements = []
            
            # Título
            elements.append(Paragraph("Catálogo de Produtos", self.styles['CustomTitle']))
            elements.append(Spacer(1, 20))
            
            # Linha separadora
            elements.append(HRFlowable(width="100%", thickness=1, lineCap='round', color=HexColor('#bdc3c7')))
            elements.append(Spacer(1, 20))
            
            # Grid de produtos
            product_elements = self._create_products_grid(products)
            elements.extend(product_elements)
            
            # Gera PDF
            doc.build(elements)
            
            success(f"Catálogo gerado com sucesso: {output_path}")
            info(f"Total de produtos: {len(products)}")
            
            return True
            
        except Exception as e:
            exception("Erro ao gerar catálogo", e)
            return False
    
    def generate_simple_catalog(self, products: List[Dict[str, Any]], output_filename: str = "catalogo_simples.pdf") -> bool:
        """
        Gera PDF simples com lista de produtos
        
        Args:
            products: Lista de produtos
            output_filename: Nome do arquivo de saída
        
        Returns:
            True se PDF foi gerado com sucesso
        """
        try:
            if not products:
                error("Nenhum produto para gerar catálogo")
                return False
            
            info(f"Gerando catálogo simples com {len(products)} produtos")
            
            output_path = OUTPUT_DIR / output_filename
            
            doc = SimpleDocTemplate(
                str(output_path),
                pagesize=self.page_size,
                rightMargin=self.margins["right"],
                leftMargin=self.margins["left"],
                topMargin=self.margins["top"],
                bottomMargin=self.margins["bottom"]
            )
            
            elements = []
            
            # Título
            elements.append(Paragraph("Catálogo de Produtos", self.styles['CustomTitle']))
            elements.append(Spacer(1, 20))
            
            # Lista de produtos
            for i, product in enumerate(products, 1):
                # Nome e preço
                name = product.get("name", "Produto sem nome")
                price = product.get("price", 0)
                price_text = f"R$ {price:.2f}".replace(".", ",") if price else "Preço não informado"
                
                product_text = f"{i}. {name} - {price_text}"
                elements.append(Paragraph(product_text, self.styles['Normal']))
                
                # Descrição se disponível
                if product.get("description"):
                    elements.append(Paragraph(f"   {product['description']}", self.styles['ProductDescription']))
                
                elements.append(Spacer(1, 10))
            
            doc.build(elements)
            
            success(f"Catálogo simples gerado: {output_path}")
            return True
            
        except Exception as e:
            exception("Erro ao gerar catálogo simples", e)
            return False
