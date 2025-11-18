/**
 * EducaDados - Dashboard ENEM 2022-2024
 * Script principal (refatorado)
 */

// ============================================================================
// CONFIGURAÇÕES GLOBAIS
// ============================================================================
const API_URL = 'http://localhost:8000';
let currentYear = 2023;
let currentView = 'overview';
let chartInstances = {
  main: null,
  comparison: null
};

// Paleta de cores para as áreas
const COLORS = {
  cn: '#10b981',      // Ciências da Natureza - Verde
  ch: '#3b82f6',      // Ciências Humanas - Azul
  lc: '#8b5cf6',      // Linguagens - Roxo
  mt: '#f59e0b',      // Matemática - Laranja
  redacao: '#ef4444'  // Redação - Vermelho
};

// ============================================================================
// HELPERS GERAIS (evitam ReferenceError e normalizam dados)
// ============================================================================

/**
 * Normaliza os dados retornados pela API para um formato consistente:
 * {
 *   year,
 *   total_inscritos,
 *   medias_gerais: { NU_NOTA_CN: ..., ... },
 *   taxa_presenca: { TP_PRESENCA_CN: ..., ... }
 * }
 *
 * Aceita tanto o formato antigo quanto o summary stream do backend.
 */
function normalizeStatsApi(data) {
  if (!data || typeof data !== 'object') {
    return {
      year: currentYear,
      total_inscritos: 0,
      medias_gerais: {},
      taxa_presenca: {}
    };
  }

  // Caso backend novo (streamed_summary)
  if (data.source === 'streamed_summary' || data.ano || data.inscritos !== undefined) {
    const year = data.ano || data.year || currentYear;
    const total_inscritos = data.inscritos !== undefined ? data.inscritos : (data.total_inscritos || 0);

    // medias: backend.streamed gives media_geral and media_redacao, ou means
    const medias_gerais = {};
    if (data.media_redacao !== undefined) {
      medias_gerais.NU_NOTA_REDACAO = data.media_redacao;
    }
    if (data.media_geral !== undefined) {
      // media_geral is an aggregate; put it in a synthetic field
      medias_gerais.MEDIA_GERAL = data.media_geral;
    }
    // se backend forneceu 'means' (stream summary), tenta mapear
    if (data.means && typeof data.means === 'object') {
      Object.assign(medias_gerais, data.means);
    }

    return {
      year,
      total_inscritos: total_inscritos || 0,
      medias_gerais,
      taxa_presenca: data.taxa_presenca || {}
    };
  }

  // Caso formato antigo com chaves mais completas
  return {
    year: data.year || currentYear,
    total_inscritos: data.total_inscritos || data.inscritos || 0,
    medias_gerais: data.medias_gerais || data.medias || data.mediasMap || {},
    taxa_presenca: data.taxa_presenca || data.taxaPresenca || {}
  };
}

/**
 * Pequeno insight para redação a partir do valor ou de objeto
 */
function getRedacaoInsight(valueOrObj) {
  const media = (typeof valueOrObj === 'number') ? valueOrObj
    : (valueOrObj && typeof valueOrObj === 'object' && valueOrObj.NU_NOTA_REDACAO !== undefined) ? valueOrObj.NU_NOTA_REDACAO
    : null;

  if (media === null || media === undefined) return 'Sem dados de redação';
  return `Média da redação: ${Number(media).toFixed(1)}`;
}

/**
 * Exibe mensagem de erro amigável no topo da UI (ou console)
 */
function showError(message) {
  const el = document.getElementById('app-error');
  if (el) {
    el.textContent = message;
    el.style.display = 'block';
  } else {
    console.error(message);
  }
}

/**
 * Fecha a sessão - ação simples de exemplo
 */
function logout() {
  // Implementação mínima: recarrega a página. Substitua pela lógica real de logout.
  window.location.reload();
}

/**
 * Força reload dos dados atuais
 */
function reloadData() {
  // limpa erro se houver
  const el = document.getElementById('app-error');
  if (el) el.style.display = 'none';
  loadYearData(currentYear);
}

/**
 * Retorna a chave de cor para uma área (string)
 */
