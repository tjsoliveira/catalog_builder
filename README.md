# 📚 Catalog Builder

**Gerador Automático de Catálogo de Roupas**

Um sistema Python que conecta com Google Sheets, baixa dados e imagens das roupas, e gera um PDF profissional automaticamente.

## 🎯 Funcionalidades

- ✅ **Integração com Google Sheets** - Lê dados diretamente da planilha
- ✅ **Download automático de imagens** - Baixa e otimiza imagens dos produtos
- ✅ **Geração de PDF profissional** - Layout em grid com design elegante
- ✅ **Processamento de dados** - Valida e limpa informações dos produtos
- ✅ **Design elegante** - Template moderno e profissional
- ✅ **Totalmente automatizado** - Um comando gera o catálogo completo
- ✅ **Configuração via variáveis de ambiente** - Configuração flexível e segura

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

### 5. Configure as variáveis de ambiente

1. Copie o arquivo de exemplo:
```bash
cp .env.example .env
```

2. Edite o arquivo `.env` e configure suas variáveis:
```bash
# ID da planilha (obrigatório)
SPREADSHEET_ID=1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms

# Configurações opcionais
SHEET_NAME=Sheet1
OUTPUT_FILENAME=
CATALOG_TYPE=grid
DOWNLOAD_IMAGES=true

# Informações de contato (opcionais)
WHATSAPP=(11) 99999-9999
INSTAGRAM=@thucakids
CONTATO=Loja • Tel: (11) 9999-9999
ENDERECO=Rua das Flores, 123 - Centro - SP
```

## 📊 Estrutura do Google Sheets

Sua planilha deve ter as seguintes colunas:

| Nome | Preço | Descrição | URL da Imagem | Categoria | Tamanho | Cor |
|------|-------|-----------|---------------|-----------|---------|-----|
| Vestido Floral | 89,90 | Vestido elegante... | https://... | Vestidos | M | Azul |
| Blusa Básica | 45,00 | Blusa confortável... | https://... | Blusas | P | Branco |

## 🎨 Uso

### Comando Básico (Recomendado)
```bash
python main.py
```
O sistema usará as configurações do arquivo `.env`.

### Comandos Avançados
```bash
# Sobrescrever configurações do .env
python main.py --sheet-name "Produtos" --output "meu_catalogo.pdf"

# Gerar catálogo simples (sem imagens)
python main.py --type simple --no-images

# Usar planilha diferente temporariamente
python main.py --spreadsheet-id "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
```

### Exemplo Completo
```bash
python main.py --sheet-name "Estoque" --output "catalogo_2024.pdf" --type grid
```

## ⚙️ Configurações

### Variáveis de Ambiente (.env)

| Variável | Obrigatório | Padrão | Descrição |
|----------|-------------|--------|-----------|
| `SPREADSHEET_ID` | ✅ | - | ID da planilha do Google Sheets |
| `SHEET_NAME` | ❌ | Sheet1 | Nome da aba da planilha |
| `OUTPUT_FILENAME` | ❌ | auto | Nome do arquivo de saída |
| `CATALOG_TYPE` | ❌ | grid | Tipo: grid ou simple |
| `DOWNLOAD_IMAGES` | ❌ | true | Baixar imagens: true/false |
| `WHATSAPP` | ❌ | - | Número do WhatsApp (ex: (11) 99999-9999) |
| `INSTAGRAM` | ❌ | - | Username do Instagram (ex: @thucakids) |
| `CONTATO` | ❌ | - | Informações gerais de contato |
| `ENDERECO` | ❌ | - | Endereço da loja |

### Configurações do PDF (config/settings.py)

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
python main.py --verbose
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

### Erro de Variáveis de Ambiente
- Verifique se o arquivo `.env` existe
- Confirme se `SPREADSHEET_ID` está configurado
- Use `cp .env.example .env` para criar o arquivo

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
