# detect_cols.py
import pandas as pd

path = "Microdados/MICRODADOS_ENEM_2023.csv"
encodings = ["utf-8", "latin-1", "cp1252", "iso-8859-1", "latin1"]

for enc in encodings:
    try:
        print(f"\nTentando encoding: {enc}")
        # leitura apenas do cabeçalho (nrows=0) com engine python e detecção de separador
        df = pd.read_csv(path, encoding=enc, sep=None, engine="python", nrows=0)
        cols = list(df.columns)
        print("→ Sucesso com encoding:", enc)
        print("Colunas encontradas (mostrar 100 primeiras se muitas):")
        print(cols[:100])
        break
    except Exception as e:
        print("→ Falhou com encoding", enc, ":", type(e).__name__, "-", e)
else:
    # última tentativa: abrir com latin-1 sem detectar separador e mostrar 1 linha
    try:
        print("\nTentativa final: leitura completa com latin-1 (fallback).")
        df = pd.read_csv(path, encoding="latin-1", low_memory=False, on_bad_lines="skip")
        cols = [c.strip() if isinstance(c, str) else c for c in df.columns]
        print("Colunas encontradas no fallback (primeiras 100):")
        print(cols[:100])
    except Exception as e:
        print("Falha final ao tentar ler o arquivo:", type(e).__name__, e)