function getColorKey(areaLabel) {
  // normaliza nomes possíveis
  const a = String(areaLabel).toLowerCase();
  if (a.includes('natureza') || a.includes('cn') || a.includes('NU_NOTA_CN'.toLowerCase())) return 'cn';
  if (a.includes('humanas') || a.includes('ch') || a.includes('NU_NOTA_CH'.toLowerCase())) return 'ch';
  if (a.includes('lingu') || a.includes('lc') || a.includes('NU_NOTA_LC'.toLowerCase())) return 'lc';
  if (a.includes('matem') || a.includes('mt') || a.includes('NU_NOTA_MT'.toLowerCase())) return 'mt';
  if (a.includes('redac') || a.includes('redacao') || a.includes('NU_NOTA_REDACAO'.toLowerCase())) return 'redacao';
  // fallback
  return 'cn';
}

// ============================================================================
// FUNÇÕES UTILITÁRIAS (existiam antes, mantive/adaptei)
// ============================================================================

/**
 * Formata número com separador de milhares
 */
function formatNumber(num) {
  return new Intl.NumberFormat('pt-BR').format(num || 0);
}

/**
 * Calcula média geral de todas as notas (objeto de médias por campo)
 */
function calculateGeneralAverage(medias) {
  if (!medias || Object.keys(medias).length === 0) return 0;
  const values = Object.values(medias).filter(v => typeof v === 'number' && !isNaN(v) && v > 0);
  if (values.length === 0) return 0;
  return values.reduce((a, b) => a + b, 0) / values.length;
}

/**
 * Calcula taxa de presença média (objeto)
 */
function calculatePresenceRate(taxas) {
  if (!taxas || Object.keys(taxas).length === 0) return 0;
  const values = Object.values(taxas).filter(v => typeof v === 'number' && !isNaN(v));
  if (values.length === 0) return 0;
  return values.reduce((a, b) => a + b, 0) / values.length;
}

// ============================================================================
// FUNÇÕES DE INICIALIZAÇÃO
// ============================================================================

window.addEventListener('load', async () => {
  console.log('🚀 Iniciando EducaDados Dashboard...');
  
  // Verifica conexão com a API
  await checkConnection();
  
  // Carrega dados iniciais
  await loadYearData(currentYear);
  
  // Configura event listeners
  setupEventListeners();
  
  // Verifica conexão periodicamente (a cada 30 segundos)
  setInterval(checkConnection, 30000);
  
  console.log('✅ Dashboard inicializado com sucesso!');
});

function setupEventListeners() {
  // Seletor de ano
  const yearSelector = document.getElementById('yearSelector');
  if (yearSelector) {
    yearSelector.addEventListener('change', (e) => {
      currentYear = parseInt(e.target.value);
      loadYearData(currentYear);
    });
  }
  
  // Radio buttons de visualização
  document.querySelectorAll('input[name="view"]').forEach(radio => {
    radio.addEventListener('change', (e) => {
      currentView = e.target.value;
      updateView();
    });
  });
  
  // Botões
  const reloadBtn = document.querySelector('.control-btn[onclick="reloadData()"]');
  if (reloadBtn) reloadBtn.addEventListener('click', reloadData, false);
  
  // Animação dos cards ao carregar
  animateCardsOnLoad();
}

/**
 * Anima os cards quando carregam
 */
function animateCardsOnLoad() {
  const cards = document.querySelectorAll('.info-card');
  cards.forEach((card, index) => {
    card.classList.add('loading');
    setTimeout(() => {
      card.classList.remove('loading');
    }, 500 + (index * 200));
  });
}

// ============================================================================
// FUNÇÕES DE CONEXÃO E STATUS
// ============================================================================

async function checkConnection() {
  try {
    const response = await fetch(`${API_URL}/health`);
    const data = await response.json();
    
    const badge = document.getElementById('connectionStatus');
    if (badge) {
      badge.textContent = '✓ Conectado';
      badge.style.background = '#4caf50';
    }
    
    console.log('✅ API Online:', data);
    return true;
    
  } catch (error) {
    const badge = document.getElementById('connectionStatus');
    if (badge) {
      badge.textContent = '✗ API Offline';
      badge.style.background = '#f44336';
    }
    
    console.error('❌ API Offline:', error);
    showError('API não está respondendo. Verifique se está rodando em ' + API_URL);
    return false;
  }
}

