from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import httpx

app = FastAPI(
    title="Casa de Sucos API", 
    description="API para gerenciamento de sucos e consulta nutricional de frutas"
)

# "Banco de dados" em memória
sucos_db: Dict[int, dict] = {}
suco_id_counter = 1

# Modelos Pydantic para validação de dados
class SucoCreate(BaseModel):
    nome: str
    frutas: List[str]
    tem_gosto_de: str

class SucoUpdate(BaseModel):
    frutas: List[str]

# Função auxiliar para consultar a API Fruityvice com tratamento de erros robusto
async def fetch_fruit_data(nome: str) -> dict:
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # A API Fruityvice espera os nomes em inglês
            url = f"https://www.fruityvice.com/api/fruit/{nome.lower()}"
            response = await client.get(url)
            
            if response.status_code == 404:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Fruta '{nome}' não encontrada na base da Fruityvice. Tente o nome em inglês (ex: apple, banana)."
                )
            
            response.raise_for_status()
            return response.json()
            
    except httpx.RequestError as exc:
        # Captura erros de conexão, timeout, ou caso a Fruityvice esteja fora do ar
        raise HTTPException(
            status_code=503, 
            detail=f"Erro de comunicação com a API Fruityvice: {str(exc)}"
        )
    except httpx.HTTPStatusError as exc:
        # Captura outros erros HTTP (500, 403, etc) retornados pela Fruityvice
        raise HTTPException(
            status_code=exc.response.status_code, 
            detail=f"Erro na API externa: {exc.response.text}"
        )

@app.get("/frutas/{nome}", summary="Consulta informações nutricionais de uma fruta")
async def get_fruta(nome: str):
    data = await fetch_fruit_data(nome)
    
    return {
        "nome": data.get("name"),
        "calorias": data.get("nutritions", {}).get("calories", 0),
        "acucar": data.get("nutritions", {}).get("sugar", 0)
    }

@app.post("/sucos", status_code=201, summary="Cadastra um novo suco")
async def create_suco(suco: SucoCreate):
    global suco_id_counter
    total_calorias = 0.0
    total_acucar = 0.0

    # Consulta cada fruta e acumula os valores nutricionais
    for fruta in suco.frutas:
        data = await fetch_fruit_data(fruta)
        total_calorias += data.get("nutritions", {}).get("calories", 0)
        total_acucar += data.get("nutritions", {}).get("sugar", 0)

    novo_suco = {
        "id": suco_id_counter,
        "nome": suco.nome,
        "frutas": suco.frutas,
        "tem_gosto_de": suco.tem_gosto_de,
        "total_calorias": round(total_calorias, 2),
        "total_acucar": round(total_acucar, 2)
    }
    
    sucos_db[suco_id_counter] = novo_suco
    suco_id_counter += 1

    return novo_suco

@app.get("/sucos", summary="Lista todos os sucos cadastrados")
async def list_sucos():
    return list(sucos_db.values())

# Desafio Bônus: Atualizar apenas as frutas e recalcular
@app.put("/sucos/{id}", summary="Atualiza as frutas de um suco e recalcula os valores")
async def update_suco(id: int, suco_update: SucoUpdate):
    if id not in sucos_db:
        raise HTTPException(status_code=404, detail="Suco não encontrado.")
    
    suco_atual = sucos_db[id]
    total_calorias = 0.0
    total_acucar = 0.0

    for fruta in suco_update.frutas:
        data = await fetch_fruit_data(fruta)
        total_calorias += data.get("nutritions", {}).get("calories", 0)
        total_acucar += data.get("nutritions", {}).get("sugar", 0)

    suco_atual["frutas"] = suco_update.frutas
    suco_atual["total_calorias"] = round(total_calorias, 2)
    suco_atual["total_acucar"] = round(total_acucar, 2)

    return suco_atual