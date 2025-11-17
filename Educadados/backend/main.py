import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import pandas as pd
from functools import lru_cache

# ==========================================
#   CONFIGURAÇÃO DE DIRETÓRIOS
# ==========================================

PROJECT_ROOT = Path(__file__).resolve().parent

MICRODADOS_PATH = PROJECT_ROOT / "Microdados"

YEARS = [2022, 2023, 2024]

# ==========================================
#   FASTAPI
# ==========================================

app = FastAPI(
    title="EducaDados ENEM API",
    description="API oficial do projeto EducaDados com acesso aos Microdados do ENEM",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
#   FUNÇÃO ATUALIZADA DE CARREGAMENTO LOCAL
# ==========================================

def load_from_local(year: int):
    """Carrega dados dos arquivos CSV locais (robusto contra CSV quebrado)."""
    try:
        print(f"📂 Carregando dados do ENEM {year} dos arquivos locais...")

        microdados_file = MICRODADOS_PATH / f"MICRODADOS_ENEM_{year}.csv"
        itens_file = MICRODADOS_PATH / f"ITENS_PROVA_{year}.csv"

        colunas_uteis = [
            "NU_INSCRICAO", "NU_ANO", "CO_UF_RESIDENCIA", "SG_UF_RESIDENCIA",
            "TP_ESCOLA", "TP_LINGUA",
            "NU_NOTA_CN", "NU_NOTA_CH", "NU_NOTA_LC", "NU_NOTA_MT", "NU_NOTA_REDACAO",
            "TP_PRESENCA_CN", "TP_PRESENCA_CH", "TP_PRESENCA_LC", "TP_PRESENCA_MT",
            "Q006"
        ]

        # -------------------------------
        # MICRODADOS
        # -------------------------------
        if microdados_file.exists():

            print(f"   📄 Lendo arquivo: {microdados_file}")

            try:
                df_micro = pd.read_csv(
                    microdados_file,
                    encoding="latin-1",
                    low_memory=False,
                    on_bad_lines="skip",
                    sep=",",
                    usecols=lambda c: c in colunas_uteis
                )

            except Exception as e:
                print(f"❌ ERRO lendo microdados: {e}")
                print("   → Tentando fallback SEM filtro...")

                try:
                    df_micro = pd.read_csv(
                        microdados_file,
                        encoding="latin-1",
                        low_memory=False,
                        on_bad_lines="skip",
                        sep=","
                    )
                    df_micro = df_micro[[c for c in colunas_uteis if c in df_micro.columns]]

                except Exception as e2:
                    print(f"❌ Falhou novamente: {e2}")
                    df_micro = pd.DataFrame()

            print(f"   ✓ Microdados carregados: {len(df_micro):,} registros")

        else:
            print(f"⚠ Arquivo não encontrado: {microdados_file}")
            df_micro = pd.DataFrame()

        # -------------------------------
        # ITENS DE PROVA
        # -------------------------------
        if itens_file.exists():

            print(f"   📄 Lendo arquivo: {itens_file}")

            try:
                df_itens = pd.read_csv(
                    itens_file,
                    encoding="latin-1",
                    low_memory=False,
                    on_bad_lines="skip"
                )
            except Exception as e:
                print(f"❌ ERRO lendo itens: {e}")
                df_itens = pd.DataFrame()

            print(f"   ✓ Itens carregados: {len(df_itens):,} registros")

        else:
            print(f"⚠ Arquivo não encontrado: {itens_file}")
            df_itens = pd.DataFrame()

        return df_micro, df_itens

    except Exception as e:
        print(f"❌ ERRO GERAL em load_from_local({year}): {e}")
        return pd.DataFrame(), pd.DataFrame()



# ==========================================
#   CACHE DO SISTEMA
# ==========================================

microdados_cache = {}
itens_cache = {}


# ==========================================
#   CARREGAMENTO DE DADOS POR ANO
# ==========================================

def load_enem_data(year: int):
    """Carrega microdados de um ano com cache"""
    if year in microdados_cache:
        return microdados_cache[year], itens_cache[year]

    df_micro, df_itens = load_from_local(year)

    microdados_cache[year] = df_micro
    itens_cache[year] = df_itens

    return df_micro, df_itens


# ==========================================
#   ENDPOINTS
# ==========================================

@app.get("/health")
def health():
    return {
        "status": "online",
        "data_source": "Local CSV",
        "datasets": {
            y: {
                "loaded": len(microdados_cache.get(y, [])) > 0,
                "records": len(microdados_cache.get(y, [])),
                "cached_stats": False
            }
            for y in YEARS
        },
        "cache_size": len(microdados_cache)
    }


@app.get("/api/enem/estatisticas/{year}")
def estatisticas(year: int):
    if year not in YEARS:
        raise HTTPException(status_code=400, detail="Ano inválido")

    df, _ = load_enem_data(year)

    if df.empty:
        raise HTTPException(status_code=404, detail="Microdados não encontrados")

    result = {
        "ano": year,
        "inscritos": len(df),
        "media_geral": df[["NU_NOTA_CN", "NU_NOTA_CH", "NU_NOTA_LC", "NU_NOTA_MT"]].mean().mean(),
        "media_redacao": float(df["NU_NOTA_REDACAO"].mean())
    }

    return result


# ==========================================
#   MAIN
# ==========================================

if __name__ == "__main__":
    print("=" * 80)
    print("🚀 Iniciando EducaDados ENEM API")
    print("=" * 80)
    print("📂 Modo: Arquivos Locais (AMOSTRA DE 1%)")
    print()

    # Pré-carregar todos os anos
    for y in YEARS:
        load_enem_data(y)

    print("API pronta em http://localhost:8000")
    print("=" * 80)

    uvicorn.run(app, host="0.0.0.0", port=8000)
