@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ╔══════════════════════════════════════════════════════════════════════════╗
echo ║                    🚀 EducaDados - Inicialização                         ║
echo ╚══════════════════════════════════════════════════════════════════════════╝
echo.

REM Verifica Python
echo 🔍 Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python não encontrado! Instale Python 3.8+
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo ✓ Python encontrado: %PYTHON_VERSION%
echo.

REM Verifica arquivos CSV
echo 📁 Verificando arquivos CSV...
set CSV_FOUND=0

if exist "microdados_ed_basica_2024.csv" (
    echo ✓ microdados_ed_basica_2024.csv
    set /a CSV_FOUND+=1
) else (
    echo ⚠ microdados_ed_basica_2024.csv não encontrado
)

if exist "RESULTADOS_2024.csv" (
    echo ✓ RESULTADOS_2024.csv
    set /a CSV_FOUND+=1
) else (
    echo ⚠ RESULTADOS_2024.csv não encontrado
)

if exist "PARTICIPANTES_2024.csv" (
    echo ✓ PARTICIPANTES_2024.csv
    set /a CSV_FOUND+=1
) else (
    echo ⚠ PARTICIPANTES_2024.csv não encontrado
)

if exist "ITENS_PROVA_2024.csv" (
    echo ✓ ITENS_PROVA_2024.csv
    set /a CSV_FOUND+=1
) else (
    echo ⚠ ITENS_PROVA_2024.csv não encontrado
)

if %CSV_FOUND% equ 0 (
    echo.
    echo ❌ Nenhum arquivo CSV encontrado!
    echo    Coloque os arquivos CSV na mesma pasta deste script.
    pause
    exit /b 1
)

echo.

REM Cria ambiente virtual se não existir
echo 🔧 Configurando ambiente virtual...
if not exist "venv" (
    echo    Criando ambiente virtual...
    python -m venv venv
    echo ✓ Ambiente virtual criado
) else (
    echo ✓ Ambiente virtual já existe
)

REM Ativa ambiente virtual
echo    Ativando ambiente virtual...
call venv\Scripts\activate.bat

REM Instala dependências
echo.
echo 📦 Instalando dependências...
if exist "requirements.txt" (
    pip install -q -r requirements.txt
    echo ✓ Dependências instaladas
) else (
    echo ⚠ requirements.txt não encontrado, instalando manualmente...
    pip install -q fastapi uvicorn pandas numpy python-multipart openpyxl
)

REM Pergunta sobre inspeção
echo.
echo 🔍 Inspecionando CSVs (opcional)...
set /p inspect="Deseja inspecionar os arquivos CSV primeiro? (s/N): "

if /i "%inspect%"=="s" (
    if exist "inspect_csv.py" (
        python inspect_csv.py
        echo.
        pause
    ) else (
        echo ⚠ inspect_csv.py não encontrado
    )
)

REM Inicia o servidor
echo.
echo ╔══════════════════════════════════════════════════════════════════════════╗
echo ║                    🎉 Tudo pronto! Iniciando servidor...                 ║
echo ╚══════════════════════════════════════════════════════════════════════════╝
echo.
echo ✓ API estará disponível em: http://localhost:8000
echo ✓ Documentação: http://localhost:8000/docs
echo.
echo Pressione Ctrl+C para parar o servidor
echo.
timeout /t 2 /nobreak >nul

REM Inicia a API
if exist "main.py" (
    python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
) else (
    echo ❌ main.py não encontrado!
    pause
    exit /b 1
)

pause