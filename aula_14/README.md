# API Casa de Sucos 🧃

API desenvolvida em Python com FastAPI para o gerenciamento de sucos e consulta de dados nutricionais de frutas (integração com a API Fruityvice).

**Funcionalidades**
- `GET /frutas/{nome}`: Consulta calorias e açúcar de uma fruta.
- `POST /sucos`: Cria um suco e calcula valores nutricionais totais.
- `GET /sucos`: Lista sucos cadastrados.
- `PUT /sucos/{id}`: Atualiza as frutas de um suco e recalcula os valores.

**Como executar**
1. Clone o repositório.
2. Crie e ative o ambiente virtual (`python -m venv venv` e `venv\Scripts\activate` ou `source venv/bin/activate`).
3. Instale as dependências: `pip install -r requirements.txt`.
4. Rode o servidor: `python -m uvicorn main:app --reload`.
5. Acesse o Swagger em: `http://127.0.0.1:8000/docs` para testar.