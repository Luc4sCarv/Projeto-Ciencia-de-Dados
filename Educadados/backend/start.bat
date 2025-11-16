@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ╔══════════════════════════════════════════════════════════════════════════╗
echo ║                  🚀 EducaDados ENEM - Inicialização da API                  ║
echo ╚══════════════════════════════════════════════════════════════════════════╝
echo.

REM Verifica Python
echo 🔍 Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python não encontrado! Instale Python 3.8+
    echo.
    echo 📥 Download: https://www.python.org/downloads/
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo ✓ Python encontrado: %PYTHON_VERSION%
echo.

REM Pergunta sobre fonte de dados
echo ╔══════════════════════════════════════════════════════════════════════════╗
echo ║                       📊 Configuração de Fonte de Dados                      ║
echo ╚══════════════════════════════════════════════════════════════════════════╝
echo.
echo Escolha a fonte de dados:
echo   [1] Arquivos CSV Locais (padrão)
echo   [2] Hugging Face Dataset
echo.
set /p DATA_SOURCE="Digite sua escolha (1 ou 2): "

if "%DATA_SOURCE%"=="" set DATA_SOURCE=1

if "%DATA_SOURCE%"=="2" (
    echo.
    echo 📦 Modo Hugging Face selecionado
    echo.
    set /p HF_DATASET="Digite o nome do dataset (ex: seu-usuario/enem-dataset): "
    
    if "!HF_DATASET!"=="" (
        echo ❌ Nome do dataset não pode ser vazio!
        pause
        exit /b 1
    )
    
    set USE_HUGGINGFACE=true
    echo.
    echo ✓ Dataset configurado: !HF_DATASET!
) else (
    echo.
    echo 📂 Modo Arquivos Locais selecionado
    set USE_HUGGINGFACE=false
    
    REM Verifica arquivos CSV
    echo.
    echo 📁 Verificando arquivos CSV do ENEM (na pasta ../MICRODADOS/)...
    set CSV_FOUND=0
    
    REM --- [CORREÇÃO AQUI] ---
    REM Adiciona ../ para subir um nível antes de procurar a pasta
    for %%Y in (2022 2023 2024) do (
        if exist "../MICRODADOS/MICRODADOS_ENEM_%%Y.csv" (
            echo ✓ MICRODADOS_ENEM_%%Y.csv encontrado
            set /a CSV_FOUND+=1
        ) else (
            echo ⚠ MICRODADOS_ENEM_%%Y.csv não encontrado
        )
        
        if exist "../MICRODADOS/ITENS_PROVA_%%Y.csv" (
            echo ✓ ITENS_PROVA_%%Y.csv encontrado
        ) else (
            echo ⚠ ITENS_PROVA_%%Y.csv não encontrado
        )
    )
    REM -------------------------
    
    if !CSV_FOUND! equ 0 (
        echo.
        echo ❌ Nenhum arquivo CSV principal do ENEM encontrado!
        echo.
        echo 📋 Arquivos necessários:
        echo    • MICRODADOS_ENEM_2022.csv
        echo    • MICRODADOS_ENEM_2023.csv
        echo    • MICRODADOS_ENEM_2024.csv
        echo.
        REM --- [CORREÇÃO AQUI] ---
        echo 💡 Coloque os arquivos na pasta 'MICRODADOS' na RAIZ do projeto.
        echo    A estrutura deve ser:
        echo    PROJETO/
        echo    ├── backend/ (você está aqui)
        echo    └── MICRODADOS/ (aqui devem estar os CSVs)
        REM -------------------------
        echo.
        echo    Ou use a opção Hugging Face reiniciando o script.
        pause
        exit /b 1
    )
    
    echo.
    echo ✓ Arquivos encontrados: !CSV_FOUND!/3 anos
)

echo.

REM Cria ambiente virtual se não existir
echo 🔧 Configurando ambiente virtual...
if not exist "venv" (
    echo    Criando ambiente virtual...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ Erro ao criar ambiente virtual
        pause
        exit /b 1
    )
    echo ✓ Ambiente virtual criado
) else (
    echo ✓ Ambiente virtual já existe
)

REM Ativa ambiente virtual
echo    Ativando ambiente virtual...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ Erro ao ativar ambiente virtual
    pause
    exit /b 1
)

REM Instala dependências
echo.
echo 📦 Instalando/Verificando dependências...
if exist "requirements.txt" (
    pip install -q -r requirements.txt
    if errorlevel 1 (
        echo ⚠ Erro ao instalar algumas dependências
    ) else (
        echo ✓ Dependências do requirements.txt instaladas
    )
) else (
    echo ⚠ requirements.txt não encontrado, instalando manualmente...
    pip install -q fastapi uvicorn pandas numpy python-multipart
)

REM Se usar Hugging Face, instala datasets
if "%USE_HUGGINGFACE%"=="true" (
    echo.
    echo 📦 Instalando biblioteca Hugging Face Datasets...
    pip install -q datasets
    if errorlevel 1 (
        echo ❌ Erro ao instalar datasets
        echo    Continuando sem suporte a Hugging Face...
        set USE_HUGGINGFACE=false
    ) else (
        echo ✓ Biblioteca datasets instalada
    )
)

REM Pergunta sobre inspeção
if "%USE_HUGGINGFACE%"=="false" (
    echo.
    echo ╔══════════════════════════════════════════════════════════════════════════╗
    echo ║                     🔍 Inspeção de Dados (opcional)                      ║
    echo ╚══════════════════════════════════════════════════════════════════════════╝
    echo.
    set /p inspect="Deseja inspecionar os arquivos CSV antes de iniciar? (s/N): "
    
    if /i "!inspect!"=="s" (
        if exist "inspect_csv.py" (
            echo.
            echo Executando inspeção...
            REM O inspect_csv.py também precisará ser corrigido para usar ../MICRODADOS/
            python inspect_csv.py
            echo.
            pause
        ) else (
            echo ⚠ inspect_csv.py não encontrado
        )
    )
)

REM Configura variáveis de ambiente
if "%USE_HUGGINGFACE%"=="true" (
    set USE_HUGGINGFACE=true
    if not "!HF_DATASET!"=="" (
        set HF_DATASET=!HF_DATASET!
    )
)

REM Inicia o servidor
echo.
echo ╔══════════════════════════════════════════════════════════════════════════╗
echo ║                 🎉 Tudo pronto! Iniciando servidor...                  ║
echo ╚══════════════════════════════════════════════════════════════════════════╝
echo.
echo ✓ API estará disponível em: http://localhost:8000
echo ✓ Documentação interativa: http://localhost:8000/docs
echo ✓ Dashboard: Abra o arquivo 'frontend/dashboard.html' no navegador
echo.
if "%USE_HUGGINGFACE%"=="true" (
    echo 📦 Fonte de Dados: Hugging Face (!HF_DATASET!)
) else (
    echo 📂 Fonte de Dados: Arquivos CSV Locais
)
echo.
echo ⏸️  Pressione Ctrl+C para parar o servidor
echo.
timeout /t 3 /nobreak >nul

REM Inicia a API
if exist "main.py" (
    python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
) else (
    echo ❌ main.py não encontrado!
    echo    Certifique-se de que o arquivo está no diretório atual.
    pause
    exit /b 1
)

pause