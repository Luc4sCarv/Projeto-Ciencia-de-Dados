# 🎓 EducaDados - Guia de Configuração

Sistema completo para análise de dados educacionais (Censo Escolar e ENEM 2024)

## 📁 Estrutura do Projeto

```
educadados/
├── backend/
│   ├── main.py              # API FastAPI
│   └── requirements.txt     # Dependências Python
├── frontend/
│   ├── index.html          # Página inicial
│   ├── dashboard.html      # Dashboard atualizado
│   ├── styles/
│   │   ├── style.css
│   │   └── dashboard.css
│   └── scripts/
│       ├── main.js
│       └── dashboard.js
└── data/
    ├── microdados_ed_basica_2024.csv
    ├── RESULTADOS_2024.csv
    ├── PARTICIPANTES_2024.csv
    └── ITENS_PROVA_2024.csv
```

## 🚀 Passo 1: Configurar o Backend

### 1.1 Instalar Python
Certifique-se de ter Python 3.8+ instalado:
```bash
python --version
```

### 1.2 Criar ambiente virtual
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 1.3 Instalar dependências
```bash
pip install -r requirements.txt
```

### 1.4 Organizar os CSVs
Coloque os 4 arquivos CSV na mesma pasta do `main.py`:
- microdados_ed_basica_2024.csv
- RESULTADOS_2024.csv
- PARTICIPANTES_2024.csv
- ITENS_PROVA_2024.csv

### 1.5 Rodar a API
```bash
python main.py
```

A API estará rodando em: `http://localhost:8000`

Teste acessando: `http://localhost:8000/docs` (documentação interativa)

## 🌐 Passo 2: Configurar o Frontend

### 2.1 Atualizar arquivos
Substitua o `dashboard.html` antigo pelo novo (com integração à API)

### 2.2 Testar localmente
Você pode usar qualquer servidor local:

**Opção 1 - Python:**
```bash
# Na pasta do frontend
python -m http.server 3000
```

**Opção 2 - Node.js:**
```bash
npx http-server -p 3000
```

**Opção 3 - VS Code:**
Instale a extensão "Live Server" e clique com botão direito em `index.html` > "Open with Live Server"

Acesse: `http://localhost:3000`

## 📊 Passo 3: Testar a Integração

1. Abra `http://localhost:3000/dashboard.html`
2. Verifique se o status mostra "✓ Conectado"
3. Teste trocar entre "Censo Escolar" e "ENEM"
4. Teste as diferentes visualizações

## 🔧 Ajustes Necessários

### Ajustar nomes das colunas
O código usa nomes genéricos. Você precisa ajustar no `main.py`:

1. Abra um dos seus CSVs e veja os nomes reais das colunas
2. No `main.py`, procure por comentários como `# Ajuste os nomes das colunas`
3. Substitua pelos nomes corretos do seu CSV

**Exemplo:**
```python
# Se sua coluna de UF se chama "SG_UF" no CSV:
if 'SG_UF' in df.columns:
    result['estados'] = df['SG_UF'].value_counts().to_dict()
```

## 🌍 Passo 4: Deploy na Web

### Opção 1: Render (Recomendado - Gratuito)

**Backend:**
1. Crie conta em [render.com](https://render.com)
2. Novo Web Service → Conecte seu repositório Git
3. Configurações:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port 10000`
4. Adicione os CSVs como arquivos estáticos ou use storage

**Frontend:**
1. Novo Static Site no Render
2. Aponte para a pasta `frontend/`
3. Atualize a variável `API_URL` no dashboard.html com a URL da API

### Opção 2: Railway

**Backend:**
1. Crie conta em [railway.app](https://railway.app)
2. New Project → Deploy from GitHub
3. Selecione a pasta com `main.py`
4. Railway detecta Python automaticamente

**Frontend:**
- Deploy como Static Site ou use Vercel/Netlify

### Opção 3: Vercel + Heroku

**Backend (Heroku):**
```bash
# Criar Procfile
echo "web: uvicorn main:app --host 0.0.0.0 --port $PORT" > Procfile

# Deploy
heroku create educadados-api
git push heroku main
```

**Frontend (Vercel):**
```bash
npm i -g vercel
vercel --prod
```

## ⚙️ Configurações Importantes

### CORS
Se tiver erro de CORS, ajuste no `main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://seu-frontend.com"],  # URL do seu frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Limites de Dados
Para produção, remova o `nrows=10000` do `main.py`:
```python
# Desenvolvimento (rápido, poucos dados)
cache[key] = pd.read_csv(file, nrows=10000)

# Produção (todos os dados)
cache[key] = pd.read_csv(file, low_memory=False)
```

### Variáveis de Ambiente
Crie um arquivo `.env`:
```
API_URL=https://sua-api.render.com
CSV_PATH=/app/data/
```

## 🐛 Solução de Problemas

### API não carrega os CSVs
- Verifique se os arquivos estão na mesma pasta do main.py
- Teste o encoding: tente `encoding='utf-8'` ou `encoding='latin-1'`
- Verifique o tamanho dos arquivos (CSVs muito grandes podem demorar)

### Frontend não conecta à API
- Verifique se a API está rodando (acesse http://localhost:8000)
- Verifique o `API_URL` no dashboard.html
- Abra o Console do navegador (F12) para ver erros

### Erro de CORS
- Adicione a origem do frontend no `allow_origins` do main.py
- Em desenvolvimento, use `allow_origins=["*"]`

### Dados não aparecem
- Verifique os nomes das colunas nos CSVs
- Ajuste o código conforme os nomes reais
- Use o endpoint `/api/colunas/censo` para ver as colunas disponíveis

## 🎯 Checklist de Deploy

- [ ] Backend rodando localmente
- [ ] Frontend rodando localmente
- [ ] Dados carregando corretamente
- [ ] Gráficos funcionando
- [ ] CSVs nos nomes corretos
- [ ] CORS configurado
- [ ] API deployada
- [ ] Frontend deployado
- [ ] URL da API atualizada no frontend
- [ ] Teste final na produção

---

**Pronto!** Seu sistema EducaDados está configurado! 🚀