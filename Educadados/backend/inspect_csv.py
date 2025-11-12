"""
Script para inspecionar os CSVs e descobrir suas colunas
Execute: python inspect_csv.py
"""

import pandas as pd
import os

def inspect_csv(filename):
    """Inspeciona um arquivo CSV e mostra informações úteis"""
    if not os.path.exists(filename):
        print(f"❌ Arquivo não encontrado: {filename}\n")
        return
    
    print(f"\n{'='*80}")
    print(f"📁 Arquivo: {filename}")
    print(f"{'='*80}")
    
    try:
        # Tenta ler o CSV com diferentes encodings
        encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
        df = None
        
        for encoding in encodings:
            try:
                df = pd.read_csv(filename, encoding=encoding, nrows=1000, low_memory=False)
                print(f"✓ Encoding detectado: {encoding}")
                break
            except:
                continue
        
        if df is None:
            print("❌ Não foi possível ler o arquivo com os encodings testados")
            return
        
        # Informações básicas
        print(f"\n📊 Informações Gerais:")
        print(f"   • Total de linhas (primeiras 1000): {len(df)}")
        print(f"   • Total de colunas: {len(df.columns)}")
        print(f"   • Tamanho do arquivo: {os.path.getsize(filename) / (1024*1024):.2f} MB")
        
        # Lista todas as colunas
        print(f"\n📋 Colunas Disponíveis ({len(df.columns)}):")
        for i, col in enumerate(df.columns, 1):
            dtype = df[col].dtype
            non_null = df[col].notna().sum()
            print(f"   {i:3d}. {col:50s} | Tipo: {dtype:10s} | Não-nulos: {non_null}")
        
        # Colunas numéricas
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        print(f"\n🔢 Colunas Numéricas ({len(numeric_cols)}):")
        for col in numeric_cols[:20]:  # Primeiras 20
            print(f"   • {col}")
        if len(numeric_cols) > 20:
            print(f"   ... e mais {len(numeric_cols) - 20} colunas")
        
        # Colunas de texto
        text_cols = df.select_dtypes(include=['object']).columns.tolist()
        print(f"\n📝 Colunas de Texto ({len(text_cols)}):")
        for col in text_cols[:20]:  # Primeiras 20
            unique_count = df[col].nunique()
            print(f"   • {col:50s} | Valores únicos: {unique_count}")
        if len(text_cols) > 20:
            print(f"   ... e mais {len(text_cols) - 20} colunas")
        
        # Colunas que podem ser interessantes para análise
        print(f"\n🎯 Colunas Potencialmente Úteis:")
        interesting_keywords = ['uf', 'estado', 'municipio', 'nome', 'nota', 'media', 
                               'total', 'quantidade', 'taxa', 'indice', 'ideb', 'codigo']
        
        for col in df.columns:
            col_lower = col.lower()
            if any(keyword in col_lower for keyword in interesting_keywords):
                print(f"   • {col}")
        
        # Preview dos dados
        print(f"\n👀 Preview dos Dados (primeiras 3 linhas):")
        print(df.head(3).to_string())
        
        # Estatísticas das colunas numéricas
        if len(numeric_cols) > 0:
            print(f"\n📈 Estatísticas Básicas (colunas numéricas):")
            stats = df[numeric_cols].describe()
            print(stats.to_string())
        
    except Exception as e:
        print(f"❌ Erro ao processar o arquivo: {e}")

def main():
    """Função principal"""
    print("""
    ╔══════════════════════════════════════════════════════════════════════════╗
    ║                    🔍 INSPETOR DE CSVs - EducaDados                      ║
    ║                                                                          ║
    ║  Este script analisa seus arquivos CSV e mostra todas as colunas        ║
    ║  disponíveis para você ajustar a API corretamente.                      ║
    ╚══════════════════════════════════════════════════════════════════════════╝
    """)
    
    # Lista de arquivos para inspecionar
    files = [
        'microdados_ed_basica_2024.csv',
        'RESULTADOS_2024.csv',
        'PARTICIPANTES_2024.csv',
        'ITENS_PROVA_2024.csv'
    ]
    
    for filename in files:
        inspect_csv(filename)
    
    print(f"\n{'='*80}")
    print("✅ Inspeção concluída!")
    print("\n💡 Dicas:")
    print("   1. Use os nomes EXATOS das colunas no código da API")
    print("   2. Colunas com 'CO_' geralmente são códigos")
    print("   3. Colunas com 'NO_' ou 'NM_' geralmente são nomes")
    print("   4. Colunas com 'NU_' geralmente são valores numéricos")
    print("   5. Procure por colunas de UF/Estado/Município para análise regional")
    print(f"{'='*80}\n")

if __name__ == "__main__":
    main()