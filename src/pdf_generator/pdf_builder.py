"""
Construtor de PDF para o catálogo
"""
import os
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.platypus.flowables import HRFlowable
from reportlab.lib.enums import TA_CENTER

from config.settings import PDF_CONFIG, OUTPUT_DIR
from src.image_processing.image_optimizer import ImageOptimizer
from src.pdf_generator.html_template_engine import HTMLTemplateEngine
from src.color_schemes import ColorSchemeGenerator
from src.logger import info, success, error, warning, debug, exception


class PDFBuilder:
    """Classe para construir PDF do catálogo"""
    
    def __init__(self):
        self.page_size = A4
        self.margins = PDF_CONFIG["margins"]
        self.grid_config = PDF_CONFIG["grid"]
        self.image_optimizer = ImageOptimizer()
        self.html_engine = HTMLTemplateEngine()
        self.color_generator = ColorSchemeGenerator()
        
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
    
    def generate_html_catalog(self, products: List[Dict[str, Any]], 
                             template_name: str = "catalogo_simples.html",
                             output_filename: str = None,
                             custom_context: Dict[str, Any] = None,
                             color_scheme: str = None) -> bool:
        """
        Gera PDF usando template HTML/CSS
        
        Args:
            products: Lista de produtos
            template_name: Nome do template HTML
            output_filename: Nome do arquivo de saída
            custom_context: Contexto adicional para o template
            color_scheme: Nome do esquema de cores a aplicar
        
        Returns:
            True se PDF foi gerado com sucesso
        """
        try:
            if not products:
                error("Nenhum produto para gerar catálogo")
                return False
            
            if not output_filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_filename = f"catalogo_html_{timestamp}.pdf"
            
            info(f"Gerando catálogo HTML com {len(products)} produtos usando template: {template_name}")
            
            # Prepara contexto para o template
            context = {
                'produtos': products,
                'titulo': 'Thuca Kids',
                'data_geracao': self._get_portuguese_date(),
                'total_produtos': len(products),
                'logo_path': self._find_logo_file(),
                'contato': os.getenv('CONTATO', ''),
                'endereco': os.getenv('ENDERECO', '')
            }
            
            # Adiciona contexto customizado se fornecido
            if custom_context:
                context.update(custom_context)
            
            # Determina arquivo CSS baseado no template
            css_file = template_name.replace('.html', '.css')
            
            # Aplica esquema de cores se especificado
            css_content = None
            if color_scheme:
                logo_path = self._find_logo_file()
                # Gera esquemas (analisa logo se disponível, senão usa padrão)
                color_schemes = self.color_generator.generate_color_schemes(logo_path)
                
                # Lê CSS original
                css_path = self.html_engine.templates_dir / css_file
                if css_path.exists():
                    original_css = css_path.read_text(encoding='utf-8')
                    # Aplica esquema de cores
                    css_content = self.color_generator.apply_scheme_to_css(original_css, color_scheme)
                    info(f"Aplicando esquema de cores: {color_scheme}")
                else:
                    warning(f"Arquivo CSS não encontrado: {css_file}")
            
            # Gera PDF usando template HTML
            output_path = OUTPUT_DIR / output_filename
            if css_content:
                # Usa CSS customizado com esquema de cores
                html_content = self.html_engine.render_template(template_name, context)
                success_flag = self.html_engine.generate_pdf_from_html(
                    html_content=html_content,
                    css_content=css_content,
                    output_path=str(output_path)
                )
            else:
                # Usa CSS padrão
                success_flag = self.html_engine.generate_pdf_from_template(
                    template_name=template_name,
                    context=context,
                    css_file=css_file,
                    output_path=str(output_path)
                )
            
            if success_flag:
                success(f"Catálogo HTML gerado com sucesso: {output_path}")
                info(f"Template usado: {template_name}")
                info(f"Total de produtos: {len(products)}")
                return True
            else:
                error("Erro ao gerar catálogo HTML")
                return False
                
        except Exception as e:
            exception("Erro ao gerar catálogo HTML", e)
            return False
    
    def generate_catalog_from_canva(self, products: List[Dict[str, Any]], 
                                   html_content: str, css_content: str = None,
                                   output_filename: str = None,
                                   custom_context: Dict[str, Any] = None) -> bool:
        """
        Gera PDF a partir de template HTML/CSS criado no Canva
        
        Args:
            products: Lista de produtos
            html_content: Conteúdo HTML do Canva
            css_content: Conteúdo CSS do Canva (opcional)
            output_filename: Nome do arquivo de saída
            custom_context: Contexto adicional para o template
        
        Returns:
            True se PDF foi gerado com sucesso
        """
        try:
            if not products:
                error("Nenhum produto para gerar catálogo")
                return False
            
            if not output_filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_filename = f"catalogo_canva_{timestamp}.pdf"
            
            info(f"Gerando catálogo a partir de template do Canva com {len(products)} produtos")
            
            # Prepara contexto para o template
            context = {
                'produtos': products,
                'titulo': 'Thuca Kids',
                'data_geracao': self._get_portuguese_date(),
                'total_produtos': len(products)
            }
            
            # Adiciona contexto customizado se fornecido
            if custom_context:
                context.update(custom_context)
            
            # Renderiza template com contexto
            from jinja2 import Template
            template = Template(html_content)
            rendered_html = template.render(**context)
            
            # Gera PDF
            output_path = OUTPUT_DIR / output_filename
            success_flag = self.html_engine.generate_pdf_from_html(
                html_content=rendered_html,
                css_content=css_content,
                output_path=str(output_path)
            )
            
            if success_flag:
                success(f"Catálogo do Canva gerado com sucesso: {output_path}")
                info(f"Total de produtos: {len(products)}")
                return True
            else:
                error("Erro ao gerar catálogo do Canva")
                return False
                
        except Exception as e:
            exception("Erro ao gerar catálogo do Canva", e)
            return False
    
    def list_available_templates(self) -> List[str]:
        """
        Lista templates HTML disponíveis
        
        Returns:
            Lista de nomes de templates
        """
        return self.html_engine.list_available_templates()
    
    def list_available_color_schemes(self, logo_path: str = None) -> Dict[str, str]:
        """
        Lista esquemas de cores disponíveis
        
        Args:
            logo_path: Caminho para a logo (opcional)
        
        Returns:
            Dicionário com esquemas disponíveis
        """
        if not logo_path:
            logo_path = self._find_logo_file()
        
        # Gera esquemas (analisa logo se disponível, senão usa padrão)
        self.color_generator.generate_color_schemes(logo_path)
        return self.color_generator.get_scheme_info()
    
    def create_template_from_canva(self, template_name: str, html_content: str, 
                                  css_content: str = None) -> bool:
        """
        Cria um novo template a partir de conteúdo HTML/CSS do Canva
        
        Args:
            template_name: Nome do template (sem extensão)
            html_content: Conteúdo HTML
            css_content: Conteúdo CSS (opcional)
        
        Returns:
            True se template foi criado com sucesso
        """
        return self.html_engine.create_template_from_canva(template_name, html_content, css_content)
    
    def _find_logo_file(self) -> Optional[str]:
        """
        Procura por arquivo de logo na pasta assets/logos
        
        Returns:
            Caminho para o arquivo de logo ou None se não encontrado
        """
        try:
            logo_dir = Path("assets/logos")
            if not logo_dir.exists():
                debug("Pasta de logos não encontrada")
                return None
            
            # Lista de nomes prioritários para a logo
            logo_names = [
                "logo_principal",
                "logo_horizontal", 
                "logo",
                "logo_thuca_kids",
                "thuca_kids"
            ]
            
            # Extensões suportadas
            extensions = [".png", ".jpg", ".jpeg", ".svg"]
            
            # Procura pelos arquivos na ordem de prioridade
            for name in logo_names:
                for ext in extensions:
                    logo_file = logo_dir / f"{name}{ext}"
                    if logo_file.exists():
                        absolute_path = logo_file.resolve()
                        info(f"Logo encontrada: {absolute_path}")
                        return str(absolute_path)
            
            # Se não encontrou pelos nomes específicos, pega qualquer arquivo de imagem
            for ext in extensions:
                logo_files = list(logo_dir.glob(f"*{ext}"))
                if logo_files:
                    absolute_path = logo_files[0].resolve()
                    info(f"Logo encontrada (genérica): {absolute_path}")
                    return str(absolute_path)
            
            debug("Nenhuma logo encontrada na pasta assets/logos")
            return None
            
        except Exception as e:
            exception("Erro ao procurar arquivo de logo", e)
            return None
    
    def _get_portuguese_date(self) -> str:
        """
        Retorna data atual formatada em português
        
        Returns:
            String com mês e ano em português
        """
        months = {
            1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
            5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
            9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
        }
        
        now = datetime.now()
        month_name = months[now.month]
        year = now.year
        
        return f"{month_name} {year}"
