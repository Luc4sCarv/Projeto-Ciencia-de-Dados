"""
Script de Teste - Verifica se tudo está configurado corretamente
Execute: python test_setup.py
"""

import os
import sys

def print_header(text):
    """Imprime cabeçalho formatado"""
    print("\n" + "="*80)
    print(f"  {text}")
    print("="*80)

def check_folder():
    """Verifica se a pasta MICRODADOS existe"""
    print_header("📁 VERIFICANDO ESTRUTURA DE PASTAS")
    
    if os.path.exists('MICRODADOS'):
        print("✅ Pasta MICRODADOS/ encontrada!")
        return True
    else:
        print("❌ Pasta MICRODADOS/ NÃO encontrada!")
        print("\n💡 Solução:")
        print("   mkdir MICRODADOS")
        print("   # Ou crie a pasta manualmente")
        return False

def check_files():
    """Verifica os arquivos CSV"""
    print_header("📄 VERIFICANDO ARQUIVOS CSV")
    
    years = [2022, 2023, 2024]
    files_found = 0
    total_files = 0
    
    for year in years:
        print(f"\n📅 Ano {year}:")
        
        # Verifica MICRODADOS
        microdados = f'MICRODADOS/MICRODADOS_ENEM_{year}.csv'
        total_files += 1
        if os.path.exists(microdados):
            size_mb = os.path.getsize(microdados) / (1024 * 1024)
            print(f"   ✅ MICRODADOS_ENEM_{year}.csv ({size_mb:.2f} MB)")
            files_found += 1
        else:
            print(f"   ❌ MICRODADOS_ENEM_{year}.csv NÃO encontrado")
        
        # Verifica ITENS_PROVA
        itens = f'MICRODADOS/ITENS_PROVA_{year}.csv'
        total_files += 1
        if os.path.exists(itens):
            size_mb = os.path.getsize(itens) / (1024 * 1024)
            print(f"   ✅ ITENS_PROVA_{year}.csv ({size_mb:.2f} MB)")
            files_found += 1
        else:
            print(f"   ⚠️  ITENS_PROVA_{year}.csv NÃO encontrado (opcional)")
    
    print(f"\n📊 Resumo: {files_found}/{total_files} arquivos encontrados")
    
    if files_found == 0:
        print("\n❌ NENHUM arquivo CSV encontrado!")
        print("\n💡 Coloque seus arquivos na pasta MICRODADOS/ com os seguintes nomes:")
        print("   • MICRODADOS/MICRODADOS_ENEM_2022.csv")
        print("   • MICRODADOS/MICRODADOS_ENEM_2023.csv")
        print("   • MICRODADOS/MICRODADOS_ENEM_2024.csv")
        return False
    
    return files_found >= 3  # Pelo menos 3 arquivos principais

def check_python_version():
    """Verifica versão do Python"""
    print_header("🐍 VERIFICANDO PYTHON")
    
    version = sys.version_info
    print(f"Versão do Python: {version.major}.{version.minor}.{version.micro}")
    
    if version.major >= 3 and version.minor >= 8:
        print("✅ Versão compatível (requer Python 3.8+)")
        return True
    else:
        print("❌ Versão incompatível! Precisa Python 3.8 ou superior")
        return False

def check_dependencies():
    """Verifica dependências instaladas"""
    print_header("📦 VERIFICANDO DEPENDÊNCIAS")
    
    required = {
        'fastapi': 'FastAPI',
        'uvicorn': 'Uvicorn',
        'pandas': 'Pandas',
        'numpy': 'NumPy'
    }
    
    missing = []
    
    for module, name in required.items():
        try:
            __import__(module)
            print(f"✅ {name} instalado")
        except ImportError:
            print(f"❌ {name} NÃO instalado")
            missing.append(module)
    
    if missing:
        print(f"\n⚠️  Faltando: {', '.join(missing)}")
        print("\n💡 Para instalar:")
        print("   pip install -r backend/requirements.txt")
        return False
    
    return True

def check_project_structure():
    """Verifica estrutura do projeto"""
    print_header("🏗️  VERIFICANDO ESTRUTURA DO PROJETO")
    
    # Os caminhos agora incluem as pastas 'backend/' e 'frontend/'
    files_to_check = {
        'backend/main.py': 'API Principal',
        'backend/start.bat': 'Script de Inicialização',
        'backend/inspect_csv.py': 'Inspetor de CSV',
        'frontend/dashboard.html': 'Dashboard',
        'frontend/scripts/dashboard.js': 'JavaScript do Dashboard',
        'backend/requirements.txt': 'Dependências'
    }
    
    all_ok = True
    
    for file, description in files_to_check.items():
        if os.path.exists(file):
            print(f"✅ {description} ({file})")
        else:
            print(f"❌ {description} ({file}) NÃO encontrado")
            all_ok = False
    
    return all_ok

