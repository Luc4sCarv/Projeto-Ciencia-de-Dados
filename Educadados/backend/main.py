from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np
from typing import Optional, List, Dict
import json
from pathlib import Path
import os

app = FastAPI(title="EducaDados ENEM API", version="2.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuração de fonte de dados
USE_HUGGINGFACE = os.getenv('USE_HUGGINGFACE', 'false').lower() == 'true'
HF_DATASET = os.getenv('HF_DATASET', 'seu-usuario/enem-dataset')

# Cache global para os dataframes
cache = {}
stats_cache = {}  # Cache para estatísticas pré-calculadas

# --- [CORREÇÃO 1] ---
# Define o caminho base de forma robusta
# Path(__file__) é 'backend/main.py'
# .resolve() encontra o caminho absoluto
# .parent é 'backend/'
# .parent.parent é a raiz do projeto 'PROJETO/'
BASE_DIR = Path(__file__).resolve().parent.parent
MICRODADOS_DIR = BASE_DIR / 'MICRODADOS'
# --------------------

def load_from_huggingface(year: int):
    """Carrega dados do Hugging Face"""
    try:
        from datasets import load_dataset
        
        print(f"📥 Carregando dados do ENEM {year} do Hugging Face...")
        
        # Carrega o dataset
        dataset = load_dataset(HF_DATASET, split=f'enem_{year}')
        
        # Converte para DataFrame
        df_microdados = dataset.to_pandas()
        
        # Carrega itens de prova se disponível
        try:
            dataset_itens = load_dataset(HF_DATASET, split=f'itens_{year}')
            df_itens = dataset_itens.to_pandas()
        except:
            df_itens = pd.DataFrame()
        
        return df_microdados, df_itens
        
    except Exception as e:
        print(f"❌ Erro ao carregar do Hugging Face: {e}")
        return pd.DataFrame(), pd.DataFrame()

def load_from_local(year: int):
    """Carrega dados dos arquivos CSV locais"""
    try:
        print(f"📂 Carregando dados do ENEM {year} dos arquivos locais...")
        
        # --- [CORREÇÃO 2] ---
        # Usa o caminho corrigido que definimos acima
        microdados_file = MICRODADOS_DIR / f'MICRODADOS_ENEM_{year}.csv'
        itens_file = MICRODADOS_DIR / f'ITENS_PROVA_{year}.csv'
        # --------------------

        # Carrega apenas colunas necessárias para economizar memória
        colunas_uteis = [
            'NU_INSCRICAO', 'NU_ANO', 'CO_UF_RESIDENCIA', 'SG_UF_RESIDENCIA',
            'TP_ESCOLA', 'TP_LINGUA',
            'NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_MT', 'NU_NOTA_REDACAO',
            'TP_PRESENCA_CN', 'TP_PRESENCA_CH', 'TP_PRESENCA_LC', 'TP_PRESENCA_MT',
            'Q006',  # Renda familiar
        ]
        
        if os.path.exists(microdados_file):
            df_microdados = pd.read_csv(
                microdados_file, 
                encoding='latin-1',
                # --- [CORREÇÃO 3] ---
                # Adiciona o separador correto
                sep=';',
                # --------------------
                low_memory=False,
                usecols=lambda x: x in colunas_uteis,
            )
            print(f"✓ Microdados carregados: {len(df_microdados)} registros")
        else:
            df_microdados = pd.DataFrame()
            print(f"⚠ Arquivo {microdados_file} não encontrado")
        
        if os.path.exists(itens_file):
            df_itens = pd.read_csv(itens_file, encoding='latin-1', sep=';', low_memory=False)
            print(f"✓ Itens de prova carregados: {len(df_itens)} registros")
        else:
            df_itens = pd.DataFrame()
            print(f"⚠ Arquivo {itens_file} não encontrado")
        
        return df_microdados, df_itens
        
    except Exception as e:
        print(f"❌ Erro ao carregar arquivos locais: {e}")
        return pd.DataFrame(), pd.DataFrame()

def load_enem_data(year: int):
    """Carrega dados do ENEM de um ano específico"""
    if USE_HUGGINGFACE:
        return load_from_huggingface(year)
    else:
        return load_from_local(year)

def calculate_statistics(df: pd.DataFrame, year: int):
    """Calcula estatísticas agregadas para cache"""
    if df.empty:
        return {}
    
    stats = {
        'year': year,
        'total_inscritos': len(df),
        'medias_gerais': {},
        'por_estado': {},
        'por_tipo_escola': {},
        'taxa_presenca': {}
    }
    
    # Colunas de notas
    nota_cols = ['NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_MT', 'NU_NOTA_REDACAO']
    presenca_cols = ['TP_PRESENCA_CN', 'TP_PRESENCA_CH', 'TP_PRESENCA_LC', 'TP_PRESENCA_MT']
    
    # Médias gerais
    for col in nota_cols:
        if col in df.columns:
            stats['medias_gerais'][col] = float(df[col].mean())
    
    # Taxa de presença
    for col in presenca_cols:
        if col in df.columns:
            stats['taxa_presenca'][col] = float((df[col] == 1).sum() / len(df) * 100)
    
    # Por estado
    if 'SG_UF_RESIDENCIA' in df.columns:
        # Pega todos os UFs únicos (geralmente 27)
        ufs = [uf for uf in df['SG_UF_RESIDENCIA'].unique() if uf and pd.notna(uf)]
        for uf in ufs:
            uf_data = df[df['SG_UF_RESIDENCIA'] == uf]
            stats['por_estado'][str(uf)] = {
                'total': len(uf_data),
                'medias': {col: float(uf_data[col].mean()) for col in nota_cols if col in df.columns}
            }
    
    # Por tipo de escola
    if 'TP_ESCOLA' in df.columns:
        for tipo in [1, 2, 3]:  # 1=Pública, 2=Privada, 3=Exterior
            tipo_data = df[df['TP_ESCOLA'] == tipo]
            if len(tipo_data) > 0:
                if tipo == 1:
                    tipo_nome = 'publica'
                elif tipo == 2:
                    tipo_nome = 'privada'
                else:
                    tipo_nome = 'exterior'
                    
                stats['por_tipo_escola'][tipo_nome] = {
                    'total': len(tipo_data),
                    'medias': {col: float(tipo_data[col].mean()) for col in nota_cols if col in df.columns}
                }
    
    return stats

@app.on_event("startup")
async def startup_event():
    """Carrega dados na inicialização"""
    global cache, stats_cache
    
    print("\n" + "="*80)
    print("🚀 Iniciando EducaDados ENEM API")
    print("="*80)
    
    if USE_HUGGINGFACE:
        print("📦 Modo: Hugging Face")
        print(f"📊 Dataset: {HF_DATASET}")
    else:
        print("📂 Modo: Arquivos Locais")
        print(f"ℹ️  Procurando dados em: {MICRODADOS_DIR}")
    
    print("\n📥 Carregando dados dos anos 2022, 2023 e 2024...")
    
    anos_carregados = 0
    for year in [2022, 2023, 2024]:
        df_micro, df_itens = load_enem_data(year)
        
        cache[f'microdados_{year}'] = df_micro
        cache[f'itens_{year}'] = df_itens
        
        # Calcula e armazena estatísticas
        if not df_micro.empty:
            stats_cache[year] = calculate_statistics(df_micro, year)
            print(f"✓ Estatísticas {year} calculadas e cacheadas")
            anos_carregados += 1
        else:
            print(f"ⓘ Dados de {year} não encontrados ou vazios.")
    
    print("\n" + "="*80)
    if anos_carregados > 0:
        print(f"✅ API pronta para uso! ({anos_carregados} ano(s) carregado(s))")
    else:
        print("⚠️  A API iniciou, mas NENHUM dado do ENEM foi carregado.")
        print("   Verifique os caminhos e nomes dos arquivos na pasta MICRODADOS.")
    print("="*80 + "\n")

@app.get("/")
async def root():
    return {
        "message": "EducaDados ENEM API",
        "version": "2.0.0",
        "data_source": "Hugging Face" if USE_HUGGINGFACE else "Local CSV",
        "years_available": [year for year in [2022, 2023, 2024] if year in stats_cache],
        "endpoints": {
            "overview": "/api/enem/overview",
            "statistics": "/api/enem/estatisticas/{year}",
            "comparison": "/api/enem/comparacao",
            "by_state": "/api/enem/por-estado/{year}",
            "by_school": "/api/enem/por-escola/{year}",
            "areas": "/api/enem/areas/{year}",
            "evolution": "/api/enem/evolucao"
        }
    }

# ==================== ENDPOINTS ENEM ====================

@app.get("/api/enem/overview")
async def enem_overview():
    """Visão geral de todos os anos"""
    overview = {
        "anos_disponiveis": [],
        "total_geral": 0,
        "fonte": "Hugging Face" if USE_HUGGINGFACE else "CSV Local"
    }
    
    for year in [2022, 2023, 2024]:
        df = cache.get(f'microdados_{year}', pd.DataFrame())
        if not df.empty:
            overview["anos_disponiveis"].append({
                "ano": year,
                "total_inscritos": len(df),
                "colunas": len(df.columns)
            })
            overview["total_geral"] += len(df)
    
    return overview

@app.get("/api/enem/estatisticas/{year}")
async def enem_stats(year: int):
    """Estatísticas detalhadas de um ano específico"""
    if year not in [2022, 2023, 2024]:
        raise HTTPException(status_code=400, detail="Ano deve ser 2022, 2023 ou 2024")
    
    # Retorna do cache se disponível
    if year in stats_cache:
        return stats_cache[year]
    
    df = cache.get(f'microdados_{year}', pd.DataFrame())
    
    if df.empty:
        raise HTTPException(status_code=404, detail=f"Dados de {year} não encontrados")
    
    # Calcula e cacheia
    stats = calculate_statistics(df, year)
    stats_cache[year] = stats
    
    return stats

@app.get("/api/enem/comparacao")
async def enem_comparacao():
    """Compara médias entre os anos 2022, 2023 e 2024"""
    comparacao = {
        "anos": [],
        "medias_por_area": {
            "ciencias_natureza": [],
            "ciencias_humanas": [],
            "linguagens": [],
            "matematica": [],
            "redacao": []
        }
    }
    
    for year in [2022, 2023, 2024]:
        if year in stats_cache:
            stats = stats_cache[year]
            comparacao["anos"].append(year)
            
            medias = stats.get('medias_gerais', {})
            comparacao["medias_por_area"]["ciencias_natureza"].append(
                medias.get('NU_NOTA_CN', 0)
            )
            comparacao["medias_por_area"]["ciencias_humanas"].append(
                medias.get('NU_NOTA_CH', 0)
            )
            comparacao["medias_por_area"]["linguagens"].append(
                medias.get('NU_NOTA_LC', 0)
            )
            comparacao["medias_por_area"]["matematica"].append(
                medias.get('NU_NOTA_MT', 0)
            )
            comparacao["medias_por_area"]["redacao"].append(
                medias.get('NU_NOTA_REDACAO', 0)
            )
    
    return comparacao

@app.get("/api/enem/por-estado/{year}")
async def enem_por_estado(year: int, top: int = Query(10, ge=1, le=27)):
    """Dados agregados por estado"""
    if year not in [2022, 2023, 2024]:
        raise HTTPException(status_code=400, detail="Ano deve ser 2022, 2023 ou 2024")
    
    if year in stats_cache:
        estados = stats_cache[year].get('por_estado', {})
        # Ordena por média geral e pega top N
        sorted_estados = sorted(
            estados.items(),
            # Calcula a média geral (soma das médias / N de áreas)
            key=lambda item: sum(item[1].get('medias', {}).values()) / max(len(item[1].get('medias', {})), 1),
            reverse=True
        )[:top]
        
        return {
            "ano": year,
            "estados": dict(sorted_estados)
        }
    
    raise HTTPException(status_code=404, detail=f"Dados de {year} não encontrados")

@app.get("/api/enem/por-escola/{year}")
async def enem_por_escola(year: int):
    """Compara escola pública vs privada"""
    if year not in [2022, 2023, 2024]:
        raise HTTPException(status_code=400, detail="Ano deve ser 2022, 2023 ou 2024")
    
    if year in stats_cache:
        return {
            "ano": year,
            "tipos_escola": stats_cache[year].get('por_tipo_escola', {})
        }
    
    raise HTTPException(status_code=404, detail=f"Dados de {year} não encontrados")

@app.get("/api/enem/areas/{year}")
async def enem_areas(year: int):
    """Médias por área de conhecimento"""
    if year not in [2022, 2023, 2024]:
        raise HTTPException(status_code=400, detail="Ano deve ser 2022, 2023 ou 2024")
    
    if year in stats_cache:
        medias = stats_cache[year].get('medias_gerais', {})
        
        return {
            "ano": year,
            "areas": {
                "Ciências da Natureza": medias.get('NU_NOTA_CN', 0),
                "Ciências Humanas": medias.get('NU_NOTA_CH', 0),
                "Linguagens e Códigos": medias.get('NU_NOTA_LC', 0),
                "Matemática": medias.get('NU_NOTA_MT', 0),
                "Redação": medias.get('NU_NOTA_REDACAO', 0)
            }
        }
    
    raise HTTPException(status_code=404, detail=f"Dados de {year} não encontrados")

@app.get("/api/enem/evolucao")
async def enem_evolucao():
    """Evolução das médias ao longo dos anos"""
    evolucao = {
        "anos": [],
        "evolucao_por_area": {}
    }
    
    areas_map = {
        'NU_NOTA_CN': 'Ciências da Natureza',
        'NU_NOTA_CH': 'Ciências Humanas',
        'NU_NOTA_LC': 'Linguagens e Códigos',
        'NU_NOTA_MT': 'Matemática',
        'NU_NOTA_REDACAO': 'Redação'
    }
    
    for year in [2022, 2023, 2024]:
        if year in stats_cache:
            evolucao["anos"].append(year)
            medias = stats_cache[year].get('medias_gerais', {})
            
            for key, nome in areas_map.items():
                if nome not in evolucao["evolucao_por_area"]:
                    evolucao["evolucao_por_area"][nome] = []
                evolucao["evolucao_por_area"][nome].append(
                    round(medias.get(key, 0), 2)
                )
    
    return evolucao

@app.get("/api/enem/presenca/{year}")
async def enem_presenca(year: int):
    """Taxa de presença por prova"""
    if year not in [2022, 2023, 2024]:
        raise HTTPException(status_code=400, detail="Ano deve ser 2022, 2023 ou 2024")
    
    if year in stats_cache:
        return {
            "ano": year,
            "taxa_presenca": stats_cache[year].get('taxa_presenca', {})
        }
    
    raise HTTPException(status_code=404, detail=f"Dados de {year} não encontrados")

@app.get("/api/enem/insights")
async def enem_insights():
    """Insights para preparação baseados nos dados"""
    insights = {
        "areas_menor_desempenho": [],
        "evolucao_geral": "",
        "dicas": []
    }
    
    # Análise dos últimos dados disponíveis
    last_year = None
    for year in [2024, 2023, 2022]:
        if year in stats_cache:
            last_year = year
            break
            
    if last_year:
        medias = stats_cache[last_year].get('medias_gerais', {})
        
        # Identifica áreas com menor desempenho
        areas = [
            ('Ciências da Natureza', medias.get('NU_NOTA_CN', 0)),
            ('Ciências Humanas', medias.get('NU_NOTA_CH', 0)),
            ('Linguagens', medias.get('NU_NOTA_LC', 0)),
            ('Matemática', medias.get('NU_NOTA_MT', 0)),
            ('Redação', medias.get('NU_NOTA_REDACAO', 0))
        ]
        
        areas_sorted = sorted(areas, key=lambda x: x[1])
        insights["areas_menor_desempenho"] = [
            {"area": a[0], "media": round(a[1], 2)} for a in areas_sorted[:3]
        ]
        
        # Dicas baseadas nas áreas
        if areas_sorted[0][0] == 'Redação':
            insights["dicas"].append("Pratique redação semanalmente focando na estrutura dissertativa-argumentativa")
        
        if areas_sorted[1][0] == 'Matemática':
            insights["dicas"].append("Foque em resolver questões de anos anteriores de Matemática")
        
        insights["dicas"].append("Mantenha constância nos estudos de todas as áreas")
        insights["dicas"].append("Simule o tempo de prova para melhorar o gerenciamento")
    
    return insights

@app.get("/health")
async def health_check():
    """Verifica o status da API"""
    datasets_info = {}
    
    for year in [2022, 2023, 2024]:
        df = cache.get(f'microdados_{year}', pd.DataFrame())
        datasets_info[f'enem_{year}'] = {
            "loaded": not df.empty,
            "records": len(df) if not df.empty else 0,
            "cached_stats": year in stats_cache
        }
    
    return {
        "status": "online",
        "data_source": "Hugging Face" if USE_HUGGINGFACE else "Local CSV",
        "datasets": datasets_info,
        "cache_size": len(stats_cache)
    }

if __name__ == "__main__":
    import uvicorn
    # A configuração do host/port é feita pelo `start.bat` ou comando uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)