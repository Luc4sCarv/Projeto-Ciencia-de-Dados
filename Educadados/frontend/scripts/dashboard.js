/**
 * EducaDados - Dashboard ENEM 2022-2024
 * Script principal para gerenciamento do dashboard
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
// FUNÇÕES DE INICIALIZAÇÃO
// ============================================================================

/**
 * Inicialização quando a página carrega
 */
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

/**
 * Configura todos os event listeners
 */
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

/**
 * Verifica conexão com a API
 */
async function checkConnection() {
    try {
        const response = await fetch(`${API_URL}/health`);
        const data = await response.json();
        
        const badge = document.getElementById('connectionStatus');
        badge.textContent = '✓ Conectado';
        badge.style.background = '#4caf50';
        
        console.log('✅ API Online:', data);
        return true;
        
    } catch (error) {
        const badge = document.getElementById('connectionStatus');
        badge.textContent = '✗ API Offline';
        badge.style.background = '#f44336';
        
        console.error('❌ API Offline:', error);
        showError('API não está respondendo. Verifique se está rodando em ' + API_URL);
        return false;
    }
}

// ============================================================================
// FUNÇÕES DE CARREGAMENTO DE DADOS
// ============================================================================

/**
 * Carrega todos os dados de um ano específico
 */
async function loadYearData(year) {
    console.log(`📊 Carregando dados do ENEM ${year}...`);
    
    try {
        // Atualiza título
        document.getElementById('mainTitle').textContent = `Dados Essenciais - ENEM ${year}`;
        
        // Carrega estatísticas
        const statsResponse = await fetch(`${API_URL}/api/enem/estatisticas/${year}`);
        const statsData = await statsResponse.json();
        
        // Atualiza cards essenciais
        updateEssentialCards(statsData);
        
        // Carrega áreas de conhecimento
        const areasResponse = await fetch(`${API_URL}/api/enem/areas/${year}`);
        const areasData = await areasResponse.json();
        
        // Atualiza gráfico principal
        updateMainChart(areasData);
        
        console.log(`✅ Dados do ENEM ${year} carregados!`);
        
    } catch (error) {
        console.error('❌ Erro ao carregar dados:', error);
        showError(`Erro ao carregar dados do ENEM ${year}`);
    }
}

/**
 * Atualiza os cards essenciais
 */
