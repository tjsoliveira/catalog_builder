# Template HTML/CSS para Catálogos

Este diretório contém o template HTML/CSS padrão para gerar catálogos em PDF.

## Template Padrão

### catalogo_simples.html + catalogo_simples.css
- **Design**: Moderno e elegante
- **Layout**: Grid dinâmico com cards elegantes (padrão: 3 colunas)
- **Características**:
  - Design inspirado no Tailwind CSS
  - Cards com sombras e bordas arredondadas
  - Layout responsivo
  - Visual profissional
  - Colunas configuráveis

## Como Usar

### Via Linha de Comando
```bash
# Gerar catálogo com configurações padrão (3 colunas)
python main.py

# Com número de colunas personalizado
python main.py --columns 2
python main.py --columns 4

# Combinando opções
python main.py --columns 2 --output meu_catalogo.pdf
```

### Via Código Python
```python
from main import CatalogBuilder

builder = CatalogBuilder()

# Gerar catálogo com configurações padrão
success = builder.generate_catalog(
    products=produtos,
    output_filename="meu_catalogo.pdf"
)

# Com número de colunas personalizado
success = builder.generate_catalog(
    products=produtos,
    output_filename="meu_catalogo.pdf",
    columns=2
)

# Com número de colunas personalizado
success = builder.generate_catalog(
    products=produtos,
    output_filename="meu_catalogo.pdf",
    columns=4
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
- `titulo`: Título do catálogo (padrão: "Catálogo de Produtos")
- `subtitulo`: Subtítulo do catálogo (opcional)
- `logo_path`: Caminho da logo (se disponível)
- `columns`: Número de colunas no grid (padrão: 2)
- `contato`: Informações de contato (opcional)
- `endereco`: Endereço (opcional)

### 3. Propriedades dos Produtos
Cada produto tem as seguintes propriedades:
- `name`: Nome do produto
- `price`: Preço (float)
- `description`: Descrição
- `size`: Tamanho
- `color`: Cor
- `local_image_path`: Caminho da imagem local
- `destaque`: Badge de destaque (ex: "NOVO", "OFERTA")

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

Veja o template `catalogo_simples.html` como referência para criar seus próprios templates.

## Configuração de Colunas

O número de colunas pode ser configurado de várias formas:

### Via Linha de Comando
```bash
python main.py --columns 2  # 2 colunas
python main.py --columns 4  # 4 colunas
```

### Via Variável de Ambiente
```bash
export COLUMNS=2
export CONTATO="Thuca Kids • WhatsApp: (11) 99999-9999 • Instagram: @thucakids"
export ENDERECO="Rua das Flores, 123 - Centro - São Paulo/SP"
python main.py
```

### Via Código Python
```python
builder.generate_catalog(products, columns=2)
```

### No Template HTML
```html
<div class="grid gap-6" style="grid-template-columns: repeat({{ columns or 2 }}, 1fr);">
```
