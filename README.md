# 📚 Catalog Builder

**Gerador Automático de Catálogo de Roupas**

Um sistema Python que conecta com Google Sheets, baixa dados e imagens das roupas, e gera um PDF profissional automaticamente.

## 🎯 Funcionalidades

- ✅ **Integração com Google Sheets** - Lê dados diretamente da planilha
- ✅ **Download automático de imagens** - Baixa e otimiza imagens dos produtos
- ✅ **Geração de PDF profissional** - Layout em grid com design elegante
- ✅ **Processamento de dados** - Valida e limpa informações dos produtos
- ✅ **Múltiplos estilos** - Templates minimalista, elegante e moderno
- ✅ **Totalmente automatizado** - Um comando gera o catálogo completo

## 🚀 Instalação

### 1. Clone o repositório
```bash
git clone <seu-repositorio>
cd catalog_builder
```

### 2. Crie um ambiente virtual
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

### 4. Configure o Google Sheets API

1. Acesse o [Google Cloud Console](https://console.cloud.google.com/)
2. Crie um novo projeto ou selecione um existente
3. Ative a API do Google Sheets
4. Crie credenciais (OAuth 2.0)
5. Baixe o arquivo `credentials.json`
6. Coloque o arquivo em `config/credentials.json`

## 📊 Estrutura do Google Sheets

Sua planilha deve ter as seguintes colunas:

| Nome | Preço | Descrição | URL da Imagem | Categoria | Tamanho | Cor |
|------|-------|-----------|---------------|-----------|---------|-----|
| Vestido Floral | 89,90 | Vestido elegante... | https://... | Vestidos | M | Azul |
| Blusa Básica | 45,00 | Blusa confortável... | https://... | Blusas | P | Branco |

## 🎨 Uso

### Comando Básico
```bash
python main.py SPREADSHEET_ID
```

### Comandos Avançados
```bash
# Especificar aba da planilha
python main.py SPREADSHEET_ID --sheet-name "Produtos"

# Gerar catálogo simples (sem imagens)
python main.py SPREADSHEET_ID --type simple

# Nome personalizado do arquivo
python main.py SPREADSHEET_ID --output "meu_catalogo.pdf"

# Não baixar imagens
python main.py SPREADSHEET_ID --no-images
```

### Exemplo Completo
```bash
python main.py 1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms --sheet-name "Estoque" --output "catalogo_2024.pdf"
```

## 📁 Estrutura do Projeto

```
catalog_builder/
├── src/
│   ├── google_sheets/          # Integração com Google Sheets
│   ├── image_processing/       # Download e otimização de imagens
│   └── pdf_generator/          # Geração de PDF
├── config/
│   ├── settings.py            # Configurações
│   └── credentials.json       # Credenciais Google (não versionar)
├── output/                    # PDFs gerados
├── temp/                     # Imagens temporárias
├── main.py                   # Script principal
└── requirements.txt          # Dependências
```

## ⚙️ Configurações

Edite `config/settings.py` para personalizar:

- **Layout do PDF**: Margens, tamanho da página, grid
- **Imagens**: Tamanho máximo, qualidade, formatos
- **Google Sheets**: Nomes das colunas esperadas

## 🎨 Tipos de Catálogo

### Grid (Padrão)
- Layout em grade com imagens
- Design profissional
- Ideal para catálogos visuais

### Simple
- Lista simples de produtos
- Sem imagens
- Ideal para listas de preços

## 🔧 Desenvolvimento

### Executar em modo desenvolvimento
```bash
# Instalar dependências de desenvolvimento
pip install -r requirements.txt

# Executar com logs detalhados
python main.py SPREADSHEET_ID --verbose
```

### Estrutura dos Módulos

- **GoogleSheetsConnector**: Conecta e lê dados da planilha
- **DataProcessor**: Valida e processa dados dos produtos
- **ImageDownloader**: Baixa imagens das URLs
- **ImageOptimizer**: Otimiza imagens para PDF
- **PDFBuilder**: Gera o PDF final

## 🐛 Solução de Problemas

### Erro de Autenticação
- Verifique se `credentials.json` está em `config/`
- Confirme se a API do Google Sheets está ativada
- Execute o script e autorize no navegador

### Imagens não baixam
- Verifique se as URLs estão corretas
- Confirme se as imagens são públicas
- Verifique sua conexão com a internet

### PDF não gera
- Verifique se há produtos válidos na planilha
- Confirme se as colunas estão com os nomes corretos
- Verifique permissões de escrita na pasta `output/`

## 📝 Logs

O sistema gera logs detalhados durante a execução:
- ✅ Sucessos
- ❌ Erros
- 📊 Estatísticas
- 🔄 Progresso

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 🆘 Suporte

Se encontrar problemas:

1. Verifique a documentação
2. Consulte os logs de erro
3. Abra uma issue no GitHub
4. Entre em contato

---

**Desenvolvido com ❤️ para automatizar catálogos de roupas**