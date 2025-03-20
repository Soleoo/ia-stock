# ia-stock

O **ia-stock** é um aplicativo de gerenciamento de estoque e vendas que utiliza inteligência artificial para fornecer análises avançadas e responder a perguntas relacionadas ao estoque, vendas e fornecedores. Ele é construído com Flask e integra o modelo de linguagem generativa da Google para consultas inteligentes.

## Funcionalidades

- **Gerenciamento de Produtos**: Adicionar, atualizar, listar e excluir produtos.
- **Gerenciamento de Vendas**: Registrar, listar e excluir vendas, com cálculo automático do preço total.
- **Gerenciamento de Fornecedores**: Adicionar, atualizar, listar e excluir fornecedores.
- **Análises de Estoque e Vendas**:
  - Produtos com baixo estoque.
  - Distribuição de categorias.
  - Valor total do estoque.
  - Tendências de vendas e previsão de receita futura.
  - Produtos mais vendidos.
  - Previsão de esgotamento de estoque.
- **Consultas Inteligentes**: Responder a perguntas sobre o estoque, vendas e fornecedores utilizando IA.

## Tecnologias Utilizadas

- **Backend**: Flask
- **Banco de Dados**: SQLAlchemy com suporte a SQLite ou outros bancos compatíveis.
- **IA**: Integração com o modelo Google Generative AI via LangChain.
- **Outras Bibliotecas**: Pandas, NumPy, Scikit-learn (para análises avançadas).

## Requisitos

- Python 3.8 ou superior
- Banco de dados compatível com SQLAlchemy
- Conta Google com chave de API para o modelo generativo

## Instalação

1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-usuario/ia-stock.git
   cd ia-stock
   ```

2. Crie um ambiente virtual e instale as dependências:
   ```bash
   python -m venv venv
   source venv/bin/activate  # No Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Configure as variáveis de ambiente no arquivo `.env`:
   ```
   DATABASE_URL=sqlite:///ia_stock.db
   GOOGLE_API_KEY=sua_chave_google_api
   ```

4. Inicialize o banco de dados:
   ```bash
   python app.py
   ```

## Uso

1. Inicie o servidor:
   ```bash
   python app.py
   ```

2. Acesse a API em `http://192.168.0.33:8080`.

### Endpoints Principais

- **Produtos**:
  - `GET /api/products`: Lista todos os produtos.
  - `POST /api/products`: Adiciona um novo produto.
  - `PUT /api/products/<id>`: Atualiza um produto existente.
  - `DELETE /api/products/<id>`: Exclui um produto.

- **Vendas**:
  - `GET /api/sales`: Lista todas as vendas.
  - `POST /api/sales`: Registra uma nova venda.
  - `DELETE /api/sales/<id>`: Exclui uma venda.

- **Fornecedores**:
  - `GET /api/suppliers`: Lista todos os fornecedores.
  - `POST /api/suppliers`: Adiciona um novo fornecedor.
  - `PUT /api/suppliers/<id>`: Atualiza um fornecedor existente.
  - `DELETE /api/suppliers/<id>`: Exclui um fornecedor.

- **Análises**:
  - `GET /api/analytics/sales`: Obtém análises de vendas.
  - `GET /api/analytics/inventory`: Obtém análises de estoque.
  - `GET /api/analytics/advanced`: Obtém análises avançadas.

- **Consultas Inteligentes**:
  - `POST /api/query`: Envia uma pergunta sobre o estoque, vendas ou fornecedores.

## Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou enviar pull requests.

## Licença

Este projeto está licenciado sob a [MIT License](LICENSE).