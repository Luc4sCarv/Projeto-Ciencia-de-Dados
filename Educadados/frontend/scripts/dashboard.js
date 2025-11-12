// Simular carregamento de dados
        window.addEventListener('load', function() {
            const cards = document.querySelectorAll('.info-card');
            cards.forEach((card, index) => {
                card.classList.add('loading');
                setTimeout(() => {
                    card.classList.remove('loading');
                }, 500 + (index * 200));
            });
        });

        // Funcionalidade dos botões de controle
        const controlBtns = document.querySelectorAll('.control-btn');
        controlBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                const action = this.textContent.trim();
                console.log('Ação executada:', action);
                // Aqui você pode adicionar funcionalidades específicas
                alert(`Funcionalidade "${action}" em desenvolvimento!`);
            });
        });

        // Funcionalidade das ferramentas
        const toolCards = document.querySelectorAll('.tool-card');
        toolCards.forEach(card => {
            card.addEventListener('click', function() {
                const toolName = this.querySelector('h4').textContent;
                console.log('Ferramenta selecionada:', toolName);
                alert(`Abrindo: ${toolName}`);
            });
        });

        // Filtros
        const filterInput = document.querySelector('.filter-input');
        if (filterInput) {
        filterInput.addEventListener('input', function() {
                console.log('Filtro aplicado:', this.value);
                // Implementar lógica de filtro aqui
            });
      }

        const checkboxes = document.querySelectorAll('input[type="checkbox"]');
        checkboxes.forEach(checkbox => {
            checkbox.addEventListener('change', function() {
                console.log('Categoria selecionada:', this.nextSibling.textContent.trim());
                // Implementar lógica de filtragem por categoria
            });
        });

// ADICIONADO CONFORME IMAGEM
function logout() {
  if(confirm('Deseja realmente sair?')) {
    window.location.href = 'index.html';
  }
}

// Aguarda o HTML ser totalmente carregado
document.addEventListener('DOMContentLoaded', () => {
    carregarDadosDoDashboard();
});

// Função para buscar os dados do nosso ARQUIVO JSON
async function carregarDadosDoDashboard() {
    try {
        // Faz a requisição para o arquivo JSON local
        // O caminho é relativo ao HTML (dashboard.html)
        const response = await fetch('data/dashboard_stats.json'); 
        
        if (!response.ok) {
            throw new Error('Falha ao carregar arquivo de dados. Verifique o caminho.');
        }
        
        const dados = await response.json();

        // Atualiza o HTML com os dados recebidos
        atualizarValoresNoHTML(dados);

    } catch (error) {
        console.error('Erro:', error);
        // Se falhar, os dados estáticos do HTML permanecerão visíveis
    }
}

// Função para atualizar o HTML (esta não muda)
function atualizarValoresNoHTML(dados) {
    const elTotalEscolas = document.getElementById('total-escolas');
    const elIdebMedio = document.getElementById('ideb-medio');
    const elTaxaAprovacao = document.getElementById('taxa-aprovacao');
    const elAlunosMatriculados = document.getElementById('alunos-matriculados');

    if (elTotalEscolas) elTotalEscolas.textContent = dados.totalEscolas;
    if (elIdebMedio) elIdebMedio.textContent = dados.idebMedio;
    if (elTaxaAprovacao) elTaxaAprovacao.textContent = dados.taxaAprovacao;
    if (elAlunosMatriculados) elAlunosMatriculados.textContent = dados.alunosMatriculados;
}

// Função de logout (você já tinha no HTML)
function logout() {
    console.log("Usuário deslogado.");
    window.location.href = 'index.html';
}