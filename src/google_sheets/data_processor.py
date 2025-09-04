"""
Processador de dados do Google Sheets
"""
from typing import List, Dict, Any, Optional
import re
from decimal import Decimal, InvalidOperation

from config.settings import SHEETS_CONFIG


class DataProcessor:
    """Classe para processar e validar dados dos produtos"""
    
    def __init__(self):
        self.required_columns = [
            SHEETS_CONFIG["columns"]["name"],
            SHEETS_CONFIG["columns"]["price"],
            SHEETS_CONFIG["columns"]["image_url"]
        ]
    
    def validate_product(self, product: Dict[str, Any]) -> bool:
        """
        Valida se um produto tem os dados mínimos necessários
        
        Args:
            product: Dicionário com dados do produto
        
        Returns:
            True se produto é válido
        """
        for column in self.required_columns:
            if not product.get(column) or not str(product[column]).strip():
                return False
        
        return True
    
    def clean_price(self, price_str: str) -> Optional[float]:
        """
        Limpa e converte string de preço para float
        
        Args:
            price_str: String com o preço
        
        Returns:
            Float com o preço ou None se inválido
        """
        if not price_str:
            return None
        
        try:
            # Remove caracteres não numéricos exceto vírgula e ponto
            cleaned = re.sub(r'[^\d,.]', '', str(price_str))
            
            # Substitui vírgula por ponto (formato brasileiro)
            cleaned = cleaned.replace(',', '.')
            
            # Converte para float
            price = float(cleaned)
            return price if price >= 0 else None
            
        except (ValueError, InvalidOperation):
            return None
    
    def clean_text(self, text: str) -> str:
        """
        Limpa texto removendo espaços extras e caracteres especiais
        
        Args:
            text: Texto a ser limpo
        
        Returns:
            Texto limpo
        """
        if not text:
            return ""
        
        # Remove espaços extras e quebras de linha
        cleaned = re.sub(r'\s+', ' ', str(text).strip())
        return cleaned
    
    def _process_destaque(self, destaque_value: str) -> str:
        """
        Processa valor de destaque (TRUE/FALSE ou texto)
        
        Args:
            destaque_value: Valor da coluna Destaque
        
        Returns:
            Texto do destaque ou string vazia
        """
        if not destaque_value:
            return ""
        
        # Converte para string e limpa
        destaque_str = str(destaque_value).strip().upper()
        
        # Se for TRUE, retorna "DESTAQUE"
        if destaque_str == "TRUE":
            return "DESTAQUE"
        
        # Se for FALSE, retorna string vazia
        if destaque_str == "FALSE":
            return ""
        
        # Se for outro texto, retorna o texto limpo
        return self.clean_text(destaque_value)
    
    def validate_image_url(self, url: str) -> bool:
        """
        Valida se URL da imagem é válida
        
        Args:
            url: URL da imagem
        
        Returns:
            True se URL é válida
        """
        if not url:
            return False
        
        # Verifica se é uma URL válida
        url_pattern = re.compile(
            r'^https?://'  # http:// ou https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        return bool(url_pattern.match(url))
    
    def process_products(self, raw_products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Processa lista de produtos brutos, validando e limpando dados
        
        Args:
            raw_products: Lista de produtos brutos do Google Sheets
        
        Returns:
            Lista de produtos processados e válidos
        """
        processed_products = []
        
        for product in raw_products:
            # Valida produto
            if not self.validate_product(product):
                print(f"Produto inválido ignorado: {product.get('Nome', 'Sem nome')}")
                continue
            
            # Processa dados
            processed_product = {
                "name": self.clean_text(product.get(SHEETS_CONFIG["columns"]["name"], "")),
                "price": self.clean_price(product.get(SHEETS_CONFIG["columns"]["price"], "")),
                "description": self.clean_text(product.get(SHEETS_CONFIG["columns"]["description"], "")),
                "image_url": product.get(SHEETS_CONFIG["columns"]["image_url"], ""),
                "category": self.clean_text(product.get(SHEETS_CONFIG["columns"]["category"], "")),
                "size": self.clean_text(product.get(SHEETS_CONFIG["columns"]["size"], "")),
                "color": self.clean_text(product.get(SHEETS_CONFIG["columns"]["color"], "")),
                "destaque": self._process_destaque(product.get("Destaque", ""))  # Coluna opcional
            }
            
            # Valida URL da imagem
            if not self.validate_image_url(processed_product["image_url"]):
                print(f"URL de imagem inválida para produto: {processed_product['name']}")
                continue
            
            # Valida preço
            if processed_product["price"] is None:
                print(f"Preço inválido para produto: {processed_product['name']}")
                continue
            
            processed_products.append(processed_product)
        
        return processed_products
    
    def get_statistics(self, products: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Gera estatísticas dos produtos processados
        
        Args:
            products: Lista de produtos processados
        
        Returns:
            Dicionário com estatísticas
        """
        if not products:
            return {
                "total_products": 0,
                "price_range": {"min": 0, "max": 0, "average": 0},
                "categories": {},
                "sizes": {},
                "colors": {}
            }
        
        prices = [p["price"] for p in products if p["price"]]
        categories = [p["category"] for p in products if p["category"]]
        sizes = [p["size"] for p in products if p["size"]]
        colors = [p["color"] for p in products if p["color"]]
        
        return {
            "total_products": len(products),
            "price_range": {
                "min": min(prices) if prices else 0,
                "max": max(prices) if prices else 0,
                "average": sum(prices) / len(prices) if prices else 0
            },
            "categories": {cat: categories.count(cat) for cat in set(categories)},
            "sizes": {size: sizes.count(size) for size in set(sizes)},
            "colors": {color: colors.count(color) for color in set(colors)}
        }