// ============================================================================
// FUNÇÕES DE CARREGAMENTO DE DADOS
// ============================================================================

async function loadYearData(year) {
  console.log(`📊 Carregando dados do ENEM ${year}...`);
  
  try {
    // Atualiza título
    const mainTitle = document.getElementById('mainTitle');
    if (mainTitle) mainTitle.textContent = `Dados Essenciais - ENEM ${year}`;
    
    // Carrega estatísticas
    const statsResponse = await fetch(`${API_URL}/api/enem/estatisticas/${year}`);
    if (!statsResponse.ok) throw new Error(`Erro ${statsResponse.status} ao buscar estatísticas`);
    const statsDataRaw = await statsResponse.json();
    const statsData = normalizeStatsApi(statsDataRaw);
    
    // Atualiza cards essenciais
    updateEssentialCards(statsData);
    
    // Carrega áreas de conhecimento (rota opcional; se falhar, tenta usar medias do stats)
    let areasData = null;
    try {
      const areasResponse = await fetch(`${API_URL}/api/enem/areas/${year}`);
      if (areasResponse.ok) {
        areasData = await areasResponse.json();
      } else {
        areasData = null;
      }
    } catch (err) {
      areasData = null;
    }
    
    // Se não vier areas, tenta construir a partir das medias do statsData
    if (!areasData) {
      areasData = {
        ano: statsData.year,
        areas: {
          "Ciências da Natureza": statsData.medias_gerais.NU_NOTA_CN || 0,
          "Ciências Humanas": statsData.medias_gerais.NU_NOTA_CH || 0,
          "Linguagens": statsData.medias_gerais.NU_NOTA_LC || 0,
          "Matemática": statsData.medias_gerais.NU_NOTA_MT || 0,
          "Redação": statsData.medias_gerais.NU_NOTA_REDACAO || statsData.medias_gerais.NU_NOTA_REDACAO === 0 ? statsData.medias_gerais.NU_NOTA_REDACAO : null
        }
      };
    }
    
    // Atualiza gráfico principal
    updateMainChart(areasData);
    
    console.log(`✅ Dados do ENEM ${year} carregados!`);
    
  } catch (error) {
    console.error('❌ Erro ao carregar dados:', error);
    showError(`Erro ao carregar dados do ENEM ${year} — ${error.message || error}`);
  }
}

/**
 * Atualiza os cards essenciais
 */
function updateEssentialCards(data) {
  const cardsContainer = document.getElementById('essentialCards');
  if (!cardsContainer) return;
  
  // data já normalizado pela normalizeStatsApi
  const medias = data.medias_gerais || {};
  const mediaGeral = calculateGeneralAverage(medias);
  const taxaPresenca = data.taxa_presenca || {};
  const taxaMedia = calculatePresenceRate(taxaPresenca);
  
  const inscritos = data.total_inscritos || 0;
  const year = data.year || currentYear;
  
  const mediaGeralDisplay = mediaGeral !== null ? (Number(mediaGeral).toFixed(1)) : '—';
  const mediaRedacaoVal = medias.NU_NOTA_REDACAO !== undefined ? Number(medias.NU_NOTA_REDACAO) : null;
  const mediaRedacaoDisplay = (mediaRedacaoVal !== null && !isNaN(mediaRedacaoVal)) ? mediaRedacaoVal.toFixed(1) : '—';
  const redacaoInsightText = getRedacaoInsight(medias);
  
  const cards = `
    <div class="info-card" style="border-left: 4px solid ${COLORS.cn}">
      <h4>👥 Total de Inscritos</h4>
      <div class="value">${formatNumber(inscritos)}</div>
      <p style="font-size: 0.875rem; color: #64748b; margin-top: 0.5rem;">
        Ano ${year}
      </p>
    </div>

    <div class="info-card" style="border-left: 4px solid ${COLORS.ch}">
      <h4>📊 Média Geral</h4>
      <div class="value">${mediaGeralDisplay}</div>
      <p style="font-size: 0.875rem; color: #64748b; margin-top: 0.5rem;">
        Todas as áreas
      </p>
    </div>

    <div class="info-card" style="border-left: 4px solid ${COLORS.redacao}">
      <h4>✍️ Média Redação</h4>
      <div class="value">${mediaRedacaoDisplay}</div>
      <p style="font-size: 0.875rem; color: #64748b; margin-top: 0.5rem;">
        ${redacaoInsightText}
      </p>
    </div>

    <div class="info-card" style="border-left: 4px solid ${COLORS.mt}">
      <h4>✅ Taxa de Presença</h4>
      <div class="value">${Number(taxaMedia).toFixed(1)}%</div>
      <p style="font-size: 0.875rem; color: #64748b; margin-top: 0.5rem;">
        Média das provas
      </p>
    </div>
  `;
  
  cardsContainer.innerHTML = cards;
  animateCardsOnLoad();
}

