# Gerador de Catálogos com Todos os Esquemas de Cores

Este script gera automaticamente catálogos PDF com todos os esquemas de cores disponíveis, permitindo comparar diferentes estilos visuais.

## Como usar

### Pré-requisitos
1. Configure o arquivo `.env` com suas credenciais:
   ```bash
   SPREADSHEET_ID=sua_planilha_id
   SHEET_NAME=nome_da_aba
   ```

2. Ative o ambiente virtual:
   ```bash
   source venv/bin/activate
   ```

### Executar o script

```bash
python generate_all_schemes.py
```

### Ou executar diretamente (se tiver permissão):
```bash
./generate_all_schemes.py
```

## O que o script faz

1. **Conecta** com o Google Sheets usando as credenciais configuradas
2. **Baixa** os dados dos produtos da planilha
3. **Baixa** as imagens dos produtos automaticamente
4. **Gera 3 catálogos** com diferentes esquemas de cores:
   - `catalogo_default.pdf` - Esquema padrão
   - `catalogo_dark_mode.pdf` - Modo escuro
   - `catalogo_minimal.pdf` - Minimalista

## Esquemas de cores disponíveis

### 🎨 Default (Padrão)
- **Fundo**: Branco (#FFFFFF)
- **Título**: Laranja chamativo (#F28E30)
- **Descrição**: Azul claro (#6BC0C9)
- **Preço**: Roxo forte (#7F4C9E)
- **Bordas**: Turquesa (#00A79D)
- **Destaque**: Azul bebê (#7AD0E0)

### 🌙 Dark Mode (Modo Escuro)
- **Fundo**: Cinza escuro (#1C1C1C)
- **Título**: Laranja chamativo (#F28E30)
- **Descrição**: Azul bebê (#7AD0E0)
- **Preço**: Roxo forte (#7F4C9E)
- **Bordas**: Turquesa (#00A79D)
- **Destaque**: Azul claro (#6BC0C9)

### 🎯 Minimal (Minimalista)
- **Fundo**: Cinza claro (#F8F8F8)
- **Título**: Cinza escuro (#333333)
- **Descrição**: Azul claro (#6BC0C9)
- **Preço**: Laranja chamativo (#F28E30)
- **Bordas**: Cinza claro (#DDDDDD)
- **Destaque**: Turquesa (#00A79D)

## Personalização

Você pode modificar o script para:

1. **Alterar esquemas**: Edite a lista `schemes` no script
2. **Mudar template**: Altere `template_name` na configuração
3. **Configurar saída**: Modifique o padrão de nome dos arquivos
4. **Adicionar filtros**: Inclua lógica para filtrar produtos específicos

## Exemplo de saída

```
📚 Catalog Builder | ℹ️  Gerando catálogo com esquema: default
📚 Catalog Builder | ✅ Catálogo 'catalogo_default.pdf' gerado com sucesso!
📚 Catalog Builder | ℹ️  Gerando catálogo com esquema: dark_mode
📚 Catalog Builder | ✅ Catálogo 'catalogo_dark_mode.pdf' gerado com sucesso!
📚 Catalog Builder | ℹ️  Gerando catálogo com esquema: minimal
📚 Catalog Builder | ✅ Catálogo 'catalogo_minimal.pdf' gerado com sucesso!

📊 Resumo da geração:
✅ Sucessos: 3/3
❌ Falhas: 0/3

📁 Catálogos gerados em: /path/to/output
   - catalogo_default.pdf
   - catalogo_dark_mode.pdf
   - catalogo_minimal.pdf
```

## Troubleshooting

### Erro: "SPREADSHEET_ID não configurado"
- Verifique se o arquivo `.env` existe e contém `SPREADSHEET_ID=sua_id`

### Erro: "ModuleNotFoundError"
- Ative o ambiente virtual: `source venv/bin/activate`
- Instale as dependências: `pip install -r requirements.txt`

### Erro de autenticação
- Verifique se o arquivo de credenciais do Google está no local correto
- Confirme se o Service Account tem acesso à planilha

## Dicas

- **Compare os PDFs** lado a lado para escolher o melhor esquema
- **Use o modo escuro** para apresentações em ambientes com pouca luz
- **O minimalista** é ideal para impressão em preto e branco
- **O padrão** funciona bem para a maioria dos casos

---

💡 **Dica**: Execute este script sempre que quiser testar novos esquemas de cores ou quando atualizar os dados da planilha!
