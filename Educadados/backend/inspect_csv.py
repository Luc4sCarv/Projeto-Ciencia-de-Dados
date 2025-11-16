"""
Script para inspecionar os CSVs do ENEM e descobrir suas colunas
Execute: python inspect_csv.py
"""

import pandas as pd
import os

def inspect_csv(filename, year):
    """Inspeciona um arquivo CSV do ENEM e mostra informações úteis"""
    if not os.path.exists(filename):
        print(f"❌ Arquivo não encontrado: {filename}\n")
        return
    
    print(f"\n{'='*80}")
    print(f"📁 Arquivo: {filename} (ENEM {year})")
    print(f"{'='*80}")
    
    try:
        # Tenta ler o CSV com diferentes encodings
        encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
        df = None
        
        for encoding in encodings:
            try:
                # Carrega apenas 5000 linhas para análise rápida
                df = pd.read_csv(filename, encoding=encoding, nrows=5000, low_memory=False)
                print(f"✓ Encoding detectado: {encoding}")
                break
            except:
                continue
        
        if df is None:
            print("❌ Não foi possível ler o arquivo com os encodings testados")
            return
        
        # Informações básicas
        print(f"\n📊 Informações Gerais:")
        print(f"   • Linhas analisadas: {len(df)} (amostra)")
        print(f"   • Total de colunas: {len(df.columns)}")
        print(f"   • Tamanho do arquivo: {os.path.getsize(filename) / (1024*1024):.2f} MB")
        
        # Colunas importantes para o ENEM
        print(f"\n🎯 Colunas Relevantes Identificadas:")
        
        colunas_importantes = {
            '📍 Geográficas': [],
            '📝 Notas': [],
            '✅ Presença': [],
            '🏫 Escola': [],
            '📊 Demográficas': [],
            '🌐 Outros': []
        }
        
        for col in df.columns:
            col_upper = col.upper()
            
            if any(x in col_upper for x in ['UF', 'MUNICIPIO', 'RESIDENCIA']):
                colunas_importantes['📍 Geográficas'].append(col)
            elif 'NOTA' in col_upper:
                colunas_importantes['📝 Notas'].append(col)
            elif 'PRESENCA' in col_upper:
                colunas_importantes['✅ Presença'].append(col)
            elif any(x in col_upper for x in ['ESCOLA', 'TP_ESCOLA']):
                colunas_importantes['🏫 Escola'].append(col)
            elif any(x in col_upper for x in ['SEXO', 'IDADE', 'RACA', 'RENDA', 'Q0']):
                colunas_importantes['📊 Demográficas'].append(col)
            elif any(x in col_upper for x in ['LINGUA', 'TREINEIRO', 'STATUS']):
                colunas_importantes['🌐 Outros'].append(col)
        
        for categoria, colunas in colunas_importantes.items():
            if colunas:
                print(f"\n{categoria}:")
                for col in colunas[:15]:  # Mostra até 15 colunas por categoria
                    print(f"   • {col}")
                if len(colunas) > 15:
                    print(f"   ... e mais {len(colunas) - 15} colunas")
        
        # Estatísticas das notas
        nota_cols = [col for col in df.columns if 'NOTA' in col.upper()]
        if nota_cols:
            print(f"\n📈 Estatísticas das Notas (amostra de {len(df)} registros):")
            stats = df[nota_cols].describe()
            print(stats.to_string())
        
        # Distribuição por UF
        uf_cols = [col for col in df.columns if 'SG_UF' in col.upper()]
        if uf_cols:
            print(f"\n🗺️ Distribuição por Estado (Top 10):")
            uf_col = uf_cols[0]
            uf_counts = df[uf_col].value_counts().head(10)
            for uf, count in uf_counts.items():
                print(f"   • {uf}: {count} inscritos")
        
        # Tipo de escola
        if 'TP_ESCOLA' in df.columns:
            print(f"\n🏫 Distribuição por Tipo de Escola:")
            escola_counts = df['TP_ESCOLA'].value_counts()
            tipos = {1: 'Pública', 2: 'Privada', 3: 'Não informado'}
            for tipo, count in escola_counts.items():
                nome = tipos.get(tipo, f'Tipo {tipo}')
                print(f"   • {nome}: {count} inscritos ({count/len(df)*100:.1f}%)")
        
        # Taxa de presença
        presenca_cols = [col for col in df.columns if 'PRESENCA' in col.upper()]
        if presenca_cols:
            print(f"\n✅ Taxa de Presença:")
            for col in presenca_cols:
                presentes = (df[col] == 1).sum()
                taxa = (presentes / len(df)) * 100
                area = col.replace('TP_PRESENCA_', '')
                print(f"   • {area}: {taxa:.1f}% presentes")
        
        # Preview dos dados
        print(f"\n👀 Preview dos Dados (primeiras 3 linhas):")
        colunas_preview = [col for col in df.columns if any(x in col.upper() for x in 
                          ['NOTA', 'UF', 'ESCOLA', 'PRESENCA'])][:10]
        if colunas_preview:
            print(df[colunas_preview].head(3).to_string())
        
    except Exception as e:
        print(f"❌ Erro ao processar o arquivo: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Função principal"""
    print("""
    ╔══════════════════════════════════════════════════════════════════════════╗
    ║                  🔍 INSPETOR DE CSVs - ENEM 2022-2024                   ║
    ║                                                                          ║
    ║  Este script analisa os microdados do ENEM e mostra informações         ║
    ║  relevantes para configurar a API e criar os dashboards.                ║
    ╚══════════════════════════════════════════════════════════════════════════╝
    """)
    
    # Anos disponíveis
    years = [2022, 2023, 2024]
    
    print("📋 Verificando arquivos disponíveis...\n")
    
    arquivos_encontrados = []
    
    for year in years:
        microdados = f'MICRODADOS_ENEM_{year}.csv'
        itens = f'ITENS_PROVA_{year}.csv'
        
        if os.path.exists(microdados):
            arquivos_encontrados.append((microdados, year, 'microdados'))
            print(f"✓ {microdados} encontrado")
        else:
            print(f"⚠ {microdados} NÃO encontrado")
        
        if os.path.exists(itens):
            arquivos_encontrados.append((itens, year, 'itens'))
            print(f"✓ {itens} encontrado")
        else:
            print(f"⚠ {itens} NÃO encontrado")
    
    if not arquivos_encontrados:
        print("\n❌ Nenhum arquivo encontrado!")
        print("\n💡 Certifique-se de que os arquivos estão no mesmo diretório:")
        print("   • MICRODADOS_ENEM_2022.csv")
        print("   • MICRODADOS_ENEM_2023.csv")
        print("   • MICRODADOS_ENEM_2024.csv")
        print("   • ITENS_PROVA_2022.csv")
        print("   • ITENS_PROVA_2023.csv")
        print("   • ITENS_PROVA_2024.csv")
        return
    
    print(f"\n{'='*80}")
    print("🔍 Iniciando análise detalhada...")
    print(f"{'='*80}")
    
    # Analisa cada arquivo encontrado
    for filename, year, tipo in arquivos_encontrados:
        inspect_csv(filename, year)
    
    print(f"\n{'='*80}")
    print("✅ Inspeção concluída!")
    print("\n💡 Informações Importantes:")
    print("   1. Use os nomes EXATOS das colunas na API")
    print("   2. Colunas NU_NOTA_* contêm as notas das provas")
    print("   3. TP_PRESENCA_* indica presença (1) ou falta (0)")
    print("   4. TP_ESCOLA: 1=Pública, 2=Privada")
    print("   5. SG_UF_RESIDENCIA contém a sigla do estado")
    print("   6. Considere usar amostragem para testes (arquivos são grandes)")
    print("\n📊 Próximos passos:")
    print("   1. Configure a API com estas colunas")
    print("   2. Teste localmente antes de subir para Hugging Face")
    print("   3. Para Hugging Face, prepare os datasets por ano")
    print(f"{'='*80}\n")

if __name__ == "__main__":
    main()