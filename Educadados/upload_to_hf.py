"""
Upload SIMPLES para Hugging Face
Faz upload dos arquivos CSV diretamente sem processar
Execute: python upload_simples_hf.py
"""

from huggingface_hub import HfApi, login, create_repo
import os

# ⚠️ CONFIGURAÇÃO - ALTERE AQUI! ⚠️
HF_USERNAME = "Luc4s-Carv"  # Seu usuário do Hugging Face
DATASET_NAME = "educadados-token"  # Nome do repositório
HF_TOKEN = ""  # Seu token do Hugging Face 

def verificar_arquivos():
    """Verifica quais arquivos existem"""
    print("📁 Verificando arquivos na pasta MICRODADOS/...\n")
    
    arquivos = []
    
    if not os.path.exists('MICRODADOS'):
        print("❌ Pasta MICRODADOS não encontrada!")
        return arquivos
    
    # Lista todos os arquivos CSV na pasta
    for arquivo in os.listdir('MICRODADOS'):
        if arquivo.endswith('.csv'):
            caminho_completo = os.path.join('MICRODADOS', arquivo)
            tamanho_mb = os.path.getsize(caminho_completo) / (1024 * 1024)
            arquivos.append({
                'nome': arquivo,
                'caminho': caminho_completo,
                'tamanho_mb': tamanho_mb
            })
            print(f"✓ {arquivo} ({tamanho_mb:.2f} MB)")
    
    if not arquivos:
        print("❌ Nenhum arquivo CSV encontrado em MICRODADOS/")
    else:
        total_mb = sum(a['tamanho_mb'] for a in arquivos)
        print(f"\n📊 Total: {len(arquivos)} arquivos ({total_mb:.2f} MB)")
    
    return arquivos

def fazer_upload(arquivos):
    """Faz upload dos arquivos para Hugging Face"""
    
    # Login
    print("\n🔐 Fazendo login no Hugging Face...")
    try:
        login(token=HF_TOKEN)
        print("✅ Login realizado!")
    except Exception as e:
        print(f"❌ Erro no login: {e}")
        return False
    
    # Cria API
    api = HfApi()
    repo_id = f"{HF_USERNAME}/{DATASET_NAME}"
    
    # Cria o repositório (se não existir)
    print(f"\n📦 Criando/verificando repositório: {repo_id}")
    try:
        create_repo(
            repo_id=repo_id,
            token=HF_TOKEN,
            repo_type="dataset",
            exist_ok=True,  # Não dá erro se já existir
            private=False
        )
        print(f"✅ Repositório pronto!")
    except Exception as e:
        print(f"⚠️  Aviso: {e}")
        print("   (Continuando...)")
    
    # Faz upload de cada arquivo
    print(f"\n📤 Fazendo upload dos arquivos...")
    print("⏳ Isso pode demorar bastante (10-30 minutos)...\n")
    
    sucesso = 0
    falhas = 0
    
    for i, arq in enumerate(arquivos, 1):
        print(f"\n[{i}/{len(arquivos)}] Enviando: {arq['nome']}")
        print(f"           Tamanho: {arq['tamanho_mb']:.2f} MB")
        
        try:
            # Upload do arquivo
            api.upload_file(
                path_or_fileobj=arq['caminho'],
                path_in_repo=arq['nome'],  # Nome no repositório
                repo_id=repo_id,
                repo_type="dataset",
                token=HF_TOKEN
            )
            print(f"           ✅ Upload concluído!")
            sucesso += 1
            
        except Exception as e:
            print(f"           ❌ Erro: {e}")
            falhas += 1
    
    # Resumo
    print("\n" + "="*80)
    print(f"📊 RESUMO DO UPLOAD")
    print("="*80)
    print(f"✅ Sucesso: {sucesso} arquivos")
    print(f"❌ Falhas: {falhas} arquivos")
    
    if sucesso > 0:
        print(f"\n🔗 Seus dados estão em:")
        print(f"   https://huggingface.co/datasets/{repo_id}")
        print(f"\n✨ Use este nome na API: {repo_id}")
        return True
    
    return False