/**
 * Atualiza o gráfico principal
 */
function updateMainChart(data) {
  const canvas = document.getElementById('mainChart');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  if (chartInstances.main) chartInstances.main.destroy();
  
  const areas = data.areas || {};
  const labels = Object.keys(areas).filter(k => areas[k] !== null && areas[k] !== undefined);
  const values = labels.map(l => Number(areas[l] || 0));
  
  // cria paleta dinâmica baseada nas labels (até 5)
  const colorKeys = ['cn','ch','lc','mt','redacao'];
  const backgroundColor = colorKeys.slice(0, labels.length).map(k => COLORS[k] + '80');
  const borderColor = colorKeys.slice(0, labels.length).map(k => COLORS[k]);
  
  chartInstances.main = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: `ENEM ${data.ano || currentYear}`,
        data: values,
        backgroundColor: backgroundColor,
        borderColor: borderColor,
        borderWidth: 2,
        borderRadius: 8
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: function(context) {
              const v = context.parsed.y;
              return `Média: ${Number(v).toFixed(2)} pontos`;
            }
          }
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          // tenta definir um max inteligente (se valores grandes)
          suggestedMax: Math.max(...values, 100) * 1.1,
          grid: { color: 'rgba(0,0,0,0.05)' }
        },
        x: { grid: { display: false } }
      }
    }
  });
}

// ============================================================================
// VIEWS E SEÇÕES (mantive sua estrutura)
// ============================================================================

function updateView() {
  hideAllSections();
  switch(currentView) {
    case 'overview':
      document.getElementById('mainChartSection').style.display = 'block';
      loadYearData(currentYear);
      break;
    case 'statistics':
      document.getElementById('detailsSection').style.display = 'block';
      loadStatistics();
      break;
    case 'regional':
      document.getElementById('regionalSection').style.display = 'block';
      loadRegionalData();
      break;
    case 'comparison':
      document.getElementById('comparisonSection').style.display = 'block';
      loadComparisonData();
      break;
    case 'charts':
      document.getElementById('mainChartSection').style.display = 'block';
      loadYearData(currentYear);
      break;
  }
}

function hideAllSections() {
  const sections = [
    'mainChartSection', 
    'detailsSection', 
    'regionalSection', 
    'comparisonSection',
    'schoolSection',
    'presenceSection',
    'insightsSection'
  ];
  sections.forEach(id => {
    const section = document.getElementById(id);
    if (section) section.style.display = 'none';
  });
}

// ============================================================================
// FUNÇÕES DE CARREGAMENTO DETALHADO (mantive suas rotinas, só deixei mais robustas)
// ============================================================================

