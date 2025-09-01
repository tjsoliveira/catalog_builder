"""
Motor de templates HTML/CSS para geração de PDFs
"""
from typing import List, Dict, Any, Optional
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, Template
import weasyprint
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

from config.settings import OUTPUT_DIR
from src.logger import info, success, error, warning, debug, exception


class HTMLTemplateEngine:
    """Motor para renderizar templates HTML/CSS em PDF"""
    
    def __init__(self, templates_dir: str = "src/pdf_generator/templates"):
        """
        Inicializa o motor de templates
        
        Args:
            templates_dir: Diretório onde estão os templates
        """
        self.templates_dir = Path(templates_dir)
        self.templates_dir.mkdir(exist_ok=True)
        
        # Configura Jinja2
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            autoescape=True
        )
        
        # Configuração de fontes para WeasyPrint
        self.font_config = FontConfiguration()
        
        info(f"Motor de templates HTML inicializado: {self.templates_dir}")
    
    def render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """
        Renderiza um template HTML com os dados fornecidos
        
        Args:
            template_name: Nome do arquivo de template
            context: Dados para renderizar no template
        
        Returns:
            HTML renderizado como string
        """
        try:
            template = self.jinja_env.get_template(template_name)
            html_content = template.render(**context)
            debug(f"Template '{template_name}' renderizado com sucesso")
            return html_content
        except Exception as e:
            exception(f"Erro ao renderizar template '{template_name}'", e)
            raise
    
    def generate_pdf_from_html(self, html_content: str, css_content: str = None, 
                              output_path: str = None) -> bool:
        """
        Gera PDF a partir de conteúdo HTML/CSS
        
        Args:
            html_content: Conteúdo HTML
            css_content: Conteúdo CSS (opcional)
            output_path: Caminho do arquivo PDF de saída
        
        Returns:
            True se PDF foi gerado com sucesso
        """
        try:
            if not output_path:
                output_path = OUTPUT_DIR / "catalogo_html.pdf"
            
            # Cria objeto HTML
            html_doc = HTML(string=html_content)
            
            # Adiciona CSS se fornecido
            stylesheets = []
            if css_content:
                stylesheets.append(CSS(string=css_content))
            
            # Gera PDF
            html_doc.write_pdf(
                str(output_path),
                stylesheets=stylesheets,
                font_config=self.font_config
            )
            
            success(f"PDF gerado com sucesso: {output_path}")
            return True
            
        except Exception as e:
            exception("Erro ao gerar PDF a partir de HTML", e)
            return False
    
    def generate_pdf_from_template(self, template_name: str, context: Dict[str, Any],
                                  css_file: str = None, output_path: str = None) -> bool:
        """
        Gera PDF a partir de um template HTML
        
        Args:
            template_name: Nome do arquivo de template
            context: Dados para renderizar
            css_file: Arquivo CSS (opcional)
            output_path: Caminho do arquivo PDF de saída
        
        Returns:
            True se PDF foi gerado com sucesso
        """
        try:
            # Renderiza template
            html_content = self.render_template(template_name, context)
            
            # Lê CSS se fornecido
            css_content = None
            if css_file:
                css_path = self.templates_dir / css_file
                if css_path.exists():
                    css_content = css_path.read_text(encoding='utf-8')
                    debug(f"CSS carregado: {css_file}")
                else:
                    warning(f"Arquivo CSS não encontrado: {css_file}")
            
            # Gera PDF
            return self.generate_pdf_from_html(html_content, css_content, output_path)
            
        except Exception as e:
            exception(f"Erro ao gerar PDF do template '{template_name}'", e)
            return False
    
    def list_available_templates(self) -> List[str]:
        """
        Lista templates HTML disponíveis
        
        Returns:
            Lista de nomes de templates
        """
        html_files = list(self.templates_dir.glob("*.html"))
        return [f.name for f in html_files]
    
    def list_available_css(self) -> List[str]:
        """
        Lista arquivos CSS disponíveis
        
        Returns:
            Lista de nomes de arquivos CSS
        """
        css_files = list(self.templates_dir.glob("*.css"))
        return [f.name for f in css_files]
    
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
        try:
            # Salva arquivo HTML
            html_path = self.templates_dir / f"{template_name}.html"
            html_path.write_text(html_content, encoding='utf-8')
            
            # Salva arquivo CSS se fornecido
            if css_content:
                css_path = self.templates_dir / f"{template_name}.css"
                css_path.write_text(css_content, encoding='utf-8')
            
            success(f"Template '{template_name}' criado com sucesso")
            return True
            
        except Exception as e:
            exception(f"Erro ao criar template '{template_name}'", e)
            return False
