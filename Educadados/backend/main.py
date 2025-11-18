import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import pandas as pd
from typing import Tuple

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
#   UTILITÁRIOS DE LEITURA CSV
# ==========================================

def try_read_csv(path: Path) -> Tuple[pd.DataFrame, str]:
    """
    Tenta ler um CSV com tentativas de encoding e detecção de separador.
    Retorna (df, used_encoding) — df pode ser vazio DataFrame se falhar.
    """
    encodings = ["utf-8", "latin-1", "cp1252"]
    # primeira tentativa: pandas detecção automática de separador via engine='python', sep=None
    for enc in encodings:
        try:
            df = pd.read_csv(path, sep=None, engine="python", encoding=enc, nrows=0)
            # se conseguiu detectar separador e colunas, agora lê completo com esse encoding e sep
            # pandas retorna DataFrame com nrows=0 mas parser detecta sep; obter o sep via read_csv com iterator
            # fallback: read a small chunk to infer sep
            sample = pd.read_csv(path, encoding=enc, engine="python", sep=None, nrows=5)
            used_encoding = enc
            # agora ler inteiro com engine C (mais rápido), mas com sep detectado por pandas (sample.columns já tem nomes corretos)
            # determine sep by splitting first line if needed
            return pd.read_csv(path, encoding=enc, engine="python", sep=None), used_encoding
        except Exception:
            continue
    # última tentativa: leitura simples com latin-1 (mais permissiva)
    try:
        df = pd.read_csv(path, encoding="latin-1", low_memory=False, on_bad_lines="skip")
        return df, "latin-1"
    except Exception:
        return pd.DataFrame(), ""

def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    # remove espaços em branco e caracteres invisíveis nas colunas
    df = df.rename(columns=lambda c: c.strip() if isinstance(c, str) else c)
    return df

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

            # tenta leitura robusta detectando encoding/separador
            df_micro, used_enc = try_read_csv(microdados_file)
            if df_micro.empty and used_enc == "":
                print("   ❌ Não foi possível ler o arquivo de microdados com as estratégias adotadas.")
                df_micro = pd.DataFrame()
            else:
                # limpa nomes de colunas (espaços extras etc)
                df_micro = clean_column_names(df_micro)

                # Se nenhuma coluna útil estiver presente, tenta fallback: ler sem filtro e exibir colunas
                available = [c for c in colunas_uteis if c in df_micro.columns]
                if not available:
                    # faz leitura completa e mostra colunas encontradas para debug
                    print("   ⚠ Nenhuma das colunas esperadas foi encontrada nas colunas detectadas.")
                    print("   >>> Colunas detectadas (microdados):", list(df_micro.columns)[:50])
                    # se df_micro tem colunas, realisticamente pode-se optar por manter e retornar vazio
                    # para evitar perder dados, tenta ler completo novamente com encoding latin-1 e limpar colunas
                    try:
                        df_full = pd.read_csv(microdados_file, encoding="latin-1", low_memory=False, on_bad_lines="skip")
                        df_full = clean_column_names(df_full)
                        available2 = [c for c in colunas_uteis if c in df_full.columns]
                        if available2:
                            df_micro = df_full[available2]
                        else:
                            # ainda nada: registra e zera
                            print("   ⚠ Mesmo no fallback com latin-1 não foram encontradas colunas úteis.")
                            df_micro = pd.DataFrame()
                    except Exception as e:
                        print("   ❌ Fallback completo falhou:", e)
                        df_micro = pd.DataFrame()
                else:
                    # filtra somente colunas úteis que existem (mantendo registro)
                    df_micro = df_micro[available]

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
                df_itens, used_enc_itens = try_read_csv(itens_file)
                if not df_itens.empty:
                    df_itens = clean_column_names(df_itens)
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

    # Se não há microdados, retornar 200 com informação clara (evita 404 em dev)
    if df.empty:
        return {
            "ano": year,
            "inscritos": 0,
            "media_geral": None,
            "media_redacao": None,
            "message": "Microdados não encontrados para este ano. Verifique os arquivos no diretório backend/Microdados."
        }

    # Cálculo de médias mais robusto (apenas com colunas disponíveis)
    score_cols = [c for c in ["NU_NOTA_CN", "NU_NOTA_CH", "NU_NOTA_LC", "NU_NOTA_MT"] if c in df.columns]
    if score_cols:
        try:
            media_geral = float(df[score_cols].mean().mean())
        except Exception:
            media_geral = None
    else:
        media_geral = None

    if "NU_NOTA_REDACAO" in df.columns:
        try:
            media_redacao = float(df["NU_NOTA_REDACAO"].mean())
        except Exception:
            media_redacao = None
    else:
        media_redacao = None

    result = {
        "ano": year,
        "inscritos": int(len(df)),
        "media_geral": media_geral,
        "media_redacao": media_redacao
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
