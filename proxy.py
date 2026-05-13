"""
ConciliaML — Proxy FastAPI
Resolve CORS entre o browser e a API do Mercado Livre

Instalação:
  pip install fastapi uvicorn httpx

Rodar local:
  uvicorn proxy:app --host 0.0.0.0 --port 8000

Deploy gratuito no Railway:
  1. Suba esse arquivo + requirements.txt no GitHub
  2. railway.app → New Project → Deploy from GitHub
  3. Sua URL: https://seu-projeto.up.railway.app
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
import httpx

app = FastAPI(title="ConciliaML Proxy")

# Libera CORS para qualquer origem
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

ML_BASE = "https://api.mercadolibre.com"

@app.api_route("/proxy/{path:path}", methods=["GET","POST","PUT","DELETE","PATCH"])
async def proxy(path: str, request: Request):
    # Montar URL do ML
    ml_url = f"{ML_BASE}/{path}"
    if request.query_params:
        ml_url += "?" + str(request.query_params)

    # Repassar headers relevantes
    headers = {}
    if auth := request.headers.get("authorization"):
        headers["authorization"] = auth
    if ct := request.headers.get("content-type"):
        headers["content-type"] = ct
    headers["accept"] = "application/json"
    headers["user-agent"] = "ConciliaML-Proxy/1.0"

    # Corpo da requisição
    body = await request.body() if request.method not in ("GET","HEAD") else None

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.request(
            method=request.method,
            url=ml_url,
            headers=headers,
            content=body,
        )

    return Response(
        content=resp.content,
        status_code=resp.status_code,
        media_type=resp.headers.get("content-type", "application/json"),
    )

@app.get("/")
def health():
    return {"status": "ok", "proxy": "ConciliaML v1.0"}