function updateEssentialCards(data) {
    const cardsContainer = document.getElementById('essentialCards');
    
    // Calcula média geral
    const medias = data.medias_gerais || {};
    const mediaGeral = calculateGeneralAverage(medias);
    
    // Calcula taxa de presença média
    const taxaPresenca = data.taxa_presenca || {};
    const taxaMedia = calculatePresenceRate(taxaPresenca);
    
    const cards = `
        <div class="info-card" style="border-left: 4px solid ${COLORS.cn}">
            <h4>👥 Total de Inscritos</h4>
            <div class="value">${formatNumber(data.total_inscritos || 0)}</div>
            <p style="font-size: 0.875rem; color: #64748b; margin-top: 0.5rem;">
                Ano ${data.year}
            </p>
        </div>

        <div class="info-card" style="border-left: 4px solid ${COLORS.ch}">
            <h4>📊 Média Geral</h4>
            <div class="value">${mediaGeral.toFixed(1)}</div>
            <p style="font-size: 0.875rem; color: #64748b; margin-top: 0.5rem;">
                Todas as áreas
            </p>
        </div>

        <div class="info-card" style="border-left: 4px solid ${COLORS.redacao}">
            <h4>✍️ Média Redação</h4>
            <div class="value">${(medias.NU_NOTA_REDACAO || 0).toFixed(1)}</div>
            <p style="font-size: 0.875rem; color: #64748b; margin-top: 0.5rem;">
                ${getRedacaoInsight(medias.NU_NOTA_REDACAO)}
            </p>
        </div>

        <div class="info-card" style="border-left: 4px solid ${COLORS.mt}">
            <h4>✅ Taxa de Presença</h4>
            <div class="value">${taxaMedia.toFixed(1)}%</div>
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
    
    // Destroi gráfico anterior se existir
    if (chartInstances.main) {
        chartInstances.main.destroy();
    }
    
    const areas = data.areas || {};
    const labels = Object.keys(areas);
    const values = Object.values(areas);
    
    chartInstances.main = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: `ENEM ${data.ano}`,
                data: values,
                backgroundColor: [
                    COLORS.cn + '80',
                    COLORS.ch + '80',
                    COLORS.lc + '80',
                    COLORS.mt + '80',
                    COLORS.redacao + '80'
                ],
                borderColor: [
                    COLORS.cn,
                    COLORS.ch,
                    COLORS.lc,
                    COLORS.mt,
                    COLORS.redacao
                ],
                borderWidth: 2,
                borderRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    padding: 12,
                    titleFont: { size: 14 },
                    bodyFont: { size: 13 },
                    callbacks: {
                        label: function(context) {
                            return `Média: ${context.parsed.y.toFixed(2)} pontos`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 1000,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

// ============================================================================
// FUNÇÕES DE VISUALIZAÇÕES ESPECIAIS
// ============================================================================

/**
 * Atualiza a visualização atual
 */
function updateView() {
    // Esconde todas as seções
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

/**
 * Esconde todas as seções
 */
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

/**
 * Carrega estatísticas detalhadas
 */
async function loadStatistics() {
    const container = document.getElementById('detailedData');
    container.innerHTML = '<p>Carregando estatísticas...</p>';
    
    try {
        const response = await fetch(`${API_URL}/api/enem/estatisticas/${currentYear}`);
        const data = await response.json();
        
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
            if (valor) {
                html += `
                    <li style="padding: 0.75rem; border-bottom: 1px solid #e2e8f0; display: flex; justify-content: space-between;">
                        <span>${nome}</span>
                        <strong>${valor.toFixed(2)} pontos</strong>
                    </li>
                `;
            }
        }
        
        html += `
                    </ul>
                </div>
                
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
            if (valor !== undefined) {
                html += `
                    <li style="padding: 0.75rem; border-bottom: 1px solid #e2e8f0; display: flex; justify-content: space-between;">
                        <span>${nome}</span>
                        <strong>${valor.toFixed(2)}%</strong>
                    </li>
                `;
            }
        }
        
        html += `
                    </ul>
                </div>
            </div>
        `;
        
        container.innerHTML = html;
        
    } catch (error) {
        console.error('Erro ao carregar estatísticas:', error);
        container.innerHTML = '<p style="color: #ef4444;">Erro ao carregar estatísticas</p>';
    }
}

/**
 * Carrega dados regionais
 */
async function loadRegionalData() {
    const container = document.getElementById('regionalData');
    container.innerHTML = '<p>Carregando dados regionais...</p>';
    
    try {
        const response = await fetch(`${API_URL}/api/enem/por-estado/${currentYear}?top=10`);
        const data = await response.json();
        
        let html = '';
        
        for (const [uf, info] of Object.entries(data.estados)) {
            const mediaGeral = calculateGeneralAverage(info.medias);
            
            html += `
                <div class="tool-card" style="background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                    <h4 style="color: #2563eb; margin-bottom: 1rem;">${uf}</h4>
                    <p style="font-size: 1.25rem; font-weight: bold; margin-bottom: 0.5rem;">
                        ${mediaGeral.toFixed(1)} pontos
                    </p>
                    <p style="font-size: 0.875rem; color: #64748b;">
                        ${formatNumber(info.total)} inscritos
                    </p>
                </div>
            `;
        }
        
        container.innerHTML = html || '<p>Nenhum dado regional encontrado</p>';
        
    } catch (error) {
        console.error('Erro ao carregar dados regionais:', error);
        container.innerHTML = '<p style="color: #ef4444;">Erro ao carregar dados regionais</p>';
    }
}

/**
 * Carrega comparação entre anos
 */
async function loadComparisonData() {
    try {
        const response = await fetch(`${API_URL}/api/enem/evolucao`);
        const data = await response.json();
        
        // Atualiza gráfico de comparação
        updateComparisonChart(data);
        
        // Atualiza cards de comparação
        updateComparisonCards(data);
        
    } catch (error) {
        console.error('Erro ao carregar comparação:', error);
        showError('Erro ao carregar comparação entre anos');
    }
}

/**
 * Atualiza gráfico de comparação
 */
