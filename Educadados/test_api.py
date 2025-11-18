"""
Teste Rápido da API
Execute enquanto a API está rodando para verificar se está OK
"""

import requests
import time

API_URL = "http://localhost:8000"

def test_connection():
    """Testa se a API está respondendo"""
    print("🔍 Testando conexão com a API...")
    
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        
        if response.status_code == 200:
            print("✅ API está ONLINE!")
            data = response.json()
            print(f"\n📊 Status: {data.get('status')}")
            
            if 'datasets' in data:
                print("\n📁 Datasets carregados:")
                for dataset, info in data['datasets'].items():
                    if info.get('loaded'):
                        print(f"   ✅ {dataset}: {info.get('records', 0):,} registros")
                    else:
                        print(f"   ❌ {dataset}: Não carregado")
            
            return True
        else:
            print(f"⚠️  API respondeu com código: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ NÃO conseguiu conectar à API!")
        print("\n💡 Verifique:")
        print("   1. A API está rodando? Execute:")
        print("      python -m uvicorn main:app --reload")
        print("   2. Aguardou aparecer '✅ API PRONTA!'?")
        return False
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def test_endpoints():
    """Testa endpoints principais"""
    print("\n" + "="*80)
    print("🧪 Testando Endpoints")
    print("="*80)
    
    endpoints = [
        ("/api/enem/overview", "Overview"),
        ("/api/enem/estatisticas/2023", "Estatísticas 2023"),
        ("/api/enem/areas/2023", "Áreas 2023"),
    ]
    
    for endpoint, nome in endpoints:
        print(f"\n📡 {nome}: {endpoint}")
        
        try:
            response = requests.get(f"{API_URL}{endpoint}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ OK - Retornou dados")
                
                # Mostra um preview dos dados
                if isinstance(data, dict):
                    keys = list(data.keys())[:3]
                    print(f"   📋 Chaves: {', '.join(keys)}...")
                    
            else:
                print(f"   ⚠️  Código: {response.status_code}")
                print(f"   {response.text[:100]}")
                
        except Exception as e:
            print(f"   ❌ Erro: {e}")

def main():
    print("""
    ╔══════════════════════════════════════════════════════════════════════════╗
    ║                    🧪 Teste Rápido da API - EducaDados                   ║
    ╚══════════════════════════════════════════════════════════════════════════╝
    """)
    
    print("⚠️  IMPORTANTE: A API deve estar rodando!")
    print("   Execute em outro terminal: python -m uvicorn main:app --reload\n")
    
    input("Pressione Enter quando a API estiver pronta... ")
    
    # Testa conexão
    if not test_connection():
        print("\n❌ Teste abortado - API não está acessível")
        input("\nPressione Enter para sair...")
        return
    
    # Aguarda um pouco
    print("\n⏳ Aguardando 2 segundos...")
    time.sleep(2)
    
    # Testa endpoints
    test_endpoints()
    
    # Resultado final
    print("\n" + "="*80)
    print("✅ TESTE CONCLUÍDO!")
    print("="*80)
    
    print("\n💡 Se todos os testes passaram:")
    print("   1. Abra dashboard.html no navegador")
    print("   2. Aguarde os cards carregarem")
    print("   3. Teste trocar entre os anos")
    print("   4. ✨ Está pronto para apresentar!")
    
    print("\n⚠️  Se algum teste falhou:")
    print("   1. Verifique os logs da API no terminal")
    print("   2. Certifique-se que os arquivos CSV estão em MICRODADOS/")
    print("   3. Aguarde a API terminar de carregar (pode demorar 2-5 min)")
    
    input("\nPressione Enter para sair...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Teste interrompido.")
    except Exception as e:
        print(f"\n\n❌ Erro: {e}")
        input("\nPressione Enter para sair...")