async function loadStatistics() {
  const container = document.getElementById('detailedData');
  if (!container) return;
  container.innerHTML = '<p>Carregando estatísticas...</p>';
  
  try {
    const response = await fetch(`${API_URL}/api/enem/estatisticas/${currentYear}`);
    if (!response.ok) throw new Error(`Erro ${response.status}`);
    const raw = await response.json();
    const data = normalizeStatsApi(raw);
    
    let html = `
      <div style="background: white; border-radius: 12px; padding: 2rem; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
        <h3>📊 Estatísticas Completas - ENEM ${data.year}</h3>
        <div style="margin-top: 1.5rem;">
          <h4 style="color: #2563eb; margin-bottom: 1rem;">Total de Inscritos</h4>
          <p style="font-size: 1.5rem; font-weight: bold;">${formatNumber(data.total_inscritos)}</p>
        </div>
        <div style="margin-top: 1.5rem;">
          <h4 style="color: #2563eb; margin-bottom: 1rem;">Médias por Área</h4>
          <ul style="list-style: none; padding: 0;">
    `;
    
    const mediasMap = {
      'NU_NOTA_CN': 'Ciências da Natureza',
      'NU_NOTA_CH': 'Ciências Humanas',
      'NU_NOTA_LC': 'Linguagens e Códigos',
      'NU_NOTA_MT': 'Matemática',
      'NU_NOTA_REDACAO': 'Redação'
    };
    
    for (const [key, nome] of Object.entries(mediasMap)) {
      const valor = data.medias_gerais[key];
      if (valor !== undefined && valor !== null) {
        html += `
          <li style="padding: 0.75rem; border-bottom: 1px solid #e2e8f0; display: flex; justify-content: space-between;">
            <span>${nome}</span>
            <strong>${Number(valor).toFixed(2)} pontos</strong>
          </li>
        `;
      }
    }
    
    html += `
          </ul>
        </div>
    `;
    
    // Presença
    html += `
        <div style="margin-top: 1.5rem;">
          <h4 style="color: #2563eb; margin-bottom: 1rem;">Taxa de Presença</h4>
          <ul style="list-style: none; padding: 0;">
    `;
    const presencaMap = {
      'TP_PRESENCA_CN': 'Ciências da Natureza',
      'TP_PRESENCA_CH': 'Ciências Humanas',
      'TP_PRESENCA_LC': 'Linguagens',
      'TP_PRESENCA_MT': 'Matemática'
    };
    for (const [key, nome] of Object.entries(presencaMap)) {
      const valor = data.taxa_presenca[key];
      if (valor !== undefined && valor !== null) {
        html += `
          <li style="padding: 0.75rem; border-bottom: 1px solid #e2e8f0; display: flex; justify-content: space-between;">
            <span>${nome}</span>
            <strong>${Number(valor).toFixed(2)}%</strong>
          </li>
        `;
      }
    }
    html += `</ul></div></div>`;
    
    container.innerHTML = html;
    
  } catch (error) {
    console.error('Erro ao carregar estatísticas:', error);
    container.innerHTML = '<p style="color: #ef4444;">Erro ao carregar estatísticas</p>';
  }
}

async function loadRegionalData() {
  const container = document.getElementById('regionalData');
  if (!container) return;
  container.innerHTML = '<p>Carregando dados regionais...</p>';
  
  try {
    const response = await fetch(`${API_URL}/api/enem/por-estado/${currentYear}?top=10`);
    if (!response.ok) throw new Error(`Erro ${response.status}`);
    const data = await response.json();
    
    let html = '';
    for (const [uf, info] of Object.entries(data.estados || {})) {
      const mediaGeral = calculateGeneralAverage(info.medias || {});
      html += `
        <div class="tool-card" style="background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
          <h4 style="color: #2563eb; margin-bottom: 1rem;">${uf}</h4>
          <p style="font-size: 1.25rem; font-weight: bold; margin-bottom: 0.5rem;">${mediaGeral.toFixed(1)} pontos</p>
          <p style="font-size: 0.875rem; color: #64748b;">${formatNumber(info.total || 0)} inscritos</p>
        </div>
      `;
    }
    
    container.innerHTML = html || '<p>Nenhum dado regional encontrado</p>';
    
  } catch (error) {
    console.error('Erro ao carregar dados regionais:', error);
    container.innerHTML = '<p style="color: #ef4444;">Erro ao carregar dados regionais</p>';
  }
}