function updateComparisonChart(data) {
    const canvas = document.getElementById('comparisonChart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    if (chartInstances.comparison) {
        chartInstances.comparison.destroy();
    }
    
    const datasets = Object.keys(data.evolucao_por_area).map(area => {
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
            labels: data.anos,
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        usePointStyle: true,
                        padding: 15
                    }
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    padding: 12
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 1000,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                }
            }
        }
    });
}

/**
 * Atualiza cards de comparação
 */
function updateComparisonCards(data) {
    const container = document.getElementById('comparisonGrid');
    
    let html = '';
    
    for (const [area, values] of Object.entries(data.evolucao_por_area)) {
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
                    <strong>${val.toFixed(1)}</strong>
                </div>
            `;
        });
        
        html += `
                <div style="display: flex; justify-content: space-between; padding: 0.75rem 0; margin-top: 0.5rem; border-top: 2px solid #e2e8f0;">
                    <span style="font-weight: 600;">${trendText}</span>
                    <strong style="color: ${trendColor}">
                        ${trend > 0 ? '+' : ''}${trend.toFixed(1)}
                    </strong>
                </div>
            </div>
        `;
    }
    
    container.innerHTML = html;
}

/**
 * Carrega comparação público vs privado
 */
async function loadSchoolComparison() {
    hideAllSections();
    document.getElementById('schoolSection').style.display = 'block';
    
    const container = document.getElementById('schoolData');
    container.innerHTML = '<p>Carregando comparação...</p>';
    
    try {
        const response = await fetch(`${API_URL}/api/enem/por-escola/${currentYear}`);
        const data = await response.json();
        
        const tipos = data.tipos_escola;
        
        let html = '';
        
        for (const [tipo, info] of Object.entries(tipos)) {
            const tipoNome = tipo === 'publica' ? '🏫 Escola Pública' : '🏛️ Escola Privada';
            const mediaGeral = calculateGeneralAverage(info.medias);
            const color = tipo === 'publica' ? COLORS.ch : COLORS.mt;
            
            html += `
                <div class="tool-card" style="background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); border-left: 4px solid ${color};">
                    <h4 style="color: ${color}; margin-bottom: 1rem;">${tipoNome}</h4>
                    <p style="font-size: 1.5rem; font-weight: bold; margin-bottom: 0.5rem;">
                        ${mediaGeral.toFixed(1)} pontos
                    </p>
                    <p style="font-size: 0.875rem; color: #64748b; margin-bottom: 1rem;">
                        ${formatNumber(info.total)} inscritos
                    </p>
                    <h5 style="margin-top: 1rem; margin-bottom: 0.5rem;">Médias por Área:</h5>
                    <ul style="list-style: none; padding: 0;">
            `;
            
            for (const [key, value] of Object.entries(info.medias)) {
                const nomeArea = key.replace('NU_NOTA_', '').replace('_', ' ');
                html += `
                    <li style="padding: 0.25rem 0; display: flex; justify-content: space-between;">
                        <span style="font-size: 0.875rem;">${nomeArea}</span>
                        <strong style="font-size: 0.875rem;">${value.toFixed(1)}</strong>
                    </li>
                `;
            }
            
            html += `
                    </ul>
                </div>
            `;
        }
        
        container.innerHTML = html;
        
    } catch (error) {
        console.error('Erro ao carregar comparação escolar:', error);
        container.innerHTML = '<p style="color: #ef4444;">Erro ao carregar dados</p>';
    }
}

/**
 * Carrega análise de presença
 */
async function loadPresenceAnalysis() {
    hideAllSections();
    document.getElementById('presenceSection').style.display = 'block';
    
    const container = document.getElementById('presenceData');
    container.innerHTML = '<p>Carregando análise de presença...</p>';
    
    try {
        const response = await fetch(`${API_URL}/api/enem/presenca/${currentYear}`);
        const data = await response.json();
        
        let html = `
            <div style="background: white; border-radius: 12px; padding: 2rem; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                <h3>✅ Taxa de Presença - ENEM ${data.ano}</h3>
                <div style="margin-top: 1.5rem;">
        `;
        
        const presencaMap = {
            'TP_PRESENCA_CN': 'Ciências da Natureza',
            'TP_PRESENCA_CH': 'Ciências Humanas',
            'TP_PRESENCA_LC': 'Linguagens e Códigos',
            'TP_PRESENCA_MT': 'Matemática'
        };
        
        for (const [key, nome] of Object.entries(presencaMap)) {
            const valor = data.taxa_presenca[key];
            if (valor !== undefined) {
                const porcentagem = valor.toFixed(2);
                const width = valor;
                
                html += `
                    <div style="margin-bottom: 1.5rem;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                            <span style="font-weight: 600;">${nome}</span>
                            <span style="font-weight: bold; color: ${COLORS.cn}">${porcentagem}%</span>
                        </div>
                        <div style="background: #e2e8f0; border-radius: 8px; height: 24px; overflow: hidden;">
                            <div style="background: linear-gradient(90deg, ${COLORS.cn}, ${COLORS.ch}); width: ${width}%; height: 100%; border-radius: 8px; transition: width 0.3s ease;"></div>
                        </div>
                    </div>
                `;
            }
        }
        
        html += `
                </div>
            </div>
        `;
        
        container.innerHTML = html;
        
    } catch (error) {
        console.error('Erro ao carregar análise de presença:', error);
        container.innerHTML = '<p style="color: #ef4444;">Erro ao carregar dados</p>';
    }
}

/**
 * Carrega insights para preparação
 */
async function loadInsights() {
    hideAllSections();
    document.getElementById('insightsSection').style.display = 'block';
    
    const container = document.getElementById('insightsData');
    container.innerHTML = '<p>Carregando insights...</p>';
    
    try {
        const response = await fetch(`${API_URL}/api/enem/insights`);
        const data = await response.json();
        
        let html = `
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 2rem; border-radius: 12px;">
                <h3 style="margin-bottom: 1.5rem;">💡 Como se Preparar Melhor</h3>
                
                <div style="margin-bottom: 1.5rem;">
                    <h4 style="margin-bottom: 1rem;">⚠️ Áreas que Precisam de Mais Atenção:</h4>
                    <ul style="list-style: none; padding: 0;">
        `;
        
        if (data.areas_menor_desempenho && data.areas_menor_desempenho.length > 0) {
            data.areas_menor_desempenho.forEach(area => {
                html += `
                    <li style="padding: 0.75rem; background: rgba(255,255,255,0.1); margin-bottom: 0.5rem; border-radius: 8px;">
                        <strong>${area.area}</strong> - Média: ${area.media.toFixed(1)} pontos
                    </li>
                `;
            });
        }
        
        html += `
                    </ul>
                </div>
                
                <div>
                    <h4 style="margin-bottom: 1rem;">📚 Dicas de Preparação:</h4>
                    <ul style="padding-left: 1.5rem;">
        `;
        
        if (data.dicas && data.dicas.length > 0) {
            data.dicas.forEach(dica => {
                html += `<li style="padding: 0.5rem 0;">${dica}</li>`;
            });
        } else {
            html += '<li>Continue seus estudos com dedicação e consistência!</li>';
        }
        
        html += `
                    </ul>
                </div>
            </div>
        `;
        
        container.innerHTML = html;
        
    } catch (error) {
        console.error('Erro ao carregar insights:', error);
        container.innerHTML = '<p style="color: #ef4444;">Erro ao carregar insights</p>';
    }
}

// ============================================================================
// FUNÇÕES UTILITÁRIAS
// ============================================================================

/**
 * Formata número com separador de milhares
 */
function formatNumber(num) {
    return new Intl.NumberFormat('pt-BR').format(num);
}

/**
 * Calcula média geral de todas as notas
 */
function calculateGeneralAverage(medias) {
    if (!medias || Object.keys(medias).length === 0) return 0;
    const values = Object.values(medias).filter(v => v > 0);
    if (values.length === 0) return 0;
    return values.reduce((a, b) => a + b, 0) / values.length;
}

/**
 * Calcula taxa de presença média
 */
function calculatePresenceRate(taxas) {
    if (!taxas || Object.keys(taxas).length === 0) return 0;
    const values = Object.values(taxas).filter(v => typeof v === 'number' && !isNaN(v));
    if (values.length === 0) return 0;
    return values.reduce((a, b) => a + b, 0) / values.length;
}