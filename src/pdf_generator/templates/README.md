# Templates HTML/CSS para Catálogos

Este diretório contém templates HTML/CSS que podem ser usados para gerar catálogos em PDF com designs personalizados.

## Templates Disponíveis

### 1. catalogo_moderno.html + catalogo_moderno.css
- **Design**: Moderno e elegante
- **Layout**: Grid responsivo de produtos
- **Características**: 
  - Cards de produtos com sombras
  - Imagens otimizadas
  - Informações organizadas
  - Cores modernas

### 2. catalogo_simples.html + catalogo_simples.css
- **Design**: Simples e limpo
- **Layout**: Lista vertical de produtos
- **Características**:
  - Layout minimalista
  - Foco na informação
  - Fácil leitura
  - Ideal para impressão

## Como Usar

### Via Linha de Comando
```bash
# Usar template moderno
python main.py --type html --template catalogo_moderno.html

# Usar template simples
python main.py --type html --template catalogo_simples.html
```

### Via Código Python
```python
from src.pdf_generator.pdf_builder import PDFBuilder

builder = PDFBuilder()

# Gerar catálogo com template HTML
success = builder.generate_html_catalog(
    products=produtos,
    template_name="catalogo_moderno.html",
    output_filename="meu_catalogo.pdf"
)
```

## Criando Templates Personalizados

### 1. Estrutura HTML
Seu template HTML deve usar a sintaxe Jinja2 para variáveis:

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>{{ titulo or "Thuca Kids" }}</title>
    <link rel="stylesheet" href="seu_template.css">
</head>
<body>
    <div class="container">
        <h1>{{ titulo or "Thuca Kids" }}</h1>
        <p class="subtitle">Catálogo - {{ data_geracao or "Janeiro 2025" }}</p>
        
        {% for produto in produtos %}
        <div class="product-card">
            <img src="file://{{ produto.local_image_path }}" alt="{{ produto.name }}">
            <h3>{{ produto.name }}</h3>
            <p class="price">R$ {{ "%.2f"|format(produto.price)|replace(".", ",") }}</p>
            <p>{{ produto.description }}</p>
        </div>
        {% endfor %}
    </div>
</body>
</html>
```

### 2. Variáveis Disponíveis
- `produtos`: Lista de produtos
- `titulo`: Título do catálogo (padrão: "Thuca Kids")
- `data_geracao`: Data de geração em português (ex: "Setembro 2025")
- `total_produtos`: Número total de produtos

### 3. Propriedades dos Produtos
Cada produto tem as seguintes propriedades:
- `name`: Nome do produto
- `price`: Preço (float)
- `description`: Descrição
- `category`: Categoria
- `size`: Tamanho
- `color`: Cor
- `local_image_path`: Caminho da imagem local

### 4. CSS para PDF
Use CSS otimizado para impressão:
```css
@page {
    size: A4;
    margin: 20mm;
}

.product-card {
    page-break-inside: avoid;
    break-inside: avoid;
}
```

## Templates do Canva

Para usar templates criados no Canva:

1. Exporte seu design como HTML/CSS do Canva
2. Use o método `generate_catalog_from_canva()`:

```python
builder = PDFBuilder()

success = builder.generate_catalog_from_canva(
    products=produtos,
    html_content=html_do_canva,
    css_content=css_do_canva,
    output_filename="catalogo_canva.pdf"
)
```

## Dicas para Templates

1. **Imagens**: Use `file://` para caminhos de imagens locais
2. **Quebras de página**: Use `page-break-before: always` no CSS
3. **Responsividade**: Templates são renderizados em A4
4. **Fontes**: Use fontes web-safe ou inclua fontes personalizadas
5. **Cores**: Teste cores que funcionem bem em impressão

## Exemplo Completo

Veja os templates `catalogo_moderno.html` e `catalogo_simples.html` como referência para criar seus próprios templates.