async function loadComparisonData() {
  try {
    const response = await fetch(`${API_URL}/api/enem/evolucao`);
    if (!response.ok) throw new Error(`Erro ${response.status}`);
    const data = await response.json();
    updateComparisonChart(data);
    updateComparisonCards(data);
  } catch (error) {
    console.error('Erro ao carregar comparação:', error);
    showError('Erro ao carregar comparação entre anos');
  }
}

function updateComparisonChart(data) {
  const canvas = document.getElementById('comparisonChart');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  if (chartInstances.comparison) chartInstances.comparison.destroy();
  
  const datasets = Object.keys(data.evolucao_por_area || {}).map(area => {
    const colorKey = getColorKey(area);
    return {
      label: area,
      data: data.evolucao_por_area[area],
      borderColor: COLORS[colorKey],
      backgroundColor: COLORS[colorKey] + '20',
      borderWidth: 3,
      tension: 0.4,
      fill: true
    };
  });
  
  chartInstances.comparison = new Chart(ctx, {
    type: 'line',
    data: {
      labels: data.anos || [],
      datasets
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      plugins: { legend: { position: 'top' } },
      scales: { y: { beginAtZero: true, suggestedMax: 1000 } }
    }
  });
}

function updateComparisonCards(data) {
  const container = document.getElementById('comparisonGrid');
  if (!container) return;
  let html = '';
  for (const [area, values] of Object.entries(data.evolucao_por_area || {})) {
    const trend = values[values.length - 1] - values[0];
    const trendIcon = trend > 0 ? '📈' : trend < 0 ? '📉' : '➡️';
    const trendText = trend > 0 ? 'Crescimento' : trend < 0 ? 'Queda' : 'Estável';
    const trendColor = trend > 0 ? COLORS.cn : trend < 0 ? COLORS.redacao : COLORS.ch;
    html += `
      <div class="tool-card" style="background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
        <h4 style="color: #2563eb; margin-bottom: 1rem;">${area} ${trendIcon}</h4>
    `;
    values.forEach((val, idx) => {
      html += `
        <div style="display: flex; justify-content: space-between; padding: 0.5rem 0; border-bottom: 1px solid #e2e8f0;">
          <span style="color: #64748b;">${data.anos[idx]}</span>
          <strong>${Number(val).toFixed(1)}</strong>
        </div>
      `;
    });
    html += `
        <div style="display:flex; justify-content:space-between; padding-top:0.75rem; border-top:2px solid #e2e8f0;">
          <span style="font-weight:600">${trendText}</span>
          <strong style="color:${trendColor}">${trend>0?'+':''}${trend.toFixed(1)}</strong>
        </div>
      </div>
    `;
  }
  container.innerHTML = html;
}

async function loadSchoolComparison() {
  hideAllSections();
  document.getElementById('schoolSection').style.display = 'block';
  const container = document.getElementById('schoolData');
  container.innerHTML = '<p>Carregando comparação...</p>';
  try {
    const response = await fetch(`${API_URL}/api/enem/por-escola/${currentYear}`);
    if (!response.ok) throw new Error(`Erro ${response.status}`);
    const data = await response.json();
    const tipos = data.tipos_escola || {};
    let html = '';
    for (const [tipo, info] of Object.entries(tipos)) {
      const tipoNome = tipo === 'publica' ? '🏫 Escola Pública' : '🏛️ Escola Privada';
      const mediaGeral = calculateGeneralAverage(info.medias || {});
      const color = tipo === 'publica' ? COLORS.ch : COLORS.mt;
      html += `
        <div class="tool-card" style="background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); border-left: 4px solid ${color};">
          <h4 style="color: ${color}; margin-bottom: 1rem;">${tipoNome}</h4>
          <p style="font-size: 1.5rem; font-weight: bold; margin-bottom: 0.5rem;">${mediaGeral.toFixed(1)} pontos</p>
          <p style="font-size: 0.875rem; color: #64748b; margin-bottom: 1rem;">${formatNumber(info.total || 0)} inscritos</p>
          <h5 style="margin-top: 1rem; margin-bottom: 0.5rem;">Médias por Área:</h5>
          <ul style="list-style: none; padding: 0;">
      `;
      for (const [key, value] of Object.entries(info.medias || {})) {
        const nomeArea = key.replace('NU_NOTA_', '').replace('_', ' ');
        html += `<li style="padding: 0.25rem 0; display:flex; justify-content:space-between;"><span>${nomeArea}</span><strong>${Number(value).toFixed(1)}</strong></li>`;
      }
      html += '</ul></div>';
    }
    container.innerHTML = html;
  } catch (error) {
    console.error('Erro ao carregar comparação escolar:', error);
    container.innerHTML = '<p style="color: #ef4444;">Erro ao carregar dados</p>';
  }
}