def criar_readme():
    """Cria um README.md para o repositório"""
    readme_content = f"""# Microdados ENEM 2022-2024

Este dataset contém os microdados do ENEM (Exame Nacional do Ensino Médio) dos anos 2022, 2023 e 2024.

## 📊 Arquivos Disponíveis

- `MICRODADOS_ENEM_2022.csv` - Microdados dos participantes do ENEM 2022
- `ITENS_PROVA_2022.csv` - Itens das provas do ENEM 2022
- `MICRODADOS_ENEM_2023.csv` - Microdados dos participantes do ENEM 2023
- `ITENS_PROVA_2023.csv` - Itens das provas do ENEM 2023
- `MICRODADOS_ENEM_2024.csv` - Microdados dos participantes do ENEM 2024
- `ITENS_PROVA_2024.csv` - Itens das provas do ENEM 2024

## 🎯 Uso

Para usar este dataset com a API EducaDados:

```bash
# Configure as variáveis de ambiente
set USE_HUGGINGFACE=true
set HF_DATASET={HF_USERNAME}/{DATASET_NAME}

# Inicie a API
start.bat
```

## 📖 Fonte dos Dados

Dados públicos do INEP - Instituto Nacional de Estudos e Pesquisas Educacionais Anísio Teixeira

https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/enem

## 📝 Licença

Dados públicos disponibilizados pelo INEP.
"""
    
    return readme_content

def fazer_upload_readme(readme_content):
    """Faz upload do README"""
    api = HfApi()
    repo_id = f"{HF_USERNAME}/{DATASET_NAME}"
    
    print("\n📝 Criando README.md...")
    
    try:
        # Salva README temporário
        with open('temp_readme.md', 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        # Faz upload
        api.upload_file(
            path_or_fileobj='temp_readme.md',
            path_in_repo='README.md',
            repo_id=repo_id,
            repo_type="dataset",
            token=HF_TOKEN
        )
        
        # Remove arquivo temporário
        os.remove('temp_readme.md')
        
        print("✅ README.md criado!")
        
    except Exception as e:
        print(f"⚠️  Erro ao criar README: {e}")

def main():
    """Função principal"""
    print("""
    ╔══════════════════════════════════════════════════════════════════════════╗
    ║         📤 Upload SIMPLES para Hugging Face - EducaDados ENEM           ║
    ║                                                                          ║
    ║  Este script faz upload direto dos arquivos CSV sem processamento.      ║
    ║  Muito mais rápido e simples que o upload_to_hf.py original!            ║
    ╚══════════════════════════════════════════════════════════════════════════╝
    """)
    
    # Verifica configuração
    if HF_USERNAME == "seu-usuario" or HF_TOKEN == "hf_...":
        print("\n❌ CONFIGURAÇÃO NECESSÁRIA!")
        print("\nAbra o arquivo upload_simples_hf.py e configure:")
        print(f"   1. HF_USERNAME = 'seu-usuario-real'")
        print(f"   2. HF_TOKEN = 'seu-token-real'")
        print(f"   3. DATASET_NAME = 'enem-microdados' (ou outro nome)")
        print("\n💡 Para obter seu token:")
        print("   https://huggingface.co/settings/tokens")
        input("\nPressione Enter para sair...")
        return
    
    # Verifica arquivos
    arquivos = verificar_arquivos()
    
    if not arquivos:
        print("\n❌ Nenhum arquivo para upload!")
        print("\n💡 Certifique-se de que os arquivos CSV estão em MICRODADOS/")
        input("\nPressione Enter para sair...")
        return
    
    # Confirmação
    print("\n" + "="*80)
    print(f"📦 UPLOAD PARA: {HF_USERNAME}/{DATASET_NAME}")
    print(f"📁 ARQUIVOS: {len(arquivos)}")
    print(f"📊 TAMANHO TOTAL: {sum(a['tamanho_mb'] for a in arquivos):.2f} MB")
    print("🌐 VISIBILIDADE: Público")
    print("="*80)
    
    confirma = input("\n⚠️  Deseja continuar? (s/N): ").strip().lower()
    
    if confirma != 's':
        print("❌ Upload cancelado.")
        return
    
    # Faz upload
    if fazer_upload(arquivos):
        # Cria README
        readme = criar_readme()
        fazer_upload_readme(readme)
        
        print("\n" + "="*80)
        print("✅ UPLOAD CONCLUÍDO COM SUCESSO!")
        print("="*80)
        
        print("\n🎯 PRÓXIMOS PASSOS:")
        print(f"\n1. Verificar no navegador:")
        print(f"   https://huggingface.co/datasets/{HF_USERNAME}/{DATASET_NAME}")
        
        print(f"\n2. Usar na API:")
        print(f"   • Execute: start.bat")
        print(f"   • Escolha: [2] Hugging Face")
        print(f"   • Digite: {HF_USERNAME}/{DATASET_NAME}")
        
        print("\n3. Ou configure via variável de ambiente:")
        print(f"   set USE_HUGGINGFACE=true")
        print(f"   set HF_DATASET={HF_USERNAME}/{DATASET_NAME}")
        
        print("\n✨ Pronto para apresentar!")
    else:
        print("\n❌ Upload falhou. Verifique os erros acima.")
    
    input("\nPressione Enter para sair...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Upload cancelado pelo usuário.")
    except Exception as e:
        print(f"\n\n❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        input("\nPressione Enter para sair...")