def test_csv_reading():
    """Tenta ler um CSV para testar"""
    print_header("🧪 TESTANDO LEITURA DE CSV")
    
    try:
        import pandas as pd
        
        # Procura o primeiro CSV disponível
        for year in [2023, 2024, 2022]:
            csv_file = f'MICRODADOS/MICRODADOS_ENEM_{year}.csv'
            if os.path.exists(csv_file):
                print(f"\n📖 Tentando ler: {csv_file}")
                print("   (apenas as primeiras 10 linhas para teste)")
                
                df = None
                try:
                    # Tenta ler com separador ; (comum no Brasil)
                    df = pd.read_csv(csv_file, nrows=10, sep=';', encoding='latin-1')
                except Exception:
                    try:
                        # Tenta com , (padrão)
                        df = pd.read_csv(csv_file, nrows=10, sep=',', encoding='latin-1')
                    except Exception as e:
                        # Tenta com utf-8
                        try:
                            df = pd.read_csv(csv_file, nrows=10, sep=';', encoding='utf-8')
                        except Exception as e_utf:
                            print(f"\n❌ Falha ao ler CSV com latin-1 e utf-8: {e_utf}")
                            return False

                # Verifica se o separador estava correto
                if len(df.columns) == 1 and ';' in df.columns[0]:
                    print("   ⚠️  Aviso: Detectado possível separador incorreto. Tentando ler de novo com ','...")
                    df = pd.read_csv(csv_file, nrows=10, sep=',', encoding='latin-1')
                elif len(df.columns) == 1:
                     print("   ⚠️  Aviso: CSV lido com apenas uma coluna, o separador pode estar incorreto.")


                print(f"\n✅ Arquivo lido com sucesso!")
                print(f"   • Colunas: {len(df.columns)}")
                print(f"   • Primeiras colunas: {', '.join(df.columns[:5])}...")
                
                # Verifica colunas importantes
                important_cols = ['NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_MT', 'SG_UF_RESIDENCIA']
                
                found_cols = [col for col in important_cols if col in df.columns]
                
                if found_cols:
                    print(f"   • Colunas importantes encontradas: {len(found_cols)}/{len(important_cols)}")
                
                return True
        
        print("⚠️  Nenhum arquivo CSV disponível para testar")
        return False
        
    except Exception as e:
        print(f"\n❌ Erro ao ler CSV: {e}")
        return False


def print_summary(results):
    """Imprime resumo dos testes"""
    print_header("📋 RESUMO DOS TESTES")
    
    total = len(results)
    passed = sum(results.values())
    
    for test, result in results.items():
        status = "✅" if result else "❌"
        print(f"{status} {test}")
    
    print(f"\n🎯 Resultado: {passed}/{total} testes passaram")
    
    if passed == total:
        print("\n" + "="*80)
        print("  🎉 TUDO PRONTO! VOCÊ PODE INICIAR A API")
        print("="*80)
        print("\n💡 Próximos passos:")
        print("   1. Vá para a pasta 'backend' (cd backend)")
        print("   2. Execute: start.bat")
        print("   3. Escolha: [1] Arquivos CSV Locais")
        print("   4. Abra: frontend/dashboard.html no navegador")
        print("\n✨ Boa apresentação!")
    else:
        print("\n" + "="*80)
        print("  ⚠️  ALGUNS PROBLEMAS ENCONTRADOS")
        print("="*80)
        print("\n💡 Corrija os problemas acima antes de continuar.")

def main():
    """Executa todos os testes"""
    print("""
    ╔══════════════════════════════════════════════════════════════════════════╗
    ║                 🧪 TESTE DE CONFIGURAÇÃO - EducaDados                      ║
    ║                                                                          ║
    ║  Este script verifica se tudo está configurado corretamente              ║
    ║  antes de iniciar a API e fazer a apresentação.                          ║
    ╚══════════════════════════════════════════════════════════════════════════╝
    """)
    
    results = {
        'Python 3.8+': check_python_version(),
        'Pasta MICRODADOS': check_folder(),
        'Arquivos CSV': check_files(),
        'Dependências': check_dependencies(),
        'Estrutura do Projeto': check_project_structure(),
        'Leitura de CSV': test_csv_reading()
    }
    
    print_summary(results)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Teste interrompido pelo usuário.")
    except Exception as e:
        print(f"\n\n❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()