async function loadPresenceAnalysis() {
  hideAllSections();
  document.getElementById('presenceSection').style.display = 'block';
  const container = document.getElementById('presenceData');
  container.innerHTML = '<p>Carregando análise de presença...</p>';
  try {
    const response = await fetch(`${API_URL}/api/enem/presenca/${currentYear}`);
    if (!response.ok) throw new Error(`Erro ${response.status}`);
    const data = await response.json();
    let html = `<div style="background: white; border-radius: 12px; padding: 2rem;">`;
    const presencaMap = {
      'TP_PRESENCA_CN': 'Ciências da Natureza',
      'TP_PRESENCA_CH': 'Ciências Humanas',
      'TP_PRESENCA_LC': 'Linguagens e Códigos',
      'TP_PRESENCA_MT': 'Matemática'
    };
    for (const [key, nome] of Object.entries(presencaMap)) {
      const valor = data.taxa_presenca ? data.taxa_presenca[key] : undefined;
      if (valor !== undefined && valor !== null) {
        const porcentagem = Number(valor).toFixed(2);
        const width = Math.min(Math.max(Number(valor), 0), 100);
        html += `<div style="margin-bottom:1.5rem;"><div style="display:flex; justify-content:space-between; margin-bottom:0.5rem;"><span style="font-weight:600;">${nome}</span><span style="font-weight:bold;color:${COLORS.cn}">${porcentagem}%</span></div><div style="background:#e2e8f0;border-radius:8px;height:24px;overflow:hidden;"><div style="background:linear-gradient(90deg, ${COLORS.cn}, ${COLORS.ch}); width:${width}%;height:100%;border-radius:8px;transition:width 0.3s ease;"></div></div></div>`;
      }
    }
    html += `</div>`;
    container.innerHTML = html;
  } catch (error) {
    console.error('Erro ao carregar análise de presença:', error);
    container.innerHTML = '<p style="color: #ef4444;">Erro ao carregar dados</p>';
  }
}

async function loadInsights() {
  hideAllSections();
  document.getElementById('insightsSection').style.display = 'block';
  const container = document.getElementById('insightsData');
  container.innerHTML = '<p>Carregando insights...</p>';
  try {
    const response = await fetch(`${API_URL}/api/enem/insights`);
    if (!response.ok) throw new Error(`Erro ${response.status}`);
    const data = await response.json();
    let html = `<div style="background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:white;padding:2rem;border-radius:12px;"><h3>💡 Como se Preparar Melhor</h3>`;
    if (data.areas_menor_desempenho && data.areas_menor_desempenho.length > 0) {
      html += `<ul style="list-style:none;padding:0;margin-top:1rem;">`;
      data.areas_menor_desempenho.forEach(area => {
        html += `<li style="padding:0.75rem;background:rgba(255,255,255,0.08);margin-bottom:0.5rem;border-radius:8px;"><strong>${area.area}</strong> - Média: ${Number(area.media).toFixed(1)}</li>`;
      });
      html += `</ul>`;
    } else {
      html += `<p>Continue seus estudos com dedicação e consistência!</p>`;
    }
    if (data.dicas && data.dicas.length) {
      html += `<h4 style="margin-top:1rem;">📚 Dicas:</h4><ul>`;
      data.dicas.forEach(d => html += `<li>${d}</li>`);
      html += `</ul>`;
    }
    html += `</div>`;
    container.innerHTML = html;
  } catch (error) {
    console.error('Erro ao carregar insights:', error);
    container.innerHTML = '<p style="color: #ef4444;">Erro ao carregar insights</p>';
  }
}
