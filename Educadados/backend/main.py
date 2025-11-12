from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np
from typing import Optional, List, Dict
import json
from pathlib import Path

app = FastAPI(title="EducaDados API", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cache global para os dataframes
cache = {}

def load_csv_data():
    """Carrega os CSVs na memória"""
    global cache
    
    # Ajuste os caminhos conforme sua estrutura
    files = {
        'censo': 'microdados_ed_basica_2024.csv',
        'resultados': 'RESULTADOS_2024.csv',
        'participantes': 'PARTICIPANTES_2024.csv',
        'itens': 'ITENS_PROVA_2024.csv'
    }
    
    for key, file in files.items():
        try:
            # Lê com limite de linhas para teste (remova nrows em produção)
            cache[key] = pd.read_csv(file, encoding='latin-1', low_memory=False, nrows=10000)
            print(f"✓ {key} carregado: {len(cache[key])} linhas")
        except Exception as e:
            print(f"✗ Erro ao carregar {key}: {e}")
            cache[key] = pd.DataFrame()

# Carrega dados na inicialização
@app.on_event("startup")
async def startup_event():
    load_csv_data()

@app.get("/")
async def root():
    return {
        "message": "EducaDados API",
        "version": "1.0.0",
        "endpoints": {
            "censo": "/api/censo/*",
            "enem": "/api/enem/*"
        }
    }

# ==================== ENDPOINTS CENSO ESCOLAR ====================

@app.get("/api/censo/overview")
async def censo_overview():
    """Dados essenciais do Censo Escolar"""
    df = cache.get('censo', pd.DataFrame())
    
    if df.empty:
        raise HTTPException(status_code=404, detail="Dados não encontrados")
    
    # Ajuste os nomes das colunas conforme seu CSV
    cols = df.columns.tolist()
    
    return {
        "total_escolas": len(df),
        "colunas_disponiveis": cols[:20],  # Primeiras 20 colunas
        "total_colunas": len(cols),
        "preview": df.head(5).to_dict('records')
    }

@app.get("/api/censo/estatisticas")
async def censo_stats():
    """Estatísticas gerais do Censo"""
    df = cache.get('censo', pd.DataFrame())
    
    if df.empty:
        return {"error": "Dados não carregados"}
    
    stats = {
        "total_registros": len(df),
        "colunas": df.columns.tolist(),
        "tipos_dados": df.dtypes.astype(str).to_dict(),
    }
    
    # Estatísticas numéricas
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) > 0:
        stats["estatisticas_numericas"] = df[numeric_cols].describe().to_dict()
    
    return stats

@app.get("/api/censo/por-regiao")
async def censo_por_regiao():
    """Agrupa dados por região (ajustar conforme colunas disponíveis)"""
    df = cache.get('censo', pd.DataFrame())
    
    if df.empty:
        return {"error": "Dados não carregados"}
    
    # Exemplo genérico - ajuste conforme suas colunas
    # Procura por colunas que possam representar região/estado/município
    possible_cols = ['CO_UF', 'NO_UF', 'SG_UF', 'CO_MUNICIPIO', 'NO_MUNICIPIO']
    
    result = {}
    for col in possible_cols:
        if col in df.columns:
            result[col] = df[col].value_counts().head(10).to_dict()
    
    return result

# ==================== ENDPOINTS ENEM ====================

@app.get("/api/enem/overview")
async def enem_overview():
    """Visão geral dos dados do ENEM"""
    resultados = cache.get('resultados', pd.DataFrame())
    participantes = cache.get('participantes', pd.DataFrame())
    itens = cache.get('itens', pd.DataFrame())
    
    return {
        "resultados": {
            "total": len(resultados),
            "colunas": resultados.columns.tolist() if not resultados.empty else []
        },
        "participantes": {
            "total": len(participantes),
            "colunas": participantes.columns.tolist() if not participantes.empty else []
        },
        "itens_prova": {
            "total": len(itens),
            "colunas": itens.columns.tolist() if not itens.empty else []
        }
    }

@app.get("/api/enem/estatisticas")
async def enem_stats():
    """Estatísticas do ENEM"""
    df = cache.get('resultados', pd.DataFrame())
    
    if df.empty:
        return {"error": "Dados não carregados"}
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    
    stats = {
        "total_participantes": len(df),
        "colunas_numericas": numeric_cols.tolist(),
    }
    
    if len(numeric_cols) > 0:
        stats["medias"] = df[numeric_cols].mean().to_dict()
        stats["medianas"] = df[numeric_cols].median().to_dict()
        stats["desvio_padrao"] = df[numeric_cols].std().to_dict()
    
    return stats

@app.get("/api/enem/por-estado")
async def enem_por_estado():
    """Agrupa resultados por estado"""
    df = cache.get('participantes', pd.DataFrame())
    
    if df.empty:
        return {"error": "Dados não carregados"}
    
    # Procura coluna de UF/Estado
    possible_cols = ['SG_UF_RESIDENCIA', 'UF', 'CO_UF_RESIDENCIA', 'NO_UF_RESIDENCIA']
    
    result = {}
    for col in possible_cols:
        if col in df.columns:
            result[col] = df[col].value_counts().to_dict()
            break
    
    return result

@app.get("/api/enem/areas-conhecimento")
async def enem_areas():
    """Médias por área de conhecimento"""
    df = cache.get('resultados', pd.DataFrame())
    
    if df.empty:
        return {"error": "Dados não carregados"}
    
    # Procura colunas de notas (ajustar conforme seu CSV)
    nota_cols = [col for col in df.columns if 'NOTA' in col.upper() or 'NU_' in col]
    
    if not nota_cols:
        return {"error": "Colunas de notas não encontradas"}
    
    medias = {}
    for col in nota_cols:
        try:
            medias[col] = float(df[col].mean())
        except:
            pass
    
    return {"areas": medias}

# ==================== ENDPOINTS ÚTEIS ====================

@app.get("/api/colunas/{dataset}")
async def get_colunas(dataset: str):
    """Retorna as colunas disponíveis de um dataset"""
    if dataset not in cache:
        raise HTTPException(status_code=404, detail="Dataset não encontrado")
    
    df = cache[dataset]
    return {
        "dataset": dataset,
        "colunas": df.columns.tolist(),
        "total": len(df.columns),
        "tipos": df.dtypes.astype(str).to_dict()
    }

@app.get("/api/filtrar/{dataset}")
async def filtrar_dados(
    dataset: str,
    coluna: Optional[str] = None,
    valor: Optional[str] = None,
    limit: int = 100
):
    """Filtra dados de um dataset"""
    if dataset not in cache:
        raise HTTPException(status_code=404, detail="Dataset não encontrado")
    
    df = cache[dataset]
    
    if coluna and valor:
        if coluna in df.columns:
            df = df[df[coluna].astype(str).str.contains(valor, case=False, na=False)]
    
    return {
        "total_resultados": len(df),
        "dados": df.head(limit).to_dict('records')
    }

@app.get("/health")
async def health_check():
    """Verifica o status da API"""
    return {
        "status": "online",
        "datasets_carregados": list(cache.keys()),
        "total_registros": {k: len(v) for k, v in cache.items()}
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)