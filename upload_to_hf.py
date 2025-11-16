"""
Script para fazer upload dos microdados do ENEM para Hugging Face
Execute: python upload_to_hf.py
"""

from datasets import Dataset, DatasetDict
import pandas as pd
from huggingface_hub import login
import os

# CONFIGURAÇÃO
HF_USERNAME = "Luc4s-Carv"  # ⚠️ ALTERE AQUI!
DATASET_NAME = "enem-dataset"
HF_TOKEN = ""  # ⚠️ COLOQUE SEU TOKEN AQUI!

def prepare_dataset(year):
    """Prepara um dataset de um ano específico"""
    print(f"\n📂 Processando ENEM {year}...")
    
    microdados_file = f'MICRODADOS_ENEM_{year}.csv'
    itens_file = f'ITENS_PROVA_{year}.csv'
    
    datasets_dict = {}
    
    # Carrega microdados
    if os.path.exists(microdados_file):
        print(f"   Lendo {microdados_file}...")
        
        # Colunas essenciais para reduzir tamanho
        colunas_uteis = [
            'NU_INSCRICAO', 'NU_ANO', 'CO_UF_RESIDENCIA', 'SG_UF_RESIDENCIA',
            'TP_ESCOLA', 'TP_LINGUA',
            'NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_MT', 'NU_NOTA_REDACAO',
            'TP_PRESENCA_CN', 'TP_PRESENCA_CH', 'TP_PRESENCA_LC', 'TP_PRESENCA_MT',
            'Q006',  # Renda
        ]
        
        # Lê CSV
        df_micro = pd.read_csv(
            microdados_file, 
            encoding='latin-1',
            usecols=lambda x: x in colunas_uteis,
            low_memory=False
        )
        
        print(f"   ✓ {len(df_micro)} registros carregados")
        
        # Converte para Dataset do Hugging Face
        datasets_dict[f'enem_{year}'] = Dataset.from_pandas(df_micro)
    
    # Carrega itens de prova (opcional)
    if os.path.exists(itens_file):
        print(f"   Lendo {itens_file}...")
        df_itens = pd.read_csv(itens_file, encoding='latin-1')
        datasets_dict[f'itens_{year}'] = Dataset.from_pandas(df_itens)
        print(f"   ✓ {len(df_itens)} itens carregados")
    
    return datasets_dict

def main():
    """Função principal"""
    print("""
    ╔══════════════════════════════════════════════════════════════════════════╗
    ║         📤 Upload de Microdados ENEM para Hugging Face                  ║
    ╚══════════════════════════════════════════════════════════════════════════╝
    """)
    
    # Login no Hugging Face
    print("🔐 Fazendo login no Hugging Face...")
    try:
        login(token=HF_TOKEN)
        print("✓ Login realizado com sucesso!")
    except Exception as e:
        print(f"❌ Erro no login: {e}")
        print("\n💡 Verifique:")
        print("   1. Token está correto")
        print("   2. Token tem permissão de 'write'")
        return
    
    # Prepara todos os anos
    all_datasets = {}
    
    for year in [2022, 2023, 2024]:
        year_datasets = prepare_dataset(year)
        all_datasets.update(year_datasets)
    
    if not all_datasets:
        print("\n❌ Nenhum dataset preparado!")
        return
    
    # Cria DatasetDict
    dataset_dict = DatasetDict(all_datasets)
    
    print(f"\n📊 Datasets preparados:")
    for name, ds in dataset_dict.items():
        print(f"   • {name}: {len(ds)} registros")
    
    # Faz upload
    print(f"\n📤 Fazendo upload para: {HF_USERNAME}/{DATASET_NAME}")
    print("⏳ Isso pode demorar alguns minutos...")
    
    try:
        dataset_dict.push_to_hub(
            f"{HF_USERNAME}/{DATASET_NAME}",
            private=False  # Público para acesso na API
        )
        print("\n✅ Upload concluído com sucesso!")
        print(f"\n🔗 Seu dataset está disponível em:")
        print(f"   https://huggingface.co/datasets/{HF_USERNAME}/{DATASET_NAME}")
        
    except Exception as e:
        print(f"\n❌ Erro no upload: {e}")
        return
    
    print("\n" + "="*80)
    print("✨ Próximos passos:")
    print("="*80)
    print(f"1. Configure a API para usar Hugging Face:")
    print(f"   • Edite o start.bat")
    print(f"   • Escolha opção [2] Hugging Face")
    print(f"   • Digite: {HF_USERNAME}/{DATASET_NAME}")
    print("")
    print("2. Ou configure variável de ambiente:")
    print(f"   set USE_HUGGINGFACE=true")
    print(f"   set HF_DATASET={HF_USERNAME}/{DATASET_NAME}")
    print("")
    print("3. Inicie a API normalmente:")
    print("   start.bat")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()